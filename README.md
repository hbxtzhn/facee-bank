# FaceE 题库

一份**开源的程序员面试题库**，505 题，覆盖 Java 后端、Python 与 FastAPI 等方向，配合 [FaceE](https://github.com/HBxtzhn/facee) 离线刷题。

当前题库版本 **1.3.0**。已有题库可在管理页点击「在线更新」；更新按题库版本判断。

## 怎么用

在 FaceE 的「我的」页添加线上题库，填写以下发布包地址：

```
https://github.com/HBxtzhn/facee-bank/releases/latest/download/question-bank.zip
```

也可以在 [Releases](https://github.com/HBxtzhn/facee-bank/releases/latest) 下载 `question-bank.zip` 后导入。需要跟随 main 源码时，可以使用 `https://github.com/HBxtzhn/facee-bank/archive/refs/heads/main.zip`。

## 包含什么

| 分类 | 题数 |
|---|---:|
| Java 基础 | 29 |
| Java 集合 | 30 |
| Java 并发 | 31 |
| JVM | 69 |
| Spring | 30 |
| Spring Cloud | 53 |
| MySQL | 32 |
| Redis | 77 |
| 计算机网络 | 28 |
| 操作系统 | 28 |
| 分布式系统 | 32 |
| 系统设计 | 26 |
| AI 应用与 RAG | 10 |
| Python 核心 | 15 |
| FastAPI | 15 |

合计 **505 题**（简单 186 / 中等 247 / 困难 72）。

Python / FastAPI 的 30 道题已逐篇核对答案与追问，明确 Python 实现和框架版本边界；人工审核范围与修正依据见 [审核记录](docs/python-fastapi-review-v1.3.0.md)。示例运行、ZIP 校验和发布资产的实际验证结果以 Release 附件为准。

## 自己维护一份题库

本仓库是**纯数据**，没有构建步骤：`catalog.json` + `questions/<id>/`，改完提交即可。
格式见 [题库规范 v1](https://github.com/HBxtzhn/facee/blob/main/docs/题库规范-v1.md)。
不想手写可以用 FaceE 仓库里的 `packages/bank-spec`，能在本地生成并校验一份合格的题库包。

## 来源与许可

- 题目与答案**改编自** [JavaGuide](https://github.com/Snailclimb/JavaGuide)（Apache-2.0）：已附带其许可证文本（`LICENSE-Apache-2.0`）并声明改动（`NOTICE`）
- v1.2.0 新增题目（JVM / Redis / Spring Cloud / AI 应用与 RAG 等）：改编自**作者自整理面试笔记**，已做脱敏与去个性化处理
- v1.3.0 Python / FastAPI 题目：新增原创编写与审核，参考官方文档核对事实和 API，详见 [`sources.md`](sources.md)
- 结构、元数据及上述新增原创部分：**CC-BY-4.0**
- 评估过但未采用的来源及原因：见 [`sources.md`](sources.md)
