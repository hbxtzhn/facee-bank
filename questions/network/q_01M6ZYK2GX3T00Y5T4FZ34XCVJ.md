---
id: q_01M6ZYK2GX3T00Y5T4FZ34XCVJ
title: 在浏览器输入 URL 到页面显示，中间经过哪些网络步骤？
type: concept
difficulty: medium
importance: 3
category: network
tags: [dns, http]
prerequisites: [q_01M6XCE2N5WJFWZTM6V5M9GP58, q_01M6XCE2X8GXVZV4VPVZDRQ68F, q_01M6XCE356XGWR545GSS6TR4PR, q_01M6XCE3D3AW5KFBE3G4CN6CF6, q_01M6ZYK20QXGH68QFVYJBT6JN4, q_01M6XCE4ATMV272YB329BZ5PY9]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
浏览器先用 DNS 把域名解析成 IP，再建立 TCP 连接和 TLS 加密，然后发 HTTP 请求、收响应，最后渲染页面。

## 要点
- [kp1|3] 先 DNS 解析出 IP，才知道要连哪台服务器
- [kp2|3] 接着 TCP 三次握手建立连接，HTTPS 还要再做 TLS 握手
- [kp3|2] 连接建立后，浏览器发 HTTP 请求，服务器返回响应
- [kp4|2] 浏览器解析 HTML，加载其中的资源，再渲染出页面

## 详解
### 先搞懂：打电话订外卖
你要订一家店的外卖，过程是：先查到店的电话号码（DNS），拨号接通（TCP 连接）。如果要讲私密信息，还要先约定暗号（TLS）。然后说出你要什么（HTTP 请求），店家回答（响应），最后外卖送到你手上（渲染）。

后文的术语：

- **DNS**：把域名翻译成 IP 地址的系统。
- **TCP 连接**：双方通过三次握手建立的可靠通信通道。
- **TLS**：给通信加密、并验证服务器身份的协议，HTTPS 就是 HTTP 加 TLS。
- **渲染**：浏览器把 HTML、CSS 等变成屏幕上看到的页面。

### 第一步：DNS 解析，找到服务器地址
浏览器要连服务器，得先知道 IP。它先查自己的缓存，再查操作系统和本地 DNS 服务器。必要时，本地 DNS 会逐级向外查询。最终得到域名对应的 IP 地址。

### 第二步：TCP 三次握手，建立连接
拿到 IP 后，浏览器和服务器通过三次握手建立 TCP 连接。握手确认双方都能收发。HTTPS 默认连接服务器的 443 端口，HTTP 默认是 80 端口。

### 第三步：TLS 握手（HTTPS）
如果是 HTTPS，TCP 连接建立后还要做 TLS 握手。浏览器验证服务器的证书，双方协商出加密用的密钥。此后传输的内容都是加密的，中途的人看不懂。

### 第四步：发送 HTTP 请求，接收响应
浏览器构造 HTTP 请求，包括请求行（如 `GET / HTTP/1.1`）、请求头，必要时带请求体。服务器处理后返回响应。响应包括状态码、响应头和内容，比如 HTML。

### 第五步：浏览器解析与渲染
浏览器拿到 HTML，开始解析。遇到里面引用的 CSS、JavaScript、图片，会再发请求去加载。然后构建页面结构、计算样式和布局，最后画到屏幕上。

### 实际中的优化
- 浏览器、本地 DNS 都有缓存，已查过的域名可以跳过 DNS 查询。
- HTTP 可以复用已建立的连接，不必每次都重新握手。
- 服务器前面常有 CDN，让用户连到更近的节点。

## 示例
```bash
# 用 curl 观察各个阶段的耗时：域名解析、TCP 连接、TLS 握手、首字节
curl -o /dev/null -s -w "dns=%{time_namelookup} tcp=%{time_connect} tls=%{time_appconnect} ttfb=%{time_starttransfer}\n" https://www.example.com
```

## 易错点
- 以为每次访问都要完整查一遍 DNS；浏览器和系统都有缓存，常常直接命中
- 以为 HTTP 和 HTTPS 的连接过程完全一样；HTTPS 在 TCP 之后多了 TLS 握手
- 以为页面在收到第一个响应后就显示完了；HTML 里引用的资源还会触发更多请求

## 追问
### [f1] 如果访问的是 IP 而不是域名，会怎样？
会跳过 DNS 解析，直接用这个 IP 建立 TCP 连接，其余步骤相同。
