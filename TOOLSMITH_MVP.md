# ToolSmith MVP — DeepResearch 落地验证包（v3，仓库位置已更新）

> 用途：直接丢进 Cursor 跑，跑完由 Sz 验收。
> 项目：DeepResearch（Mac 本地，LangGraph 多智能体深度研究系统）
> **工作目录（Cursor 在这里开项目、建分支、跑验证）：`/Users/zhousl/Developer/workspace/github_repo/DeepResearch`**
> **GitHub 仓库：https://github.com/zhousl-hub/DeepResearch （公开，默认分支 main，首个提交 2000e019，135 个纯文本文件，1.05 MiB）**
> 原始运行目录（只读对照，不要直接在上面改 MVP）：`/Users/zhousl/Developer/workspace/agent/DeepResearch/DeepResearch/`
> 目标：只验证一件事——从失败轨迹里造出来的 1 个新工具，能不能让报告变好。
> 时间预算：约 2.5 小时。
> 核对时间：2026-11-25 21:10 CST 实读 Mac 代码修正 v2；2026-11-25 21:38 更新仓库位置为 v3。

---

## 0. v2 修正说明（先读这节，v1 有 4 处错）

以下都是按 Mac 上实际代码改的，v1 是按 2026-11-16 的旧记录写的：

1. **模型不是 Qwen，是 DeepSeek。** `backend/src/agent/configuration.py` 现在写的是 `MODEL_ID_FLASH="deepseek-flash"`、`MODEL_ID_MAX="deepseek-v4-pro"`、`MODEL_ID_JUDEG="deepseek-v4-pro"`。查询生成默认用 `deepseek-flash`，评委默认用 `EVAL_MODEL` / `JUDGE_MODEL` 环境变量，拿不到就回退到 `deepseek-v4-pro`。所以“换一个家族当评委”不一定能直接换——要先看 `.env` / `AVAILABLE_MODELS` 里到底有哪些模型，没有跨家族模型就别硬换，改用盲评 + 人工抽查，并在结论里写明这个局限。
2. **`fresh_level` 的时间窗不是 7 / 30 / 90 天。** `backend/src/agent/kb/lifecycle.py` 的 `FRESHNESS_MAX_AGE` 是 `high=7，medium=30，low=180`。新工具必须复用这个映射，不许自己另定一套。
3. **`fresh_level` 在 eval 里会被强制成 medium。** `backend/src/agent/graph.py` 的 `confirm_plan` 里，用户说“开始研究”或“需求确认”就直接返回 `{"fresh_level": "medium"}`，不走 LLM 判断。而 `backend/eval/evaluator.py` 的自动确认流程恰恰就是发“需求确认”。所以如果触发条件只写“只有 high 才用”，在 eval 跑分时这个工具永远不会触发。v2 已把触发条件改成：`fresh_level != "low"` 且主题有时效要求，才用；同时允许测试时显式指定。
4. **`_web_search` 拿不到 `fresh_level`。** `research_agent.py` 里 `_web_search(state: WebSearchState, ...)` 收到的只有 `search_query` 和 `id` 两个字段，`fresh_level` 在 `OverallState` 里。`_fan_out_to_web_search` 和 `_route_after_critique` 用 `Send` 派发时也只传了这两个字段。所以 Cursor 必须先把 `fresh_level` 穿过 `Send` 传进去（见第 3.4 节），或者改在 `_generate_queries` 里加时间词——不许假设 `_web_search` 里能直接读到。
5. **搜索有缓存，A/B 会撞缓存。** `WebSearchAgent.step()` 先查 `search_cache`，key 是归一化后的 prompt，Redis TTL 3600 秒。基线和新工具如果用同一个查询词，第二轮会直接命中缓存，A/B 就失效了。v2 要求：时间感知查询必须改写成不同的 prompt（带时间词），并在日志里记缓存命中情况；两轮之间如果要清缓存，只清 `search_cache:*` 这个前缀。
6. **搜索返回的不是摘要，是原始页面列表。** `WebSearchAgent.step(prompt, count=10)` 返回 `list[{snippet, title, url}]`，摘要是 `_web_search` 里另外用 `Agent(model_id=query_generator_model)` + `web_searcher_instructions` 做的。还有一种降级情况：MCP 直接返回 Markdown 文本时，会返回一条 `url="https://mcp.local/search-result"` 的假页面——这不是真实来源，不许当引用计分。

