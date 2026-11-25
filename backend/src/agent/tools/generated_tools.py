"""ToolSmith MVP 生成工具：time_aware_search。

只返回带来源的事实清单，不输出最终结论，不做冲突裁决。
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

from loguru import logger

from agent.base_agent import Agent, WebSearchAgent
from agent.kb.lifecycle import FRESHNESS_MAX_AGE
from agent.post import Post
from agent.prompts import get_current_date, web_searcher_instructions
from agent.search_cache import get_cached

# 降级假来源，不计为真实引用
_MCP_LOCAL_URL = "https://mcp.local/search-result"

# 模块级调用计数，供 A/B 对照表统计
_CALL_COUNT = 0
_CACHE_HIT_COUNT = 0
_CACHE_MISS_COUNT = 0
_FALLBACK_COUNT = 0

# 时效主题启发词
_TIME_NEED_RE = re.compile(
    r"(最近|最新|本周|本月|今年|当前|排行|榜单|榜|发布|上市|更新|"
    r"202[4-9]|11\s*月|时效|今天|近\s*\d+|本季|本年度| presently|latest|recent)",
    re.IGNORECASE,
)

_FACT_EXTRACT_PROMPT = """# 角色
你是事实抽取器。只从检索结果中抽出可核验的事实句，不写结论、不编造日期。

# 规则
1. 每条事实必须能对应到某一条检索结果的 url。
2. published_date：结果里能读到就原样填；读不到填 "unknown"，绝对不许编造。
3. source_type 只能是：official / primary / news / other。
4. 同一事实多来源时只保留一条最权威的，其余 url 不要混进 statement。
5. 若两条事实互相冲突，两条都保留，不要自行裁决。
6. 输出严格 JSON 数组，形如：
[{{"statement":"...","url":"...","published_date":"unknown","source_type":"news"}}]

# 当前日期
{current_date}

# 查询
{query}

