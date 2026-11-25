"""研究完成后的会话动作：意图识别 → 工具调用 / 报告问答 → 结果回传.

流程：
  用户自然语言
    → 关键字快路径 / JsonAgent 意图识别
    → 导出：调用 export_report
    → 查看：回传定位报告动作
    → 问答：基于报告正文用 LLM 回答
    → 继续研究：delegate=research
"""

from __future__ import annotations

import re
from typing import Any

from loguru import logger

from agent.base_agent import Agent, JsonAgent
from agent.configuration import Configuration
from agent.task_queue import build_task_snapshot
from agent.tools.export_report import export_report
from agent.tools_and_schemas import SessionIntent, ToolCallDecision

# 导出意图关键字（优先于 LLM，降低延迟与误判）
_EXPORT_KEYWORDS = re.compile(
    r"(导出|下載|下载|保存报告|保存研报|存成|另存|export|download|save\s*(the\s*)?report)",
    re.I,
)

# 查看报告：定位已有正文，不重新生成
_VIEW_KEYWORDS = re.compile(
    r"(查看(最新)?报告|看(一下|下)?报告|打开报告|显示报告|最新报告|报告在哪|翻到报告)",
    re.I,
)

# 继续研究快路径
_CONTINUE_KEYWORDS = re.compile(
    r"(继续研究|补充调研|再搜|重新研究|扩大范围|加深研究|再调研)",
    re.I,
)

# 报告问答上下文上限（字符），避免撑爆上下文
_REPORT_CONTEXT_CHARS = 28000


_INTENT_PROMPT = """# 角色
你是 DeepResearch 会话意图分类器。

# 任务
根据用户输入，判断意图，并输出 JSON。

# 意图定义
- export_report: 用户想导出/下载/保存当前研究报告到服务器文件
- view_report: 用户想查看/打开/定位当前已有报告正文
- continue_research: 用户想继续补充研究、改范围、再搜一轮（需要新开研究任务）
- general_chat: 针对报告内容提问、总结、解释，或其它普通对话

# 用户输入
{user_message}

# 上下文
当前是否已有研究报告: {has_report}
"""


_TOOL_PROMPT = """# 角色
你是工具调度助手。当前可用工具只有一个：export_report（把研究报告写入服务器固定导出目录）。

# 规则
1. 用户要导出/保存/下载报告时，tool_name 必须为 export_report
2. format 只能是 md 或 txt；用户说「文本/txt」用 txt，否则默认 md
3. title_hint：若用户给了文件名/标题则提取，否则留空
4. reply：用中文简短说明你将执行的操作

# 用户输入
{user_message}
"""


_CHAT_PROMPT = """# 角色
你是 DeepResearch 报告助手。用户已完成一轮深度研究，你基于报告正文回答追问。

# 规则
1. 只依据下方研究报告回答；不要编造报告中没有的事实
2. 用简洁中文，优先给结论，再补关键依据（可引用报告小节标题）
3. 若用户只是寒暄/确认/无明确问题，用一两句话说明：可直接问报告内容，或说「导出报告」「继续研究」
4. 若问题明显超出报告覆盖范围，说明缺口，并建议用户说「继续研究」补充调研
5. 不要重复粘贴整篇报告

# 研究报告
{report}

# 用户消息
{user_message}
"""


def _keyword_intent(message: str) -> SessionIntent | None:
    if _EXPORT_KEYWORDS.search(message or ""):
        fmt = "txt" if re.search(r"\btxt\b|纯文本|文本文件", message, re.I) else "md"
        return SessionIntent(
            intent="export_report",
            format=fmt,
            title_hint="",
            reason="命中导出关键字",
        )
    if _VIEW_KEYWORDS.search(message or ""):
        return SessionIntent(
            intent="view_report",
            format="md",
            title_hint="",
            reason="命中查看报告关键字",
        )
    if _CONTINUE_KEYWORDS.search(message or ""):
        return SessionIntent(
            intent="continue_research",
            format="md",
            title_hint="",
            reason="命中继续研究关键字",
        )
    return None


async def _llm_intent(message: str, has_report: bool, model_id: str) -> SessionIntent:
    agent = JsonAgent(model_id=model_id, keys=SessionIntent)
    agent.set_step_prompt(_INTENT_PROMPT)
    result = await agent.astep(
        user_message=message,
        has_report="是" if has_report else "否",
    )
    if isinstance(result, SessionIntent):
        return result
    logger.warning(f"[SessionAct] 意图识别返回异常类型 {type(result).__name__}，回落 general_chat")
    return SessionIntent(
        intent="general_chat",
        format="md",
        title_hint="",
        reason="意图识别失败",
    )


async def _llm_tool_decision(message: str, model_id: str) -> ToolCallDecision:
    agent = JsonAgent(model_id=model_id, keys=ToolCallDecision)
    agent.set_step_prompt(_TOOL_PROMPT)
    result = await agent.astep(user_message=message)
    if isinstance(result, ToolCallDecision):
        return result
    return ToolCallDecision(
        tool_name="export_report",
        format="md",
        title_hint="",
        reply="正在导出研究报告。",
    )


