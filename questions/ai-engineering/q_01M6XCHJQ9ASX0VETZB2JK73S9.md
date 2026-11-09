---
id: q_01M6XCHJQ9ASX0VETZB2JK73S9
title: Prompt、Skill、Function Calling 和 MCP 四者怎样分工？
type: concept
difficulty: medium
importance: 2
category: ai-engineering
tags: [tool-calling, prompt-engineering]
prerequisites: [q_01M6XCG5D32GZ09MCE0M5MW0ZX, q_01M6XCGERJKJACA2R23WQ9FRHH]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
Prompt 给出任务，Skill 提供做事的方法和经验，Function Calling 让模型表达要调用哪个工具，MCP 负责工具的发现与连接。

## 要点
- [kp1|3] Prompt 说明这次要做什么任务
- [kp2|3] Skill 沉淀某类任务的方法、约束和步骤
- [kp3|2] Function Calling 让模型按固定格式说出要调的工具和参数
- [kp4|2] MCP 是标准协议，让应用发现并连接各种工具服务
- [kp5] 模型本身不执行工具，由宿主程序执行

## 详解
### 先搞懂：像让助理订机票
你对助理说：帮我订周五去上海的机票。这是**任务**。助理有一份公司差旅规范，写明舱位等级和预算上限，这是**方法**。助理决定要用订票网站，把要填的信息列出来，这是**表达调用意图**。最后订票网站要有统一的接入方式，助理才能连上，这是**连接工具**。

四个概念对应的就是这四件事。下面是后文要用的术语：

- **Prompt**：给模型的指令。
- **Skill**：可按需加载的任务说明。
- **Function Calling**：模型输出结构化的工具调用请求。
- **MCP**：工具服务和应用之间的标准通信协议。

### Prompt：给任务
用户的需求和当次的要求，都在 Prompt 里，如查什么、输出什么格式。它随每次对话变化。

### Skill：给方法
同一类任务有稳定的做法。把做法写成 Skill，Agent 遇到相关任务时按需加载，就能按既定步骤和约束来做。

### Function Calling：表达调用意图
模型本身不能直接执行代码或访问网络。使用 Function Calling 时，应用会提前告诉模型有哪些工具及参数格式。模型判断需要时，输出一个结构化的调用请求，由应用程序真正去执行，再把结果交回给模型。

### MCP：发现与连接
没有统一标准时，每接入一个工具，都要写一套专门的对接代码。MCP 规定了应用（Client）和工具服务（Server）之间的通信方式，应用可以用同样的方法发现并连接不同的工具服务。

### 四者对比
| 概念 | 解决什么 | 由谁提供 | 举例 |
|---|---|---|---|
| Prompt | 这次做什么 | 用户或应用 | 帮我总结这份文档 |
| Skill | 怎么做更好 | 经验沉淀 | 总结的格式和步骤 |
| Function Calling | 要调用哪个工具 | 模型输出 | 调用搜索，参数是关键词 |
| MCP | 工具怎么接入 | 协议和服务 | 连接文件系统服务 |

结论：四者不是替代关系。一个 Agent 完成任务时，通常会同时用到这四个层面。

## 易错点
- 以为 Function Calling 和 MCP 是同一种东西；前者是模型表达调用，后者是工具接入协议
- 以为模型自己执行了工具；真正执行的是宿主程序
- 把 Skill 当成工具接口；它是说明文档，不是可调用的接口

## 追问
### [f1] 用了 MCP 还需要 Function Calling 吗？
通常需要。MCP 解决工具怎么发现和连接，Function Calling 解决模型怎么表达要调用工具。应用会把 MCP 工具的描述转成模型能理解的调用格式。
