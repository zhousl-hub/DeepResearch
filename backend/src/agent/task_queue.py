"""基于 Redis Streams 的任务队列和事件流。

职责：
  - 任务入队：XADD research:tasks
  - 后台消费：XREADGROUP + 执行 LangGraph 图 + XACK
  - 事件发布：XADD research:events:{task_id}
  - SSE 读取：XREAD research:events:{task_id}

整个模块在 FastAPI 进程内以 asyncio 协程运行，无需独立 Worker 进程。
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import uuid

import redis.asyncio as redis
from langchain_core.messages import HumanMessage, AIMessage
from loguru import logger

from agent.graph import build_graph
from langgraph.checkpoint.redis.aio import AsyncRedisSaver

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
TASK_STREAM = "research:tasks"
EVENT_STREAM_PREFIX = "research:events"
CONSUMER_GROUP = "research-workers"
# 单个任务的事件流最大保留条数，防止无限增长
EVENT_STREAM_MAXLEN = 500
# XREAD 阻塞超时（毫秒），避免空轮询
STREAM_BLOCK_MS = 5000

# ── 子图内部节点名 → 前端事件名映射 ──────────────────────────────
# 重构为子图架构后，graph.astream() 需启用 subgraphs=True 才能获取子图内部事件。
# 子图内部节点名与前端约定的扁平事件名不一致，此处做翻译。
_SUBGRAPH_EVENT_MAP = {
    "generate_queries": "generate_query",
    "web_search": "web_research",
    "critique": "reflection",
}

_redis: redis.Redis | None = None
_persistent_graph = None  # 延迟初始化，带 Redis checkpoint 持久化


def _redis_client_kwargs() -> dict:
    """跨机器 Redis 长连接参数.

    长任务（如 Critic 十几分钟）期间连接不能空闲被掐断：
    - socket_keepalive：启用 TCP keepalive
    - health_check_interval：周期性 PING，避免 NAT/中间盒掐半开连接
    - retry_on_timeout：瞬时超时自动重试
    - 不设短 socket_timeout：避免 XREAD block 与长空闲后的误杀
    """
    return {
        "decode_responses": True,
        "socket_connect_timeout": 5,
        "socket_keepalive": True,
        "health_check_interval": 30,
        "retry_on_timeout": True,
    }


def _is_redis_transport_error(exc: BaseException) -> bool:
    """判断是否为 Redis 传输层断开（需重建连接）."""
    msg = str(exc).lower()
    name = type(exc).__name__
    return (
        name in {"TimeoutError", "ConnectionError", "ConnectionResetError", "OSError", "RuntimeError"}
        and any(
            s in msg
            for s in (
                "closed",
                "handler is closed",
                "connection",
                "timeout reading",
                "broken pipe",
                "connect",
            )
        )
    )


async def _reset_redis() -> None:
    """关闭并丢弃当前 Redis 客户端，下次取用时重建."""
    global _redis
    if _redis is not None:
        try:
            await _redis.aclose()
        except Exception:
            pass
        _redis = None


async def _get_redis() -> redis.Redis:
    """延迟获取 Redis 连接（复用同一个连接池）."""
    global _redis
    if _redis is None:
        _redis = redis.from_url(REDIS_URL, **_redis_client_kwargs())
    return _redis


async def _get_graph(*, force_new: bool = False):
    """获取带 Redis 持久化的编译图（延迟初始化 + 单例）.

    force_new=True 时丢弃旧图（通常因 checkpointer 底层连接已死）。
    """
    global _persistent_graph
    if force_new:
        _persistent_graph = None
    if _persistent_graph is None:
        checkpointer = AsyncRedisSaver(
            REDIS_URL,
            ttl={"default_ttl": 60 * 24 * 7, "refresh_on_read": True},
        )
        await checkpointer.asetup()
        _persistent_graph = build_graph(checkpointer=checkpointer)
        logger.info("[TaskQueue] 已创建 AsyncRedisSaver 持久化图（TTL=7天）")
    return _persistent_graph


# ═══════════════════════════════════════════════════════════════════════
# 任务入队
# ═══════════════════════════════════════════════════════════════════════

async def enqueue_task(
    messages: list[dict],
    initial_search_query_count: int,
    max_research_loops: int,
    reasoning_model: str,
    plan_status: str = "unconfirmed",
    plan: str = "",
    task_id: str = "",
) -> str:
    """将研究任务写入 Redis Stream，返回 task_id。

    调用方（POST /api/research）拿到 task_id 后立即返回给前端。
    如果传入 task_id 则复用，否则生成新的 UUID。
    """
    r = await _get_redis()
    reuse_task_id = bool(task_id)
    if not task_id:
        task_id = str(uuid.uuid4())
    # 确认后续跑会复用同一 task_id：先清空旧事件流，避免 SSE 从 0 回放历史
    # task_paused 后立刻断开，导致前端看不到后续研究与终稿。
    if reuse_task_id:
        stream_key = f"{EVENT_STREAM_PREFIX}:{task_id}"
        deleted = await r.delete(stream_key)
        if deleted:
            logger.info(f"[TaskQueue] 已清空旧事件流 task_id={task_id[:8]}...")
    task_payload = json.dumps({
        "task_id": task_id,
        "messages": messages,
        "initial_search_query_count": initial_search_query_count,
        "max_research_loops": max_research_loops,
        "reasoning_model": reasoning_model,
        "plan_status": plan_status,
        "plan": plan,
    })
    await r.xadd(TASK_STREAM, {"task": task_payload}, maxlen=1000)
    logger.info(f"[TaskQueue] 任务已入队 task_id={task_id[:8]}...")
    return task_id


# ═══════════════════════════════════════════════════════════════════════
# 后台消费协程（FastAPI startup 时启动）
# ═══════════════════════════════════════════════════════════════════════

async def start_worker() -> None:
    """启动后台消费协程，不阻塞 HTTP 请求处理。

    调用方式（在 app.py 的 startup 事件中）：
        asyncio.create_task(start_worker())
    """
    r = await _get_redis()
    await _ensure_consumer_group(r)
    logger.info("[TaskQueue] worker 协程已启动，等待任务...")
    while True:
        try:
            await _process_one_task(r)
        except asyncio.CancelledError:
            logger.info("[TaskQueue] worker 协程被取消")
            break
        except Exception as exc:
            if _is_redis_transport_error(exc):
                logger.warning(
                    f"[TaskQueue] Redis 连接异常，重建后继续 ({type(exc).__name__}): {exc}"
                )
                await _reset_redis()
                # checkpointer 可能也已死，下次任务强制重建
                await _get_graph(force_new=True)
                r = await _get_redis()
                try:
                    await _ensure_consumer_group(r)
                except Exception as group_exc:
                    logger.warning(f"[TaskQueue] 重建 Consumer Group 失败: {group_exc}")
                await asyncio.sleep(0.5)
                continue
            logger.error(f"[TaskQueue] worker 异常 ({type(exc).__name__}): {exc}")
            await asyncio.sleep(1)  # 短暂等待后继续


async def _ensure_consumer_group(r: redis.Redis) -> None:
    """创建 Consumer Group（如果不存在）."""
    try:
        await r.xgroup_create(TASK_STREAM, CONSUMER_GROUP, id="0", mkstream=True)
        logger.info(f"[TaskQueue] Consumer Group '{CONSUMER_GROUP}' 已创建")
    except redis.ResponseError as e:
        if "BUSYGROUP" in str(e):
            logger.debug(f"[TaskQueue] Consumer Group 已存在，跳过创建")
        else:
            raise


async def _process_one_task(r: redis.Redis) -> None:
    """消费并执行一个任务."""
    # 从 Consumer Group 读取一条待处理任务
    result = await r.xreadgroup(
        CONSUMER_GROUP,
        "worker-1",  # 消费者名称（多实例时每实例一个唯一名）
        {TASK_STREAM: ">"},
        block=STREAM_BLOCK_MS,
        count=1,
    )
    if not result:
        return  # 超时，没有任务

    stream_name, messages = result[0]
    redis_msg_id, payload = messages[0]
    task = json.loads(payload["task"])
    task_id = task["task_id"]

    plan_status = task.get("plan_status", "unconfirmed")
    logger.info(
        f"[流水线] ① 开始执行 task_id={task_id[:8]}... "
        f"plan_status={plan_status} model={task.get('reasoning_model') or '-'} "
        f"loops={task.get('max_research_loops')} queries={task.get('initial_search_query_count')}"
    )

    try:
        # 重建消息列表（保留完整历史及原始 ID，确保 add_messages 按 ID 正确去重）
        messages = [
            HumanMessage(content=m["content"], id=m.get("id")) if m.get("type") == "human"
            else AIMessage(content=m["content"], id=m.get("id")) if m.get("type") == "ai"
            else None
            for m in task["messages"]
        ]
        messages = [m for m in messages if m is not None]

        # 这个函数将大模型流式输出的token借助Redis也流式输出到前端页面（供节点内 Agent 使用）
        async def emit_token(text: str, node: str) -> None:
            """将 LLM token 推送到 Redis 事件流."""
            try:
                event_json = json.dumps(
                    {"token": {"text": text, "node": node}},
                    ensure_ascii=False,
                )
                await r.xadd(
                    f"{EVENT_STREAM_PREFIX}:{task_id}",
                    {"event": event_json},
                    maxlen=EVENT_STREAM_MAXLEN,
                )
            except Exception as exc:
                logger.warning(f"[TaskQueue] token事件发送失败 node={node}: {exc}")

        config = {
            "configurable": {
                "thread_id": task_id,  # 将 task_id 作为 LangGraph 的 checkpoint thread_id
                "initial_search_query_count": task["initial_search_query_count"],
                "max_research_loops": task["max_research_loops"],
                "reasoning_model": task["reasoning_model"],
                "_emit_token": emit_token,
            }
        }

        # 图初始状态（支持 plan 确认后的 resume 场景）
        initial_state: dict = {
            "messages": messages,
            "plan_status": plan_status,
            "plan": task.get("plan", ""),
        }

        # 节点名 → 可读步骤说明（日志过滤用关键字：[流水线]）
        _STEP_LABELS = {
            "generate_plan": "② 生成研究计划",
            "evaluate_plan": "②b 评估计划路由",
            "awaiting_plan_confirmation": "②c 等待需求确认",
            "confirm_plan": "②d 确认计划/补充需求",
            "replan": "②e 重新规划",
            "generate_queries": "③ 生成搜索查询",
            "generate_query": "③ 生成搜索查询",
            "web_search": "④ 网络搜索",
            "web_research": "④ 网络搜索",
            "critique": "⑤ 研究反思/评估",
            "reflection": "⑤ 研究反思/评估",
            "research": "③ 研究子图完成",
            "outline": "⑥ 撰写提纲",
            "draft": "⑦ 撰写/修订草稿",
            "critic_review": "⑧ 审稿打分",
            "cite_and_polish": "⑨ 引用润色终稿",
            "write": "⑨ 写作子图完成",
        }

        # 执行图（Checkpointer可绑定 Redis，通过 thread_id 实现会话隔离）
        # subgraphs=True: 穿透子图边界，获取内部节点事件
        # 事件格式: (namespace, {node_name: node_output})
        # event = (("research:abc123",), {"generate_queries": {...}})
        #         └──── namespace ────┘  └──────── data ──────────┘
        #   - 父图节点:  namespace = (),     data = {"generate_plan": {...}}
        #   - 子图内部:  namespace = ("research:<id>",), data = {"generate_queries": {...}}
        final_answer_event = None
        persistent_graph = await _get_graph()
        async for event in persistent_graph.astream(initial_state, config, subgraphs=True):
            # ── 解析 subgraphs=True 的 2 元组格式 ─────────────────────
            #避免处理非节点事件，如：子图进入/退出时的边界事件、LangGraph调度层面的内部生命周期事件
            if not isinstance(event, tuple) or len(event) != 2:
                continue

            namespace: tuple = event[0]
            data: dict = event[1]

            if not isinstance(data, dict) or not data:
                continue

            # 从 data 中提取原始节点名和节点输出
            node_name = list(data.keys())[0]
            node_output = data[node_name]

            # 跳过 LangGraph 内部事件
            if not node_name or str(node_name).startswith("__"):
                continue

            # ── 事件名翻译：子图内部节点 → 前端扁平事件名 ────────────
            is_subgraph = len(namespace) > 0
            frontend_event_name = (
                _SUBGRAPH_EVENT_MAP.get(node_name, node_name)
                if is_subgraph
                else node_name
            )
            translated_event = {frontend_event_name: node_output}

            # 关键步骤一行日志，便于 tail/rg 跟踪进度（不打印大段正文）
            step_label = _STEP_LABELS.get(node_name) or _STEP_LABELS.get(frontend_event_name)
            if step_label:
                detail = ""
                if isinstance(node_output, dict):
                    if "plan" in node_output and isinstance(node_output["plan"], str):
                        detail = f" plan_chars={len(node_output['plan'])}"
                    if "search_query" in node_output:
                        qs = node_output.get("search_query") or []
                        detail = f" queries={len(qs) if isinstance(qs, list) else 1}"
                    if "report_draft" in node_output and isinstance(node_output["report_draft"], str):
                        detail = f" draft_chars={len(node_output['report_draft'])}"
                    if "critic_score" in node_output:
                        detail = (
                            f" score={node_output.get('critic_score')} "
                            f"ready={node_output.get('ready_for_polish')}"
                        )
                    if "revision_count" in node_output:
                        detail += f" rev={node_output.get('revision_count')}"
                scope = "子图" if is_subgraph else "主图"
                logger.info(
                    f"[流水线] {step_label} task={task_id[:8]}... "
                    f"node={node_name} ({scope}){detail}"
                )

            # 写入 Redis 事件流（前端根据事件名更新 UI，如气泡的显示，页面文本的合并等等或关闭SSE连接）
            event_json = json.dumps(translated_event, default=str, ensure_ascii=False)
            await r.xadd(
                f"{EVENT_STREAM_PREFIX}:{task_id}",
                {"event": event_json},
                maxlen=EVENT_STREAM_MAXLEN,
            )

            # 如果是 writer 子图返回（包含最终报告），提取为 finalize_answer
            if frontend_event_name == "write" and isinstance(node_output, dict):
                if "messages" in node_output:
                    # 子图返回的消息列表可能包含历史消息（由 add_messages reducer 累积），
                    # 取最后一条 AI 消息作为最终报告内容
                    msgs = node_output["messages"]
                    ai_msgs = [m for m in msgs if getattr(m, "type", None) == "ai"]
                    final_msg = ai_msgs[-1] if ai_msgs else (msgs[-1] if msgs else None)
                    if final_msg:
                        final_answer_event = {
                            "finalize_answer": {
                                "messages": [
                                    {"content": final_msg.content, "type": "ai"}
                                ]
                            }
                        }

        # 判断是正常完成还是暂停在 Plan 确认
        if final_answer_event:
            logger.info(f"[流水线] ⑩ 终稿完成 task_id={task_id[:8]}... → finalize_answer")
            # 图正常完成 → 发射 finalize_answer
            event_json = json.dumps(final_answer_event, default=str, ensure_ascii=False)
            await r.xadd(
                f"{EVENT_STREAM_PREFIX}:{task_id}",
                {"event": event_json},
                maxlen=EVENT_STREAM_MAXLEN,
            )
        else:
            logger.info(f"[流水线] ⑩ 暂停待确认 task_id={task_id[:8]}... → task_paused")
            # 图执行完毕但未生成最终答案 → 在 Plan 确认处暂停
            pause_json = json.dumps({"task_paused": True}, ensure_ascii=False)
            await r.xadd(
                f"{EVENT_STREAM_PREFIX}:{task_id}",
                {"event": pause_json},
                maxlen=EVENT_STREAM_MAXLEN,
            )

        # 任务终态立即持久化到 Postgres（不依赖用户刷新才写库）
        try:
            await build_task_snapshot(task_id)
        except Exception as persist_exc:
            logger.warning(
                f"[TaskQueue] 任务结束持久化失败 ({type(persist_exc).__name__}): {persist_exc}"
            )

    except Exception as exc:
        logger.error(f"[TaskQueue] 任务失败 task_id={task_id[:8]}... ({type(exc).__name__}): {exc}")
        # 将错误作为事件推送给前端（连接已死时尽量重连再写）
        error_json = json.dumps({"error": str(exc)}, ensure_ascii=False)
        try:
            if _is_redis_transport_error(exc):
                await _reset_redis()
                r = await _get_redis()
                await _get_graph(force_new=True)
            await r.xadd(
                f"{EVENT_STREAM_PREFIX}:{task_id}",
                {"event": error_json},
                maxlen=EVENT_STREAM_MAXLEN,
            )
        except Exception as publish_exc:
            logger.error(
                f"[TaskQueue] 错误事件写入失败 ({type(publish_exc).__name__}): {publish_exc}"
            )
        try:
            await build_task_snapshot(task_id)
        except Exception as persist_exc:
            logger.warning(
                f"[TaskQueue] 失败任务持久化失败 ({type(persist_exc).__name__}): {persist_exc}"
            )

    finally:
        # 确认消息已处理
        try:
            await r.xack(TASK_STREAM, CONSUMER_GROUP, redis_msg_id)
            # 清理事件流（设置过期，24 小时后自动删除）
            await r.expire(f"{EVENT_STREAM_PREFIX}:{task_id}", 86400)
        except Exception as cleanup_exc:
            if _is_redis_transport_error(cleanup_exc):
                await _reset_redis()
            logger.warning(
                f"[TaskQueue] 任务收尾失败 ({type(cleanup_exc).__name__}): {cleanup_exc}"
            )



# ═══════════════════════════════════════════════════════════════════════
# SSE 事件读取
# ═══════════════════════════════════════════════════════════════════════

async def read_task_events(task_id: str, last_event_id: str = "0"):
    """Generator: 从 Redis Stream 读取任务事件，用于 SSE 推送。

    支持断线重连：客户端通过 SSE 的 Last-Event-ID / after 查询参数传入 last_event_id，
    服务端从该 ID 之后开始推送。

    yield 值为 (msg_id, event_str)，供上层写出标准 SSE id 字段。
    """
    r = await _get_redis()
    stream_key = f"{EVENT_STREAM_PREFIX}:{task_id}"
    current_id = last_event_id or "0"

    while True:
        try:
            result = await r.xread(
                {stream_key: current_id},
                block=STREAM_BLOCK_MS,
                count=10,
            )
            if result:
                for _, messages in result:
                    for msg_id, data in messages:
                        event_str = data.get("event", "{}")
                        current_id = msg_id
                        yield msg_id, event_str

                        # 检查是否为终止事件（错误 / finalize_answer / task_paused）
                        try:
                            event = json.loads(event_str)
                            if any(k in event for k in ("error", "finalize_answer", "task_paused")):
                                return  # 任务结束，关闭 SSE 连接
                        except json.JSONDecodeError:
                            pass

        except asyncio.CancelledError:
            break
        except Exception as exc:
            # Redis 瞬时超时在长阻塞 XREAD 时较常见，降频避免刷屏淹没流水线日志
            if _is_redis_transport_error(exc):
                logger.warning(
                    f"[TaskQueue] SSE Redis 瞬断，重建连接后继续 "
                    f"({type(exc).__name__}): {exc}"
                )
                await _reset_redis()
                r = await _get_redis()
                await asyncio.sleep(1)
            else:
                logger.warning(f"[TaskQueue] SSE 读取异常 ({type(exc).__name__}): {exc}")
                await asyncio.sleep(1)


async def _persist_snapshot_to_db(snapshot: dict) -> None:
    """将快照写入 Postgres，消除 Redis 事件过期后无法恢复的问题."""
    try:
        from agent.db.threads import save_thread_snapshot

        await save_thread_snapshot(
            snapshot["task_id"],
            status=snapshot.get("status") or "running",
            messages=snapshot.get("messages") or [],
            report=snapshot.get("report") or "",
            error=snapshot.get("error") or "",
        )
    except Exception as exc:
        logger.warning(f"[TaskQueue] 持久化会话快照失败 ({type(exc).__name__}): {exc}")


async def build_task_snapshot(task_id: str) -> dict:
    """重建任务快照：优先 Redis 事件流，事件过期则读 Postgres 持久化记录.

    返回：
      status: running | paused | completed | failed | not_found
      messages: [{type, content, id}, ...]
      report: 最终报告或 draft（若有）
      error: 失败信息（若有）
    """
    r = await _get_redis()
    stream_key = f"{EVENT_STREAM_PREFIX}:{task_id}"
    if not await r.exists(stream_key):
        # Redis 事件已过期：直接使用持久化会话
        try:
            from agent.db.threads import load_durable_snapshot
            durable = await load_durable_snapshot(task_id)
            if durable is not None:
                return durable
        except Exception as exc:
            logger.debug(f"[TaskQueue] 读取持久化快照失败: {exc}")
        return {
            "task_id": task_id,
            "status": "not_found",
            "messages": [],
            "report": "",
            "error": "任务事件流不存在或已过期",
        }

    events = await r.xrange(stream_key)
    human_content = ""
    plan_content = ""
    draft_content = ""
    final_content = ""
    error = ""
    paused = False
    # 暂停后若已出现研究/写作进度，状态应回到 running，不能一直 sticky 为 paused
    progress_after_pause = False

    for _, fields in events:
        try:
            ev = json.loads(fields.get("event", "{}"))
        except json.JSONDecodeError:
            continue

        if "generate_plan" in ev and isinstance(ev["generate_plan"], dict):
            msgs = ev["generate_plan"].get("messages") or []
            # messages 可能是字符串化的 Message 列表，优先取 plan 字段
            plan_content = ev["generate_plan"].get("plan") or plan_content
            if not plan_content and msgs:
                # 取最后一条 AI 文本
                last = msgs[-1]
                if isinstance(last, dict):
                    plan_content = last.get("content", "") or plan_content
                elif isinstance(last, str) and "content=" in last:
                    # 兼容 str(AIMessage)：粗提取
                    pass

        if "awaiting_plan_confirmation" in ev:
            paused = True
            progress_after_pause = False
            msgs = (ev.get("awaiting_plan_confirmation") or {}).get("messages") or []
            if msgs and isinstance(msgs[0], str) and "content=" in msgs[0]:
                # content='...' 粗解析 Message 字符串
                m = re.search(r"content='(.*?)'(?:\s+additional_kwargs=|\s*$)", msgs[0], re.S)
                if m and not human_content:
                    human_content = m.group(1)

        if "research" in ev and isinstance(ev["research"], dict):
            if paused:
                progress_after_pause = True
            msgs = ev["research"].get("messages") or []
            if msgs and isinstance(msgs[0], str) and "content=" in msgs[0] and not human_content:
                m = re.search(r"content='(.*?)'(?:\s+additional_kwargs=|\s*$)", msgs[0], re.S)
                if m:
                    human_content = m.group(1)

        # 确认后的研究进度事件：清掉 sticky paused
        if any(k in ev for k in ("generate_query", "web_research", "reflection", "write", "draft")):
            if paused:
                progress_after_pause = True

        if "draft" in ev and isinstance(ev["draft"], dict):
            draft_content = ev["draft"].get("report_draft") or draft_content

        if "finalize_answer" in ev and isinstance(ev["finalize_answer"], dict):
            msgs = ev["finalize_answer"].get("messages") or []
            if msgs:
                final_content = msgs[0].get("content", "") if isinstance(msgs[0], dict) else str(msgs[0])

        if "task_paused" in ev:
            paused = True
            progress_after_pause = False

        if "error" in ev:
            error = str(ev["error"])
            paused = False
            progress_after_pause = False

    # 若事件里没解析出用户问题，用 user_threads.title
    if not human_content:
        try:
            from agent.db.threads import get_thread_record
            row = await get_thread_record(task_id)
            if row and row.title:
                human_content = row.title
        except Exception as exc:
            logger.debug(f"[TaskQueue] 读取 user_threads.title 失败: {exc}")

    report = final_content or draft_content
    if final_content:
        status = "completed"
        # 终稿已回填后，历史 error 事件仅作痕迹，不再作为当前状态
        error = ""
    elif error:
        status = "failed"
    elif paused and not progress_after_pause:
        status = "paused"
    else:
        status = "running"

    # 终态会话优先保留 DB 中已追加的 session_act 对话
    durable_messages: list[dict] = []
    if status in ("completed", "paused", "failed"):
        try:
            from agent.db.threads import load_durable_snapshot
            durable = await load_durable_snapshot(task_id)
            if durable and len(durable.get("messages") or []) > 3:
                durable_messages = durable["messages"]
        except Exception:
            pass

    messages: list[dict] = []
    if durable_messages:
        messages = durable_messages
        # 若持久化消息尚无报告而事件流已有，则补上报告气泡
        has_long_ai = any(
            m.get("type") == "ai" and len(str(m.get("content") or "")) > 800
            for m in messages
        )
        if report and not has_long_ai:
            messages.append({"type": "ai", "content": report, "id": str(len(messages) + 1)})
    else:
        if human_content:
            messages.append({"type": "human", "content": human_content, "id": "1"})
        if plan_content:
            messages.append({"type": "ai", "content": plan_content, "id": "2"})
        if report:
            note = ""
            if not final_content and draft_content:
                note = (
                    "\n\n---\n> 说明：任务在审稿修订阶段因 Redis 连接中断未完成终稿润色；"
                    "以下为已生成的研究初稿（draft）。\n"
                )
            messages.append({
                "type": "ai",
                "content": report + note,
                "id": "3",
            })

    snapshot = {
        "task_id": task_id,
        "status": status,
        "messages": messages,
        "report": report,
        "error": error,
        "has_draft": bool(draft_content),
        "has_final": bool(final_content),
        "source": "redis",
    }

    # 终态写入 Postgres，供历史列表与事件过期后恢复
    if status in ("completed", "paused", "failed"):
        await _persist_snapshot_to_db(snapshot)

    return snapshot


async def publish_draft_as_final(task_id: str, report: str | None = None) -> dict:
    """将已有 draft（或传入正文）发布为 finalize_answer，便于界面恢复查看.

    不重跑搜索；用于长任务中断后的结果回填。
    """
    snapshot = await build_task_snapshot(task_id)
    content = (report or snapshot.get("report") or "").strip()
    if not content:
        return {"ok": False, "error": "没有可发布的 draft/报告内容"}

    # 去掉恢复说明尾巴，避免重复叠加
    marker = "\n\n---\n> 说明：任务在审稿修订阶段"
    if marker in content:
        content = content.split(marker, 1)[0].rstrip()

    r = await _get_redis()
    event = {
        "finalize_answer": {
            "messages": [{"content": content, "type": "ai"}],
        }
    }
    await r.xadd(
        f"{EVENT_STREAM_PREFIX}:{task_id}",
        {"event": json.dumps(event, ensure_ascii=False)},
        maxlen=EVENT_STREAM_MAXLEN,
    )
    await r.expire(f"{EVENT_STREAM_PREFIX}:{task_id}", 86400)
    logger.info(f"[TaskQueue] 已发布 draft 为 finalize task_id={task_id[:8]}...")
    return {"ok": True, "task_id": task_id, "chars": len(content)}