其他已核对无误的点：主图名 `pro-research-agent`、`research_agent.py` 342 行、`_generate_queries → _web_search → _critique` 循环、`Configuration` 默认 `number_of_initial_queries=2`、`max_research_loops=2`、eval 入口 `backend/eval/run_eval.py`、评委 `E2EScore` 五项（事实准确、信息覆盖、逻辑结构、时效、引用质量，每项 1–5 分）。

---

## 0.5 仓库位置与分支流程（v3 新增，先读这节）

### 两个目录，别弄混

| 目录 | 用途 | 能不能改 |
|---|---|---|
| `/Users/zhousl/Developer/workspace/github_repo/DeepResearch` | **工作目录**：GitHub 仓库的本地副本，Cursor 在这里开项目、建分支、改代码、跑验证、推送 | 能改，改动都在 `toolsmith-mvp-20261125` 分支上 |
| `/Users/zhousl/Developer/workspace/agent/DeepResearch/DeepResearch/` | **原始运行目录**：DeepResearch 原来跑的地方，里面有运行时的日志、缓存和本地配置 | **本次不要直接改**，只用来对照代码和配置 |

### GitHub 仓库现状（2026-11-25 21:34 已核实）

- 仓库：https://github.com/zhousl-hub/DeepResearch ，公开，默认分支 `main`
- 首个提交：`2000e019065e1e1b5baca34552ee1c5f8b7bab50`，135 个纯文本文件，1.05 MiB
- 本地 `github_repo/DeepResearch` 是 163 项的干净拷贝，已排除 `frontend/node_modules`、`backend/logs`、所有 `__pycache__`、`*.egg-info`、`exports/`；里面有 8 张 PNG（根目录 `app.png` + backend 7 张图），**这 8 张不在 GitHub 上**，只在本地拷贝里
- 仓库里没有密钥：`configuration.py` 只读环境变量，`docker-compose.yml` 只有本地开发默认账号密码；**`.env` 不在 GitHub 上，也不在本地拷贝的 163 项里**——跑 eval 需要密钥时，从原始运行目录复制 `.env` 到工作目录本地使用，**绝不提交 `.env`**

### 分支与推送流程

1. Cursor 先在工作目录核对 git 状态：`git status`、`git log --oneline -3`、`git remote -v`。要求：当前在 `main`、工作区干净、`origin` 是 `https://github.com/zhousl-hub/DeepResearch.git`。如果 `.git` 不存在或 remote 不对，**先停下来报告，不要自己 `git init` 覆盖本地拷贝**——让 Sz 确认是重新 clone 还是就地接管。
2. 建分支并推送上游（只推分支，不直接推 main）：
   ```
   git checkout main
   git pull origin main
   git checkout -b toolsmith-mvp-20261125
   git push -u origin toolsmith-mvp-20261125
   ```
3. MVP 的所有改动、测试集、运行日志都提交到这个分支上，跑完先推送，Sz 在 GitHub 上能看到分支和提交再验收。
4. 验收通过（结论是“留”）之后才合并：Sz 决定是直接在 GitHub 上合到 `main`，还是由 Cursor 把分支上改动的文件同步回原始运行目录。**结论是“删”就不合并**，分支留在 GitHub 上备查，原始运行目录不动。
5. `.gitignore` 检查：提交前确认 `.gitignore` 已排除 `.env`、`backend/logs/`、`__pycache__/`、`frontend/node_modules/`、`exports/`、`*egg-info`；没有就先补一个再提交，不要把密钥和日志推上去。