def _clip_report(report: str) -> str:
    text = (report or "").strip()
    if len(text) <= _REPORT_CONTEXT_CHARS:
        return text
    head = text[: _REPORT_CONTEXT_CHARS - 200]
    return head + "\n\n…（报告过长，已截断后半部分）"


async def _answer_about_report(*, message: str, report: str, model_id: str) -> str:
    """基于报告正文回答用户追问."""
    agent = Agent(model_id=model_id)
    agent.set_step_prompt(_CHAT_PROMPT)
    reply = await agent.astep(
        user_message=message,
        report=_clip_report(report) or "（当前无报告正文）",
    )
    text = (reply or "").strip()
    if text:
        return text
    return (
        "我暂时没能基于报告生成回答。你可以换一种问法，"
        "或说「导出报告」「继续研究」。"
    )


def _pick_title(snapshot: dict[str, Any], title_hint: str) -> str:
    if title_hint and title_hint.strip():
        return title_hint.strip()
    report = snapshot.get("report") or ""
    for line in report.splitlines():
        s = line.strip()
        if s.startswith("#"):
            return re.sub(r"^#+\s*", "", s)
    # 用户问题作为 fallback
    for m in snapshot.get("messages") or []:
        if m.get("type") == "human" and m.get("content"):
            return str(m["content"]).split("\n", 1)[0][:40]
    return "research_report"


async def handle_session_act(
    *,
    user_message: str,
    task_id: str,
    model_id: str = "",
) -> dict[str, Any]:
    """处理研究完成后的自然语言动作."""
    message = (user_message or "").strip()
    if not message:
        return {"ok": False, "error": "消息为空"}

    # 校验/回落模型：前端可能仍缓存旧模型名（如 qwen-plus-latest）
    allowed = {m.model_id for m in Configuration().available_models}
    if not model_id or model_id not in allowed:
        model_id = next(iter(allowed), "deepseek-flash")
        logger.info(f"[SessionAct] 模型回落到可用列表: {model_id}")

    snapshot = await build_task_snapshot(task_id) if task_id else {
        "status": "not_found",
        "report": "",
        "messages": [],
    }
    report = (snapshot.get("report") or "").strip()
    has_report = bool(report)

    # 1) 意图识别（关键字快路径 → LLM）
    intent = _keyword_intent(message)
    if intent is None:
        intent = await _llm_intent(message, has_report, model_id)
    logger.info(f"[SessionAct] intent={intent.intent} reason={intent.reason}")

    if intent.intent == "export_report":
        if not has_report:
            return {
                "ok": False,
                "intent": "export_report",
                "reply": "当前没有可导出的研究报告。请先完成一次研究，或通过 ?task_id= 打开历史任务。",
            }

        # 2) 工具参数：关键字快路径直接用；否则让大模型确认工具调用
        if intent.reason == "命中导出关键字":
            decision = ToolCallDecision(
                tool_name="export_report",
                format=intent.format or "md",
                title_hint=intent.title_hint or "",
                reply="已识别到导出意图，正在调用 export_report 工具。",
            )
        else:
            decision = await _llm_tool_decision(message, model_id)
            if decision.tool_name != "export_report":
                decision.tool_name = "export_report"
                decision.reply = decision.reply or "正在导出研究报告。"

        fmt = (decision.format or intent.format or "md").lower()
        title = _pick_title(snapshot, decision.title_hint or intent.title_hint)

        # 3) 调用工具落盘（固定目录 + 规范文件名）
        result = export_report(
            snapshot["report"],
            task_id=task_id,
            title=title,
            fmt=fmt,
        )
        if not result.get("ok"):
            return {
                "ok": False,
                "intent": "export_report",
                "reply": f"导出失败：{result.get('error')}",
                "tool_result": result,
            }

        reply = (
            f"{decision.reply}\n\n"
            f"工具：`export_report`\n"
            f"目录：`{result['dir']}`\n"
            f"文件：`{result['filename']}`\n"
            f"路径：`{result['path']}`"
        )
        return {
            "ok": True,
            "intent": "export_report",
            "reply": reply,
            "tool_name": "export_report",
            "tool_result": result,
        }

    if intent.intent == "view_report":
        if not has_report:
            return {
                "ok": False,
                "intent": "view_report",
                "reply": "当前没有可查看的研究报告。",
            }
        return {
            "ok": True,
            "intent": "view_report",
            "action": "scroll_to_report",
            "reply": "已定位到上方研究报告。可复制全文或下载 .md；需要落盘到服务器时说「导出报告」。",
        }

    if intent.intent == "continue_research":
        return {
            "ok": True,
            "intent": "continue_research",
            "reply": "好的，将按你的补充继续研究。",
            "delegate": "research",
        }

    # general_chat：有报告则基于正文回答，否则给短提示
    if has_report:
        reply = await _answer_about_report(
            message=message,
            report=report,
            model_id=model_id,
        )
        return {
            "ok": True,
            "intent": "general_chat",
            "reply": reply,
        }

    return {
        "ok": True,
        "intent": "general_chat",
        "reply": "当前还没有研究报告。先提交一个研究问题开始探索。",
    }
