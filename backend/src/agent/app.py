# mypy: disable - error - code = "no-untyped-def,misc"
import pathlib
import json
import asyncio
import traceback
from contextlib import asynccontextmanager
from fastapi import FastAPI, Response, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, StreamingResponse
from loguru import logger
from agent.logger import setup_logger, log_request_details
from agent.configuration import Configuration, load_available_models_from_env
from agent.task_queue import (
    enqueue_task,
    start_worker,
    read_task_events,
    build_task_snapshot,
    publish_draft_as_final,
)
from agent.session_act import handle_session_act
from agent.auth.middleware import AuthMiddleware
from agent.auth.routes import router as auth_router

# ── 应用 lifespan（管理后台任务启动/关闭）───────────────────────────


@asynccontextmanager
async def _app_lifespan(app: FastAPI):
    """应用级 lifespan：管理后台任务的启动和关闭."""
    # 补齐 user_threads 会话持久化列
    try:
        from agent.db.threads import ensure_thread_schema
        await ensure_thread_schema()
    except Exception as exc:
        logger.warning(f"[数据库] 会话表结构检查失败 ({type(exc).__name__}): {exc}")
    try:
        asyncio.create_task(start_worker())
    except Exception as exc:
        logger.warning(f"[TaskQueue] worker 启动失败 ({type(exc).__name__}): {exc}")
    yield
    # 关闭数据库引擎
    try:
        from agent.db.engine import close_engine
        await close_engine()
    except Exception as exc:
        logger.warning(f"[数据库] 关闭引擎时出错 ({type(exc).__name__}): {exc}")


app = FastAPI(docs_url=None, redoc_url=None, lifespan=_app_lifespan)
setup_logger()

# ── 认证中间件（最先添加 = 最外层，拦截非登录请求）─────────────
app.add_middleware(AuthMiddleware)

# ── 注册认证路由 ───────────────────────────────────────────────────
app.include_router(auth_router)

# ── API 路由 ─────────────────────────────────────────────────────────

# 添加获取模型列表的API端点
@app.get("/api/models")
async def get_available_models():
    """获取可用的LLM模型列表"""
    try:
        # 直接从环境变量加载模型列表
        models = load_available_models_from_env()
        models_data = [
            {
                "model_id": model.model_id,
                "display_name": model.display_name,
                "icon": model.icon,
                "icon_color": model.icon_color
            }
            for model in models
        ]
        logger.info(f"返回模型列表: {models_data}")
        return JSONResponse(content={"models": models_data})
    except ValueError as e:
        # 配置解析错误（如 AVAILABLE_MODELS JSON 格式错误）
        logger.error(f"模型配置解析失败 (ValueError): {e}")
        return JSONResponse(
            content={"error": "模型配置格式错误，请检查 AVAILABLE_MODELS 环境变量", "details": str(e)},
            status_code=500
        )
    except Exception as e:
        # 未知异常 — 记录完整 traceback 用于排查
        logger.error(f"获取模型列表失败 ({type(e).__name__}): {e}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            content={"error": "获取模型列表失败", "details": str(e)},
            status_code=500
        )

# 添加请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    try:
        # 记录请求基本信息
        logger.info(f"收到用户请求：{request.method} {request.url}")

        # 如果是POST请求且有body，记录详细信息
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()
            if body:
                try:
                    body_data = json.loads(body.decode())
                    log_request_details(body_data)
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    logger.debug(
                        f"无法解析请求体为JSON ({type(e).__name__}): "
                        f"{body[:200]!r}"
                    )
                    log_request_details(body.decode())
    except Exception as e:
        # 日志记录本身的错误不应影响请求处理
        logger.error(
            f"记录请求日志时出错 ({type(e).__name__}): {e}\n"
            f"{traceback.format_exc()}"
        )

    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(
            f"处理请求时出错 ({type(e).__name__}): {e}\n"
            f"请求: {request.method} {request.url}\n"
            f"{traceback.format_exc()}"
        )
        raise


# ── 异步研究端点（任务队列 + SSE）────────────────────────────────────