## 一、怎么用（3 步）

1. 把本文件存到**工作目录** `/Users/zhousl/Developer/workspace/github_repo/DeepResearch/`，命名 `TOOLSMITH_MVP.md`（不要放进原始运行目录）。
2. 在 Cursor 里打开**工作目录**，开 **Agent 模式**，把下面第 2 节的提示词整段粘贴进去（或直接说“按 TOOLSMITH_MVP.md 执行”）。
3. 跑完后按第 6 节验收清单逐项核对，Cursor 必须先给你结果表和分支链接，你再决定留还是删。

---

## 二、直接粘贴给 Cursor 的提示词（整段复制）

```text
在 DeepResearch 项目里，做一个 ToolSmith MVP 验证。工作目录是 /Users/zhousl/Developer/workspace/github_repo/DeepResearch，GitHub 仓库是 https://github.com/zhousl-hub/DeepResearch（main 分支）。

第 -1 步：先核对 git，再动手。按 TOOLSMITH_MVP.md 第 0.5 节执行：git status、git log --oneline -3、git remote -v，确认在 main、工作区干净、origin 是上面那个仓库。如果 .git 不存在或 remote 不对，先停下来报告，不要自己 git init 覆盖本地拷贝。确认无误后：git checkout main && git pull origin main && git checkout -b toolsmith-mvp-20261125 && git push -u origin toolsmith-mvp-20261125。所有改动都在这个分支上，不要直接改 main，不要改原始运行目录 /Users/zhousl/Developer/workspace/agent/DeepResearch/DeepResearch/。

第 0 步：先读实际代码，不要臆测。重点文件都在 TOOLSMITH_MVP.md 第 0 节和第 7 节列出，关键事实已按 2026-11-25 实读结果写在里面，仍以你本地实际代码为准，有出入以实际代码为准并在结果里写明。跑 eval 需要密钥时，从原始运行目录复制 .env 到工作目录本地使用，绝不提交 .env；提交前检查 .gitignore 已排除 .env、backend/logs/、__pycache__/、frontend/node_modules/、exports/、*egg-info。

只做一件事：加 1 个新工具 time_aware_search，验证 ToolSmith 的思路在 DeepResearch 上是否成立。

禁区（不要碰）：
- 不要改 backend/src/agent/graph.py 的主图结构
- 不要改 backend/src/agent/sub_agents/writer_agent.py
- 不要改 backend/src/agent/kb/（Milvus research_facts）
- 不要改 auth/、db/、前端、docker-compose.yml、.env，不要输出任何密钥
- 不要覆盖 backend/eval/test_set.json，MVP 主题另外建一个测试集文件
- 不要一次性加第 2 个工具

新工具规格（见 TOOLSMITH_MVP.md 第 3 节）：
- 新文件 backend/src/agent/tools/generated_tools.py，只放这 1 个工具。tools/__init__.py 不用改，除非导入确实需要。
- 复用 backend/src/agent/base_agent.py 里的 WebSearchAgent：WebSearchAgent() 不带参数，.step(prompt, count=10) 返回 list[{snippet, title, url}]。不要另起一套搜索客户端，不要假设它返回摘要。
- 时间窗复用 backend/src/agent/kb/lifecycle.py 的 FRESHNESS_MAX_AGE：high=7 天，medium=30 天，low=180 天。
- 触发条件：fresh_level != "low" 且主题有时效要求时才用；其他情况走原有搜索。注意：_web_search 收到的 WebSearchState 里只有 search_query 和 id，没有 fresh_level，必须先把它穿过 Send 传进去（改 _fan_out_to_web_search 和 _route_after_critique，同时改 WebSearchState），默认 "medium"。
- 输出：事实列表，每条带 statement、url、published_date、source_type，不直接给结论、不 hardcode 任何主题的答案。url 是 https://mcp.local/search-result 的降级结果不算真实来源，要标记为 unknown 并丢弃。
- 缓存注意：WebSearchAgent 会按归一化后的 prompt 查缓存（TTL 3600 秒），时间感知查询必须改写成不同的 prompt，否则 A/B 第二轮会命中缓存。日志里记下每次是否命中缓存。

验证流程（见 TOOLSMITH_MVP.md 第 4、5 节）：
1. 新建 backend/eval/test_set_mvp_20261125.json，放 5 个基线主题，每个 initial_search_query_count=3、max_research_loops=3，不要动原 test_set.json。
2. 先用原有流程跑 5 个主题做基线，记录循环次数、critique 结论、缺什么、引用够不够，日志存到 runs/mvp_20261125/。
3. 再用带新工具的流程跑同一 5 个主题，同一套评分标准。入口用 python -m eval.run_eval --mode e2e --test-set test_set_mvp_20261125.json --output <文件>，从 backend/ 目录运行。
4. 评分用 eval/judge.py 的 E2EScore 五项：factual_accuracy、information_coverage、logical_structure、timeliness、citation_quality，每项 1-5 分。先查 .env / AVAILABLE_MODELS 里评委模型到底有哪些；如果只有 DeepSeek 一个家族，就不要谎称换了家族，改用盲评（不告诉评委哪份是新工具版）+ 人工抽查，并在结论里写明这个局限。
5. 输出一张对照表：每题基线分、新工具分、变好/持平/变差、新工具调用次数、循环次数变化、缓存命中情况。
6. 按第 5 节的判赢标准给出明确结论：留，还是删。不要只给“总体变好”这种模糊结论。

最后交付：
- 分支链接：https://github.com/zhousl-hub/DeepResearch/tree/toolsmith-mvp-20261125，以及 git log 和 git diff --stat（相对 main）
- 改了哪些文件（git diff --stat）
- 对照表 + 每题的报告文件路径
- 结论：留 / 删，以及理由；如果是留，写明下一步是合到 main 还是同步回原始运行目录，不要自己直接合并 main
- 如果结论是删，给出回滚命令，不要留半成品代码在主分支上。
```

