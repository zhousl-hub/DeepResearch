"""用户研究会话（UserThread）读写：列表、所有权、快照持久化."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from loguru import logger
from sqlalchemy import select, text

from agent.db.engine import get_engine, get_session_factory
from agent.db.models import UserThread


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _dumps_messages(messages: list[dict] | None) -> str | None:
    if not messages:
        return None
    return json.dumps(messages, ensure_ascii=False)


def _loads_messages(raw: str | None) -> list[dict]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


# 表/字段中文注释（写入 PostgreSQL COMMENT，可在 \d+ / information_schema 查看）
_TABLE_COMMENTS: dict[str, str] = {
    "users": "用户账号表：存储登录账号与密码哈希，供会话鉴权使用",
    "user_threads": (
        "用户研究会话表：记录用户与研究线程的归属关系，"
        "并持久化报告正文与对话消息，供历史列表与刷新恢复"
    ),
}

_COLUMN_COMMENTS: dict[str, dict[str, str]] = {
    "users": {
        "id": "用户主键 ID，自增",
        "username": "登录用户名，全局唯一",
        "password": "登录密码的 bcrypt 哈希，不明文存储",
        "created_at": "账号创建时间",
    },
    "user_threads": {
        "id": "会话记录主键 ID，自增",
        "user_id": "所属用户 ID，对应 users.id",
        "thread_id": "研究线程 ID，等于 task_id / LangGraph thread_id",
        "title": "会话标题，通常取用户首条研究问题摘要，用于历史列表展示",
        "status": "会话状态：running=进行中 / paused=待确认 / completed=已完成 / failed=失败",
        "report": "持久化研究报告正文；不受 Redis 事件流 TTL 限制",
        "messages_json": "对话消息 JSON 数组，元素形如 {type, content, id}，含 session_act 追问",
        "created_at": "会话创建时间",
        "updated_at": "会话最近更新时间（研究推进、问答追加、状态变更时刷新）",
    },
}


async def ensure_thread_schema() -> None:
    """为已有库补齐 user_threads 新列，并同步表/字段注释（幂等）."""
    engine = get_engine()
    alter_statements = [
        "ALTER TABLE user_threads ADD COLUMN IF NOT EXISTS status VARCHAR(32) NOT NULL DEFAULT 'running'",
        "ALTER TABLE user_threads ADD COLUMN IF NOT EXISTS report TEXT",
        "ALTER TABLE user_threads ADD COLUMN IF NOT EXISTS messages_json TEXT",
        "ALTER TABLE user_threads ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW()",
    ]
    def _sql_str(value: str) -> str:
        # COMMENT ON 不支持绑定参数，字面量转义单引号
        return "'" + value.replace("'", "''") + "'"

    async with engine.begin() as conn:
        for stmt in alter_statements:
            await conn.execute(text(stmt))
        for table, comment in _TABLE_COMMENTS.items():
            await conn.execute(
                text(f"COMMENT ON TABLE {table} IS {_sql_str(comment)}")
            )
        for table, cols in _COLUMN_COMMENTS.items():
            for col, comment in cols.items():
                await conn.execute(
                    text(
                        f"COMMENT ON COLUMN {table}.{col} IS {_sql_str(comment)}"
                    )
                )
    logger.info("[数据库] user_threads 会话列与表注释已就绪")


async def delete_user_thread(*, user_id: int, thread_id: str) -> bool:
    """删除当前用户的历史会话（Postgres 记录 + Redis 事件流）.

    返回 True 表示删除了至少一行；不存在则 False。
    """
    from sqlalchemy import delete

    async with get_session_factory()() as session:
        result = await session.execute(
            delete(UserThread).where(
                UserThread.user_id == user_id,
                UserThread.thread_id == thread_id,
            )
        )
        await session.commit()
        deleted = (result.rowcount or 0) > 0

    # 清理 Redis 研究事件流，避免残留可被猜测 task_id 读取
    try:
        import redis.asyncio as redis
        import os

        redis_url = (os.getenv("REDIS_URL") or "").strip()
        if redis_url:
            r = redis.from_url(redis_url, decode_responses=True)
            try:
                await r.delete(f"research:events:{thread_id}")
            finally:
                await r.aclose()
    except Exception as exc:
        logger.warning(f"[会话] 清理 Redis 事件流失败 thread_id={thread_id[:8]}...: {exc}")

    if deleted:
        logger.info(f"[会话] 已删除历史会话 thread_id={thread_id[:8]}... user_id={user_id}")
    return deleted


async def create_user_thread(
    *,
    user_id: int,
    thread_id: str,
    title: str = "",
) -> None:
    """首次提交研究时写入会话索引；已存在则只刷新 title/updated_at."""
    async with get_session_factory()() as session:
        existing = (
            await session.execute(
                select(UserThread).where(
                    UserThread.user_id == user_id,
                    UserThread.thread_id == thread_id,
                )
            )
        ).scalar_one_or_none()
        now = _utcnow()
        if existing is None:
            messages = []
            if title:
                messages.append({"type": "human", "content": title, "id": "1"})
            session.add(
                UserThread(
                    user_id=user_id,
                    thread_id=thread_id,
                    title=title or None,
                    status="running",
                    messages_json=_dumps_messages(messages),
                    updated_at=now,
                )
            )
        else:
            if title and not existing.title:
                existing.title = title
            existing.updated_at = now
            if existing.status not in ("completed", "failed"):
                existing.status = "running"
        await session.commit()


async def user_owns_thread(user_id: int, thread_id: str) -> bool:
    """校验 thread 是否属于当前用户.

    规则：
    - 存在本用户记录 → True
    - 无任何用户记录 → True（入库与 SSE 竞态窗口，或尚未写完索引）
    - 仅存在其他用户记录 → False
    """
    async with get_session_factory()() as session:
        mine = (
            await session.execute(
                select(UserThread.id).where(
                    UserThread.user_id == user_id,
                    UserThread.thread_id == thread_id,
                )
            )
        ).scalar_one_or_none()
        if mine is not None:
            return True
        any_owner = (
            await session.execute(
                select(UserThread.id).where(UserThread.thread_id == thread_id).limit(1)
            )
        ).scalar_one_or_none()
        return any_owner is None


async def list_user_threads(user_id: int, limit: int = 50) -> list[dict[str, Any]]:
    """按更新时间倒序列出会话摘要."""
    limit = max(1, min(limit, 200))
    async with get_session_factory()() as session:
        rows = (
            await session.execute(
                select(UserThread)
                .where(UserThread.user_id == user_id)
                .order_by(UserThread.updated_at.desc().nullslast(), UserThread.created_at.desc())
                .limit(limit)
            )
        ).scalars().all()

    result: list[dict[str, Any]] = []
    for row in rows:
        title = (row.title or "").strip() or "未命名研究"
        result.append(
            {
                "thread_id": row.thread_id,
                "title": title[:80],
                "status": row.status or "running",
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                "has_report": bool((row.report or "").strip()),
            }
        )
    return result


async def get_thread_record(thread_id: str, user_id: int | None = None) -> UserThread | None:
    """按 thread_id 取会话行；传 user_id 时附带所有权过滤."""
    async with get_session_factory()() as session:
        stmt = select(UserThread).where(UserThread.thread_id == thread_id)
        if user_id is not None:
            stmt = stmt.where(UserThread.user_id == user_id)
        return (await session.execute(stmt)).scalar_one_or_none()


async def load_durable_snapshot(thread_id: str) -> dict[str, Any] | None:
    """从 Postgres 读取持久化快照；无记录则返回 None."""
    async with get_session_factory()() as session:
        row = (
            await session.execute(
                select(UserThread).where(UserThread.thread_id == thread_id)
            )
        ).scalar_one_or_none()
        if row is None:
            return None
        messages = _loads_messages(row.messages_json)
        report = (row.report or "").strip()
        # 若 messages 为空但有 title/report，重建最小消息列表
        if not messages:
            if row.title:
                messages.append({"type": "human", "content": row.title, "id": "1"})
            if report:
                messages.append({"type": "ai", "content": report, "id": "3"})
        return {
            "task_id": thread_id,
            "status": row.status or "running",
            "messages": messages,
            "report": report,
            "error": "",
            "has_draft": False,
            "has_final": bool(report),
            "title": row.title or "",
            "source": "db",
        }


async def save_thread_snapshot(
    thread_id: str,
    *,
    status: str,
    messages: list[dict] | None = None,
    report: str | None = None,
    title: str | None = None,
    error: str = "",
) -> None:
    """将研究快照写入 Postgres（按 thread_id 更新全部关联行）."""
    async with get_session_factory()() as session:
        rows = (
            await session.execute(
                select(UserThread).where(UserThread.thread_id == thread_id)
            )
        ).scalars().all()
        if not rows:
            logger.debug(f"[会话] 保存快照跳过：无 user_threads 记录 thread_id={thread_id[:8]}...")
            return

        now = _utcnow()
        for row in rows:
            row.status = status
            row.updated_at = now
            if messages is not None:
                row.messages_json = _dumps_messages(messages)
            if report is not None:
                row.report = report
            if title and not row.title:
                row.title = title[:256]
            if error and status == "failed" and not (row.title or "").startswith("[失败]"):
                pass
        await session.commit()
        logger.info(
            f"[会话] 快照已持久化 thread_id={thread_id[:8]}... status={status} "
            f"msgs={len(messages or [])} report_chars={len(report or '')}"
        )


async def append_thread_messages(
    thread_id: str,
    new_messages: list[dict],
) -> None:
    """追加会话消息（如 session_act 的问答），并刷新 updated_at."""
    if not new_messages:
        return
    async with get_session_factory()() as session:
        rows = (
            await session.execute(
                select(UserThread).where(UserThread.thread_id == thread_id)
            )
        ).scalars().all()
        if not rows:
            return
        now = _utcnow()
        for row in rows:
            existing = _loads_messages(row.messages_json)
            next_id = len(existing) + 1
            for msg in new_messages:
                existing.append(
                    {
                        "type": msg.get("type", "ai"),
                        "content": msg.get("content", ""),
                        "id": msg.get("id") or str(next_id),
                    }
                )
                next_id += 1
            row.messages_json = _dumps_messages(existing)
            row.updated_at = now
        await session.commit()
