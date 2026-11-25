# ToolSmith MVP A/B 对照表

- 评委模型：`deepseek-v4-pro`
- 局限：AVAILABLE_MODELS 仅 deepseek-flash / deepseek-v4-pro，无跨家族评委；采用盲评（评委不知哪份是新工具版）+ 人工抽查。
- 结论：**删**
- 判据：{"better_count>=3": true, "no_clear_worse": false, "timeliness_or_citation_up": true, "tool_actually_called": true, "better": 3, "worse": 2, "tie": 0, "error": 0}

| 主题 | 基线 | 新工具 | 判定 | 循环(基→新) | 工具调用 | 缓存命中/未命中 |
|---|---:|---:|---|---|---:|---|
| ToolSmith 是什么，四阶段怎么跑，效果到底多大？ | 3.8 | 4.6 | 更好 | 2→2 | 4 | 0/4 |
| OpenAI 公开了什么，又提议了什么？关注最近一周尤其是11月20日到25日的 | 4.6 | 4.4 | 变差 | 2→2 | 4 | 0/4 |
| LMArena 文本榜和 Agent Arena 到底是不是同一张榜？最近30天 | 4.2 | 4.6 | 更好 | 2→2 | 4 | 0/4 |
| Artificial Analysis 现在智能指数第一是谁，开源最高是谁？关注 | 4.2 | 4.8 | 更好 | 2→2 | 4 | 0/4 |
| 2026年11月1日到25日这波大模型发布与榜单变化，按时间排清楚。 | 4.4 | 4.2 | 变差 | 2→2 | 4 | 0/4 |