---

## 三、新工具规格：`time_aware_search`

### 3.1 为什么选它

- DeepResearch 的 plan 本来就带 `fresh_level`，这个工具正好把它用起来，不用改主图。
- 失败最容易复现：问最近的事，搜到旧闻，critique 说信息不够，循环打到 `max_research_loops`。
- 验证最干净：同一主题，跑基线 vs 跑新工具，对比报告质量就行。

### 3.2 接口（按实际代码调整，语义不变）

```python
# backend/src/agent/tools/generated_tools.py
def time_aware_search(query: str, fresh_level: str = "medium") -> list[dict]:
    """返回事实列表，每条形如：
    {
        "statement": str,        # 一条事实，不写结论句
        "url": str,              # 来源 URL，必须有；是 https://mcp.local/search-result 的算 unknown，不计分
        "published_date": str,   # 能拿到就填，拿不到填 "unknown"，不许编
        "source_type": str,      # official / primary / news / other
    }
    """
```

调用方式（已核对）：

```python
from agent.base_agent import WebSearchAgent
searcher = WebSearchAgent()                       # 不带参数
pages = searcher.step(prompt=timed_query, count=10)  # 返回 list[{snippet, title, url}]
```

注意：`WebSearchAgent` 继承 `MCPAgent`，内部走 DashScope `Application.call`，用 `DASHSCOPE_API_KEY` / `APP_TOKEN` 和 `MCP_APP_ID`，自带 12 QPS 限速和 3 次重试。不要自己再包一层限速或换客户端。

### 3.3 实现要点

