# ToolSmith MVP 交付（2026-11-25）

## 分支

- https://github.com/zhousl-hub/DeepResearch/tree/toolsmith-mvp-20261125
- 工作目录：`/Users/zhousl/Developer/workspace/github_repo/DeepResearch`
- 未改原始运行目录，未合并 `main`

## 结论：**删**

按第 5.2 节逐条：

| 判据 | 结果 |
|---|---|
| ≥3 题 overall 变好 | 通过（3/5） |
| 没有明显变差 | **不通过**（2 题 overall 掉分） |
| 时效或引用至少一项提升 | 通过（多题 timeliness / citation 上升） |
| 新工具确实被调用 | 通过（treatment 共 20 次调用，每题 4 次；缓存 0 hit / 20 miss） |

因此不合并 `main`，也不回写原始运行目录。分支保留备查。

## 对照表

| 主题 | 基线 | 新工具 | 判定 | 循环 | 工具调用 | 缓存命中/未命中 |
|---|---:|---:|---|---|---:|---|
| ToolSmith 是什么… | 3.8 | 4.6 | 更好 | 2→2 | 4 | 0/4 |
| OpenAI 公开了什么… | 4.6 | 4.4 | 变差 | 2→2 | 4 | 0/4 |
| LMArena 两张榜… | 4.2 | 4.6 | 更好 | 2→2 | 4 | 0/4 |
| Artificial Analysis… | 4.2 | 4.8 | 更好 | 2→2 | 4 | 0/4 |
| 11 月发布与榜单时间线… | 4.4 | 4.2 | 变差 | 2→2 | 4 | 0/4 |

## 改动文件（相对 main）

见 `git diff --stat main...HEAD`。要点：

- 新工具：`backend/src/agent/tools/generated_tools.py`（仅 `time_aware_search`）
- 接入：`WebSearchState` + `_fan_out_to_web_search` / `_route_after_critique` 两处 `Send` 传入 `fresh_level`；`_web_search` 条件调用
- 未改：`graph.py` 主图结构、`writer_agent.py`、`kb/`、auth/db/前端/`docker-compose`/`test_set.json`
- eval：`evaluator.py` 改为复用 event loop 的 `ainvoke`（否则多题会因 loop 关闭崩溃）

## 评委

- 模型：`deepseek-v4-pro`（来自 `.env` 缺省 / `AVAILABLE_MODELS`）
- 局限：只有 DeepSeek 一个家族，**未跨家族评委**；盲评（不告知哪份是新工具版）+ 人工抽查

## `fresh_level` 传法

采用文档主方案：改 `WebSearchState` + 两处 `Send`，默认 `"medium"`。未改 `_generate_queries` 加时间词（二选一）。

## 报告路径

- 对照：`runs/mvp_20261125/ab_comparison.json` / `ab_comparison.md`
- 基线/新工具报告：`runs/mvp_20261125/baseline_*.md`、`treatment_*.md`
- 沙箱门：`runs/mvp_20261125/sandbox_gate.json`（PASS）
- 完整日志：`runs/mvp_20261125/ab_run.log`

## 回滚（不合并 main，仅清理本地开关）

主分支未合入，无需回滚 main。若要丢弃本分支本地检出：

```bash
cd /Users/zhousl/Developer/workspace/github_repo/DeepResearch
git checkout main
git branch -D toolsmith-mvp-20261125   # 仅删本地；远程分支可留备查
# 远程备查保留：origin/toolsmith-mvp-20261125
# 若连远程也要删（一般不建议）：
# git push origin --delete toolsmith-mvp-20261125
```

## 下一步（若以后再试）

只做 1 件事：收紧触发/摘要策略，避免在基线已经很强的时效题上用「只取前 2 页」导致覆盖变窄；不要一次加第 2 个工具。