# 检索结果（最多 2 条页面摘要）
{web_search_result}
"""


def reset_time_aware_stats() -> None:
    """重置调用/缓存统计，便于每轮 eval 独立计量。"""
    global _CALL_COUNT, _CACHE_HIT_COUNT, _CACHE_MISS_COUNT, _FALLBACK_COUNT
    _CALL_COUNT = 0
    _CACHE_HIT_COUNT = 0
    _CACHE_MISS_COUNT = 0
    _FALLBACK_COUNT = 0


def get_time_aware_stats() -> dict[str, int]:
    """返回当前进程内的调用统计。"""
    return {
        "call_count": _CALL_COUNT,
        "cache_hit_count": _CACHE_HIT_COUNT,
        "cache_miss_count": _CACHE_MISS_COUNT,
        "fallback_count": _FALLBACK_COUNT,
    }


def topic_needs_timeliness(text: str) -> bool:
    """判断主题/查询是否有时效要求。"""
    if os.getenv("TIME_AWARE_SEARCH_FORCE", "0") == "1":
        return True
    return bool(_TIME_NEED_RE.search(text or ""))


def should_use_time_aware_search(query: str, fresh_level: str = "medium") -> bool:
    """触发条件：开关开启 + fresh_level != low + 主题有时效要求。"""
    if os.getenv("TIME_AWARE_SEARCH_ENABLED", "1") != "1":
        return False
    if (fresh_level or "medium") == "low":
        return False
    return topic_needs_timeliness(query)


def _rewrite_query(query: str, fresh_level: str) -> str:
    """按新鲜度窗口改写查询，必须与原查询不同以免撞缓存。"""
    days = FRESHNESS_MAX_AGE.get(fresh_level, 30)
    now = datetime.now()
    ym = f"{now.year}年{now.month}月"
    if days <= 7:
        time_phrase = f"最近一周 {ym} 最新进展"
    elif days <= 30:
        time_phrase = f"最近{days}天 {ym} 最新"
    else:
        time_phrase = f"最近{days}天 近半年动态"
    # 显式加时间词与来源偏好，保证 prompt 与原查询不同
    return f"{query} {time_phrase} 优先官方或一手来源 site:gov OR 官方公告 OR 一手报道"


def _classify_source_type(url: str) -> str:
    """按域名启发式划分来源类型。"""
    host = urlparse(url).netloc.lower()
    if not host:
        return "other"
    if host.endswith(".gov") or host.endswith(".gov.cn") or "arxiv.org" in host:
        return "official"
    if any(k in host for k in ("arxiv", "nature.com", "science.org", "ieee.org", "acm.org")):
        return "primary"
    if any(
        k in host
        for k in (
            "news", "reuters", "bloomberg", "bbc", "nytimes", "theverge",
            "techcrunch", "36kr", "sina", "qq.com", "smol.ai", "deeplearning.ai",
        )
    ):
        return "news"
    return "other"


def _authority_rank(source_type: str) -> int:
    order = {"official": 0, "primary": 1, "news": 2, "other": 3}
    return order.get(source_type, 9)


def _is_real_url(url: str) -> bool:
    if not url or not isinstance(url, str):
        return False
    if url.startswith(_MCP_LOCAL_URL):
        return False
    return url.startswith("http://") or url.startswith("https://")


def _dedupe_facts(facts: list[dict]) -> list[dict]:
    """同一事实只留最权威来源；冲突事实都保留。"""
    best: dict[str, dict] = {}
    for fact in facts:
        key = re.sub(r"\s+", "", fact.get("statement", "")).lower()
        if not key:
            continue
        prev = best.get(key)
        if prev is None or _authority_rank(fact.get("source_type", "other")) < _authority_rank(
            prev.get("source_type", "other")
        ):
            best[key] = fact
    return list(best.values())


def _normalize_fact(raw: dict, fallback_url: str = "") -> dict | None:
    """规范化单条事实；假来源直接丢弃。"""
    statement = str(raw.get("statement", "")).strip()
    url = str(raw.get("url", "") or fallback_url).strip()
    if not statement:
        return None
    if not _is_real_url(url):
        logger.info(f"[time_aware_search] 丢弃非真实来源 url={url!r}")
        return None
    published = str(raw.get("published_date", "unknown") or "unknown").strip()
    if not published:
        published = "unknown"
    source_type = str(raw.get("source_type", "") or "").strip().lower()
    if source_type not in {"official", "primary", "news", "other"}:
        source_type = _classify_source_type(url)
    return {
        "statement": statement,
        "url": url,
        "published_date": published,
        "source_type": source_type,
    }


def time_aware_search(query: str, fresh_level: str = "medium") -> list[dict]:
    """时间感知搜索：改写查询 → WebSearchAgent → 摘要 → 抽事实。

    返回事实列表；失败时返回空列表，由调用方回退到原有搜索。
    """
    global _CALL_COUNT, _CACHE_HIT_COUNT, _CACHE_MISS_COUNT, _FALLBACK_COUNT
    _CALL_COUNT += 1
    fresh_level = fresh_level or "medium"
    days = FRESHNESS_MAX_AGE.get(fresh_level, 30)
    timed_query = _rewrite_query(query, fresh_level)
    logger.info(
        f"[time_aware_search] CALL#{_CALL_COUNT} fresh_level={fresh_level} "
        f"window={days}d query={query!r} timed_query={timed_query!r}"
    )

    # 缓存命中预检（WebSearchAgent.step 内部还会再查一次并打日志）
    cached = get_cached(timed_query)
    if cached is not None:
        _CACHE_HIT_COUNT += 1
        logger.info(f"[time_aware_search] cache_hit=True prompt={timed_query[:80]!r}")
    else:
        _CACHE_MISS_COUNT += 1
        logger.info(f"[time_aware_search] cache_hit=False prompt={timed_query[:80]!r}")

    try:
        searcher = WebSearchAgent()
        pages = searcher.step(prompt=timed_query, count=10) or []
    except Exception as exc:
        _FALLBACK_COUNT += 1
        logger.warning(f"[time_aware_search] 搜索失败，回退原因=search_error: {exc}")
        return []

    # 过滤假来源，只取前 2 页
    real_pages = [p for p in pages if _is_real_url(str(p.get("url", "")))]
    if not real_pages:
        _FALLBACK_COUNT += 1
        logger.warning("[time_aware_search] 无真实来源页面，回退原因=no_real_pages")
        return []
    top_pages = real_pages[:2]

    raw_results = json.dumps(
        [
            {
                "snippet": p.get("snippet", ""),
                "title": p.get("title", ""),
                "url": p.get("url", ""),
            }
            for p in top_pages
        ],
        ensure_ascii=False,
        indent=2,
    )

    try:
        # 先复用现有摘要指令，再做结构化事实抽取
        summarizer = Agent()
        summarizer.set_step_prompt(web_searcher_instructions)
        summary = summarizer.step(
            query=timed_query,
            current_date=get_current_date(),
            web_search_result=raw_results,
        )
        summary = Post.extract_pattern(summary, pattern="text") or str(summary)

        extractor = Agent()
        extractor.set_step_prompt(_FACT_EXTRACT_PROMPT)
        raw = extractor.step(
            current_date=get_current_date(),
            query=timed_query,
            web_search_result=f"{summary}\n\n原始页面:\n{raw_results}",
        )
        facts_raw = _parse_facts_json(raw)
    except Exception as exc:
        _FALLBACK_COUNT += 1
        logger.warning(f"[time_aware_search] 抽事实失败，回退原因=extract_error: {exc}")
        return []

    facts: list[dict] = []
    fallback_url = str(top_pages[0].get("url", ""))
    for item in facts_raw:
        if not isinstance(item, dict):
            continue
        norm = _normalize_fact(item, fallback_url=fallback_url)
        if norm:
            facts.append(norm)

    facts = _dedupe_facts(facts)
    if not facts:
        _FALLBACK_COUNT += 1
        logger.warning("[time_aware_search] 未抽出有效事实，回退原因=empty_facts")
        return []

    logger.info(f"[time_aware_search] 返回 {len(facts)} 条事实，stats={get_time_aware_stats()}")
    return facts


def _parse_facts_json(raw: Any) -> list[dict]:
    """从模型输出中解析事实 JSON 数组。"""
    if isinstance(raw, list):
        return [x for x in raw if isinstance(x, dict)]
    text = str(raw or "").strip()
    if not text:
        return []
    # 尝试直接解析或截取首个 JSON 数组
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return [x for x in data if isinstance(x, dict)]
        if isinstance(data, dict) and isinstance(data.get("facts"), list):
            return [x for x in data["facts"] if isinstance(x, dict)]
    except json.JSONDecodeError:
        pass
    match = re.search(r"\[[\s\S]*\]", text)
    if match:
        try:
            data = json.loads(match.group(0))
            if isinstance(data, list):
                return [x for x in data if isinstance(x, dict)]
        except json.JSONDecodeError:
            return []
    return []


def format_facts_as_summary(facts: list[dict]) -> str:
    """把事实列表格式化为 research_agent 可用的摘要文本。"""
    lines = ["## 时间感知检索事实（仅事实，不含结论）"]
    for i, f in enumerate(facts, 1):
        lines.append(
            f"{i}. {f['statement']} "
            f"[来源:{f['url']}] [日期:{f.get('published_date', 'unknown')}] "
            f"[类型:{f.get('source_type', 'other')}]"
        )
    return "\n".join(lines)