1. 时间窗：直接 `from agent.kb.lifecycle import FRESHNESS_MAX_AGE`，`high=7`、`medium=30`、`low=180`（天）。
2. 查询改写：原查询 + 时间词（如 `2026年11月` / `最近一周`）+ 来源限定，优先官方 / 一手。**改写后的 prompt 必须和原查询不同**，否则缓存会直接返回旧结果。
3. 取回：只取前 2 页正文抽事实，不只抄搜索摘要。摘要那一步复用 `_web_search` 现有的做法：`Agent(model_id=configurable.query_generator_model)` + `web_searcher_instructions`。
4. 去重：同一事实多个来源只留最权威的一条，其余记为佐证 URL。
5. 失败处理：超时、取回失败、没有带日期的结果时，回退到原有搜索，并在日志里写明回退原因。
6. 反单点锁定（来自 ToolSmith 论文第 7.3 节的教训）：这个工具只返回带来源的事实清单，不输出“最终答案”；如果同一事实有冲突来源，两个都返回，交给 research_agent 的 critique 环节判断，不许工具自己拍板。

### 3.4 接入点（最容易错的地方）

`research_agent.py` 里的 `_web_search` 是这样被调用的：

```python
# _generate_queries 生成查询后
Send(_WEB_SEARCH, {"search_query": q, "id": int(idx)})
# _route_after_critique 决定继续时
Send(_WEB_SEARCH, {"search_query": q, "id": state["number_of_ran_queries"] + int(idx)})
```

而 `WebSearchState` 只有两个字段：

```python
class WebSearchState(TypedDict):
    search_query: str
    id: str
```

所以接入分两步做：

1. 把 `fresh_level: str` 加进 `WebSearchState`（`backend/src/agent/state.py`），上面两个 `Send` 都带上 `fresh_level=state.get("fresh_level", "medium")`。
2. 在 `_web_search` 里读 `state.get("fresh_level", "medium")`，按第 3.3 节决定是否用时间感知查询。

备选方案（如果上面改动比预期大）：不改 `_web_search`，改在 `_generate_queries` 里——那里本来就能读到 `state.get("fresh_level", "medium")`，直接在生成查询时给时效主题加上时间词。选哪种由 Cursor 按实际代码量决定，但只能选一种，不要两处都改。

### 3.5 两道人工门（替代论文的双门验证）

- 沙箱门：拿 3 个没见过的查询跑一遍，不报错、不超时、返回带来源。
- 代码门：检查有没有写死答案、有没有绕过限速、有没有吞掉来源、有没有把 `https://mcp.local/search-result` 当真来源。

两道都过才能进 A/B；不过就改，改完重跑，不许带病上。

---

## 四、5 个基线主题（A/B 用同一套）

> 全部是 2026-11-25 已核实的内容。跑的时候不许把“必须查到”直接喂给模型，那是评分用的答案，不是输入。
> 测试集文件：新建 `backend/eval/test_set_mvp_20261125.json`，每个主题 `initial_search_query_count=3`、`max_research_loops=3`，并把下面的 `expected_key_facts` 写进去。不要覆盖原 `test_set.json`（原文件是 10 个主题，5 个唯一主题 + 5 个带用户反馈的变体）。

### 主题 1：ToolSmith 论文本身

- 提问：ToolSmith 是什么，四阶段怎么跑，效果到底多大？
- `fresh_level`：high；时间窗：最近 7 天。
- 必须查到：arXiv:2611.31198，2026 年 11 月 23 日提交，UCLA + AWS GenAI，EMNLP 2026 Findings；8 个基础工具；入库 264 个新工具；域内 / 域外提升 +1.04 到 +2.98，36/39 个格子提升。
- 来源：https://arxiv.org/abs/2611.31198 ，https://threesr.github.io/toolsmith/

### 主题 2：OpenAI 五年预训练困惑度曲线

- 提问：OpenAI 公开了什么，又提议了什么？
- `fresh_level`：high；时间窗：11 月 20 日到 25 日。
- 必须查到：公开五年预训练困惑度曲线，提议行业共设发展上限，微软率先加入；同一期里英伟达董事会恢复黄仁勋 CEO 职务。
- 来源：AI News 11 月 23 日那期，news.smol.ai

### 主题 3：LMArena 两张榜，别混了

