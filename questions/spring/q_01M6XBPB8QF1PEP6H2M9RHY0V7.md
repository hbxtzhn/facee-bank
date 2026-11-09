---
id: q_01M6XBPB8QF1PEP6H2M9RHY0V7
title: DispatcherServlet 是做什么的？
type: concept
difficulty: easy
importance: 3
category: spring
tags: [mvc, design-pattern]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
DispatcherServlet 是 SpringMVC 的前端控制器，所有请求都先到它这里，再由它分发给对应的处理器并组织响应。

## 要点
- [kp1|3] 它是 SpringMVC 的统一入口，所有请求先经过它
- [kp2|3] 它自己不处理业务，只负责找人、调用、返回
- [kp3|2] 找处理器靠 HandlerMapping，调用处理器靠 HandlerAdapter
- [kp4] 它本质是一个 Servlet，对应前端控制器设计模式

## 详解
### 先搞懂：公司前台
访客来公司，不会自己乱闯，而是先到前台。前台问清楚找谁，通知对应的人，办完事再送访客出门。DispatcherServlet 就是 SpringMVC 的前台：浏览器发来请求，它负责判断“该交给哪个 Controller 方法”。

后文术语：
- **Servlet**：Java Web 中接收 HTTP 请求的标准组件。
- **Controller**：你写的处理请求的类，里面的方法处理具体业务。
- **前端控制器模式**：用一个统一入口接管所有请求，再统一分发。

### 它做哪些事
- **接收请求**：作为一个 Servlet 接收所有匹配的 HTTP 请求。
- **找处理器**：询问 `HandlerMapping`，这个请求该由哪个 Controller 方法处理。
- **调用处理器**：交给 `HandlerAdapter` 去执行。
- **处理结果**：根据返回值，渲染视图或把数据写进响应体。
- **统一异常处理**：处理器抛出异常时，交给异常解析器处理。

### 为什么要统一入口
没有统一入口，每个 Controller 都要自己处理编码、参数转换、异常等重复工作。统一入口之后，这些公共环节由框架完成，Controller 只写业务。

## 易错点
- 以为 DispatcherServlet 就是 Controller；它是调度者，Controller 才处理业务
- 以为它直接调用 Controller；中间还有 HandlerAdapter
- 以为它只用于返回页面；返回 JSON 的接口也要经过它

## 追问
### [f1] Spring Boot 里 DispatcherServlet 需要自己配置吗？
一般不用。Spring Boot 的自动配置会自动注册它，默认映射到根路径。
