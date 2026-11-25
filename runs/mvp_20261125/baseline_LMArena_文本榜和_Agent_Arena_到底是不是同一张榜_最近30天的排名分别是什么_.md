# LMArena 文本榜与 Agent Arena 关系及近30天排名核验报告（基于二手快照的部分核验）

> **证据限定**：截至 2026-11-25，本次未能直接抓取 arena.ai 官方原始榜单页；报告中的精确排名与分数主要来自二手快照、媒体转述与检索跳转页，统一按 **C 级证据**处理。凡涉及“前五”“前三”“完整 Top 10”的表述，均应以官方完整页、Wayback 快照或原始技术文档进一步复核。

## 1. 结论摘要与研究口径

### 1.1 一页结论

1. **LMArena 文本榜与 Agent Arena 不是同一张榜，但同属 Arena/LMArena 平台生态。** 二者共享 arena.ai 入口与平台品牌，但任务对象、评分机制、数据来源和分数体系均不同；文本榜与 WebDev 等子榜也各自独立计分，不能跨榜比较[开发者文摘](https://www.developersdigest.tech/benchmarks/lmarena)[Kaggle](https://www.kaggle.com/datasets/kaitoland/arena-multi-arena-leaderboard-panel#1)。
2. **文本榜近期排名只能作片段性确认。** 单一公开快照片段可确认的前五为 Gemini 4 Carbon、Gemini 4 Argon、Gemini 4 Neon、Muse Wonder、Claude Opus 5.5（C 级，待官方完整页复核）；其中 Muse Wonder 仅见于该单一来源，其他材料未出现，不能视为交叉确认[知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)[值得买](https://post.smzdm.com/p/a826g9w0/)[DataLearner](https://www.datalearner.com/en/leaderboards/external/text-generation)。第 6—10 名只能列为候选池。
3. **Agent Arena 近期排名需按两套口径分列。** Index 综合分方面，11-19 与 11-22 片段均显示 Claude Fable 5.2 第 1；11-19 为 Gemini 4 Neon 第 2、Claude Opus 5.5 第 3，11-22 为 Claude Opus 5.5 第 2、Gemini 4 Neon 第 3。Net Improvement 口径下，11-23 转述显示 Claude Fable 5.2 以 27.44% 居首，Claude Opus 5.5、Gemini 4 Neon 分列其后[谷歌榜](https://www.sohu.com/a/1105995736_362225)[华军软件](https://www.onlinedown.net/article/10048945.htm)。
4. **核心边界**：两榜任务、评分量纲和数据来源不同，**不能直接横向比较或混排**；Agent Arena 内部的 **Index 综合分**与 **Net Improvement 净提升度**也不能混算[华军软件](https://www.onlinedown.net/article/10048945.htm)[Kaggle](https://www.kaggle.com/datasets/kaitoland/arena-multi-arena-leaderboard-panel#1)。

### 1.2 时间范围、排名口径与证据等级

- **时间范围**：2026-10-26 至 2026-11-25；最新可核实公开更新集中在 11 月 19 日至 11 月 23 日。
- **排名口径**：文本榜以 Overall Top 10 + 可核实变化为主；Agent Arena 区分 **Index 综合分**与 **Net Improvement 净提升度**，分表呈现。
- **证据等级**：
  - **A 级**：官方原始榜单页、官方方法论/公告，本次直接核验；
  - **B 级**：官方页面经 Wayback 或权威媒体完整转录；
  - **C 级**：二手快照、媒体转述、检索跳转页。
  - 本次材料以 **C 级为主**，故全文对精确分数和完整位次均加“待官方复核”限定。

### 1.3 报告结构与数据缺口提示

报告按“身份核验 → 文本榜分析 → Agent 榜分析 → 综合讨论 → 结论与核验清单”展开。需要集中提示的数据缺口有三类：

| 缺口类型 | 具体缺口 | 影响 |
|---|---|---|
| 官方完整快照 | arena.ai 在 2026-10-26、11-19、11-22/11-25 的官方完整页未直接取得 | 无法给出 A/B 级完整 Top 10 |
| Agent 榜完整性 | Agent Arena 完整 Top 10、Net Improvement 第 4—10 名、2026-10-26 前后基线缺失 | 无法还原完整 30 天序列 |
| 文本榜完整性 | 第 6—10 名官方完整页、各模型版本说明与误差条明细缺失 | 第 6—10 名只能列为候选池 |

同时，报告将“当前排名”“30 天变化”“30 天内新上榜/显著升降”分开呈现，避免混为一谈。基于以上口径，下一章先核验两榜的身份关系。

---

## 2. 榜单身份核验：LMArena 文本榜与 Agent Arena 是否同一张榜

### 2.1 平台关系、主办方与榜单入口

Arena（原 LMArena/Chatbot Arena）于 2026 年 1 月更名；早期由 UC Berkeley SkyLab/LMSYS 创建，现由 Arena Team 运营。官网统一入口为 arena.ai，文本榜入口为 `arena.ai/leaderboard`，Agent Arena 入口为 `arena.ai/leaderboard/agents`[CSDN](https://blog.csdn.net/Pu847044653/article/details/163890040)[AI热报](https://airebao.com/item/57417)[百度百科](https://baike.baidu.com/item/Agent%20Arena/69630264)。因此，两者是“同平台生态、不同榜单页面”的关系，而非同一张榜。

关于第三方同名榜单：**给定材料未提供第三方同名权威榜单的证据**。本报告仅按材料锁定 `arena.ai/leaderboard/agents` 这一官方可核实实体，不对第三方实体作穷尽性排除；若后续出现同名产品，需另行核验其主办方、网址与评分方法。

### 2.2 六维对照：任务、评分、数据源、更新与可比性

| 维度 | LMArena 文本榜 | Agent Arena | 是否同源/可互换 |
|---|---|---|---|
| 主办方/网址 | Arena Team；arena.ai/leaderboard | Arena Team；arena.ai/leaderboard/agents | 同平台，不同页面 |
| 评测任务 | 数学、编码、创意写作、开放式对话等；匿名模型两两盲测 | 真实智能体长周期任务/会话，关注任务完成、可纠偏性、Shell 命令可靠性 | 任务对象不同 |
| 评分机制 | Bradley-Terry 类模型将成对偏好折算为 Elo/相对分，并给出置信区间 | Index 综合分；Net Improvement 为相对基线的百分比信号，采用因果追踪/IPS 类方法 | **不是同一量纲** |
| 数据来源 | 真人偏好投票；材料显示截至 2026-11-06 约 914 万票、419 个模型 | 真实用户智能体会话信号（确认、赞扬、投诉、纠正指令、Shell 错误等）；11-22 快照统计 3,175,883 次会话、69 款模型 | 来源不同 |
| 更新频率 | **材料未明确更新频率；仅见 11-06、11-14、11-19、11-22、11-23 等离散快照**，需以官方说明复核 | 同上；材料仅有离散快照，未给出官方更新周期 | 均待官方说明 |
| 模型覆盖与可比性 | 文本模型；Overall 与 WebDev 等子榜各自独立 | Agent/智能体配置；Index 与 Net Improvement 分列 | **不可跨榜比较** |

表中信息综合自上述平台、任务与评分材料[开发者文摘](https://www.developersdigest.tech/benchmarks/lmarena)[CSDN](https://blog.csdn.net/Pu847044653/article/details/163890040)[百度百科](https://baike.baidu.com/item/Agent%20Arena/69630264)[Kaggle](https://www.kaggle.com/datasets/kaitoland/arena-multi-arena-leaderboard-panel#1)。文本榜的 Elo 类分数前沿区间约 1450–1560；Agent Arena 的评分方法明确不同于 Bradley-Terry，Kaggle 材料特别提醒“classic arenas 用 Bradley-Terry，Agent Arena 用 IPS，勿把 IPS 标成 Elo”[BWIKI](https://wiki.biligame.com/ai/LMArena)[Kaggle](https://www.kaggle.com/datasets/kaitoland/arena-multi-arena-leaderboard-panel#1)。

### 2.3 判定结论与常见混淆点

综合六维对照，判定如下：

- **二者为独立榜单，分数体系不可互换**；文本榜与 WebDev 等子榜也各自独立。
- **Agent Arena 的 Index 综合分与 Net Improvement 净提升度必须分列**：前者是综合分排名，后者是相对基线的百分比信号，不能混算[华军软件](https://www.onlinedown.net/article/10048945.htm)。
- 媒体转述中常见三类风险：把两榜误称为“同一张榜”；把 Agent Arena 的 IPS/净改进率误标为 Elo；直接用文本榜分数对比 Agent 榜排名。

身份关系明确后，下一章转入文本榜的具体排名与近 30 天变化。

---

## 3. LMArena 文本榜：近 30 天排名与变化

### 3.1 最新 Top 5 与第 6—10 名候选池

下表前五来自**单一公开快照片段**（知乎 11-22 转述），属 **C 级证据**，待官方完整页复核。其中第 4 名 Muse Wonder 仅见该来源，B 站复盘、值得买、DataLearner 等材料未出现该模型，故不能称“交叉确认”[知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)[B站复盘](https://www.bilibili.com/video/BV162sD6gEVq/)[值得买](https://post.smzdm.com/p/a826g9w0/)[DataLearner](https://www.datalearner.com/en/leaderboards/external/text-generation)。

| 位次 | 模型 | 分数 | 备注 |
|---|---|---|---|
| 1 | Gemini 4 Carbon (High) | 1527 | 标注“初步结果”（Preliminary）；不同快照有 1526/1527/1528/1538 等口径 |
| 2 | Gemini 4 Argon (High) | 1520 | 与第 1 名误差条重叠，“Carbon 强于 Argon”尚不成立 |
| 3 | Gemini 4 Neon | 1512 | 与 Muse Wonder 同分，按两两对战胜率排位 |
| 4 | Muse Wonder (Max) | 1512 | **仅单一来源出现，待复核** |
| 5 | Claude Opus 5.5 | 1506 | 较 10 月底第 3 降至第 5 |

**分数差异说明**：Carbon 在 11-06 材料中为 1526±9（Preliminary），10 月底快照为 1528，11-22 快照为 1527，B 站复盘的数据集口径为 1538[开发者文摘](https://www.developersdigest.tech/benchmarks/lmarena)[知乎榜单](https://zhuanlan.zhihu.com/p/2100793100956443766)[知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)[B站复盘](https://www.bilibili.com/video/BV162sD6gEVq/)。这些差异主要来自抓取时点、数据集口径与“初步结果”状态，不能视为同一快照内的误差。

第 6—10 名无法从 11-22 片段直接确认。下表为**第 6—10 名候选池（含边界候选）**，按 11 月初快照在 Neon 插入后顺延整理，仅供定位参考，非官方确认位次：

| 候选模型 | 分数 | 备注 |
|---|---|---|
| Claude Fable 5.1 (Max) | 1504 | 10 月底第 5，11-22 可能降至第 6 |
| Claude Fable 5 (High) | 1504 | 与 Fable 5.1 同分，先后待官方页确认 |
| Claude Opus 4.6 (High) | 1503 | 候选 |
| Claude Opus 4.7 (High) | 1501 | 候选 |
| Claude Opus 4.6 | 1496 | 候选 |
| Gemini 3.8 Flash (High) | 1496 | **边界候选，约第 11**，可能挤入第 10 边界 |

> 表题中的“候选池”不表示六个连续位次；第 11 名可能挤入第 10 边界，需以官方完整页为准。

### 3.2 近 30 天排名变化与关键观察

以 10 月 27—28 日快照与 11 月 22 日快照对比，前五变化如下：

| 模型 | 10-27/28 分数（位次） | 11-22 分数（位次） | 变化观察 |
|---|---|---|---|
| Gemini 4 Carbon | 1528（1） | 1527（1） | 稳居第 1，分数基本持平 |
| Gemini 4 Argon | 1520（2） | 1520（2） | 稳居第 2 |
| Claude Opus 5.5 | 1509（3） | 1506（5） | 第 3 降至第 5 |
| Muse Wonder | 1507（4） | 1512（4） | 位次不变，分数上升 |
| Gemini 4 Neon | 未列 | 1512（3） | 进入前三 |
| Claude Fable 5.1 | 1504（5） | 1504（第 6 候选） | 掉出前五 |

数据来源：[知乎榜单](https://zhuanlan.zhihu.com/p/2100793100956443766)[知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)。

关键观察：

- **Claude 系从多人霸榜转为最高第 5**。10 月底快照中 Claude 系仍占前十多数；11-22 前五中 Claude 最高仅 Opus 5.5 第 5，第 6—10 候选池则多为 Claude 系[知乎榜单](https://zhuanlan.zhihu.com/p/2100793100956443766)[知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)。
- **Google Gemini 4 系列包揽前三**。Carbon、Argon 稳居前列，Neon 插入前三；材料称约两个月前前六名全为 Claude，如今前三已由 Google 占据[知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)。
- **OpenAI GPT 未进文本总榜前 20**（据 11-22 媒体转述，C 级）[值得买](https://post.smzdm.com/p/a826g9w0/)。
- **背景数据**：2026 年榜首全年已换 13 次，样本约 900 万票、419 个模型；中国最强 MiMo-V2.6-Pro 约 1491.6、世界第 14，中外差距从 2023 年 5 月的约 180 Elo 收窄至 2026 年 11 月的约 46.8 Elo，收窄约 74%[什么值得买](https://post.smzdm.com/p/a826g9w0/)[B站复盘](https://www.bilibili.com/video/BV162sD6gEVq/)。上述均为媒体复盘口径，待官方数据复核。

### 3.3 子榜、误差条与读榜注意事项

文本榜应以 **Overall 总榜为主、关键子榜为辅**。Overall 反映的是人类偏好式综合表现，不能替代代码、数学、长链推理等硬能力判断；WebDev 等子榜与 Overall 各自独立计分，不能互相换算[开发者文摘](https://www.developersdigest.tech/benchmarks/lmarena)。

读榜时需注意：

- **置信区间与采样误差**：Carbon 为 1526±9 且标注 Preliminary，前两名误差条重叠，微小分差不足以支撑强弱结论[开发者文摘](https://www.developersdigest.tech/benchmarks/lmarena)[知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)。
- **快照时点差异**：1527/1528/1538 等分数差异说明不同快照不可直接拼接[知乎榜单](https://zhuanlan.zhihu.com/p/2100793100956443766)[知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)[B站复盘](https://www.bilibili.com/video/BV162sD6gEVq/)。
- **读榜建议**：结合细分榜、成本与任务适配性，并用自有任务做盲测复核，不宜用单一总分替代能力判断。

文本榜的排名与口径已明确，下一章转入 Agent Arena 的两套评分口径与可核实排名片段。

---

## 4. Agent Arena：近 30 天排名与变化

### 4.1 评测定位、Index 与 Net Improvement 两套口径

Agent Arena 面向真实智能体任务与长周期会话，关注“能否把活干完”，包括任务完成、可纠偏性、Shell 命令可靠性等[百度百科](https://baike.baidu.com/item/Agent%20Arena/69630264)[榜单日报](http://mp.weixin.qq.com/s?__biz=Mzg3MzI5MjY4MA==&mid=2247483900&idx=1&sn=269e6ce370f6bbf15ba9222d02be5767)。其评分不从“两个回答投票”产生，而是从真实用户智能体会话中提取确认、赞扬、投诉、纠正指令、Shell 执行错误等信号，用因果追踪/IPS 类方法估算相对基线的净改进率；**它不是 Elo**[Kaggle](https://www.kaggle.com/datasets/kaitoland/arena-multi-arena-leaderboard-panel#1)。

**本报告对 Agent Arena 的统一口径**：

- **会话量统计仅采用 11-22 快照口径**（3,175,883 次会话、69 款模型）；材料中另有“上线不到 5 个月完成 700 万次交互会话”的报道，属不同统计窗口，不与此快照合并[华军软件](https://www.onlinedown.net/article/10048945.htm)[百度百科](https://baike.baidu.com/item/Agent%20Arena/69630264)。
- **排名分析按 11-19、11-22、11-23 各快照分别标注，不跨快照合并计算趋势**；跨快照只作“趋势观察”，不构成连续时间序列。
- **Index 综合分与 Net Improvement 净提升度分表呈现**：前者是综合分排名，后者是相对基线的百分比信号，不能混算[华军软件](https://www.onlinedown.net/article/10048945.htm)。

### 4.2 最新可核实排名片段与 30 天变化

#### 4.2.1 Index 综合分片段（非完整 Top 10）

| 模型 | 11-19 分数（位次） | 11-22 分数（位次） | 跨快照观察 |
|---|---|---|---|
| Claude Fable 5.2 (Max) | 1453（1） | 1449（1） | 保持第 1，约 -4 |
| Claude Opus 5.5 (Max) | 1335（3） | 1342（2） | 第 3→第 2，约 +7 |
| Gemini 4 Neon | 1336（2） | 1331（3） | 第 2→第 3，约 -5 |
| Gemini 4 Carbon | 未给分数（4） | 未列 | 11-22 第 4—8 名未完整列出，无法确认变化 |
| Gemini 4 Hydrogen | 未给分数（9） | 1272（9） | 第 9 保持 |
| Claude Fable 5.1 | 未列 | 1265（10） | 11-22 进入第 10 |
| Gemini 4 Argon | 未给分数（11） | 未列 | 无法确认变化 |

数据来自 11-19 谷歌榜片段与 11-22 华军软件转述[谷歌榜](https://www.sohu.com/a/1105995736_362225)[华军软件](https://www.onlinedown.net/article/10048945.htm)。11-19 片段可确认 Fable 5.2 第 1、Neon 第 2、Opus 5.5 第 3（Neon 仅比 Opus 高 1 分），Carbon、Hydrogen、Argon 分别第 4、第 9、第 11；11-22 片段可确认第 1—3 与第 9—10，第 4—8 名未完整列出。

#### 4.2.2 Net Improvement 净提升度片段

| 时点 | 模型 | 净提升度 | 备注 |
|---|---|---|---|
| 11-14 | Claude Fable 5.2 (Max) | 30.35% | 第 1 |
| 11-14 | Claude Opus 5.5 | 19.52% | 第 2 |
| 11-23 | Claude Fable 5.2 (Max) | 27.44% | 第 1 |
| 11-23 | Claude Opus 5.5 (Max) | 19.12% | 第 2 |
| 11-23 | Gemini 4 Neon (High) | 18.29% | 第 3 |
| 11-23 | 阿里 Qwen4-Max (xHigh) | 7.3% | 第 18 |

数据来自 17NAS 11-14 转述与华军软件 11-23 转述[17NAS](https://17nas.com/llm-leaderboard.php?group=tier&lang=en-US&q=GLM-5)[华军软件](https://www.onlinedown.net/article/10048945.htm)。两个时点的 Fable 5.2 数值分别为 30.35% 与 27.44%，差异可能来自统计窗口与样本更新，**不能合并计算**；第 4—10 名在材料中缺失。

#### 4.2.3 30 天变化与缺口

材料中的较早口径显示，Opus 5.5 曾居第 1、Carbon 第 2、GPT-6 Astra 第 5；结合 11-19 与 11-22 的 Index 片段，可作趋势参考：Fable 5.2 已居首，Neon 升至第 2/第 3，Opus 5.5 退至第 2/第 3 且与 Neon 分差仅 1—11 分，Carbon 退至第 4 附近[知乎/ITBEAR](https://www.sohu.com/a/1105995736_362225)[谷歌榜](https://www.sohu.com/a/1105995736_362225)[华军软件](https://www.onlinedown.net/article/10048945.htm)。但必须明确：材料没有 2026-10-26 前后的 Agent Arena 官方快照，上述只能视为“较早口径 + 11-19 至 11-22 跨快照观察”，**不能强行还原完整 30 天序列**；完整 Top 10、第 4—10 名变化及 30 天前基线均不可得。

### 4.3 成本、场景指标与非任务榜区分

材料提供的成本观察如下（量纲不同，不能直接横比）：

| 模型 | 成本指标 | 相对关系 |
|---|---|---|
| Gemini 4 Neon | 单任务中位成本 2.82 美元 | 比 Opus 5.5 低 53%，比 Fable 5.2 低 69% |
| Gemini 4 Carbon | 单任务约 1.8 美元 | 比 Opus 5.5 低 72% |
| Gemini 4 Argon | 混合价约 8 美元/百万 token | 约为 Opus 5.5（约 16 美元/百万 token）的一半 |

数据来自知乎/ITBEAR 转述与什么值得买[知乎/ITBEAR](https://www.sohu.com/a/1105995736_362225)[什么值得买](https://post.smzdm.com/p/a826g9w0/)。需注意“单任务中位成本”与“每百万 token 价格”不是同一量纲，不能直接比较。

此外，材料提到“AI Agent 对齐指数”属于**非任务榜**：OpenAI 85.2 第一，Kimi K3.1 Pro 78.2 与 Anthropic 并列第二；该指数不应混入 Agent Arena 任务榜[什么值得买](https://post.smzdm.com/p/a826g9w0/)。同一材料还称腾讯混元 Hy4 进入 Agent Arena 全球前 5，但该说法未在 11-19/11-22 的 Index 片段中得到核实，标注为**待确认**。

总体而言，Agent 榜更适合看“能否把活干完”，文本榜更适合看“人类偏好式对话与开放任务表现”。下一章在此基础上讨论两榜的可比性、可靠性与选型建议。

---

## 5. 综合讨论：可比性、可靠性与选型建议

### 5.1 两榜能否横向比较及适用场景

**结论：可以并列参考，但不能当作同一榜单或同一分数体系。** 文本榜的 Elo 类分数与 Agent Arena 的 Index/Net Improvement 分属不同量纲，不能直接换算或混排。

| 使用场景 | 优先参考 | 原因与注意 |
|---|---|---|
| 通用对话、内容生成、开放任务偏好 | 文本榜 Overall | 反映真人偏好式综合表现；需结合子榜与误差条 |
| 代码、数学、长链推理 | 文本榜关键子榜 + 自有盲测 | Overall 不能替代硬能力判断 |
| 真实代理任务、长周期执行、工具调用 | Agent Arena Index | 关注任务完成与可纠偏性 |
| 评估“相对基线净改进” | Agent Arena Net Improvement | 百分比信号，不能与 Index 混算 |
| 成本敏感型部署 | Agent 成本指标 + Index/NI | 注意单任务成本与 token 价格量纲不同 |

### 5.2 数据可靠性、快照差异与榜单博弈风险

主要可靠性风险包括：

- **采样误差与置信区间**：文本榜 Carbon 为 1526±9 且前两名误差条重叠，微小分差不足以支撑强弱结论[开发者文摘](https://www.developersdigest.tech/benchmarks/lmarena)[知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)。
- **初步结果与快照时点**：Carbon 标注 Preliminary；1527/1528/1538 等分数差异说明不同快照不可拼接[知乎榜单](https://zhuanlan.zhihu.com/p/2100793100956443766)[知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)[B站复盘](https://www.bilibili.com/video/BV162sD6gEVq/)。
- **Benchmark contamination 与任务覆盖偏差需关注**：文本榜以人类偏好为主，Agent 榜以真实会话为主，二者都可能受任务覆盖与样本结构影响[Kaggle](https://www.kaggle.com/datasets/kaitoland/arena-multi-arena-leaderboard-panel#1)。
- **榜单博弈风险**：厂商围绕榜单的评测套利、选择性披露、营销引用、刷榜嫌疑等风险需简要提示；本报告不据此推断任何厂商动机。
- **信源优先级**：官方信源优先，媒体快照需交叉验证；社区讨论可作佐证，但不作排名主数据。

### 5.3 选型与持续监测建议

选型上，建议按任务类型分流：**通用对话/内容生成看文本榜 Overall，任务执行/工具调用看 Agent Arena Index，关注净改进时另看 Net Improvement**。无论何种场景，都应联合使用 Overall、关键子榜、成本指标与自有任务盲测，避免单一榜单决策。

监测上，建议固定快照日期、区分 Index 与 Net Improvement、记录模型版本与误差条；按周留存快照，重点跟踪榜首切换、前三差距、显著升降与新上榜模型。上述讨论的边界，将在下一章汇总为核心结论与核验清单。

---

## 6. 结论与后续核验清单

### 6.1 核心问题回答

1. **LMArena 文本榜与 Agent Arena 不是同一张榜。** 二者同属 Arena/LMArena 平台生态，但任务、评分、数据源与分数体系均不同，排名与分数不可直接互换[开发者文摘](https://www.developersdigest.tech/benchmarks/lmarena)[Kaggle](https://www.kaggle.com/datasets/kaitoland/arena-multi-arena-leaderboard-panel#1)。
2. **文本榜近期可核实片段**：单一公开快照片段显示 Gemini 4 Carbon、Gemini 4 Argon、Gemini 4 Neon 居前三，Claude Opus 5.5 第 5（C 级，待官方完整页复核；Muse Wonder 仅单一来源，待复核）[知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)。第 6—10 名只能列为候选池。
3. **Agent Arena 近期可核实片段**：Index 榜 11-19/11-22 均显示 Claude Fable 5.2 第 1；11-19 为 Neon 第 2、Opus 第 3，11-22 为 Opus 第 2、Neon 第 3。Net Improvement 口径 11-23 显示 Claude Fable 5.2 以 27.44% 第 1，Opus 5.5、Neon 分列第 2、第 3[谷歌榜](https://www.sohu.com/a/1105995736_362225)[华军软件](https://www.onlinedown.net/article/10048945.htm)。
4. **所有不完整、待确认或口径冲突的数据均已标注**：文本榜第 6—10 名为候选池；Agent 完整 Top 10 与 Net Improvement 第 4—10 名缺失；2026-10-26 前后基线不可得。

### 6.2 尚需补齐的数据与信源

| 需补齐项 | 具体内容 | 用途 |
|---|---|---|
| 官方完整快照 | arena.ai 在 2026-10-26、11-19、11-22/11-25 的完整榜单页 | 将 C 级证据升级为 A/B 级 |
| Agent 榜完整性 | 完整 Top 10、Net Improvement 第 4—10 名、30 天前基线 | 还原 Agent 30 天序列 |
| 文本榜完整性 | 第 6—10 名官方完整页、各模型版本说明、误差条明细 | 确认候选池位次 |
| 原始链接 | 以官方页面、Wayback、Kaggle/技术文档替换 search.com 跳转链接 | 提升可核验性 |

### 6.3 后续更新与复核机制

- **主信源**：官方榜单页、方法论说明、Kaggle/技术文档与官方公告。
- **历史核验**：用 Wayback、官方公告、权威媒体快照做交叉验证，但需标注“重建值”与“官方值”的区别。
- **记录机制**：建议按周记录快照，持续跟踪榜首切换、前三差距、显著升降与新上榜模型；每次记录模型版本、快照日期、证据等级与误差条。
- **口径纪律**：Index 与 Net Improvement 分表记录；文本榜 Overall 与子榜分列；不跨快照合并计算趋势。

### 6.4 信源与证据等级表（基于二手快照的部分核验）

> 本次未能直接取得官方原始页面；下表均为二手转述/快照，统一标 **C 级**，官方原页尚未取得。

| 信源 | 等级 | 主要用途 | 链接 | 局限 |
|---|---|---|---|---|
| 开发者文摘 | C | 平台关系、文本评分、票数与模型数 | [开发者文摘](https://www.developersdigest.tech/benchmarks/lmarena) | 检索跳转页，原始 URL 尚未取得 |
| CSDN | C | 更名背景与官网入口 | [CSDN](https://blog.csdn.net/Pu847044653/article/details/163890040) | 二手转述 |
| AI热报 | C | 平台入口 | [AI热报](https://airebao.com/item/57417) | 二手转述 |
| 百度百科 | C | Agent 任务定位、会话规模 | [百度百科](https://baike.baidu.com/item/Agent%20Arena/69630264) | 百科类，需官方复核 |
| Kaggle | C（转述） | IPS 与 Bradley-Terry 的方法区分 | [Kaggle](https://www.kaggle.com/datasets/kaitoland/arena-multi-arena-leaderboard-panel#1) | 未见原始文档全文 |
| BWIKI | C | 文本 Elo 区间 | [BWIKI](https://wiki.biligame.com/ai/LMArena) | 二手整理 |
| 17NAS | C | 11-14 文本分数、Net Improvement 数值 | [17NAS](https://17nas.com/llm-leaderboard.php?group=tier&lang=en-US&q=GLM-5) | 快照时点有限 |
| 知乎 11-22 | C | 文本前五、Carbon 初步结果、误差条 | [知乎 11-22](https://zhuanlan.zhihu.com/p/2108995691875919223) | 单一来源，Muse Wonder 待复核 |
| 知乎榜单 | C | 10 月底文本快照 | [知乎榜单](https://zhuanlan.zhihu.com/p/2100793100956443766) | 快照不完整 |
| B站复盘 | C | 1538 口径、MiMo 位次、中外差距 | [B站复盘](https://www.bilibili.com/video/BV162sD6gEVq/) | 媒体复盘口径 |
| 什么值得买 | C | 全年换榜次数、票数、成本、对齐指数 | [什么值得买](https://post.smzdm.com/p/a826g9w0/) | 部分数据与官方口径冲突 |
| 知乎/ITBEAR | C | 较早 Agent 口径、成本、Argon 价格 | [知乎/ITBEAR](https://www.sohu.com/a/1105995736_362225) | 二手转述 |
| 华军软件 | C | 11-22 Agent Index、11-23 Net Improvement、会话量 | [华军软件](https://www.onlinedown.net/article/10048945.htm) | 第 4—8 名缺失 |
| 谷歌榜 | C | 11-19 Agent Index 片段 | [谷歌榜](https://www.sohu.com/a/1105995736_362225) | 分数不完整 |
| 榜单日报 | C | Agent 任务定位 | [榜单日报](http://mp.weixin.qq.com/s?__biz=Mzg3MzI5MjY4MA==&mid=2247483900&idx=1&sn=269e6ce370f6bbf15ba9222d02be5767) | 二手转述 |
| AI Later | C | BenchLM 非 LMArena 对照 | [AI Later](http://a.ailater.com/leaderboard) | 口径不同，未纳入主表 |
| DataLearner | C | 文本榜冲突快照对照 | [DataLearner](https://www.datalearner.com/en/leaderboards/external/text-generation) | 日期未标明，与 1538 口径冲突 |
| 值得买 11-22 | C | 文本前三与 GPT 未进前 20 | [值得买 11-22](https://post.smzdm.com/p/a826g9w0/) | 未给完整 Top 10 |

**总体结论**：现有证据足以支持“两榜不同、分数不可互换”的定性判断，也足以给出文本榜前五与 Agent Arena 前三的**片段性**排名；但不足以支撑“完整 30 天 Top 10”或“官方最终排名”的强结论。后续应以官方完整页、Wayback 快照与原始技术文档补齐数据，并将本报告的 C 级片段升级为可复核的 A/B 级证据。