@app.post("/api/research")
async def submit_research(request: Request):
    """提交研究任务，立即返回 task_id 和 SSE 流地址.

    请求体示例：
    {
        "messages": [{"type": "human", "content": "分析AI芯片市场趋势"}],
        "initial_search_query_count": 3,
        "max_research_loops": 3,
        "reasoning_model": "qwen-plus-latest"
    }
    """
    user_id: int = getattr(request.state, "user_id", 0)

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            content={"error": "请求体必须是 JSON 格式"},
            status_code=400,
        )

    try:
        task_id = await enqueue_task(
            messages=body.get("messages", []),
            initial_search_query_count=body.get("initial_search_query_count", 2),
            max_research_loops=body.get("max_research_loops", 2),
            reasoning_model=body.get("reasoning_model", ""),
            plan_status=body.get("plan_status", "unconfirmed"),
            plan=body.get("plan", ""),
            task_id=body.get("task_id", "")  # 前端回传则复用，否则后端生成新 UUID
        )
    except Exception as exc:
        logger.error(f"[TaskQueue] 任务入队失败 ({type(exc).__name__}): {exc}")
        return JSONResponse(
            content={"error": f"任务提交失败: {exc}"},
            status_code=503,
        )

    # 建立用户与 task（thread）的关联（会话历史索引）
    try:
        from agent.db.threads import create_user_thread

        messages = body.get("messages", [])
        title_text = ""
        for m in messages:
            if m.get("type") == "human" and m.get("content", "").strip():
                title_text = m["content"].strip()[:256]
                break

        await create_user_thread(
            user_id=user_id,
            thread_id=task_id,
            title=title_text,
        )
    except Exception as exc:
        logger.warning(f"[用户关联] 写入 user_threads 失败 ({type(exc).__name__}): {exc}")

    return JSONResponse(content={
        "task_id": task_id,
        "stream_url": f"/api/research/{task_id}/stream",
    })


async def _require_thread_owner(request: Request, thread_id: str) -> JSONResponse | None:
    """校验当前用户拥有该 thread；失败时返回错误响应，通过则返回 None."""
    user_id: int = getattr(request.state, "user_id", 0)
    if not user_id:
        return JSONResponse(content={"error": "未登录"}, status_code=401)
    try:
        from agent.db.threads import user_owns_thread
        if not await user_owns_thread(user_id, thread_id):
            return JSONResponse(content={"error": "无权访问该会话"}, status_code=403)
    except Exception as exc:
        logger.warning(f"[会话] 所有权校验失败 ({type(exc).__name__}): {exc}")
        return JSONResponse(content={"error": "会话校验失败"}, status_code=500)
    return None


@app.get("/api/threads")
async def list_threads(request: Request):
    """列出当前用户的历史研究会话."""
    user_id: int = getattr(request.state, "user_id", 0)
    try:
        limit = int(request.query_params.get("limit", "50"))
    except ValueError:
        limit = 50
    try:
        from agent.db.threads import list_user_threads
        threads = await list_user_threads(user_id, limit=limit)
        return JSONResponse(content={"threads": threads})
    except Exception as exc:
        logger.error(f"[会话] 列表失败 ({type(exc).__name__}): {exc}")
        return JSONResponse(
            content={"error": f"获取会话列表失败: {exc}"},
            status_code=500,
        )


@app.get("/api/threads/{thread_id}")
async def get_thread(thread_id: str, request: Request):
    """获取单个会话详情（持久化快照）."""
    denied = await _require_thread_owner(request, thread_id)
    if denied is not None:
        return denied
    try:
        from agent.db.threads import load_durable_snapshot
        snapshot = await load_durable_snapshot(thread_id)
        if snapshot is None:
            return JSONResponse(
                content={"error": "会话不存在", "status": "not_found"},
                status_code=404,
            )
        return JSONResponse(content=snapshot)
    except Exception as exc:
        logger.error(f"[会话] 读取详情失败 ({type(exc).__name__}): {exc}")
        return JSONResponse(
            content={"error": f"读取会话失败: {exc}"},
            status_code=500,
        )


@app.delete("/api/threads/{thread_id}")
async def delete_thread(thread_id: str, request: Request):
    """删除历史会话：Postgres 记录 + Redis 事件流（导出文件保留）."""
    denied = await _require_thread_owner(request, thread_id)
    if denied is not None:
        return denied
    try:
        from agent.db.threads import delete_user_thread

        user_id: int = getattr(request.state, "user_id", 0)
        deleted = await delete_user_thread(user_id=user_id, thread_id=thread_id)
        if not deleted:
            return JSONResponse(
                content={"ok": False, "error": "会话不存在或已删除"},
                status_code=404,
            )
        return JSONResponse(content={"ok": True, "thread_id": thread_id})
    except Exception as exc:
        logger.error(f"[会话] 删除失败 ({type(exc).__name__}): {exc}")
        return JSONResponse(
            content={"ok": False, "error": str(exc)},
            status_code=500,
        )


