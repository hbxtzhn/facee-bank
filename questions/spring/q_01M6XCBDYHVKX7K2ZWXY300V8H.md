---
id: q_01M6XCBDYHVKX7K2ZWXY300V8H
title: HandlerMapping 和 HandlerAdapter 分别做什么？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [mvc, design-pattern]
prerequisites: [q_01M6XBH59XNJ9FCTA43MEZGTFR, q_01M6ZYJFSEHF4YSEXPRNPCQ620]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "Spring Framework 参考文档：DispatcherServlet Special Bean Types（HandlerMapping、HandlerAdapter）", url: "https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-servlet/special-bean-types.html" }
estimatedMinutes: 3
---

## 一句话
HandlerMapping 负责根据请求 URL 找到该由哪个处理器处理；HandlerAdapter 负责用统一的方式去调用这个处理器。

## 要点
- [kp1|3] HandlerMapping 解决“谁来处理”：把请求映射到处理器
- [kp2|3] HandlerAdapter 解决“怎么调用”：统一执行不同类型的处理器
- [kp3|2] 映射结果还会带上要执行的拦截器链
- [kp4|2] 适配器让 DispatcherServlet 不必关心处理器的具体类型
- [kp5] 这里用到了适配器模式

## 详解
### 先搞懂：问路和翻译
你到一个陌生城市，先问路（找到目的地在哪），再坐对应的交通工具（地铁、公交用法各不同）。HandlerMapping 就是问路的人，告诉你该找哪个处理器；HandlerAdapter 则是“会用各种交通工具的人”，知道每种处理器该怎么调用。

后文术语：
- **处理器**：处理请求的对象，常见是带 `@RequestMapping` 的方法。
- **适配器模式**：把不同接口转换成统一接口，让调用方用一种方式调用。

### HandlerMapping：按请求找处理器
它保存了请求路径、请求方式等条件与处理器之间的对应关系。DispatcherServlet 把请求交给它，得到一个执行链，包含处理器和相关拦截器。最常用的是处理 `@RequestMapping` 系列注解的实现，启动时会扫描 Controller，把映射关系登记好。

### HandlerAdapter：统一调用
处理器有不同的形式：注解标注的方法、实现了特定接口的类等，调用方式并不一样。如果 DispatcherServlet 自己判断，每增加一种类型就要改它的代码。于是 Spring 为每种处理器配一个适配器，DispatcherServlet 只调用适配器统一的方法。注解方法的适配器还负责解析请求参数、调用方法、处理返回值。

### 方案对比：两者的分工
| 组件 | 要回答的问题 | 输入 | 输出 |
|---|---|---|---|
| HandlerMapping | 谁来处理这个请求 | 请求 | 处理器和拦截器链 |
| HandlerAdapter | 怎么执行这个处理器 | 处理器 | 执行结果（视图或数据） |

结论：映射负责“找”，适配负责“调”，分开后新增处理器类型只需增加一对实现，DispatcherServlet 不用改。

## 易错点
- 把两者混为一谈；一个管查找，一个管调用
- 以为参数解析由 Controller 自己完成；参数解析由适配器负责
- 以为 HandlerAdapter 是写业务代码的地方；业务写在 Controller

## 追问
### [f1] 为什么需要 HandlerAdapter，而不是 DispatcherServlet 直接调用？
处理器类型多样，直接调用要写大量类型判断，新增类型还要改核心代码。加一层适配器，核心流程保持不变。