- 提问：文本榜和 Agent Arena 到底是不是同一张榜？
- `fresh_level`：medium；时间窗：最近 30 天。
- 必须查到并分开写：文本榜前三是 Google，Carbon 1527、Argon 1520、Neon 1513；Agent Arena 第一是 Claude Fable 5.2 (Max) 1449，第二 Claude Opus 5.5 1342，第三 Gemini 4 Neon 1331。
- 来源：lmarena.ai / arena.ai

### 主题 4：Artificial Analysis v5.0.2

- 提问：现在智能指数第一是谁，开源最高是谁？
- `fresh_level`：medium；时间窗：最近 30 天。
- 必须查到：版本是 v5.0.2，第一 Claude Fable 5.2 (Max) 65 分，第二梯队 GPT-6.2 Astra (Max) 62 分；开源权重最高 Kimi K3.1 Pro 47 分；共 124 个模型；最快 GPT-6 Luna (Low) 0.6 分钟 / 任务。
- 来源：artificialanalysis.ai

### 主题 5：11 月大模型发布与榜单时间线

- 提问：11 月这波模型和榜单变化，按时间排清楚。
- `fresh_level`：high；时间窗：11 月 1 日到 25 日。
- 必须查到：Claude Fable 5.2 同时领跑 Agent Arena 和 AA 智能指数；Gemini 4 Neon 登顶 LiveBench 2.0；The Batch 11 月 20 日那期提到 Claude Fable 5.2、Anthropic IPO 和 World Labs Atlas。
- 来源：deeplearning.ai/the-batch，lmarena.ai，artificialanalysis.ai

---

## 五、评分与判赢标准

### 5.1 评分维度（就是 `eval/judge.py` 里 `E2EScore` 的五项，每项 1–5 分）

1. `factual_accuracy` 事实准确：数字、人名、日期有没有错
2. `information_coverage` 信息覆盖：关键事实有没有漏
3. `logical_structure` 逻辑结构：结构是否通顺，前后是否自洽
4. `timeliness` 时效：用的是否是最新的来源，有没有拿旧闻当新闻
5. `citation_quality` 引用质量：每个关键事实有没有可查的来源

评委入口：`Evaluator(judge_model_id=...)` → `Judge.evaluate_report(research_topic, search_sources, report)`。命令行入口：从 `backend/` 运行 `python -m eval.run_eval --mode e2e --test-set test_set_mvp_20261125.json --output <文件>`，`--judge-model` 可指定评委模型。

### 5.2 判赢标准（全部满足才留）

- 5 个主题里至少 3 个整体变好（`overall_score` 提升）
- 没有 1 个明显变差（任一维度掉 2 分以上，或整体掉分，算明显变差）
- 时效和引用这两项，至少有一项明显提升
- 新工具确实被调用了，不是摆设（调用次数和调用场景要在日志里看得见，缓存命中情况也要记）

不满足就删。删的时候不要留半成品：回滚分支，日志和对照表保留，代码不合并。

---

## 六、Sz 验收清单

跑完后，Cursor 必须先交出下面这些，你再逐项打勾：

- [ ] 工作目录是 `/Users/zhousl/Developer/workspace/github_repo/DeepResearch`，不是原始运行目录；新分支名是 `toolsmith-mvp-20261125`，已推送到 GitHub，分支链接已给出，工作区原来是干净的
- [ ] 改了哪些文件：`git diff --stat`（相对 main）已贴出，没有动禁区文件，没有覆盖 `test_set.json`，没有提交 `.env`、日志、`node_modules`、`__pycache__`
- [ ] 如果结论是“留”，合并方式已写明（GitHub 上合到 main，还是同步回原始运行目录），没有擅自合并 main
- [ ] 新工具文件在 `backend/src/agent/tools/generated_tools.py`，只有 1 个工具
- [ ] `fresh_level` 是怎么传进 `_web_search` 的已写明（改了 `WebSearchState` + 两处 `Send`，还是改在 `_generate_queries`）
- [ ] 5 个主题的基线报告 + 5 个带新工具的报告，文件路径都给了
- [ ] 对照表：每题基线分、新工具分、变好/持平/变差、调用次数、循环次数、缓存命中情况
- [ ] 评委模型已写明型号和来源（`.env` / `AVAILABLE_MODELS` 里到底有哪些）；如果只有 DeepSeek 一个家族，结论里已写明这个局限，没有谎称换了家族
- [ ] 结论明确：留 / 删，以及按第 5.2 节逐条对过的理由
- [ ] 如果是删，回滚命令已给出；如果是留，下一步只做 1 件事是什么也写清楚了（不许一次加多个工具）

