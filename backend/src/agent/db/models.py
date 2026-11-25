"""数据库表模型（纯 SQL 表定义，不含 ORM 关系）.

字段 comment 会进入 PostgreSQL 的 COLUMN COMMENT（建表/迁移时同步）。
"""
from __future__ import annotations

from sqlalchemy import Column, Integer, String, DateTime, Text, func, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class User(Base):
    """用户账号表：登录鉴权."""
    __tablename__ = "users"
    __table_args__ = {
        "comment": "用户账号表：存储登录账号与密码哈希，供会话鉴权使用",
    }

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="用户主键 ID，自增",
    )
    username = Column(
        String(64),
        nullable=False,
        unique=True,
        index=True,
        comment="登录用户名，全局唯一",
    )
    password = Column(
        String(256),
        nullable=False,
        comment="登录密码的 bcrypt 哈希，不明文存储",
    )
    created_at = Column(
        DateTime,
        server_default=func.now(),
        comment="账号创建时间",
    )


class UserThread(Base):
    """用户研究会话表：历史列表索引 + 持久化快照.

    thread_id 与研究 task_id、LangGraph thread_id 同一取值。
    """
    __tablename__ = "user_threads"
    __table_args__ = (
        UniqueConstraint("user_id", "thread_id", name="uq_user_threads_user_thread"),
        {
            "comment": (
                "用户研究会话表：记录用户与研究线程的归属关系，"
                "并持久化报告正文与对话消息，供历史列表与刷新恢复"
            ),
            "sqlite_autoincrement": True,
        },
    )

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="会话记录主键 ID，自增",
    )
    user_id = Column(
        Integer,
        nullable=False,
        index=True,
        comment="所属用户 ID，对应 users.id",
    )
    thread_id = Column(
        String(128),
        nullable=False,
        comment="研究线程 ID，等于 task_id / LangGraph thread_id",
    )
    title = Column(
        Text,
        nullable=True,
        comment="会话标题，通常取用户首条研究问题摘要，用于历史列表展示",
    )
    status = Column(
        String(32),
        nullable=False,
        server_default="running",
        comment="会话状态：running=进行中 / paused=待确认 / completed=已完成 / failed=失败",
    )
    report = Column(
        Text,
        nullable=True,
        comment="持久化研究报告正文；不受 Redis 事件流 TTL 限制",
    )
    messages_json = Column(
        Text,
        nullable=True,
        comment="对话消息 JSON 数组，元素形如 {type, content, id}，含 session_act 追问",
    )
    created_at = Column(
        DateTime,
        server_default=func.now(),
        comment="会话创建时间",
    )
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        comment="会话最近更新时间（研究推进、问答追加、状态变更时刷新）",
    )
