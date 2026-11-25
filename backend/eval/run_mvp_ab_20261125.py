"""ToolSmith MVP A/B：基线 vs time_aware_search，同一测试集。"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from agent.search_cache import clear_cache  # noqa: E402
from agent.tools.generated_tools import (  # noqa: E402
    get_time_aware_stats,
    reset_time_aware_stats,
)
from eval.evaluator import Evaluator, TopicCfg  # noqa: E402
from eval.run_eval import load_test_set  # noqa: E402


def _score_one(evaluator: Evaluator, cfg: TopicCfg, label: str, out_dir: Path) -> dict:
    """跑单题并收集分数、循环次数、工具统计。"""
    before = get_time_aware_stats()
    try:
        raw = evaluator._invoke_agent_with_feedback(cfg)
        report = raw.get("report") or ""
        sources = raw.get("sources") or "[]"
        phase2 = raw.get("phase2_state") or {}
        error = None
    except Exception as exc:
        report, sources, phase2, error = "", "[]", {}, str(exc)

    after = get_time_aware_stats()
    tool_calls = after["call_count"] - before["call_count"]
    cache_hits = after["cache_hit_count"] - before["cache_hit_count"]
    cache_misses = after["cache_miss_count"] - before["cache_miss_count"]
    fallbacks = after["fallback_count"] - before["fallback_count"]

    score_obj = None
    dims = {}
    overall = None
    if report and not error:
        try:
            score_obj = evaluator.judge.evaluate_report(
                research_topic=cfg.topic,
                search_sources=sources,
                report=report,
            )
            overall = score_obj.overall_score
            dims = {
                "factual_accuracy": score_obj.factual_accuracy.score,
                "information_coverage": score_obj.information_coverage.score,
                "logical_structure": score_obj.logical_structure.score,
                "timeliness": score_obj.timeliness.score,
                "citation_quality": score_obj.citation_quality.score,
            }
        except Exception as exc:
            error = f"judge_failed: {exc}"

    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in cfg.topic)[:60]
    report_path = out_dir / f"{label}_{safe}.md"
    report_path.write_text(report or f"(error) {error}", encoding="utf-8")

    return {
        "topic": cfg.topic,
        "error": error,
        "overall": overall,
        "dims": dims,
        "research_loop_count": phase2.get("research_loop_count"),
        "number_of_ran_queries": phase2.get("number_of_ran_queries"),
        "is_sufficient": phase2.get("is_sufficient"),
        "fresh_level": phase2.get("fresh_level"),
        "tool_calls": tool_calls,
        "cache_hits": cache_hits,
        "cache_misses": cache_misses,
        "fallbacks": fallbacks,
        "report_path": str(report_path),
        "report_chars": len(report or ""),
    }


def _run_arm(label: str, enabled: bool, out_dir: Path) -> dict:
    os.environ["TIME_AWARE_SEARCH_ENABLED"] = "1" if enabled else "0"
    # 测试集主题均有时效要求；强制开启避免启发式漏触发
    os.environ["TIME_AWARE_SEARCH_FORCE"] = "1" if enabled else "0"
    reset_time_aware_stats()
    clear_cache()

    cfgs = load_test_set("test_set_mvp_20261125.json")
    judge_model = os.getenv("JUDGE_MODEL") or os.getenv("EVAL_MODEL") or "deepseek-v4-pro"
    evaluator = Evaluator(judge_model_id=judge_model)

    print(f"\n{'=' * 60}\n  MVP {label}: enabled={enabled}, topics={len(cfgs)}, judge={judge_model}\n{'=' * 60}")
    scores = []
    for i, cfg in enumerate(cfgs, 1):
        print(f"\n--- [{label}] {i}/{len(cfgs)} {cfg.topic[:80]} ---")
        item = _score_one(evaluator, cfg, label, out_dir)
        scores.append(item)
        print(
            f"overall={item['overall']} loops={item['research_loop_count']} "
            f"tool_calls={item['tool_calls']} cache_hit={item['cache_hits']} "
            f"err={item['error']}"
        )

    summary = {
        "label": label,
        "enabled": enabled,
        "judge_model": judge_model,
        "stats": get_time_aware_stats(),
        "scores": scores,
    }
    (out_dir / f"eval_{label}.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary


def _dim_drop(b: dict, t: dict) -> bool:
    """任一维度掉 2 分以上视为明显变差。"""
    bd, td = b.get("dims") or {}, t.get("dims") or {}
    for k in bd:
        if k in td and (bd[k] - td[k]) >= 2:
            return True
    return False


def main() -> int:
    out_dir = REPO / "runs" / "mvp_20261125"
    out_dir.mkdir(parents=True, exist_ok=True)

    baseline = _run_arm("baseline", enabled=False, out_dir=out_dir)
    treatment = _run_arm("treatment", enabled=True, out_dir=out_dir)

    table = []
    better = worse = tie = err = 0
    timeliness_up = citation_up = False
    for b, t in zip(baseline["scores"], treatment["scores"]):
        b_ov, t_ov = b.get("overall"), t.get("overall")
        if b_ov is None or t_ov is None:
            verdict = "error"
            err += 1
        elif t_ov > b_ov:
            verdict = "更好"
            better += 1
        elif t_ov < b_ov or _dim_drop(b, t):
            verdict = "变差"
            worse += 1
        else:
            verdict = "持平"
            tie += 1

        bd, td = b.get("dims") or {}, t.get("dims") or {}
        if bd and td:
            if td.get("timeliness", 0) > bd.get("timeliness", 0):
                timeliness_up = True
            if td.get("citation_quality", 0) > bd.get("citation_quality", 0):
                citation_up = True

        table.append(
            {
                "topic": b["topic"],
                "verdict": verdict,
                "baseline_overall": b_ov,
                "treatment_overall": t_ov,
                "baseline_dims": bd,
                "treatment_dims": td,
                "baseline_loops": b.get("research_loop_count"),
                "treatment_loops": t.get("research_loop_count"),
                "tool_calls": t.get("tool_calls"),
                "cache_hits": t.get("cache_hits"),
                "cache_misses": t.get("cache_misses"),
                "baseline_report": b.get("report_path"),
                "treatment_report": t.get("report_path"),
            }
        )

    tool_called = (treatment.get("stats") or {}).get("call_count", 0) > 0
    keep = (
        better >= 3
        and worse == 0
        and (timeliness_up or citation_up)
        and tool_called
    )
    decision = "留" if keep else "删"
    reasons = {
        "better_count>=3": better >= 3,
        "no_clear_worse": worse == 0,
        "timeliness_or_citation_up": timeliness_up or citation_up,
        "tool_actually_called": tool_called,
        "better": better,
        "worse": worse,
        "tie": tie,
        "error": err,
    }

    payload = {
        "judge_model": baseline["judge_model"],
        "judge_family_note": (
            "AVAILABLE_MODELS 仅 deepseek-flash / deepseek-v4-pro，"
            "无跨家族评委；采用盲评（评委不知哪份是新工具版）+ 人工抽查。"
        ),
        "decision": decision,
        "reasons": reasons,
        "baseline": baseline,
        "treatment": treatment,
        "table": table,
        "generated_at": datetime.now().isoformat(),
    }
    cmp_path = out_dir / "ab_comparison.json"
    cmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# ToolSmith MVP A/B 对照表",
        "",
        f"- 评委模型：`{payload['judge_model']}`",
        f"- 局限：{payload['judge_family_note']}",
        f"- 结论：**{decision}**",
        f"- 判据：{json.dumps(reasons, ensure_ascii=False)}",
        "",
        "| 主题 | 基线 | 新工具 | 判定 | 循环(基→新) | 工具调用 | 缓存命中/未命中 |",
        "|---|---:|---:|---|---|---:|---|",
    ]
    for row in table:
        md_lines.append(
            f"| {row['topic'][:40]} | {row['baseline_overall']} | {row['treatment_overall']} | "
            f"{row['verdict']} | {row['baseline_loops']}→{row['treatment_loops']} | "
            f"{row['tool_calls']} | {row['cache_hits']}/{row['cache_misses']} |"
        )
    (out_dir / "ab_comparison.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(f"\n对照表: {cmp_path}")
    print(f"结论: {decision} | {reasons}")
    for row in table:
        print(
            f"[{row['verdict']}] {row['baseline_overall']} -> {row['treatment_overall']} | "
            f"loops {row['baseline_loops']}→{row['treatment_loops']} | "
            f"calls={row['tool_calls']} | {row['topic'][:50]}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
