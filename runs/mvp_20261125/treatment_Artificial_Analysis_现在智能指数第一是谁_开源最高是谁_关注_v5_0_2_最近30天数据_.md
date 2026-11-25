# Artificial Analysis 智能指数快报：v5 快照（v5.0.2 未能核验）

## 1. 报告概述与口径界定

### 1.1 研究问题与结论摘要

| 研究问题 | 当前可回答结论 | 置信度与限制 |
|---|---|---|
| 智能指数总榜第一是谁？ | 截至2026-11-17总榜快照，总榜第一为 **Anthropic Claude Fable 5.2**；官方文章确认OpenAI GPT-6.2 Astra为第二，仅落后于Fable 5.2。[官方：AA文章](https://artificialanalysis.ai/articles/openai-has-the-2-model-in-the-intelligence-index-with-the-release-of-gpt-6-2-astra-and-gpt-6-2-sol/) | 中高：官方确认榜首/第二关系；具体分差主要依赖第三方快照。 |
| 开源/开放权重最高是谁？ | **据第三方材料**，DeepSeek V4.1 Flash 1017 得33分，为开放模型最高，并称MIT许可。[第三方：Hokai](https://hokai.io/guides/best-open-weight-models) | 中低：未见AA官方Open Weights分类及DeepSeek官方模型卡/HF/GitHub核验。 |
| v5.0.2口径是否可确认？ | **v5.0.2未能核验**；材料仅能确认v5方法及2026-11-17总榜快照（并以2026-11-21 HLE-Diamond子项作为补充）。 | 不可将v5证据外推为v5.0.2结论。 |

### 1.2 数据范围、时间窗口与榜单版本（v5.0.2 / 最近30天）

时间窗口按 **2026-10-27至2026-11-26** 理解，访问日期为2026-11-26。材料可确认v5于2026-10-27替换Intelligence Index，但 **未出现v5.0.2的独立changelog、榜单或分数**；总榜可核验快照为2026-11-17，2026-11-21可核验的是HLE-Diamond子项。因此，本报告标题与结论均限定为“v5快照（v5.0.2未能核验）”，不将v5证据表述为v5.0.2口径结论。[第三方：RITS](http://rits.shanghai.nyu.edu/ai/artificial-analysis-rebuilds-its-index-60-now-private/)

### 1.3 关键定义：总榜第一、开源/开放权重、并列与排除规则

- **总榜第一**：Artificial Analysis Intelligence Index总榜（含闭源与开源）在快照时点的最高分模型。
- **开源/开放权重最高**：原则上按AA的Open Weights/开放权重分类；但本报告材料未取得AA官方分类页，故采用“据第三方材料的开放模型最高”表述，置信度中低。
- **并列与排除**：同分并列展示；排除未公开、不可复现、纯预览模型，除非官方榜单已纳入。

以下按总榜与开源两条线分别展开。

## 2. 智能指数总榜第一分析

### 2.1 当前总榜第一模型与所属机构

截至2026-11-17总榜快照，总榜第一为 **Anthropic Claude Fable 5.2**。AA官方文章称OpenAI GPT-6.2 Astra为Intelligence Index第二，且“仅落后于Claude Fable 5.2”。[官方：AA文章](https://artificialanalysis.ai/articles/openai-has-the-2-model-in-the-intelligence-index-with-the-release-of-gpt-6-2-astra-and-gpt-6-2-sol/)

### 2.2 得分、模型版本与评测设置（max/xhigh/high等）

AA官方模型页显示Claude Fable 5.2得分为 **65（max）、62（xhigh）、62（high）、56（medium）、54（low）**；max设置下生成275M输出token。[官方：Fable 5.2模型页](https://artificialanalysis.ai/zh/models/claude-fable-5-2) 第三方BizStack同日快照给出 **64.6**，与官方max的65相差0.4，可能与四舍五入、快照时间或设置口径有关，材料未说明。[第三方：BizStack](https://bizstack.tech/anthropic-leads-the-ai-benchmark-race-for-7-straight-months/)

### 2.3 与第二名及头部梯队的分差与领先格局

第三方快照显示Fable 5.2为64.6，GPT-6.2 Astra为62.1，分差 **2.5分**；但官方文章未在材料中给出两者Intelligence Index的完整分数表。头部梯队中，材料仅充分支持前二关系；AA-3D中GPT-6.2 Astra为1318、Fable 5.2为1271，但AA-3D是另一项指标，不能用于本指数分差判断。[官方：AA文章](https://artificialanalysis.ai/articles/openai-has-the-2-model-in-the-intelligence-index-with-the-release-of-gpt-6-2-astra-and-gpt-6-2-sol/)

总榜之外，开源/开放权重口径另需单独核验。

## 3. 开源/开放权重最高模型分析

### 3.1 当前开源/开放权重最高模型与机构

**据第三方材料**，DeepSeek V4.1 Flash 1017 于2026-11-05在Artificial Analysis Intelligence Index得 **33分**，为开放模型最高；GLM-5.3为32分，MiMo-V2.6-Pro为30分。[第三方：Hokai](https://hokai.io/guides/best-open-weight-models) 该结论尚未由AA官方榜单/模型页或DeepSeek官方模型卡确认，置信度中低。

### 3.2 许可、权重可获取性与版本说明

第三方称DeepSeek V4.1 Flash 1017为 **MIT许可**，但材料未包含DeepSeek官方模型卡、Hugging Face或GitHub页面，因此“权重可公开下载且许可允许研究/商用”的完整链条 **未能核验**。本报告仅将其作为“据第三方的许可信息”，不作为官方确认结论。[第三方：Hokai](https://hokai.io/guides/best-open-weight-models)

### 3.3 开源梯队内部排名及与闭源头部的差距

| 模型 | Index分数 | 口径说明 |
|---|---:|---|
| DeepSeek V4.1 Flash 1017 | 33 | 第三方；称MIT许可 |
| GLM-5.3 | 32 | 第三方；另见代理运行48.9（不同口径） |
| MiMo-V2.6-Pro | 30 | 第三方 |
| Claude Fable 5.2（闭源头部） | 64.6/65 | 第三方快照/官方max |

按现有分数粗略比较，开源最高与闭源头部存在 **约31.6–32分**的明显分数差距；但设置、来源和快照并不完全一致，只能说明“分数差距”，不能据此证明“代际差异”。第三方还称Codex设置下DeepSeek V4.1 Flash为47.3、GLM-5.3代理运行为48.9，这些与Index的33/32不是同一口径。[第三方：GPUWerk](https://gpuwerk.com/blog/best-open-weight-coding-models/)

开源结论的第三方属性也影响最近30天变化的解释。

## 4. 最近30天排名变化与关键分差

### 4.1 时间窗口内榜单更新、新收录与名次变化

| 日期 | 可确认事件 | 来源与限制 |
|---|---|---|
| 2026-10-27 | AA以v5测试套件替换Intelligence Index；称60%分数来自私有/留出答案 | [第三方：RITS](http://rits.shanghai.nyu.edu/ai/artificial-analysis-rebuilds-its-index-60-now-private/)；非v5.0.2记录 |
| 2026-11-05 | DeepSeek V4.1 Flash 1017得33，称开放模型最高 | [第三方：Hokai](https://hokai.io/guides/best-open-weight-models)；未获官方分类核验 |
| 2026-11-09 | Claude Fable 5.2发布 | [官方：Fable 5.2模型页](https://artificialanalysis.ai/zh/models/claude-fable-5-2) |
| 2026-11-17 | AA官方文章确认OpenAI GPT-6.2 Astra为第二、仅落后Fable 5.2；第三方称64.6 vs 62.1 | [官方：AA文章](https://artificialanalysis.ai/articles/openai-has-the-2-model-in-the-intelligence-index-with-the-release-of-gpt-6-2-astra-and-gpt-6-2-sol/) + [第三方：BizStack](https://bizstack.tech/anthropic-leads-the-ai-benchmark-race-for-7-straight-months/) |
| 2026-11-21 | HLE-Diamond中Fable 5.2为80.2%，GPT-6.2 Astra为72.2% | [第三方：BenchLeader](http://www.benchleader.com/zh/benchmarks/aa_hle_diamond)；子项，不是总指数 |

**逐日排名无法重建**：2026-10-27至11-09期间第一归属材料未给出；不能表述为Fable 5.2“整个窗口保持第一”。开源第一“未易主”也仅是“未见到相反材料”，不是正向证据。

### 4.2 总榜头部与开源最高模型的关键分差拆解

| 对比 | 分差 | 口径提示 |
|---|---:|---|
| Fable 5.2 vs GPT-6.2 Astra | 2.5分（64.6 vs 62.1） | 第三方；官方未给完整分数表 |
| DeepSeek V4.1 Flash 1017 vs GLM-5.3 | 1分（33 vs 32） | 第三方Index |
| DeepSeek V4.1 Flash 1017 vs MiMo-V2.6-Pro | 3分（33 vs 30） | 第三方Index |
| 开源最高 vs Fable 5.2 | 约31.6–32分 | 跨来源、跨设置，仅粗略比较 |
| HLE-Diamond：Fable 5.2 vs Astra | 8.0个百分点（80.2% vs 72.2%） | 子项，不是总指数 |
| Codex/代理运行：DeepSeek 47.3；GLM 48.9 | 不可与Index混用 | DeepSeek为Codex设置，GLM为开放模型代理运行 |

### 4.3 数据一致性核查：版本差异、分数口径与来源冲突

| 核查项 | 状态 |
|---|---|
| v5.0.2 | **未能核验**：无独立changelog、榜单或分数；本报告不作v5.0.2断言 |
| Fable 5.2分数 | 官方模型页65（max） vs 第三方64.6；差异0.4，原因未说明 |
| 总榜第二名分数 | 官方确认第二为GPT-6.2 Astra，但材料未给官方绝对分数；62.1来自第三方 |
| 开源最高33分 | 仅第三方Hokai；未见AA官方Open Weights页或DeepSeek官方模型卡 |
| Codex 47.3 vs Index 33 | 不同设置，不可直接比较 |
| HLE-Diamond 80.2% | 子项成绩，不能替代Intelligence Index总榜 |

这些不一致需要在口径与局限中明确。

## 5. 口径、局限与综合讨论

### 5.1 v5 / v5.0.2 方法变更与跨版本可比性

据第三方解读，v5新增两项测试、升级三项测试，并从AA-Omniscience移除已饱和和公开集题目；RITS称v5于2026-10-27替换旧指数、60%分数来自私有/留出答案。[第三方：Appauxin](https://appauxin.com/intelligence-index-v5-explained/) [第三方：RITS](http://rits.shanghai.nyu.edu/ai/artificial-analysis-rebuilds-its-index-60-now-private/) 但材料 **没有v5.0.2独立记录**，因此v5与v5.0.2之间、以及v5与更早版本之间的可比性无法确认。

### 5.2 数据更新延迟、评测污染与模型版本风险

- **更新延迟**：总榜可核验快照为2026-11-17，非11-26逐日数据；10-27至11-09存在空档。
- **评测污染**：第三方称v5中60%分数来自私有测试集或留出答案；该说法本身未由官方changelog核验，因此无法据此独立确认污染控制效果。
- **版本风险**：Fable 5.2存在max/xhigh/high等设置差异；开源模型还有Codex/代理等不同运行方式，混用会产生误读。

### 5.3 “第一”与“开源最高”结论的适用边界

“总榜第一”仅适用于AA Intelligence Index总榜在2026-11-17快照的语境；“开源最高”仅指第三方材料中转述的开放模型分数最高，不等同于AA官方Open Weights分类结论。两者均不适用于AA-3D、HLE-Diamond、Codex/代理等子项或设置，也不证明模型间存在“代际差异”。

据此给出结论与后续观察清单。

## 6. 结论与后续观察

### 6.1 核心结论回答：总榜第一与开源最高

截至2026-11-17总榜快照（2026-11-21仅有HLE-Diamond子项补充）：**总榜第一为Anthropic Claude Fable 5.2**（官方模型页65 max；第三方快照64.6，第二名OpenAI GPT-6.2 Astra为62.1）。**据第三方材料，开源/开放权重最高为DeepSeek V4.1 Flash 1017（33分，称MIT许可），置信度中低**，未获AA官方Open Weights分类及DeepSeek官方模型卡/HF/GitHub核验。**v5.0.2未能核验，以上不构成v5.0.2口径结论。**

### 6.2 未来30天观察指标与信源追踪清单

| 观察指标 | 触发条件/目的 |
|---|---|
| AA官方是否发布v5.0.2 changelog/榜单 | 若发布，重新核验版本与分数 |
| AA官方Open Weights分类/DeepSeek模型页 | 验证DeepSeek V4.1 Flash 1017是否属官方开放权重最高 |
| DeepSeek官方模型卡/HF/GitHub | 核验MIT许可与权重可获取性 |
| 2026-10-27至11-09历史快照 | 补足窗口内第一归属与逐日变化 |
| 同设置下Fable 5.2 vs GPT-6.2 Astra分数 | 核验2.5分差及max/xhigh/high差异 |
| 新开源模型发布与AA收录 | 判断开源第一是否变化 |
| Codex/代理设置单独追踪 | 避免与Index混用 |

**来源表（官方/第三方标注，访问日期均为2026-11-26）**

| 编号 | 标注 | 标题/内容 | 发布方 | 日期 | 类型 | 链接 |
|---|---|---|---|---|---|---|
| S1 | 官方 | OpenAI has the #2 model in the Intelligence Index with the release of GPT-6.2 Astra and GPT-6.2 Sol | Artificial Analysis | 2026-11-17 | 官方文章 | [链接](https://artificialanalysis.ai/articles/openai-has-the-2-model-in-the-intelligence-index-with-the-release-of-gpt-6-2-astra-and-gpt-6-2-sol/) |
| S2 | 官方 | Claude Fable 5.2 模型页 | Artificial Analysis | 未标注 | 官方模型页 | [链接](https://artificialanalysis.ai/zh/models/claude-fable-5-2) |
| S3 | 第三方 | Anthropic leads the AI benchmark race | BizStack | 2026-11-17 | 新闻 | [链接](https://bizstack.tech/anthropic-leads-the-ai-benchmark-race-for-7-straight-months/) |
| S4 | 第三方 | AA HLE-Diamond | BenchLeader | 未标注 | 榜单页 | [链接](http://www.benchleader.com/zh/benchmarks/aa_hle_diamond) |
| S5 | 第三方 | Best open-weight models | Hokai | 未标注 | 指南 | [链接](https://hokai.io/guides/best-open-weight-models) |
| S6 | 第三方 | Best open-weight coding models | GPUWerk | 未标注 | 博客 | [链接](https://gpuwerk.com/blog/best-open-weight-coding-models/) |
| S7 | 第三方 | Intelligence Index v5 explained | Appauxin | 未标注 | 解读 | [链接](https://appauxin.com/intelligence-index-v5-explained/) |
| S8 | 第三方 | Artificial Analysis rebuilds its index, 60% now private | RITS Shanghai NYU | 未标注 | 机构文章 | [链接](http://rits.shanghai.nyu.edu/ai/artificial-analysis-rebuilds-its-index-60-now-private/) |
