---
id: q_01M6ZYK4NC2JVK0WXNS0YK3B0T
title: Session 是什么？
type: concept
difficulty: easy
importance: 2
category: network
tags: [http]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
Session 是服务器保存的一次会话状态，浏览器只拿一个 Session ID，服务器凭这个编号找回用户的状态。

## 要点
- [kp1|3] Session 数据保存在服务器端，不在浏览器里
- [kp2|3] 服务器为每个会话生成一个 Session ID，作为查找凭证
- [kp3|2] Session ID 常放在 Cookie 里，由浏览器自动带上
- [kp4] Session 常用来保存登录状态等信息，通常会设有效期

## 详解
### 先搞懂：存包柜的取件码
你去商场存包，工作人员把你的东西放进柜子，只给你一张小票，上面是编号。你下次来，出示小票，就能取回自己的东西。东西放在商场里，你手里只有编号。

Session 就是这样。几个词：

- **会话**：一个用户从开始访问到结束的一段交互。
- **Session ID**：服务器给这次会话分配的唯一编号。
- **Cookie**：浏览器保存的小数据，常用来存放 Session ID。

### Session 是怎么工作的
以登录为例：

1. 用户登录成功，服务器创建一个 Session，里面记录用户 ID 等信息；
2. 服务器生成一个 Session ID，把它通过 Cookie 发给浏览器；
3. 浏览器保存这个 Cookie，之后的每个请求都自动带上它；
4. 服务器收到请求，用 Session ID 找到对应的 Session，就知道这是谁、是否已登录。

### 为什么要用 Session
HTTP 是无状态的，服务器不会自己记住谁登录了。Session 让服务器记住。

和直接把信息放在 Cookie 里相比，Session 的数据放在服务器上。用户看不到，也改不了，只有一个编号在外面。所以比较重要的信息适合放在 Session 里。

### 要注意什么
- **有效期**：Session 一般会设置超时。用户一段时间不活动，就会失效。
- **集群部署**：如果 Session 存在某台服务器的内存里，请求换了一台机器就找不到了。解决办法是把 Session 存到共享的地方，或者让同一用户固定走同一台机器。
- **Session ID 的安全**：编号被别人拿到，就可能冒充你。所以要用 HTTPS 保护，并生成难以猜测的编号。

## 易错点
- 以为 Session 数据存在浏览器里；浏览器里只有 Session ID
- 以为 Session 一定依赖 Cookie；Cookie 只是常见的传递方式
- 以为 Session 会永久有效；它通常有过期时间

## 追问
### [f1] 浏览器禁用了 Cookie，Session 还能用吗？
可以换别的方式传递 Session ID，比如放在 URL 参数或请求头里。但放 URL 里更容易泄漏，要谨慎。
