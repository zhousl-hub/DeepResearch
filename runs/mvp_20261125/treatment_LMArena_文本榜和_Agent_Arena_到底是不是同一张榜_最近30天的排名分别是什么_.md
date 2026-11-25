# LMArena 文本榜与 Agent Arena 同一性判定及最近30天排名报告

**报告日期：2026-11-26（UTC）**  
**时间窗：2026-10-28 至 2026-11-26（UTC）**  
**口径说明：** 本报告所称“LMArena 文本榜”默认指 LMArena Text Leaderboard；“Agent Arena”采用同名歧义核验策略，对平台内子榜与同名独立项目同时排查。由于本次材料未直接取得官方完整榜单页面，部分数据为第三方索引或二手转述，相关结论仍需官方页面复核。

---

## 1. 结论先行与报告框架

### 1.1 研究问题、判定标准与时间口径

本报告回答两个问题：第一，LMArena 文本榜与 Agent Arena 是否为同一张榜、同一评测体系或同一排名入口；第二，二者在 2026-10-28 至 2026-11-26（UTC）附近可得快照中的排名分别是什么。

判定采用分层标准：平台/网站入口、评测任务、数据体系、排名指标、更新周期、排名结果。时间口径采用“最新一期排名 + 关键更新快照”，而非逐日全量快照。文本榜可取得 2026-10-27（10-28 发布）、11-07、11-19、11-22 等关键节点；Agent Arena 可取得更早的二手名次/成本转述，以及 11-19、11-22 两个综合分快照，另有 11-23 报道的净提升度口径。因此，Agent Arena 不能据此还原严格意义上的完整 30 天逐日排名。

“是不是同一张榜”的初步结论是：**两者不是同一张榜，也不应视为同一排名结果；材料更倾向于显示其为同一品牌/平台生态下拆分的不同评测体系与指标。** 但需强调：文本榜入口在材料中有转述，Agent Arena 的官方唯一入口在本次材料中未获确认，因此“是否同一平台入口”只能判为“未确认”，不能直接写成“入口不同”。此外，Agent Arena 更早二手转述与 11-19/11-22 综合分快照的第一名不同，说明至少存在时点或口径差异，不能合并为同一快照。

### 1.2 核心结论：两榜关系与30天排名速览

**核心判断：** LMArena 文本榜与 Agent Arena 在评测任务、数据体系、排名指标和排名结果上均不同。文本榜是开放式盲测偏好类榜单，Agent Arena 是任务执行类榜单，二者不能用“同榜第一”表述，也不能把 Text 分数与 Agent Arena Index 综合分或净提升度直接比较。

**表1-1 LMArena 文本榜最新可得 Top5 速览（2026-11-22 快照）**

