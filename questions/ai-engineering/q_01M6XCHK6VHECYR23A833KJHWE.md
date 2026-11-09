---
id: q_01M6XCHK6VHECYR23A833KJHWE
title: 什么是 MCP（Model Context Protocol）？
type: concept
difficulty: easy
importance: 3
category: ai-engineering
tags: [tool-calling]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
MCP 是让 AI 应用（MCP Client）发现并连接工具服务（MCP Server）的标准通信协议，让各种工具可以用同一种方式接入。

## 要点
- [kp1|3] MCP 全称 Model Context Protocol，是一套标准协议
- [kp2|3] 通信双方是 MCP Client（宿主应用）和 MCP Server（工具服务）
- [kp3|2] 宿主可以通过它发现服务提供了哪些工具
- [kp4] 标准化后，工具只需实现一次，就能被多个应用使用

## 详解
### 先搞懂：像手机的统一充电口
以前每个品牌的手机充电口都不一样，换手机就得换充电器。统一成同一种接口后，一根线就能充各种设备。

MCP 对工具接入做的就是这件事。下面是后文要用的术语：

- **MCP Client**：使用工具的一方，通常是 AI 应用。
- **MCP Server**：提供工具的一方，把具体能力暴露出来。
- **协议**：双方约定好的沟通格式和流程。

### 没有 MCP 时的麻烦
一个 AI 应用想接入文件系统、数据库、搜索等工具，每个都要写专门的对接代码。换一个应用，又要重写一遍。

### MCP 怎么解决
MCP 规定了统一的沟通方式：

- Client 向 Server 询问：你都有哪些工具？
- Server 返回工具的名称、说明和参数格式。
- Client 需要时发出调用请求，Server 执行并返回结果。

这样 Server 只要按标准实现一次，所有支持 MCP 的应用都能直接使用。

### 它和模型的关系
MCP 不是模型的一部分。它是应用和工具之间的协议。应用拿到工具信息后，再交给模型，由模型决定要不要调用。

## 易错点
- 以为 MCP 是一种模型；它是应用与工具之间的通信协议
- 以为 MCP 自己决定调用什么工具；决定调用的是模型，MCP 负责连接
- 以为接入 MCP 工具就不用考虑权限和安全；仍然要控制工具能访问什么

## 追问
### [f1] MCP 和 Function Calling 有什么区别？
Function Calling 是模型输出调用请求的方式。MCP 是应用发现、连接工具服务的协议。前者在模型和应用之间，后者在应用和工具之间。
