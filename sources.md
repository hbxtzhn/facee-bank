# 内容来源与许可

## 主要来源

| 来源 | 许可证 | 用途 | 是否改动 |
|---|---|---|---|
| [Snailclimb/JavaGuide](https://github.com/Snailclimb/JavaGuide) | Apache-2.0 | 原有 Java 等题目与答案的改编基础；不包括 v1.3.0 新增 Python / FastAPI 内容 | 是（拆分/规范化/精简/去推广，详见 NOTICE） |
| 自整理面试笔记（作者原创笔记） | 随本仓库 CC-BY-4.0 | v1.2.0 新增题目（JVM/Redis/Spring Cloud/AI 应用与 RAG 及部分基础、场景题）的内容基础 | 是（脱敏、去个性化、标题规范化，详见 NOTICE） |

## v1.3.0 Python / FastAPI 内容

`questions/python-*/`（15 题）与 `questions/fastapi-*/`（15 题）为本项目新增编写并审核的内容，随本仓库 CC-BY-4.0 提供。官方文档、PEP 与 RFC 用于核对事实、版本边界和 API；参考链接及逐题修正记录见 [审核记录](docs/python-fastapi-review-v1.3.0.md)。这些参考链接不表示将相应上游文档全文或软件源代码打包进题库，原有 JavaGuide 改编内容的 Apache-2.0 声明继续保留。

## v1.5.0 Web 前端 AI 架构与前端场景实战内容（共 145 题）

`questions/fe-ai-*/`（77 题）与 `questions/fe-scenario-*/`（68 题）为本项目新增编写并审核的内容，随本仓库 CC-BY-4.0 提供。
- 题目列表来源：知乎专栏最新整理的《前端+AI及场景题完整面试题库》（https://zhuanlan.zhihu.com/p/2040501306578756424）
- 结构化与答案撰写：全面遵循“面试鸭”结构化标准进行深度原创编写（包含：一句话总结、分点深度剖析、极简核心代码、面试加分项、以及 2 个深度追问），降低死记硬背成本，强调口头表达与底层机制。

## 评估过但**未采用**的来源

| 来源 | Stars | 许可证 | 未采用原因 |
|---|---:|---|---|
| doocs/advanced-java | 79.1k | CC-BY-SA-4.0 | README 自述「大部分内容来自中华石杉，版权归作者所有」，上游权利不清；且 ShareAlike 会传染 |
| CyC2018/CS-Notes | 186k | 无 | 无许可证 = 保留所有权利 |
| AobingJava/JavaFamily | 37k | 无 | 同上 |
| 0voice/interview_internal_reference | 37.2k | 无 | 同上 |
| hadyang/interview | 4.8k | GPL-3.0 | 传染性过强 |
| frank-lam/fullstack-tutorial | 11.7k | 无 | 同上 |
| xingshaocheng/architect-awesome | 60.8k | 无 | 同上（且仅链接清单） |

详见 FaceE 项目仓库 `docs/题库内容来源调研.md`。

## v1.6.0 AgentHub 项目深挖（120 题）

`questions/agenthub-001/` 至 `questions/agenthub-120/` 为本项目新增原创编写内容，随 CC-BY-4.0 提供。按经授权的简历项目描述与项目设计经验整理为通用场景，不复制私有源码、日志、个人资料和运维配置；私有材料不随仓库或发行包公开。

TypeScript、Node.js、SQLite、Cloudflare、MDN 和 OWASP 官方资料用于核对通用机制与 API 边界，访问日期为 2026-10-30。具体题号、链接和核对范围见 [复习索引](docs/agenthub-interview-120.md#官方资料与核对范围)。官方文档不作为项目上线、个人贡献或性能指标的证明；扩展题不代表已有实现。未复制上游文档全文或私有软件源代码。
