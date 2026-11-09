---
id: q_01M6XBH59XNJ9FCTA43MEZGTFR
title: 怎么把 HTTP 请求映射到 Java 方法上？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [mvc, http]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
用 @RequestMapping 指定请求路径，把 URL 映射到某个方法上；@GetMapping、@PostMapping 是它的简化写法，分别只处理 GET 和 POST 请求。

## 要点
- [kp1|3] @RequestMapping 把 URL 路径映射到 Controller 的方法，类和方法上都可以用
- [kp2|3] @GetMapping、@PostMapping 等是 @RequestMapping 限定请求方法的简化写法
- [kp3|2] 类上的路径和方法上的路径会拼接起来，组成完整的访问路径
- [kp4] 还有 @PutMapping、@DeleteMapping 等对应其他 HTTP 方法的注解

## 详解
### 先搞懂：前台接待把请求分给对应的人
浏览器访问 `/users/1`，服务器里有很多方法，应该由哪一个来处理？就像公司前台，根据来访目的把人带到对应部门。

Spring MVC 里这件事就靠「映射」：在方法上用注解声明「我负责处理哪个路径、哪种请求」，请求来了，框架就据此找到方法并调用。

后文用到的词：
- **URL 路径**：地址里域名后面的部分，如 `/users/1`。
- **HTTP 方法**：GET（查询）、POST（提交）等，表示请求想做什么。
- **映射**：声明请求和方法之间的对应关系。

### @RequestMapping：最通用的映射注解
`@RequestMapping` 可以用在类上，也可以用在方法上：

- 用在类上：指定这个类下所有方法共同的路径前缀；
- 用在方法上：指定该方法自己的路径；
- 两者拼起来才是完整路径，比如类上是 `/users`，方法上是 `/list`，访问路径就是 `/users/list`。

它还可以通过 `method` 属性限定 HTTP 方法；不写 `method` 时，什么方法的请求都能进来。

### 简化写法：@GetMapping、@PostMapping
每次都写 `@RequestMapping(value = "/x", method = RequestMethod.GET)` 太啰嗦，Spring 提供了几个简化注解：

- `@GetMapping`：只处理 GET 请求，一般用于查询；
- `@PostMapping`：只处理 POST 请求，一般用于新增、提交；
- 另外还有 `@PutMapping`、`@DeleteMapping`、`@PatchMapping`。

它们本质上就是带了固定 `method` 的 `@RequestMapping`，用法一样，意图更清晰，推荐优先使用。如果请求方法不匹配，会返回 405（方法不允许）。

## 示例
```java
@RestController
@RequestMapping("/users")                 // 类上：公共前缀
public class UserController {

    @GetMapping("/{id}")                  // GET /users/1
    public User get(@PathVariable Long id) { ... }

    @PostMapping                          // POST /users
    public User create(@RequestBody User user) { ... }
}
```

## 易错点
- 以为只写 @RequestMapping 就只处理 GET；不指定 method 时，所有方法的请求都会匹配
- 类上和方法上都写了完整路径，导致路径重复拼接
- 用浏览器直接访问 @PostMapping 的路径，得到 405，因为浏览器地址栏发的是 GET

## 追问
### [f1] 路径里的变量怎么拿到？
路径里用大括号占位，如 `/users/{id}`，方法参数上加 `@PathVariable` 就能拿到对应的值。查询字符串里的参数用 `@RequestParam`。

### [f2] 两个方法映射了同一个路径和方法，会怎么样？
Spring 启动时会发现映射冲突，抛出异常，应用无法正常启动，所以同一个路径加方法只能对应一个处理方法。