---

## 七、背景（给 Cursor 读，不用改）

- DeepResearch 主图：`backend/src/agent/graph.py`，图名 `pro-research-agent`，流程 generate_plan → 计划确认（HITL，`awaiting_plan_confirmation`）→ research 子图 → writer 子图 → 结束。`confirm_plan` 里用户说“开始研究”或“需求确认”直接返回 `fresh_level="medium"`，否则用 `PlanReflection` 的 `fresh_level`（`high` = 市场数据/排行/价格，`medium` = 产品/战略/趋势，`low` = 技术原理/历史）。
- 研究子 Agent：`backend/src/agent/sub_agents/research_agent.py`（342 行），`_generate_queries` → `_web_search`（并行 `Send` 扇出）→ `_critique` 循环，直到信息足够或打到 `max_research_loops`。`_generate_queries` 里已用 `fresh_level` 查 KB：`FRESHNESS_MAX_AGE.get(freshness, 30)`，KB 默认模式 `freshness`。
- `_web_search` 实际写法：`searcher = WebSearchAgent()`，`response = searcher.step(prompt=state["search_query"], count=10)`，返回原始页面列表后走 reranker（默认关闭，`reranker_web_enabled=False`）、`resolve_urls`、再用 `Agent(model_id=configurable.query_generator_model)` + `web_searcher_instructions` 做摘要，最后抽事实写回 KB。
- 写作者子 Agent：`backend/src/agent/sub_agents/writer_agent.py`，outline → draft → critic_review（打分）→ cite_and_polish，修订上限 3 次。
- 配置：`backend/src/agent/configuration.py`，模型默认 `deepseek-flash` / `deepseek-v4-pro`，`number_of_initial_queries` 默认 2，`max_research_loops` 默认 2。
- 知识库：`backend/src/agent/kb/`，Milvus 集合 `research_facts`，本次不动。
- 评估：`backend/eval/run_eval.py`、`evaluator.py`、`judge.py`、`test_set.json`。`Evaluator._invoke_agent` 分两阶段：先拿 plan，再发“需求确认”自动确认并继续。`Judge` 默认模型取 `EVAL_MODEL` / `JUDGE_MODEL` 环境变量，拿不到回退到 `deepseek-v4-pro`。
- 北极星：最终报告质量，拆成上面五项。
- 仓库：工作目录 `/Users/zhousl/Developer/workspace/github_repo/DeepResearch` 对应 GitHub https://github.com/zhousl-hub/DeepResearch（公开，main，首个提交 2000e019，135 个纯文本文件）；原始运行目录 `/Users/zhousl/Developer/workspace/agent/DeepResearch/DeepResearch/` 本次只读对照。本地拷贝 163 项，已排除 node_modules、logs、__pycache__、egg-info、exports/，8 张 PNG 只在本地、不在 GitHub 上。
- ToolSmith 出处：arXiv:2611.31198，UCLA + AWS GenAI，EMNLP 2026 Findings。四阶段：轨迹挖掘 → 复用还是新造 → 工具生成 → 双门验证；8 个基础工具；13 个基准；36/39 格子提升。论文第 7.3 节承认的短板：视觉认错会单点锁定、越查越像，Agent 还会轻信生成工具而忽略基础工具的正确结果——所以本包第 3.3 节第 6 条要求工具只返事实清单、不拍板。
