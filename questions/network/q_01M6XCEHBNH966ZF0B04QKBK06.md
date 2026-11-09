---
id: q_01M6XCEHBNH966ZF0B04QKBK06
title: Cookie 和 Session 有什么区别？
type: concept
difficulty: medium
importance: 3
category: network
tags: [http]
prerequisites: [q_01M6XCEGKFNFAJ9D20XZFQQVEX, q_01M6ZYK4NC2JVK0WXNS0YK3B0T, q_01M6XCEH2SNS5NGVT4T73KV5FJ]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
Cookie 存在浏览器里，容量小、只能存文本；Session 存在服务器上，能存任意数据，靠 Cookie 里的 Session ID 找回。

## 要点
- [kp1|3] Cookie 存在客户端，Session 存在服务端
- [kp2|3] Session 靠 Session ID 找回，ID 通常放在 Cookie 里
- [kp3|2] Cookie 容量小、只能存文本，Session 可存任意对象
- [kp4|2] Cookie 有效期可以很长，Session 通常较短
- [kp5] Cookie 用户可见可改，敏感数据放 Session 更稳妥

## 详解
### 先搞懂：服务器怎么记住你登录过
HTTP 本身是**无状态**的：服务器处理完一个请求，就忘了你是谁。可是网站要让你登录一次后，后面的请求都认得你。

可以把它想成去健身房：

- Cookie 像一张会员卡，你自己揣在身上，每次进门出示；
- Session 像前台的会员档案，存在健身房里；卡上只印一个编号，前台凭编号翻档案。

后文要用的术语：

- **Cookie**：服务器让浏览器保存的一小段文本，浏览器之后每次请求都会自动带上。
- **Session**：服务器为每个用户保存的一份数据，放在服务端。
- **Session ID**：给这份数据起的唯一编号，用来找回它。

### Cookie：数据放在客户端
服务器通过响应头 `Set-Cookie` 让浏览器保存数据，之后同一网站的请求都会自动带上它。

- 它存在用户的浏览器里，用户能看到，也能改；
- 容量很小，内容是文本；
- 有效期可以设得很长，比如「记住我」，关掉浏览器也还在。

### Session：数据放在服务端
用户登录成功后，服务器创建一份 Session，把用户 ID 等信息放进去，再生成一个 Session ID。

- Session ID 通过 Cookie 发给浏览器；
- 浏览器之后带着它来，服务器就能找出这份数据；
- 数据在服务端，可以存任意对象，用户改不了；
- 有效期通常较短，一段时间没有访问，服务器就会清掉它。

所以两者不是互相替代，而是配合：Session 的「会员卡」常常就是一个 Cookie。

### 方案对比：Cookie 和 Session
| 维度 | Cookie | Session |
|---|---|---|
| 存在哪 | 客户端浏览器 | 服务端 |
| 能存什么 | 小段文本 | 任意对象 |
| 安全性 | 用户可见可改 | 数据不暴露给用户 |
| 有效期 | 可设置得很长 | 通常较短，空闲会过期 |
| 服务端开销 | 没有 | 要占服务器内存或存储 |

结论：登录状态、用户信息放 Session，Cookie 只负责带着 Session ID；偏好设置这类不敏感的小数据，直接放 Cookie 就行。

### 进阶：多台服务器怎么共享 Session（基础薄弱可先跳过）
服务器有多台时，请求可能落到另一台机器，那台机器上没有这个 Session。常见做法是把 Session 放到 Redis 这类共享存储里，所有机器都从那里读。

另一种做法是不在服务端存 Session，而是把登录信息签名后交给客户端保存，比如 Token。代价是服务器不方便主动让它失效。

## 示例
```http
HTTP/1.1 200 OK
Set-Cookie: JSESSIONID=abc123; HttpOnly; Path=/
```

## 易错点
- 以为 Session 和 Cookie 无关；Session 通常靠 Cookie 传递 Session ID
- 以为关掉浏览器 Session 就立刻消失；服务端的 Session 要等超时或主动销毁
- 把密码等敏感信息直接存进 Cookie；用户能看到也能改

## 追问
### [f1] 用户禁用了 Cookie，Session 还能用吗？
默认的做法会失效，因为 Session ID 带不过去。可以把 Session ID 拼在 URL 里传递，但容易泄露，一般不推荐。

### [f2] 为什么说 Session ID 要保护好？
谁拿到 Session ID，服务器就会当他是这个用户。所以要用 HTTPS 传输，Cookie 加 `HttpOnly`，登录后重新生成 ID。