@app.get("/api/research/{task_id}/stream")
async def stream_research(task_id: str, request: Request):
    """SSE 端点：推送研究进度事件。

    客户端断开后可用 Last-Event-ID header 或 ?after= 重连，不会丢失中间事件。
    """
    denied = await _require_thread_owner(request, task_id)
    if denied is not None:
        return denied

    # EventSource 新建连接时不会带 Last-Event-ID，确认后续跑用 ?after= 接续
    last_event_id = (
        request.query_params.get("after")
        or request.headers.get("Last-Event-ID")
        or "0"
    )

    async def event_generator():
        try:
            async for msg_id, event_str in read_task_events(task_id, last_event_id):
                yield f"id: {msg_id}\ndata: {event_str}\n\n"
        except Exception as exc:
            logger.warning(f"[TaskQueue] SSE 推送异常 ({type(exc).__name__}): {exc}")
            yield f"data: {{\"error\": \"{exc}\"}}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 nginx 缓冲
        },
    )


@app.get("/api/research/{task_id}/snapshot")
async def research_snapshot(task_id: str, request: Request):
    """按 task_id 恢复研究快照（刷新后仍可查看计划/初稿/终稿）."""
    denied = await _require_thread_owner(request, task_id)
    if denied is not None:
        return denied
    try:
        snapshot = await build_task_snapshot(task_id)
        return JSONResponse(content=snapshot)
    except Exception as exc:
        logger.error(f"[TaskQueue] 读取快照失败 ({type(exc).__name__}): {exc}")
        return JSONResponse(
            content={"error": f"读取快照失败: {exc}"},
            status_code=500,
        )


@app.post("/api/research/{task_id}/publish-draft")
async def research_publish_draft(task_id: str, request: Request):
    """将中断任务中的 draft 发布为 finalize_answer，便于界面直接展示."""
    denied = await _require_thread_owner(request, task_id)
    if denied is not None:
        return denied
    try:
        result = await publish_draft_as_final(task_id)
        status = 200 if result.get("ok") else 404
        return JSONResponse(content=result, status_code=status)
    except Exception as exc:
        logger.error(f"[TaskQueue] 发布 draft 失败 ({type(exc).__name__}): {exc}")
        return JSONResponse(
            content={"ok": False, "error": str(exc)},
            status_code=500,
        )


@app.post("/api/session/act")
async def session_act(request: Request):
    """研究完成后的自然语言动作入口.

    流程：意图识别 →（导出时）工具调用 export_report → 返回回复。
    请求体：
      {
        "message": "导出报告为 md",
        "task_id": "uuid",
        "reasoning_model": "deepseek-chat"  // 可选
      }
    """
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(content={"error": "请求体必须是 JSON"}, status_code=400)

    message = (body.get("message") or "").strip()
    task_id = (body.get("task_id") or "").strip()
    if not message:
        return JSONResponse(content={"error": "message 不能为空"}, status_code=400)
    if not task_id:
        return JSONResponse(content={"error": "task_id 不能为空"}, status_code=400)

    denied = await _require_thread_owner(request, task_id)
    if denied is not None:
        return denied

    try:
        result = await handle_session_act(
            user_message=message,
            task_id=task_id,
            model_id=body.get("reasoning_model") or "",
        )
        # 非委派研究的对话回合写入持久化会话
        if result.get("ok") and result.get("delegate") != "research":
            try:
                from agent.db.threads import append_thread_messages
                reply = result.get("reply") or "已处理。"
                await append_thread_messages(
                    task_id,
                    [
                        {"type": "human", "content": message},
                        {"type": "ai", "content": reply},
                    ],
                )
            except Exception as persist_exc:
                logger.warning(
                    f"[会话] session_act 消息持久化失败 ({type(persist_exc).__name__}): {persist_exc}"
                )
        return JSONResponse(content=result)
    except Exception as exc:
        logger.error(f"[SessionAct] 处理失败 ({type(exc).__name__}): {exc}")
        return JSONResponse(
            content={"ok": False, "error": str(exc)},
            status_code=500,
        )
