"""沙箱门：对 3 个未见查询跑 time_aware_search，检查不报错、有来源。"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
load_dotenv(ROOT / ".env")

from agent.tools.generated_tools import (  # noqa: E402
    get_time_aware_stats,
    reset_time_aware_stats,
    time_aware_search,
)

QUERIES = [
    "Anthropic 最近一周有什么产品或融资动态",
    "Hugging Face 最新开源模型排行有哪些变化",
    "欧盟 AI Act 最新实施时间表 2026年11月",
]


def main() -> int:
    os.environ["TIME_AWARE_SEARCH_FORCE"] = "1"
    reset_time_aware_stats()
    results = []
    ok = True
    for q in QUERIES:
        print(f"\n=== QUERY: {q} ===")
        try:
            facts = time_aware_search(q, fresh_level="medium")
        except Exception as exc:
            ok = False
            print(f"FAIL exception: {exc}")
            results.append({"query": q, "error": str(exc), "facts": []})
            continue
        print(f"facts={len(facts)}")
        for f in facts[:5]:
            print(f"  - {f.get('statement', '')[:120]}")
            print(f"    url={f.get('url')} date={f.get('published_date')} type={f.get('source_type')}")
        if not facts:
            ok = False
            print("FAIL: empty facts")
        elif any(not f.get("url") for f in facts):
            ok = False
            print("FAIL: missing url")
        else:
            print("PASS")
        results.append({"query": q, "facts": facts})

    out_dir = ROOT.parent / "runs" / "mvp_20261125"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "sandbox_gate.json"
    payload = {"ok": ok, "stats": get_time_aware_stats(), "results": results}
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nstats={get_time_aware_stats()}")
    print(f"wrote {out_path}")
    print("SANDBOX_GATE:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
