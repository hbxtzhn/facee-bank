# FaceE 题库

一份**开源的程序员面试题库**，配合 [FaceE](https://github.com/hbxtzhn/facee) 离线刷题。

当前版本 **2.0.0**：按[题库规范 v2](https://github.com/hbxtzhn/facee/blob/main/docs/题库规范-v2-草案.md) 重建的基础题库第一版，**784 题**，覆盖 Java 后端与 AI 应用的八股基础。答案以「通俗好懂」为第一优先级，面向基础薄弱、主要做过项目的求职者。

## 怎么用

在 FaceE 的「我的」页添加线上题库，填写：

```
https://github.com/hbxtzhn/facee-bank/releases/latest/download/latest.json
```

已添加的题库会按版本自动检查更新。2.0.0 与 1.x 题库格式不兼容，需要使用支持规范 v2 的 FaceE 版本。

## 包含什么

| 分类 | 题数 |
|---|---:|
| Java 基础与集合 | 59 |
| Java 并发 | 71 |
| JVM | 58 |
| Spring 生态（含 MyBatis） | 155 |
| MySQL | 89 |
| Redis | 94 |
| 网络与 HTTP | 61 |
| 操作系统 | 59 |
| 分布式与微服务（含消息队列） | 56 |
| AI 应用工程 | 82 |

- **学习路线**：11 条，每条按思维导图顺序把一块知识完整过一遍，前置题排在前面。
- **知识点标签**：126 个，两层树，可跨领域（如「I/O 多路复用」同时串起 Redis、操作系统和 Java NIO 的题）。
- **前置关系**：442 道题标注了需要先懂的题，App 里可以直接跳转。
- **难度与重要度**：easy / medium / hard；重要度 3 / 2 / 1 约占 20% / 60% / 20%。

## 每道题的结构

一句话结论 → 3–5 条要点（自评用）→ 详解（「先搞懂」白话铺垫、机制讲解、方案对比表、进阶）→ 示例 → 易错点 → 追问。写作规范见 [`prompts/answer.md`](prompts/answer.md) 与 [`prompts/write.md`](prompts/write.md)。

## 反馈

题目有错或讲得不清楚：在 App 里点「反馈」，或直接[提 issue](https://github.com/hbxtzhn/facee-bank/issues/new?template=content.yml)。

## 自己维护

本仓库是**题目源文件**：`bank.yaml`（分类、标签、学习路线）+ `questions/<分类>/q_<ULID>.md`。工具在 [FaceE 仓库](https://github.com/hbxtzhn/facee) 的 `packages/bank-spec`，常用命令和维护脚本见 [`AGENTS.md`](AGENTS.md)。

- 每次 PR 和推送由 CI 校验格式、内容规则、标签和学习路线顺序。
- 推送 `v*` 标签自动构建并发布 Release（`bundle-<版本>.json` + `latest.json`）。
- 题目清单在 `plans/`，批量生成与审校流程见 `scripts/fast.mjs`、`prompts/review.md`。

## 来源与许可

- 2.0.0 的题目由作者整理的八股知识大纲确定范围，答案为重新编写，并按官方文档抽查核对了含具体数字和版本行为的说法。
- 题目内容采用 **CC-BY-4.0**。1.x 版本中改编自 [JavaGuide](https://github.com/Snailclimb/JavaGuide)（Apache-2.0）的内容的许可与改动声明见 `LICENSE-Apache-2.0` 与 `NOTICE`。
