---
id: q_01M6ZYJFSEHF4YSEXPRNPCQ620
title: SpringMVC 的请求处理流程是怎样的？
type: concept
difficulty: medium
importance: 3
category: spring
tags: [mvc]
prerequisites: [q_01M6XBH51ARHWJV4MY6ECCXRB4, q_01M6XBPB8QF1PEP6H2M9RHY0V7]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "Spring Framework 参考文档：DispatcherServlet Processing", url: "https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-servlet/sequence.html" }
  - { title: "Spring Framework 参考文档：DispatcherServlet Special Bean Types", url: "https://docs.spring.io/spring-framework/reference/web/webmvc/mvc-servlet/special-bean-types.html" }
estimatedMinutes: 4
---

## 一句话
请求先到 DispatcherServlet，它让 HandlerMapping 找到处理器，再交给 HandlerAdapter 执行，最后把结果渲染成视图或直接写回响应。

## 要点
- [kp1|3] 请求先到 DispatcherServlet，它是整个流程的调度中心
- [kp2|3] HandlerMapping 根据 URL 找到处理该请求的 Controller 方法
- [kp3|2] HandlerAdapter 负责执行处理器，并处理参数和返回值
- [kp4|2] 返回页面走视图解析和渲染，返回 JSON 直接写入响应体
- [kp5] 拦截器在处理器执行前后介入

## 详解
### 先搞懂：点外卖的全过程
你下单（请求）。平台调度中心（DispatcherServlet）查哪家店能做（HandlerMapping）。接着安排骑手和商家对接（HandlerAdapter）。商家做出餐品（Controller）。最后调度中心把餐送回你手里（响应）。

后文术语：
- **处理器（Handler）**：真正处理请求的东西，通常是 Controller 里的某个方法。
- **视图（View）**：最终展示给用户的页面。
- **拦截器（Interceptor）**：在处理器执行前后做检查的组件，如登录校验。

### 按顺序走一遍
1. **发起请求**：浏览器发 HTTP 请求。
2. **到达前端控制器**：请求先进入 DispatcherServlet。
3. **找处理器**：DispatcherServlet 询问 `HandlerMapping`，得到处理器和需要经过的拦截器。
4. **找适配器**：根据处理器类型选择合适的 `HandlerAdapter`。
5. **执行拦截器前置方法**：任何一个拒绝就不再往下走。
6. **执行处理器**：HandlerAdapter 解析参数，调用 Controller 方法。
7. **处理返回值**：返回页面名则得到视图；返回 JSON 则消息转换器直接写入响应体。
8. **渲染视图**：视图解析器找到视图并渲染，数据填入模板。
9. **返回响应**：执行拦截器的完成方法，响应返回浏览器。

### 现在的常见变化
前后端分离的项目里，Controller 多用 `@RestController`，第 7 步直接写入响应体，第 8 步的视图渲染就不会发生。

## 示例
```java
@RestController
public class UserController {
    @GetMapping("/users/{id}")
    public User get(@PathVariable Long id) {
        return userService.find(id);
    }
}
```

## 易错点
- 以为请求先到 Controller；先到的是 DispatcherServlet
- 以为所有请求都会渲染视图；返回 JSON 时没有视图渲染
- 把拦截器和过滤器混为一谈；过滤器在 Servlet 层，拦截器在 SpringMVC 层

## 追问
### [f1] 拦截器和过滤器有什么区别？
过滤器属于 Servlet 规范，在请求进入 DispatcherServlet 之前执行；拦截器属于 SpringMVC，在 DispatcherServlet 内部、处理器前后执行，可以拿到处理器信息。
