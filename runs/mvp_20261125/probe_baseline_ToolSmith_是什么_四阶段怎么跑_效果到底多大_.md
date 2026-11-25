# ToolSmith 技术情报报告：定义、四阶段机制与效果证据评估

> 引用说明：本报告沿用材料包提供的检索标识链接（`search.com/id/...`）；正文不虚构未提供的题录信息。分析对象锁定为“面向多模态搜索智能体的自动工具生成框架”这一学术版 ToolSmith，不与企业 API 工具创建框架、AI Agent 工具使用评估工具或其他同名对象混用。

## 1. 报告范围与对象界定

### 1.1 研究问题与评估口径

本报告围绕三个核心问题展开：

1. **ToolSmith 是什么**：它不是一个通用企业级 API 工具创建平台，而是面向多模态搜索智能体的自动工具生成与复用框架，在精简基础工具库之上生长、复用并路由工具模块[框架](https://threesr.github.io/toolsmith/)、[四阶段](https://aclanthology.org/2026.findings-emnlp.1699.pdf#1#6#1)。
2. **四阶段如何运行**：其流水线包括轨迹挖掘、复用或生长决策、工具生成、验证与推理路由四个阶段；核心逻辑是从基线智能体的失败轨迹中识别基础工具无法覆盖的能力缺口，再决定复用已有工具还是生成新工具[四阶段](https://aclanthology.org/2026.findings-emnlp.1699.pdf#1#6#1)、[阶段](https://arxiv.org/html/2611.31198v1)。
3. **效果到底多大**：论文报告在 3 个域内多模态搜索基准与 10 个域外基准上，相较基础工具库有稳定增益；但需区分“跨骨干/跨基准的稳定增益区间”与“特定消融/工具预算片段的单点增益”，并注意独立复现仍不足[论文评估](https://papers.cool/arxiv/2611.31198)、[结果表](https://aclanthology.org/2026.findings-emnlp.1699.pdf#2#6#2)。

评估口径采用“**定义—机制—证据—边界**”四维框架：先界定对象与同名边界，再拆解四阶段机制，随后以定量结果、实验对比、消融、成本与复现信息评估效果，最后讨论适用边界、失败条件与安全合规风险。证据强度上，本报告区分作者自评、论文实验、独立评测与生产案例；对缺少独立复现或生产部署证据的结论，明确降级表述。

### 1.2 ToolSmith 同名对象辨析与本文锁定

本文锁定的分析对象是：**面向多模态搜索智能体的自动工具生成框架**，其关键识别特征是“由 8 个原语工具组成的基础工具库 + 四阶段流水线 + 推理期工具路由”[框架](https://threesr.github.io/toolsmith/)、[基础库](https://aclanthology.org/2026.findings-emnlp.1699.pdf#2#6#2)。

围绕“ToolSmith”检索到的同名或近名对象至少包括以下几类，需在证据使用中排除或降为背景参考：

| 对象类型 | 主要特征 | 与本文对象的关系 | 本报告处理方式 |
|---|---|---|---|
| 学术版 ToolSmith（本文锁定） | 面向多模态搜索智能体；由 8 个原语工具组成基础工具库；四阶段自动工具生成与复用；推理期路由 | 本文核心对象 | 作为主要证据链 |
| 企业 API 工具创建框架 | 多智能体式 Tool Generation/Test/Validation 流程，面向企业 API 创建工具，强调沙箱闭环验证 | 同名但架构与目标不同 | 仅作验证实践背景，不作为四阶段搜索框架证据[企业版](https://ojs.aaai.org/index.php/AAAI/article/view/42388/46349#1#1#1)、[企业版2](https://openreview.net/pdf?id=S4nwmpmJK8#1#1#1) |
| AI Agent 工具使用评估工具 | 报告 `wrong_tool`、`missing_tool_call`、`hallucinated_tool`、`invalid_arguments` 等失败分类；v1.1.0 明确“不执行选中的工具” | 同名但定位为测试、lint、report，而非生产执行验证 | 仅作失败分类参考，不能直接套用于学术版框架[失败类别](https://landon-personal.github.io/toolsmith/SCHEMA.html)、[路线图](https://landon-personal.github.io/toolsmith/site/roadmap.html) |
| 动态工具管理/验证器 | 涉及工具目录查询、缓存复用、Pydantic 参数校验等 | 与四阶段框架部分概念相近，但来源独立 | 仅作验证实践参考，不能等同学术版验证标准[动态版](https://cdn.jsdelivr.net/npm/aiwg@2026.8.27/agentic/code/plugins/sdlc/agents/toolsmith-dynamic.md#1)、[验证器](https://dougli.github.io/toolsmith/) |
| Vintage Story Mod 兼容性故障 | Toolsmith 1.2.19 在特定 Optimum/Vintage Story 版本下无法启动，影响锋利度条与工具打磨 | 完全无关的同名故障 | 明确排除[兼容故障](https://github.com/StratumServer/Optimum/issues/730) |

因此，后文涉及“效果”“四阶段”“生成工具”“路由”等核心判断时，只采用学术版 ToolSmith 的论文、项目页与相关实验材料；企业版、评估版、动态验证器与游戏 Mod 故障只作为边界辨析或背景参考。

### 1.3 证据来源、时间窗与证据等级说明

本报告的时间窗默认聚焦 2024 年 11 月至 2026 年 11 月，当前日期为 2026 年 11 月 25 日。信源组合包括：论文/项目页、官方文档或项目说明、GitHub/复现资源、技术社区与独立评论。核心材料显示，学术版 ToolSmith 已有论文页、项目页与结果表信息[论文页](https://arxiv.org/abs/2611.31198v1)、[项目页](https://hot.atechcom.net/items/w7q99v48ms4rq8rwtvoxdrpp7)、[结果表](https://aclanthology.org/2026.findings-emnlp.1699.pdf#2#6#2)；作者称代码和数据已在项目页公开[项目页](https://hot.atechcom.net/items/w7q99v48ms4rq8rwtvoxdrpp7)，但截至当前材料检索，未见独立复现研究或第三方系统评估。

证据等级可按如下方式理解：

| 证据等级 | 本报告中的对应材料 | 使用方式 |
|---|---|---|
| 作者自评/项目自述 | 项目页、作者对代码和数据公开的说明 | 可确认“作者声称公开”，不能确认“独立复现成功” |
| 论文实验 | 3 个域内 + 10 个域外基准、VLM-as-a-Judge、多骨干结果 | 作为当前最强定量证据，但仍属作者实验 |
| 独立评测 | 当前材料中主要见独立批评对评估协议的讨论，未见独立复现 | 用于提示评估协议风险，不用于确认增益 |
| 生产案例 | 当前材料未见真实生产部署案例 | 生产 ROI 与长期维护结论只能标为弱证据 |

需要特别说明：该论文被来源标注为近期 preprint，真实生产系统表现、生成工具维护开销仍未验证[论文局限](https://agentic-design.ai/news-hub/toolsmith-automatic-tool-generation-framework-multimodal-search-agents-3f4c36)、[论文局限](https://agentic-design.ai/zh/news-hub/toolsmith-automatic-tool-generation-framework-multimodal-search-agents-3f4c36)。此外，VLM-as-Judge 适合 benchmark 评估，但若用于“自生成代码路径”的门控，评估协议需先加固[独立批评](https://kiranramanna.github.io/thinkit/2026/11/25/when-your-agent-runs-out-of-tools-it-should-make-one.html)。这些限制将贯穿第 4、5、6 章。

## 2. ToolSmith 定义、定位与核心架构

### 2.1 定义与问题背景

本文将 ToolSmith 定义为：**在精简基础工具库之上自动生长、复用并路由工具模块的框架**。它不要求一开始就构建庞大工具集，而是以少量基础原语工具为起点，通过四阶段流水线从失败轨迹中挖掘能力缺口，生成或复用工具，并在推理期将相关工具路由给智能体[框架](https://threesr.github.io/toolsmith/)、[四阶段](https://aclanthology.org/2026.findings-emnlp.1699.pdf#1#6#1)。

其问题背景是：多模态搜索智能体面对复杂查询模式时，基础原语工具往往无法覆盖全部能力需求。例如搜索、视觉、代码执行等原语工具可以处理通用操作，但特定查询模式可能需要组合能力、专用处理逻辑或更细粒度的工具模块。ToolSmith 试图让工具库从“静态配置”变为“可生长、可复用、可路由”的系统，以弥补基础工具库的能力缺口[基础库](https://aclanthology.org/2026.findings-emnlp.1699.pdf#2#6#2)、[流程](https://aclanthology.org/2026.findings-emnlp.1699.pdf#1#6#1)。

### 2.2 设计原则与适用场景

ToolSmith 的核心设计可以概括为三点：

1. **由 8 个原语工具组成的基础工具库**：以搜索、视觉、代码执行等八种原语工具为起点，而不是预置大量专用工具[基础库](https://aclanthology.org/2026.findings-emnlp.1699.pdf#2#6#2)。
2. **四阶段流水线**：轨迹挖掘、复用或生长决策、工具生成、验证与推理路由，形成从失败轨迹到工具准入的闭环[四阶段](https://aclanthology.org/2026.findings-emnlp.1699.pdf#1#6#1)、[阶段](https://arxiv.org/html/2611.31198v1)。
3. **推理期工具路由**：推理时以轻量检索按查询选择相关生成工具，将新工具路由给智能体[阶段](https://arxiv.org/html/2611.31198v1)。

其关键特性包括：模型无关设计[流程](https://aclanthology.org/2026.findings-emnlp.1699.pdf#1#6#1)、自动工具生成与复用、面向多模态搜索智能体部署。适用场景主要是：多模态搜索智能体、基础工具库存在明确能力缺口、且可承担端到端四阶段重跑成本的团队。若只是普通 API 编排或企业工具创建，不应直接套用该框架的结论。

### 2.3 与相关方法及同名系统的边界

同名对象的锁定与排除已在 1.2 节说明，本节只讨论技术边界。与 ToolMem、ToolLibGen 等相近工作相比，当前材料明确提示：部分搜索结果混入 ToolMem、ToolLibGen 等其他工作，不应直接作为 ToolSmith 的证据[混合页](https://arxivsignals.io/papers/2611.31198)。因此，本报告对 ToolMem、ToolLibGen 仅作背景参考，不用其指标替代 ToolSmith 的结果。

与企业版 ToolSmith 的边界在于：企业版强调 API 工具创建与沙箱闭环验证[企业版](https://d3ccyth396mz21.cloudfront.net/publications/toolsmith-a-multi-agent-framework-for-enterprise-tool-creation)、[AAAI26](https://d3ccyth396mz21.cloudfront.net/publications/a-multi-agent-framework-for-enterprise-tool-creation)，而学术版 ToolSmith 的核心是“失败轨迹挖掘—复用或生长—生成—验证与路由”的四阶段搜索智能体工具演化。与 AI Agent 工具使用评估工具相比，后者的 `wrong_tool`、`missing_tool_call` 等失败分类可用于理解工具调用失败，但不能直接套用于学术版框架的失败条件[失败类别](https://landon-personal.github.io/toolsmith/SCHEMA.html)。与动态验证器相比，其 Pydantic 参数校验等实践可作为验证参考，但不能等同于四阶段搜索框架的验证标准[验证器](https://dougli.github.io/toolsmith/)。

基于上述边界，下一章只拆解学术版 ToolSmith 的四阶段流水线。

## 3. 四阶段流水线拆解：怎么跑

### 3.1 阶段一：轨迹挖掘

阶段一的目标是从基线智能体的失败轨迹中挖掘基础工具无法处理的查询模式与能力缺口[流程](https://aclanthology.org/2026.findings-emnlp.1699.pdf#1#6#1)。其基本逻辑不是让模型直接“凭空造工具”，而是先用失败轨迹定位工具库的真实缺口，再将这些缺口转化为后续工具生成或复用的输入。

关键点有两个：

- **Phase 1 聚类数量 C 是重要超参数**：材料明确指出 Phase 1 存在聚类数量 C，并会影响最终工具库形态[聚类消融](https://aclanthology.org/2026.findings-emnlp.1699.pdf#3#6#3)、[TOOLSMITH](https://aclanthology.org/2026.findings-emnlp.1699.pdf#1#6#1)。
- **挖掘模型应与实际推理模型一致**：若挖掘模型与部署推理模型分布不匹配，可能挖到与实际推理失败模式不一致的缺口，削弱后续工具生成的有效性[ToolSmith](https://threesr.github.io/toolsmith/)。

当前材料只给出“失败轨迹—能力缺口—聚类数量”层面的描述，未提供距离度量、聚类算法、采样策略等更细的算法细节[TOOLSMITH](https://aclanthology.org/2026.findings-emnlp.1699.pdf#1#6#1)。因此，阶段一的机制可以确认，但其完整实现仍需以论文原文复核。

### 3.2 阶段二：复用或生长决策

阶段二对每个能力缺口逐一判断现有工具目录是否已覆盖；只有在未覆盖时才触发生成新工具[阶段](https://arxiv.org/html/2611.31198v1)。这体现了“先复用、后生长”的成本控制逻辑：不是每个缺口都造新工具，而是优先检查已有工具能否复用，避免工具库无序膨胀。

这一阶段的重要性在于，它把“工具生成”从无约束的扩张变为有条件的生长。若覆盖判断错误，可能导致两类问题：一是已有工具可覆盖却重复生成，增加维护成本；二是未覆盖却误判为已覆盖，导致能力缺口继续存在。当前材料对覆盖判断的具体实现细节仍不充分，需结合论文原文复核。

### 3.3 阶段三与阶段四：工具生成、验证与推理路由

阶段三针对能力缺口生成候选工具[阶段](https://arxiv.org/html/2611.31198v1)。阶段四则包含验证与推理路由：候选工具通过验证门槛后准入；推理时以轻量检索按查询选择相关生成工具[阶段](https://arxiv.org/html/2611.31198v1)、[四阶段](https://aclanthology.org/2026.findings-emnlp.1699.pdf#1#6#1)。

材料提到的验证门槛包括 **Gate 1 静态检查**与 **Gate 2 LLM critic**：失败候选可在 Gate 1 被丢弃，critic 可使用不同模型，过窄描述或缺失错误处理可在此被发现[生成管线](https://arxiv.org/html/2611.31198v1)。推理路由方面，材料明确“推理时把新工具路由给 Agent”，但未给出具体路由策略（如工具检索、选择打分、回退机制等）[ToolSmith](https://threesr.github.io/toolsmith/)。另有“动态版 ToolSmith”提到先查工具目录、返回已有工具路径与用法、缓存和复用工具，但其定位是解耦工具创建与主工作流，不能直接视为四阶段论文的路由算法[动态版](https://cdn.jsdelivr.net/npm/aiwg@2026.8.27/agentic/code/plugins/sdlc/agents/toolsmith-dynamic.md#1)。

因此，阶段三与阶段四可以确认“生成—验证—路由”的主线，但材料对 Phase 3/4 的完整实现、验证标准和路由算法仍不充分，需以论文原文复核[TOOLSMITH](https://aclanthology.org/2026.findings-emnlp.1699.pdf#1#6#1)、[ToolSmith](https://threesr.github.io/toolsmith/)。

机制明确后，下一章评估其效果到底多大、证据强度如何。

## 4. 效果评估：到底多大、证据多强

### 4.1 实验设置与基线

论文实验覆盖 3 个域内多模态搜索基准与 10 个域外基准，采用 VLM-as-a-Judge 协议评估；基线为按能力分组的 8 个原始工具组成的基础库，并覆盖多个推理骨干与部署规模[论文评估](https://papers.cool/arxiv/2611.31198)、[结果表](https://aclanthology.org/2026.findings-emnlp.1699.pdf#2#6#2)。代表性消融/工具预算片段显示：C=0 的八工具基线在 FVQA 为 55.00、MMSearch 为 51.46；C=500、|Tnew|=264 时分别升至 58.00、55.56[消融表](https://aclanthology.org/2026.findings-emnlp.1699.pdf#3#6#3)。

需要强调，实验协议是 benchmark 评估，不是生产部署评估；VLM-as-Judge 的结论适合比较基准表现，但不足以直接证明生产可靠性。

### 4.2 定量结果与增益

本节需要先校准口径：材料同时给出“跨骨干/跨基准的稳定增益区间”和“特定消融/工具预算片段的单点结果”，两者不能混为同一统计口径。

| 口径 | 设置与统计范围 | 基线 | 结果 | 增益 | 证据说明 |
|---|---|---|---|---|---|
| 整体稳定增益 | 三个推理骨干，域内与域外基准，基础库叠加 ToolSmith 生成工具 | 由 8 个原语工具组成的基础工具库 | 域内/域外均再提升约 1–3 分 | 约 +1–3 分 | 论文结果表概括，属于跨骨干/跨基准的稳定区间[结果表](https://aclanthology.org/2026.findings-emnlp.1699.pdf#2#6#2)、[结果](https://aclanthology.org/2026.findings-emnlp.1699.pdf#2#6#2) |
| 代表性消融/工具预算片段 | C=0 → C=500，\|Tnew\|=264；FVQA 与 MMSearch 单点 | FVQA 55.00；MMSearch 51.46 | FVQA 58.00；MMSearch 55.56 | FVQA +3.00；MMSearch +4.10 | 特定消融/工具预算片段，材料未明确该片段的推理骨干，不能直接外推为三骨干均值[消融表](https://aclanthology.org/2026.findings-emnlp.1699.pdf#3#6#3) |
| 更大骨干模型 | 32B 与 GPT-5 在域外基准上的表现 | 基础库 | 均有提升 | 收益更大，体现可扩展性 | 材料称更大骨干收益更大，且 32B 与 GPT-5 在所有域外基准上均有提升[结果表](https://aclanthology.org/2026.findings-emnlp.1699.pdf#2#6#2)、[论文页](https://arxiv.org/abs/2611.31198v1) |

因此，更稳妥的概括是：**基础库叠加 ToolSmith 生成工具后，三个推理骨干在域内/域外整体再提升约 1–3 分；代表性消融/工具预算片段中，FVQA +3.00、MMSearch +4.10，其中 MMSearch 的 +4.10 属 C=500、\|Tnew\|=264 的特定片段，不能等同于跨骨干整体均值。**

### 4.3 成本、消融与可复现性

成本方面：以 GPT-5 为生成器、C=500 时，一次性运行产出 264 个已验证工具，成本主要由 completion tokens 构成[成本](https://aclanthology.org/2026.findings-emnlp.1699.pdf#6#6#6)。这说明成本不是单纯的“生成工具数量”问题，而需结合生成器与 critic 调用等 token 消耗评估。

消融方面：Phase 1 聚类数量 C 会影响工具库形态与最终增益；端到端重跑 Phase 1–4 成本较高，消融变量包括由哪个模型编写新工具、挖掘哪些模型的轨迹、以及聚类数量 knob 如何塑造工具库[消融表](https://aclanthology.org/2026.findings-emnlp.1699.pdf#2#6#2)、[聚类消融](https://aclanthology.org/2026.findings-emnlp.1699.pdf#3#6#3)。这意味着实际采用时，C 与工具预算需要作为系统性超参数管理，而不能只看单次结果。

复现方面：作者称代码和数据已在项目页公开[项目页](https://hot.atechcom.net/items/w7q99v48ms4rq8rwtvoxdrpp7)，但截至当前材料检索，未见独立复现或第三方系统评估。因此，“有开放材料线索”可以确认，“独立复现成功”不能确认。下一章讨论局限、风险与适用边界。

## 5. 局限、风险与综合讨论

### 5.1 效果夸大与可复现性风险

第一，论文为近期 preprint，基准提升不等于生产可靠；真实生产系统表现、生成工具维护开销仍未验证[论文局限](https://agentic-design.ai/news-hub/toolsmith-automatic-tool-generation-framework-multimodal-search-agents-3f4c36)、[论文局限](https://agentic-design.ai/zh/news-hub/toolsmith-automatic-tool-generation-framework-multimodal-search-agents-3f4c36)。第二，VLM-as-Judge 适合 benchmark，但用于“自生成代码路径”门控时，评估协议需先加固[独立批评](https://kiranramanna.github.io/thinkit/2026/11/25/when-your-agent-runs-out-of-tools-it-should-make-one.html)。第三，当前未见独立复现或第三方系统评估，因此论文自评结果虽较强，独立证据仍不足。

此外，论文提到用 within-distribution 指标衡量生成工具是否覆盖目标失败模式[生成管线](https://arxiv.org/html/2611.31198v1)，但这仍主要是作者自评，而非独立复现。采用者不应把 benchmark 增益直接换算为生产 ROI。

### 5.2 适用边界与失败条件

适用边界：多模态搜索智能体；基础工具库存在明确能力缺口；可承担端到端四阶段重跑成本。若没有明确失败轨迹或工具库已高度覆盖，四阶段流水线的边际收益可能下降。

失败条件包括：

- 挖掘模型与推理模型分布不匹配，导致挖出的能力缺口与实际推理失败模式错位[ToolSmith](https://threesr.github.io/toolsmith/)。
- 工具目录覆盖判断错误，导致重复生成或漏生成。
- 生成工具过窄、缺少错误处理，或在 Gate 1/Gate 2 被误判。
- 路由失败：推理期轻量检索未能选择相关生成工具，导致新工具无法发挥作用[阶段](https://arxiv.org/html/2611.31198v1)。

还需注意：AI Agent 工具使用评估版 ToolSmith 的 `wrong_tool`、`missing_tool_call` 等失败分类不能直接套用于学术版框架[失败类别](https://landon-personal.github.io/toolsmith/SCHEMA.html)。它们可以帮助理解工具调用失败，但不是四阶段搜索框架的官方失败分类。

### 5.3 安全合规与滥用风险

自动生成代码执行会带来沙箱、权限、数据隐私与供应链风险。生成工具若在真实环境中执行外部 API 或文件操作，需要最小权限、隔离执行、审计日志与回滚机制。当前材料中，企业版 ToolSmith 的沙箱闭环测试可作为验证实践参考[企业版](https://d3ccyth396mz21.cloudfront.net/publications/toolsmith-a-multi-agent-framework-for-enterprise-tool-creation)、[AAAI26](https://d3ccyth396mz21.cloudfront.net/publications/a-multi-agent-framework-for-enterprise-tool-creation)；但需明确，这属于企业 API 工具创建框架，不等同于学术版四阶段搜索框架的验证标准。

另外，Pydantic 参数校验来自另一“Toolsmith 验证器”片段，仅可作为参数校验实践参考，不能直接归为企业版 ToolSmith，也不能等同于四阶段搜索框架的验证标准[验证器](https://dougli.github.io/toolsmith/)。因此，安全合规结论应分层表述：企业版材料支持沙箱闭环测试；独立验证器材料支持 Pydantic 参数校验参考；二者均不能替代学术版 ToolSmith 的 Gate 1/Gate 2 验证证据。

## 6. 结论与行动建议

### 6.1 核心结论与证据强度分级

**一句话回答：ToolSmith 是面向多模态搜索智能体的自动工具生成框架，以由 8 个原语工具组成的基础工具库为起点，通过“轨迹挖掘—复用或生长决策—生成—验证与路由”四阶段运行；论文报告基础库叠加生成工具后整体再提升约 1–3 分，代表性片段中 MMSearch 可达 +4.10，但独立复现与生产证据仍不足。**

证据强度分级如下：

| 结论 | 证据强度 | 说明 |
|---|---|---|
| 学术版 ToolSmith 的四阶段主线与基础工具库设计 | 较强（论文/项目材料一致） | 多来源一致描述四阶段与基础库[四阶段](https://aclanthology.org/2026.findings-emnlp.1699.pdf#1#6#1)、[基础库](https://aclanthology.org/2026.findings-emnlp.1699.pdf#2#6#2) |
| 基准上的稳定增益 | 中等偏强（作者实验） | 3 个域内 + 10 个域外、多骨干结果，但属作者自评[论文评估](https://papers.cool/arxiv/2611.31198) |
| 代表性消融片段 +4.10 | 中等（单点片段） | C=500、\|Tnew\|=264，骨干未在摘要明确，不能外推为整体均值[消融表](https://aclanthology.org/2026.findings-emnlp.1699.pdf#3#6#3) |
| 独立复现与第三方评估 | 弱（当前未见） | 作者称代码和数据公开，但未见独立复现[项目页](https://hot.atechcom.net/items/w7q99v48ms4rq8rwtvoxdrpp7) |
| 生产 ROI 与长期维护 | 弱（缺少生产案例） | 真实生产表现与维护开销未验证[论文局限](https://agentic-design.ai/news-hub/toolsmith-automatic-tool-generation-framework-multimodal-search-agents-3f4c36) |

### 6.2 对采用者与研究者的建议

对采用者：

1. **先小规模试点**：选择一条多模态搜索业务线，建立基础库基线，再引入 ToolSmith 生成工具，避免一次性全量替换。
2. **建立工具预算与失败轨迹监控**：把 C、|Tnew|、生成器模型、critic 模型纳入配置管理；监控失败轨迹是否被新工具覆盖。
3. **重点验证路由与维护成本**：不仅看 benchmark 增益，还要看推理期路由准确率、工具调用失败率、生成工具维护开销与回滚成本。
4. **设置回滚机制**：生成工具准入后仍需保留禁用与回退路径，避免路由失败或工具过窄导致系统退化。

对研究者：

1. **优先复现 Phase 1–4**：尤其是 Phase 1 聚类算法、距离度量、采样策略，以及 Phase 3/4 的验证门槛与路由打分。
2. **补充第三方独立评测**：在相同基准与不同骨干上复现，并报告置信区间与统计口径。
3. **区分整体增益与片段增益**：报告跨骨干均值、逐基准结果与消融片段，避免把单点 +4.10 写成整体结论。

### 6.3 后续研究重点

仍缺少的证据包括：完整四阶段实现细节、Phase 1 聚类算法与距离度量、工具验证门槛、路由选择打分与回退机制。后续研究可优先开展：生产环境案例、成本收益分析、跨骨干模型泛化、安全合规评估与长期工具库演化研究。

总体而言，ToolSmith 的机制创新与 benchmark 证据值得关注，但其“效果到底多大”应表述为：**整体稳定增益约 1–3 分，代表性片段中 MMSearch 可达 +4.10，当前证据以作者实验为主，独立复现与生产 ROI 证据仍较弱。**