| 排名 | 模型 | 主指标分数 | 备注 | 更新时间 | 信源 |
|---:|---|---:|---|---|---|
| 1 | Gemini 4 Carbon | 1527 | 多份材料称仍标注 Preliminary；前两名误差范围存在重叠 | 2026-11-22 | [知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)；[smzdm](https://post.smzdm.com/p/a826g9w0/) |
| 2 | Gemini 4 Argon | 1520 | 10-27 快照亦为 1520 | 2026-11-22 | [知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)；[知乎10-27](https://zhuanlan.zhihu.com/p/2100793100956443766) |
| 3 | Gemini 4 Neon | 1512 | 11-19 日文页为 1519、英文页为 1513，存在页面版本差异 | 2026-11-22 | [知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)；[benchleader ja](http://www.benchleader.com/ja/benchmarks/lmarena_text)；[benchleader en](https://www.benchleader.com/benchmarks/lmarena_text) |
| 4 | Meta Muse Wonder | 1512 | 与 Neon 同为 1512，但分列第 3、第 4，排序规则未披露 | 2026-11-22 | [知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)；[benchleader en](https://www.benchleader.com/benchmarks/lmarena_text) |
| 5 | Claude Opus 5.5 | 1506 | 11-19 英文版显示其由第 4 降至第 5 | 2026-11-22 | [知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)；[benchleader en](https://www.benchleader.com/benchmarks/lmarena_text) |

**表1-2 Agent Arena 可得 Top5 速览（非完整；综合分为 2026-11-22，净提升度为 2026-11-23 报道口径）**

| 排名 | Agent/模型 | 综合分（2026-11-22） | 净提升度（2026-11-23 报道） | 每任务成本（USD） | 备注 | 信源 |
|---:|---|---:|---:|---:|---|---|
| 1 | Claude Fable 5.2 (Max) | 1449 | 27.44% | 9.16 | 领先第 2 名 107 分 | [华军软件园](https://www.onlinedown.net/article/10048945.htm) |
| 2 | Claude Opus 5.5 (Max) | 1342 | 19.12% | 5.85 | Opus 成本约为 Fable 的 64%（Fable 约为 Opus 的 1.57 倍） | [华军软件园](https://www.onlinedown.net/article/10048945.htm) |
| 3 | Gemini 4 Neon (High) | 1331 | 18.29% | 2.48 | 耗时 8.2 分钟；Fable 成本约为 Neon 的 3.7 倍 | [华军软件园](https://www.onlinedown.net/article/10048945.htm) |
| 4 | 未披露 | 未披露 | 未披露 | 未披露 | 材料未披露 | — |
| 5 | 未披露 | 未披露 | 未披露 | 未披露 | 材料未披露 | — |

注：另有更早二手转述称 Opus 5.5 在 Agent Arena 居首、Carbon 第二、GPT-6 Astra 第五，并称 Carbon 中位成本 1.8 美元、较当时榜首 Opus 5.5 低 72%；该组材料未给出可与 11-22 综合分快照直接对齐的日期/分数口径，故不并入本表，详见 4.3。

**30天速览：** 文本榜在 10-27 至 11-22 可得快照中，Gemini 4 Carbon 持续居首（分数在 1528、1526、1526、1527 间变动，且仍标 Preliminary），Gemini 4 Argon 居第二，Gemini 4 Neon 进入前三，Meta Muse Wonder 与 Claude Opus 5.5 降至第 4、第 5；前两名误差范围存在重叠。Agent Arena 方面，材料有更早的二手名次/成本转述，以及 11-19、11-22 两个综合分快照；仍不能构成严格 30 天序列。在可对齐的 11-19 至 11-22 综合分窗口中，Claude Fable 5.2 居首，领先第 2 名由 117 分收窄至 107 分，第 2、第 3 名由 Neon/Opus 互换，成本效率差异显著。

需特别标注：Agent Arena 名称存在同名/子榜歧义；Agent Arena Index 综合分与净提升度百分比不是同一套数字，不可混算；成本与耗时是否计入综合分，材料未给出方法论文档，不能由并列披露直接推断。下文进入概念界定与同一性判定。

### 1.3 报告结构与信源采信规则

本报告按“概念界定与同一性判定—文本榜排名—Agent Arena 排名—综合讨论”展开。排名表字段包括排名、模型/Agent、主指标分数、票数/置信区间（若可得）、成本/耗时（仅 Agent 表）、更新时间、信源链接。由于大量票数/置信区间未在材料中披露，表中统一写“未披露”；成本/耗时仅作为独立观察维度，不直接推断为综合分构成。

信源采信规则如下：

1. **一级：官方榜单、公告、文档、官方账号。** 本次材料未直接取得官方页面全文，仅取得对官方入口和官方 leaderboard 的转述。
2. **二级：可追溯至官方 leaderboard 的索引页或技术媒体。** 如 [developersdigest](https://www.developersdigest.tech/benchmarks/lmarena) 声称其条目来自 arena.ai 官方 leaderboard，可作为结构化参考与交叉核验。
3. **三级：知乎、什么值得买、华军软件园等二手转述。** 在官方与二级来源不可得时，可作为临时排名依据，但需在表注或信源列中标注来源层级；二手转述结论仍需官方复核。

数据冲突处理规则：同一指标不同快照以快照日期近者为主；官方优先于二级，二级优先于三级；无法判定时并列标注，不把不同快照混成同一张榜。下文先做概念与同一性判定。

---

## 2. 概念界定与同一性判定

### 2.1 LMArena 文本榜的定位、入口与评测对象

LMArena Text 榜（Text Arena Overall）覆盖数学、编程、创意写作及其他开放式任务，核心是对模型回答进行盲测偏好比较。材料显示，LMArena 将 Text 榜与 WebDev 榜（Code Arena WebDev Overall）分开计分，各自只应在同一榜单内比较，不能把 WebDev 分数与 Text 分数直接混排。[developersdigest](https://www.developersdigest.tech/benchmarks/lmarena)

材料记录：Text 榜列出 419 个模型、9,140,146 票，页面日期为 2026-11-06；10-27 快照约 900 万次累计投票、419 个模型参与。文本榜入口在二手材料中记为 `arena.ai/leaderboard/chat/text`，并提及 `canary.arena.ai`。[知乎10-27](https://zhuanlan.zhihu.com/p/2100793100956443766) 截至 2026-11-07，Gemini 4 Carbon (High) 在 Text 榜排名第一，分数 1526±9，标记 Preliminary；Claude Opus 5.5 (Max) 在 WebDev 榜排名第一，分数 1814+12/-12。[developersdigest](https://www.developersdigest.tech/benchmarks/lmarena)

这里的关键点是：Text 榜是“偏好分数”体系，WebDev 是独立子榜，二者不可跨榜比较。这也构成后文判断 Agent Arena 不能与 Text 榜混算的基础之一。接下来核验 Agent Arena 的指代。

### 2.2 Agent Arena 的指代核验

**核验 A：LMArena 平台内 Agent Arena 子榜。** 材料中，知乎文章称 Agent Arena 是需要实际执行任务的竞技场，与 Text 盲测榜不同；什么值得买文章称 Arena（原 LMArena、Chatbot Arena 一脉）将 Text Arena、Code Arena（WebDev）和 Agent Arena 拆为不同榜单，各有各的第一，并非同一张总榜。[知乎10-27](https://zhuanlan.zhihu.com/p/2100793100956443766)；[smzdm](https://post.smzdm.com/p/a826g9w0/) 这些材料支持“Agent Arena 是与 Text 不同的任务执行类榜单”，但**未给出 Agent Arena 的官方唯一入口 URL、官方公告或方法论文档**。

同一知乎材料另称，在该任务执行类 Agent Arena 中，Claude Opus 5.5 排名第一、Gemini 4 Carbon 排名第二、GPT-6 Astra 排名第五。[知乎10-27](https://zhuanlan.zhihu.com/p/2100793100956443766) 这与 11-19/11-22 综合分快照中 Fable 5.2 居首不同，说明至少存在时点或子口径差异，不能合并为同一快照。

**核验 B：同名独立第三方 Agent Arena 项目。** 本次材料中未发现可核验的独立同名项目官网、GitHub、论文或官方社交账号证据。材料另出现“AI Agent 对齐指数”（OpenAI 85.2 分居首、Kimi K3.1 Pro 78.2 分与 Anthropic 并列第二）以及“腾讯混元 Hy4 进入 Agent Arena 全球前五”等表述，但这些表述无法与本文采用的 Agent Arena Index 的 69 款模型、3,175,883 次会话口径直接对齐，故列为待核验的同名/子榜信息，不并入排名表。[smzdm](https://post.smzdm.com/p/a826g9w0/)；[华军软件园](https://www.onlinedown.net/article/10048945.htm)

**本文采用口径：** 以材料中“Agent Arena Index/Agent Arena 排名（综合分、净提升度、成本、耗时）”作为分析对象，但明确标注其官方唯一入口与方法论文档尚未在材料中确认；同名独立项目未发现可核验证据，暂不采用。对 Agent Arena 排名按快照分组呈现，不把不同时点/口径的第一名混写。该指代口径直接影响同一性矩阵中的“入口”判定，因此下一节将入口维度标为“未确认”而非“不同”。

### 2.3 同一性判定矩阵

**表2-1 LMArena 文本榜与 Agent Arena 同一性判定矩阵**

| 维度 | LMArena 文本榜 | Agent Arena | 判定 |
|---|---|---|---|
| 平台/网站入口 | 入口在二手材料中记为 `arena.ai/leaderboard/chat/text` | 官方唯一入口未在材料中确认 | **不能判定相同（未确认），非“不同”** |
| 评测任务 | 数学、编程、创意写作、开放式任务的盲测偏好 | 实际执行任务/agentic 任务 | 不同 |
| 数据体系 | 约 419 个模型、约 900 万/914 万票 | 3,175,883 次会话、69 款模型 | 不同 |
| 排名指标 | 偏好分数/Elo 类分数（如 1527） | Agent Arena Index 综合分（如 1449）与净提升度（如 27.44%） | 不同，不可混算 |
| 更新周期 | 材料有 10-27、11-07、11-19、11-22 多快照 | 更早二手名次/成本转述 + 11-19、11-22 综合分快照 | 无法证明同一更新周期 |
| 排名结果 | 第一为 Gemini 4 Carbon | 11-22 综合分第一为 Claude Fable 5.2；更早二手转述为 Opus 5.5 第一，不能合并 | 不同榜第一/不同快照第一 |

分层回答：

1. **是否同一平台入口：** 文本榜入口有二手转述；Agent Arena 官方唯一入口未确认。故只能判定“不能确认相同”，不能判定“入口不同”。
2. **是否同一评测方法：** 否。Text 是盲测偏好体系，Agent Arena 是任务执行体系。
3. **是否同一排名结果：** 否。Text 第一为 Carbon；Agent Arena 11-22 综合分第一为 Fable 5.2，更早二手转述为 Opus 5.5 第一；指标也不可换算。

风险提示：同名混淆、把 Agent Arena 的不同子口径（综合分、净提升度、AI Agent 对齐指数）混为一谈、跨榜引用“同榜第一”均可能造成误导。基于以上矩阵，下文分别列出文本榜与 Agent Arena 的可得排名。

---

## 3. LMArena 文本榜最近30天排名

### 3.1 时间窗、快照选择与指标口径

时间窗为 2026-10-28 至 2026-11-26（UTC）。文本榜选取的关键快照为：2026-10-27 数据/10-28 发布、2026-11-07、2026-11-19、2026-11-22。最新一期采用 11-22 快照；11-19 与 11-07 用于观察 30 天变化。

主指标为偏好分数；若材料提供，则保留置信区间、票数与 Preliminary 标记。实际可得情况是：11-07 材料提供 Carbon 1526±9、WebDev Opus 1814+12/-12；其余多数票数/置信区间未披露。因此表中票数/置信区间列统一写“未披露”，旧分数与名次变化放入“备注/旧值参考”列。

官网与第三方索引页存在分数差异。本次未直接取得官网页面，采信顺序按 1.3 节：一级官方不可得时，二级可追溯索引优先，三级二手转述作为临时依据。分数差异可能源于抓取时间、数据版本或页面更新滞后，需官方版本说明确认；本报告不把具体原因写成确定结论。以下进入可得范围排名表。

### 3.2 最新一期可得范围排名表与关键子类表现

**数据缺口声明：** 研究计划要求总榜 Top20 + 关键子类，但本次公开可得材料不足以还原完整 Top20。为避免把不同快照混成同一张榜，以下标题改为“可得范围排名表（非完整 Top20）”，缺失名次标“未披露”；若必须完整 Top20，应补充官方页面抓取或调整交付范围。

**表3-1 LMArena Text 可得范围排名表（非完整 Top20；以 2026-11-22 快照为主）**

| 排名（11-22） | 模型 | 主指标分数 | 票数/置信区间 | 备注/旧值参考 | 更新时间 | 信源 |
|---:|---|---:|---|---|---|---|
| 1 | Gemini 4 Carbon | 1527 | 未披露 | 仍标 Preliminary；10-27 为 1528、11-07 为 1526±9、11-19 为 1526 | 2026-11-22 | [知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)；[知乎10-27](https://zhuanlan.zhihu.com/p/2100793100956443766)；[developersdigest](https://www.developersdigest.tech/benchmarks/lmarena)；[benchleader ja](http://www.benchleader.com/ja/benchmarks/lmarena_text) |
| 2 | Gemini 4 Argon | 1520 | 未披露 | 10-27 为 1520 | 2026-11-22 | [知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)；[知乎10-27](https://zhuanlan.zhihu.com/p/2100793100956443766) |
| 3 | Gemini 4 Neon | 1512 | 未披露 | 11-19 日文页 1519、英文页 1513，存在页面版本差异 | 2026-11-22 | [知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)；[benchleader ja](http://www.benchleader.com/ja/benchmarks/lmarena_text)；[benchleader en](https://www.benchleader.com/benchmarks/lmarena_text) |
| 4 | Meta Muse Wonder | 1512 | 未披露 | 与 Neon 同为 1512，但分列第 3、第 4；11-19 英文版显示由第 3 降至第 4 | 2026-11-22 | [知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)；[benchleader en](https://www.benchleader.com/benchmarks/lmarena_text) |
| 5 | Claude Opus 5.5 | 1506 | 未披露 | 11-19 英文版显示由第 4 降至第 5 | 2026-11-22 | [知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)；[benchleader en](https://www.benchleader.com/benchmarks/lmarena_text) |
| 6-20 | 未披露 | 未披露 | 未披露 | 材料未提供完整 Top20 | — | — |

**表3-2 其他可得条目（不同快照，不能合并为 11-22 Top20）**

| 快照内名次 | 模型 | 分数 | 备注 | 快照 | 信源 |
|---:|---|---:|---|---|---|
| 7 | Claude Fable 5.2 | 1503 | 11-19 英文版榜单 | 2026-11-19 | [benchleader en](https://www.benchleader.com/benchmarks/lmarena_text) |
| 14 | Gemini 4 Hydrogen | 1490 | 11-19 日文页榜单 | 2026-11-19 | [benchleader ja](http://www.benchleader.com/ja/benchmarks/lmarena_text) |

关键子类 WebDev/Code Arena 单独列示，不与 Text 榜混排：

**表3-3 LMArena WebDev/Code Arena 可得第一**

| 榜单 | 快照 | 第一 | 分数 | 备注 | 信源 |
|---|---|---|---|---|---|
| LMArena WebDev | 2026-10-27 | Claude Opus 5.5 (Max) | 1810 | Text 榜与 WebDev 分开计分 | [知乎10-27](https://zhuanlan.zhihu.com/p/2100793100956443766) |
| LMArena WebDev | 2026-11-07 | Claude Opus 5.5 (Max) | 1814+12/-12 | 只应在 WebDev 榜内比较 | [developersdigest](https://www.developersdigest.tech/benchmarks/lmarena) |

文本榜最新可得前列显示：Carbon 仍第一但为 Preliminary，Argon 第二，Neon 进入前三，Muse Wonder 与 Opus 5.5 退至第 4、第 5；WebDev 则由 Opus 5.5 领先。下一步汇总 30 天变化与数据冲突。

### 3.3 30天排名变化、数据冲突与核验说明

在 10-27 至 11-22 的可得快照中，Carbon 的分数为 10-27 的 1528、11-07 的 1526±9、11-19 的 1526、11-22 的 1527，始终居首；多份材料称其第一名仍标 Preliminary，前两名误差范围存在重叠。[知乎10-27](https://zhuanlan.zhihu.com/p/2100793100956443766)；[developersdigest](https://www.developersdigest.tech/benchmarks/lmarena)；[benchleader ja](http://www.benchleader.com/ja/benchmarks/lmarena_text)；[smzdm](https://post.smzdm.com/p/a826g9w0/) Argon 在 10-27 与 11-22 均为 1520，居第二。[知乎10-27](https://zhuanlan.zhihu.com/p/2100793100956443766)；[知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)

Neon 在 11-19 日文页为第 3、1519，英文页为第 3、1513；11-22 为第 3、1512。[benchleader ja](http://www.benchleader.com/ja/benchmarks/lmarena_text)；[benchleader en](https://www.benchleader.com/benchmarks/lmarena_text)；[知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223) Muse Wonder 在 11-19 英文版由第 3 降至第 4，11-22 为第 4、1512；Opus 5.5 在 11-19 英文版由第 4 降至第 5，11-22 为第 5、1506。[benchleader en](https://www.benchleader.com/benchmarks/lmarena_text)；[知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)

数据冲突主要有两类：一是 Carbon 的 1526/1527/1528 差异；二是 Neon 的 1512/1513/1519 差异。结合快照日期，这些差异至少与不同快照、第三方页面更新时点和索引版本有关；但材料未提供官方版本说明，不能把“翻译版本”“取整方式”等写成确定原因。更稳妥的表述是：**可能源于抓取时间、数据版本或页面更新滞后，需官方版本说明确认。** 此外，11-22 表第 4 名 Muse Wonder 与第 3 名 Neon 同为 1512，但分列第 3、第 4；材料未说明具体排序规则，故只写“同分但排序规则未披露”。

综上，文本榜可给出的结论是：Carbon 在可得窗口内保持第一但为初步结果，Argon 稳定第二，Neon 进入前三，Muse/Opus 名次下移；完整 Top20 与票数/置信区间仍缺失。下面转向 Agent Arena 的指标口径与可得排名。

---

## 4. Agent Arena 最近30天排名

### 4.1 指标口径：综合分、净提升度、成本与耗时

Agent Arena 至少涉及两套不可混算的数字：**Agent Arena Index 综合分**（如 1449、1342）与**净提升度百分比**（如 27.44%、19.12%）。材料明确称二者不是同一套数字，不能混算。[华军软件园](https://www.onlinedown.net/article/10048945.htm) 综合分是榜单分数，净提升度是相对基线/对比口径的百分比，二者不可相加、相减或互相换算。

11-22 快照的统计口径为 3,175,883 次会话、69 款模型；排名更新时间按 2026-11-22 快照记录，净提升度按 2026-11-23 报道口径单独标注。[华军软件园](https://www.onlinedown.net/article/10048945.htm) 成本与耗时方面，11-22 华军转述数值为：Claude Fable 5.2 每任务成本 9.16 美元，Claude Opus 5.5 为 5.85 美元，Gemini 4 Neon 为 2.48 美元、耗时 8.2 分钟。按原始数值计算，9.16/5.85≈1.57，即 **Fable 5.2 每任务成本约为 Opus 5.5 的 1.57 倍；反过来说，Opus 5.5 成本约为 Fable 5.2 的 64%**。Fable 5.2 成本约为 Neon 的 3.7 倍。

另有知乎材料转述称，Neon 单任务中位成本为 2.82 美元，比 Opus 5.5 便宜 53%、比 Fable 5.2 便宜 69%；该组数值与 11-22 华军数值不同，不能混用。[知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)；[华军软件园](https://www.onlinedown.net/article/10048945.htm)

与文本榜的根本差异在于：Text 榜是盲测偏好/Elo 类分数体系；Agent Arena 是任务执行类体系，综合分与净提升度是不同指标，成本与耗时是独立观察维度。材料未说明综合分计算方法是否计入成本/耗时，因此本报告不直接推断“综合分=效果/成本”或“排名=谁在给定成本下完成得更好”；综合分是否计入成本/耗时需以官方方法论文档为准。以下按可得范围列出排名。

### 4.2 最新一期可得范围排名表与关键子类

**数据缺口声明：** 研究计划要求 Top20 + 关键子类，但材料仅能还原部分名次，且存在更早二手转述与 11-19/11-22 综合分快照两套口径。以下标题为“可得范围排名表（非完整 Top20）”，缺失名次标“未披露”。同时，综合分与净提升度分列并分别标注日期，避免把 11-22 综合分与 11-23 报道的净提升度误认为同一快照。

**表4-1 Agent Arena Index 可得范围排名表（非完整 Top20；综合分 2026-11-22，净提升度 2026-11-23 报道）**

| 排名（11-22） | Agent/模型 | 综合分（2026-11-22） | 净提升度（2026-11-23 报道） | 每任务成本（USD） | 耗时 | 备注 | 信源 |
|---:|---|---:|---:|---:|---|---|---|
| 1 | Claude Fable 5.2 (Max) | 1449 | 27.44% | 9.16 | 未披露 | 领先第 2 名 107 分 | [华军软件园](https://www.onlinedown.net/article/10048945.htm) |
| 2 | Claude Opus 5.5 (Max) | 1342 | 19.12% | 5.85 | 未披露 | Opus 成本约为 Fable 的 64%（Fable 约为 Opus 的 1.57 倍） | [华军软件园](https://www.onlinedown.net/article/10048945.htm) |
| 3 | Gemini 4 Neon (High) | 1331 | 18.29% | 2.48 | 8.2 分钟 | Fable 成本约为 Neon 的 3.7 倍 | [华军软件园](https://www.onlinedown.net/article/10048945.htm) |
| 4-8 | 未披露 | 未披露 | 未披露 | 未披露 | 未披露 | 材料未披露 | — |
| 9 | Gemini 4 Hydrogen (High) | 1272 | 未披露 | 1.51 | 5.4 分钟 | — | [华军软件园](https://www.onlinedown.net/article/10048945.htm) |
| 10 | Claude Fable 5.1 (Max) | 1265 | 未披露 | 7.28 | 10.3 分钟 | 第 2 至第 10 名分差 77 分 | [华军软件园](https://www.onlinedown.net/article/10048945.htm) |
| 11-17 | 未披露 | 未披露 | 未披露 | 未披露 | 未披露 | 材料未披露 | — |
| 18 | 阿里 Qwen4-Max (xHigh) | 未披露 | 7.3% | 未披露 | 未披露 | 净提升度为 11-23 报道口径 | [华军软件园](https://www.onlinedown.net/article/10048945.htm) |
| 19-20 | 未披露 | 未披露 | 未披露 | 未披露 | 未披露 | 材料未披露 | — |

**表4-2 Agent Arena 2026-11-19 快照关键名次对照**

| 排名（11-19） | Agent/模型 | 综合分 | 备注 | 信源 |
|---:|---|---:|---|---|
| 1 | Claude Fable 5.2 | 1453 | 11-22 降至 1449 | [知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)；[华军软件园](https://www.onlinedown.net/article/10048945.htm) |
| 2 | Gemini 4 Neon | 1336 | 11-22 与 Opus 互换，Neon 降至第 3 | [知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)；[华军软件园](https://www.onlinedown.net/article/10048945.htm) |
| 3 | Claude Opus 5.5 | 1335 | 11-22 升至第 2 | [知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)；[华军软件园](https://www.onlinedown.net/article/10048945.htm) |

知乎材料另述：Neon 单任务中位成本为 2.82 美元，比 Opus 5.5 便宜 53%，比 Fable 5.2 便宜 69%。该成本口径与 11-22 华军数值（Neon 2.48、Opus 5.85、Fable 9.16）不同，不能混用；本报告在表4-1 使用 11-22 数值，在表4-2 备注中使用知乎材料所述口径。[知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)

从 11-19 到 11-22：Fable 5.2 由 1453 降至 1449，仍居首；领先第 2 名由 117 分（1453-1336）收窄至 107 分（1449-1342）；与第 3 名分差由 118 分（1453-1335）到 118 分（1449-1331），基本持平；第 2、第 3 名由 Neon/Opus 互换。11-22 第 2 至第 10 名分差为 77 分（1342-1265），中段密集；成本效率方面，Neon 成本 2.48 美元、8.2 分钟，Hydrogen 1.51 美元、5.4 分钟，Fable 5.2 9.16 美元，差异显著。[知乎11-22](https://zhuanlan.zhihu.com/p/2108995691875919223)；[华军软件园](https://www.onlinedown.net/article/10048945.htm)

此外，另一组二手转述称 Opus 5.5 在 Agent Arena 居首、Carbon 第二、GPT-6 Astra 第五，并称 Carbon 中位成本 1.8 美元、较当时榜首 Opus 5.5 低 72%。该组材料未给出可与 11-19/11-22 综合分快照直接对齐的日期与分数口径，故仅作为时点/口径差异证据，不并入表4-1或表4-2。[知乎10-27](https://zhuanlan.zhihu.com/p/2100793100956443766)；[smzdm](https://post.smzdm.com/p/a826g9w0/)

### 4.3 30天排名变化、同榜歧义与跨口径比较禁忌

必须限定：**Agent Arena 缺乏 2026-10-28 至 2026-11-26 的完整快照序列。材料可对齐的综合分快照仅有 11-19 与 11-22，跨度约 3 天；另有更早的二手名次/成本转述，但未给出可与综合分快照直接对齐的日期与分数口径。因此不能据此代表严格 30 天排名变化。** 以下仅为“可得的 11-19 至 11-22 综合分窗口”观察，不写“最近 30 天由 Fable 领跑”这类超出数据的判断。

在该可得窗口内，Fable 5.2 保持第一；第 2、第 3 名互换；Fable 对第 2 名的领先由 117 分收窄至 107 分，对第 3 名分差基本持平。成本效率维度上，Neon 与 Hydrogen 成本较低，Fable 5.2 成本最高；但成本/耗时是否计入综合分，仍需官方方法论文档确认，不能由排名直接推断。

同名歧义排查结果：材料未发现可核验的独立第三方“Agent Arena”项目官网/论文/GitHub；但出现“AI Agent 对齐指数”“腾讯混元 Hy4 进入 Agent Arena 全球前五”，以及更早二手转述中 Opus 5.5 居首、Carbon 第二、GPT-6 Astra 第五等表述。这些信息无法与 11-22 Agent Arena Index 的 69 款模型、3,175,883 次会话口径直接对齐，故不并入本报告排名表，列为待核验的同名/子榜/时点信息。最终指代判断为：本文分析对象是材料中的 Agent Arena Index/任务执行类排名，但官方唯一入口与完整方法论文档仍待确认。[smzdm](https://post.smzdm.com/p/a826g9w0/)；[华军软件园](https://www.onlinedown.net/article/10048945.htm)；[知乎10-27](https://zhuanlan.zhihu.com/p/2100793100956443766)

跨口径禁忌：不得把 LMArena Text 分数（如 1527）与 Agent Arena Index 综合分（如 1449）直接比较；不得把 Text 分数与净提升度（如 27.44%）混算；不得把 Agent 成本/耗时直接解释为综合分构成；不得用“同榜第一”描述两个榜单的第一名。基于以上，下文给出综合讨论与结论展望。

---

## 5. 综合讨论与结论展望

### 5.1 两榜关系综合判断与使用场景

综合 2.3 节矩阵，分层结论如下：

1. **同一平台入口：未确认。** 文本榜入口有二手转述；Agent Arena 官方唯一入口未在材料中确认，故不能判定相同，也不能判定不同。
2. **同一评测方法：否。** Text 是盲测偏好体系；Agent Arena 是任务执行体系。
3. **同一数据体系与指标：否。** Text 为模型/票数/偏好分数；Agent Arena 为会话/模型/综合分/净提升度/成本/耗时。
4. **同一排名结果：否。** Text 第一为 Carbon；Agent Arena 11-22 综合分第一为 Fable 5.2，更早二手转述为 Opus 5.5 第一；不可换算。

使用场景上，LMArena 文本榜适合观察开放式任务的人类偏好排序；Agent Arena 适合观察任务执行表现、成本与耗时效率。适用边界是：各自排名只在各自榜内有效；跨榜只能做“不同维度”的并列观察，不能做分数换算或“同榜第一”传播。

### 5.2 榜单可信度、同名混淆与风险提示

主要风险包括：刷票/样本偏差、方法透明度不足、Preliminary 结果、不同快照差异、同名混淆、二手转述误差。文本榜 Carbon 第一名仍标 Preliminary 且前两名误差范围重叠，说明“第一”并非统计上不可挑战；Agent Arena 的综合分与净提升度分属不同口径，且本次材料未取得官方方法论文档，成本/耗时是否计入综合分不能确定。传播中若写“同榜第一”或“跨榜比较”，容易把不同评测体系误读为同一排名。

引用规范建议：必须注明榜单名称、入口、指标、快照时间、信源层级与是否 Preliminary/二手转述。例如引用文本榜时应写“LMArena Text Leaderboard，偏好分数，2026-11-22 快照，二手转述待官方复核”；引用 Agent Arena 时应写“Agent Arena Index，综合分 2026-11-22，净提升度为 2026-11-23 报道口径”。

### 5.3 结论、信源脚注与后续跟踪建议

**核心结论：** LMArena 文本榜与 Agent Arena 不是同一张榜，也不是同一排名结果；材料更倾向于显示其为同一品牌/平台生态下拆分的不同评测体系与指标，但 Agent Arena 官方唯一入口仍未确认。文本榜在可得窗口内由 Gemini 4 Carbon 居首（仍标 Preliminary，前两名误差范围重叠），Argon 第二，Neon 进入前三，Muse Wonder 与 Opus 5.5 降至第 4、第 5。Agent Arena 在可得的 11-19 至 11-22 两个综合分快照中由 Claude Fable 5.2 居首，领先第 2 名由 117 分收窄至 107 分；更早二手转述则称 Opus 5.5 居首，说明至少存在时点/口径差异；材料不足以给出严格 30 天排名，且完整 Top20 缺失。

未决问题：Agent Arena 官方唯一入口与完整方法论文档；综合分是否计入成本/耗时；数据可复现性；文本榜 1526/1527/1528 与 Neon 1512/1513/1519 的分数冲突原因；Agent Arena 11-22 成本数值（9.16/5.85/2.48）与知乎材料所述 Neon 2.82、Carbon 1.8 的口径差异；更早二手转述与 11-19/11-22 快照第一名差异的时点/口径原因；完整 Top20 的官方页面数据。

**信源脚注（按层级与用途列示）：**

1. [developersdigest — LMArena benchmarks](https://www.developersdigest.tech/benchmarks/lmarena)：二级索引/技术媒体，声称条目来自 arena.ai 官方 leaderboard，读取日期 2026-11-07；用于 Text/WebDev 定位、419 模型/914 万票、Carbon 1526±9、Opus WebDev 1814+12/-12。
2. [知乎 — 10-27 文本榜快照](https://zhuanlan.zhihu.com/p/2100793100956443766)：三级二手转述，2026-10-27 数据/10-28 发布；用于 Carbon 1528、Argon 1520、WebDev Opus 1810、Text 入口、Agent Arena 任务执行说明及 Opus/Carbon/GPT-6 名次转述。
3. [benchleader ja — LMArena Text](http://www.benchleader.com/ja/benchmarks/lmarena_text)：第三方索引，2026-11-19；用于最高分 1526、Neon 1519、Hydrogen 1490。
4. [benchleader en — LMArena Text](https://www.benchleader.com/benchmarks/lmarena_text)：第三方索引，2026-11-19；用于 Neon 1513、Fable 5.2 1503、Muse/Opus 名次下移。
5. [知乎 — 11-22 文本榜与 11-19 Agent Arena](https://zhuanlan.zhihu.com/p/2108995691875919223)：三级二手转述；用于 11-22 Text Top5、11-19 Agent Arena 1453/1336/1335、Neon 成本 2.82 与便宜 53%/69%。
6. [smzdm — Arena 榜单拆分与 Carbon Preliminary](https://post.smzdm.com/p/a826g9w0/)：三级二手/社区转述；用于 Text/Code/Agent 拆榜、Carbon 初步结果、前两误差重叠、AI Agent 对齐指数、Hy4、Carbon Agent Arena 中位成本 1.8 美元及较榜首 Opus 5.5 低 72% 等待核验信息。
7. [华军软件园 — Agent Arena Index 11-22 与 IT之家 11-23 净提升度](https://www.onlinedown.net/article/10048945.htm)：三级二手转述；用于 3,175,883 会话/69 模型、Fable 1449、Opus 1342、Neon 1331、Hydrogen 1272、Fable 5.1 1265、成本 9.16/5.85/2.48、净提升度 27.44%/19.12%/18.29%、Qwen4-Max 第 18 名 7.3%。

**后续跟踪建议：** 优先补抓 LMArena 官方 Text/WebDev 页面与 Agent Arena 官方入口/方法论文档；对 11-22 文本 Top20 与 Agent Arena Top20 做官方快照留存；对 Carbon Preliminary、前两误差重叠、Neon 1512/1513/1519、成本 2.48/2.82/1.8、更早名次转述与 11-19/11-22 快照第一名差异等冲突做版本说明核验；跟踪官方公告、技术文档/arXiv、第三方技术媒体与社区争议，必要时引入 Reddit/HN/X 作交叉核验。
