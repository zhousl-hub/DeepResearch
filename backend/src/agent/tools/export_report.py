"""导出研究报告工具.

将报告正文写入固定目录，命名规范：
  {YYYYMMDD_HHMMSS}_{标题slug}_{task前8位}.{md|txt}
"""

from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path

from loguru import logger

# 默认落盘到仓库 DeepResearch/exports（相对 backend/src/agent/tools 上溯）
_DEFAULT_EXPORT_DIR = (
    Path(__file__).resolve().parents[4] / "exports"
)
EXPORT_DIR = Path(os.getenv("REPORT_EXPORT_DIR", str(_DEFAULT_EXPORT_DIR))).expanduser()


def _slugify(text: str, max_len: int = 40) -> str:
    """标题转文件名安全片段."""
    text = (text or "").strip()
    # 取首行 / 去 markdown 标题符
    text = text.split("\n", 1)[0]
    text = re.sub(r"^#+\s*", "", text)
    # 半角/全角非法文件名字符与空白统一成下划线
    text = re.sub(r"[\\/:*?\"<>|\s　：？＊｜]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("._")
    if not text:
        text = "research_report"
    return text[:max_len]


def export_report(
    content: str,
    *,
    task_id: str = "",
    title: str = "",
    fmt: str = "md",
) -> dict:
    """导出报告到固定目录.

    Args:
        content: 报告正文
        task_id: 任务 ID（用于文件名后缀）
        title: 标题（用于 slug）；为空则从正文首行推断
        fmt: md | txt

    Returns:
        {ok, path, filename, bytes, dir}
    """
    body = (content or "").strip()
    if not body:
        return {"ok": False, "error": "报告内容为空，无法导出"}

    fmt = (fmt or "md").lower().strip(".")
    if fmt not in {"md", "txt"}:
        fmt = "md"

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = _slugify(title or body)
    task_part = (task_id or "notask").replace("-", "")[:8]
    filename = f"{ts}_{slug}_{task_part}.{fmt}"
    path = EXPORT_DIR / filename

    # 避免极端情况下重名覆盖
    if path.exists():
        filename = f"{ts}_{slug}_{task_part}_{os.getpid()}.{fmt}"
        path = EXPORT_DIR / filename

    path.write_text(body + "\n", encoding="utf-8")
    size = path.stat().st_size
    logger.info(f"[ExportTool] 已导出 {path} ({size} bytes)")
    return {
        "ok": True,
        "path": str(path.resolve()),
        "filename": filename,
        "dir": str(EXPORT_DIR.resolve()),
        "bytes": size,
        "format": fmt,
    }
