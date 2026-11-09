---
id: q_01M6XBH51ARHWJV4MY6ECCXRB4
title: "@RestController 是做什么的，返回的数据是什么格式？"
type: concept
difficulty: easy
importance: 2
category: spring
tags: [mvc, http]
appliesTo: ["Spring Framework >= 4.0"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
@RestController 标在 Controller 类上，表示这个类里每个方法的返回值都直接写进响应体，常用来返回 JSON，它等价于 @Controller 加 @ResponseBody。

## 要点
- [kp1|3] @RestController 是 @Controller 和 @ResponseBody 的组合注解
- [kp2|3] 方法返回值直接写入 HTTP 响应体，不会再去找页面视图
- [kp3|2] 返回对象时通常被转成 JSON，由消息转换器完成
- [kp4] 想返回页面（如模板）时，用 @Controller，不要用 @RestController

## 详解
### 先搞懂：返回的是页面，还是数据
做项目时，接口有两类：

- 传统网站：浏览器请求，服务端返回一个页面；
- 前后端分离：前端请求，服务端只返回数据（通常是 JSON），页面由前端渲染。

`@Controller` 标注的类，默认方法返回的字符串会被当作**视图名**，Spring 会去找对应的页面。而 `@RestController` 说的是：这里每个方法返回的就是数据本身，别去找页面。

后文用到的词：
- **响应体**：HTTP 响应里真正承载内容的部分（和状态码、响应头区分）。
- **JSON**：一种文本数据格式，比如 `{"id":1,"name":"tom"}`。
- **消息转换器**：把 Java 对象转成 JSON 的组件。

### 它是怎么起作用的
`@RestController` 本身是一个组合注解，它由 `@Controller` 和 `@ResponseBody` 组成：

- `@Controller`：声明这是一个控制层组件，交给 Spring 管理；
- `@ResponseBody`：返回值不走视图解析，直接写入响应体。

所以写在类上，等于该类所有方法都带了 `@ResponseBody`。

### 返回的数据是什么格式
方法返回的内容由 Spring 的消息转换器按情况处理：

- 返回对象或集合：通常转换成 JSON（项目里引入了 Jackson 之类的库时）；
- 返回字符串：直接作为文本写出；
- 返回的具体格式也可以根据请求头和配置协商，比如 XML，不过现在大多是 JSON。

## 示例
```java
@RestController
@RequestMapping("/users")
public class UserController {

    @GetMapping("/{id}")
    public User get(@PathVariable Long id) {
        return new User(id, "tom"); // 直接转成 JSON 写入响应体
    }
}
```

## 易错点
- 以为 @RestController 会返回页面；它返回的是数据，要返回页面应该用 @Controller
- 在 @RestController 里返回字符串想跳转页面，结果页面名被原样输出给了浏览器
- 以为它一定返回 JSON；格式取决于消息转换器和请求协商，只是 JSON 最常见

## 追问
### [f1] @Controller 和 @RestController 有什么区别？
@Controller 的方法返回值默认当视图名解析，想返回数据要在方法上另加 @ResponseBody；@RestController 相当于类上直接带了 @ResponseBody，所有方法都返回数据。

### [f2] 返回的对象是怎么变成 JSON 的？
Spring MVC 里有一组 HttpMessageConverter，遇到 @ResponseBody 时，选择能处理该返回类型的转换器，比如基于 Jackson 的，把对象序列化成 JSON 再写入响应。
