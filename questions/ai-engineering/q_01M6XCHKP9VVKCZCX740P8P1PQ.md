---
id: q_01M6XCHKP9VVKCZCX740P8P1PQ
title: 什么是 MCP Server？
type: concept
difficulty: easy
importance: 2
category: ai-engineering
tags: [tool-calling]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
MCP Server 是 MCP 里提供具体能力的一端，它把文件系统、数据库或 API 等外部能力，通过标准接口暴露给 AI 应用。

## 要点
- [kp1|3] MCP Server 是能力的具体提供者
- [kp2|3] 它把文件、数据库、API 等外部能力封装成标准接口
- [kp3|2] 它向 Client 说明自己有哪些工具，并执行 Client 发来的调用
- [kp4] 一个应用可以同时连接多个 Server

## 详解
### 先搞懂：像一个服务窗口
一个政务大厅里有很多窗口，每个窗口办一类事：办身份证、办社保。市民用同样的取号流程找到窗口，窗口负责真正办事。

MCP Server 就是这样的窗口。下面是后文要用的术语：

- **MCP Server**：提供能力的服务程序。
- **MCP Client**：连接 Server、使用其能力的一方，在 AI 应用中。
- **工具（Tool）**：Server 暴露出来、可以被调用的一个具体功能。

### Server 做了什么
- **封装能力**：把已有的外部能力包起来，如读文件、查数据库、调用某个网络接口。
- **说明自己**：告诉 Client 自己提供哪些工具，每个工具的名称、用途和参数。
- **执行调用**：收到 Client 的调用请求后，真正去执行，并把结果返回。

### 一个例子
有一个数据库的 MCP Server，暴露了一个查询工具。AI 应用连上它后，发现了这个工具。用户问订单情况，模型决定调用，应用把请求发给 Server，Server 查数据库并返回结果。

### 使用时的注意点
Server 往往直接接触真实数据，所以权限要最小化。比如数据库 Server 只给只读权限，除非确实需要写入。

## 易错点
- 以为 Server 一定是远程的大服务；它也可以是本机上运行的一个小程序
- 以为 Server 里包含模型；它只提供能力，不做推理
- 给 Server 过大的权限；应只开放任务必需的能力

## 追问
### [f1] 要接入自己公司的内部系统，怎么用 MCP？
写一个 MCP Server，把内部系统的接口封装成工具。写好后，所有支持 MCP 的应用都能连接它，不需要为每个应用单独对接。
