---
id: q_01M6XCC5X3JCG5VMYD8EYMYD8A
title: Controller 方法怎么接收请求参数（@RequestParam、@PathVariable、@RequestBody）？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [mvc, http]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
`@RequestParam` 取问号后面的参数，`@PathVariable` 取路径里的变量，`@RequestBody` 把 JSON 请求体转成 Java 对象。

## 要点
- [kp1|3] `@RequestParam` 取查询字符串或表单参数，如 `/users?name=tom`
- [kp2|3] `@PathVariable` 取路径占位符，如 `/users/{id}` 里的 id
- [kp3|2] `@RequestBody` 读取请求体，用消息转换器把 JSON 转成对象
- [kp4] `@RequestParam` 默认必填，缺了会返回 400，可设默认值或设为非必填

## 详解
### 先搞懂：前端的数据可以放在三个地方
前端调用后端接口，数据可以放在三个位置：地址问号后面、地址路径里、请求体里。可以把它想成寄快递：

- 写在快递单上的备注（问号后面的 `name=tom`）；
- 收件地址本身（路径里的 `/users/5`，5 是地址的一部分）；
- 包裹里装的东西（请求体里的 JSON）。

Controller 方法用不同的注解，告诉 Spring 到哪里去取值。

### @RequestParam：取问号后面的参数
请求 `GET /users?name=tom&age=20` 时，参数名对应方法形参名：

- 表单提交的字段也用它来取；
- 默认必填，缺少就返回 400；
- 想让它可选，可以写 `required = false`，或用 `defaultValue` 给默认值。

### @PathVariable：取路径里的变量
路径里用大括号占位，如 `/users/{id}`。请求 `/users/5` 时，`@PathVariable Long id` 拿到的就是 5。这种写法常见于 REST 风格接口，用路径表示要操作哪一个资源。

### @RequestBody：把 JSON 转成对象
前端用 POST 或 PUT 发 JSON 时，数据在请求体里。加上 `@RequestBody`，Spring 会用 JSON 转换器（Spring Boot 默认是 Jackson）把它转成方法参数对象。

- 一个方法最多只能有一个 `@RequestBody`，因为请求体只能读一次；
- 请求头要带 `Content-Type: application/json`，否则转换可能失败；
- JSON 字段名要和对象属性名对得上。

## 示例
```java
@RestController
@RequestMapping("/users")
public class UserController {

    // GET /users?name=tom
    @GetMapping
    public String search(@RequestParam String name) {
        return "search " + name;
    }

    // GET /users/5
    @GetMapping("/{id}")
    public String detail(@PathVariable Long id) {
        return "user " + id;
    }

    // POST /users，请求体是 JSON
    @PostMapping
    public UserDTO create(@RequestBody UserDTO dto) {
        return dto;
    }
}
```

## 易错点
- 以为 `@RequestParam` 可以取 JSON 请求体里的字段；它只取查询字符串和表单，JSON 要用 `@RequestBody`
- 路径变量名和形参名不一致又没写 `@PathVariable("id")`，可能取不到值
- 在同一个方法上写两个 `@RequestBody`，请求体只能读一次，不能这样用

## 追问
### [f1] 不加注解，直接写一个对象参数会怎样？
Spring 会按表单或查询参数的名字，逐个填进对象的同名属性，不会去读 JSON 请求体。

### [f2] 参数校验怎么做？
在参数前加 `@Valid` 或 `@Validated`，配合对象属性上的 `@NotNull`、`@Size` 等注解。校验不通过会抛异常，通常统一处理成 400。
