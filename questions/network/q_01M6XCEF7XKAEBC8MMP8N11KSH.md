---
id: q_01M6XCEF7XKAEBC8MMP8N11KSH
title: HTTP 请求报文和响应报文分别由哪些部分组成？
type: concept
difficulty: easy
importance: 2
category: network
tags: [http]
prerequisites: [q_01M6XCEECTHDY46D0V5JBTG5ZS]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
请求报文由请求行、请求头、空行和正文组成，响应报文由状态行、响应头、空行和正文组成。

## 要点
- [kp1|3] 请求报文：请求行、请求头、空行、请求正文
- [kp2|3] 响应报文：状态行、响应头、空行、响应正文
- [kp3|2] 请求行有方法、路径和协议版本，状态行有版本和状态码
- [kp4] 空行用来分隔头部和正文，正文可以没有

## 详解
### 先搞懂：一封信的结构
寄一封信，信封上写收件人和寄件人，信封里有信纸。HTTP 报文也像信：最前面是“这封信是干嘛的”，然后是一堆附加信息，再空一行，最后才是正文。

几个词：

- **报文**：HTTP 通信中一次发送的完整文本消息。
- **头部**：附加信息，以“名字: 值”的形式一行一条。
- **正文**：真正要传的数据，可能没有。

### 请求报文
由四部分按顺序组成：

1. **请求行**：一行，写方法、路径和协议版本，例如 `GET /index.html HTTP/1.1`；
2. **请求头**：多行，每行一条，如 Host、User-Agent、Content-Type；
3. **空行**：只有换行，用来表示头部结束；
4. **请求正文**：可选，如 POST 提交的表单数据。

### 响应报文
同样四部分：

1. **状态行**：写协议版本、状态码和说明，例如 `HTTP/1.1 200 OK`；
2. **响应头**：多行，如 Content-Type、Content-Length；
3. **空行**：头部结束的标记；
4. **响应正文**：可选，返回的网页、图片、JSON 数据等。

### 为什么要空行
接收方是一行一行读的。读到空行，就知道头部结束，后面是正文。没有空行，就分不清哪里是头、哪里是内容。

## 示例
```bash
# 请求报文示例
GET /index.html HTTP/1.1
Host: example.com
Accept: text/html

# 响应报文示例
HTTP/1.1 200 OK
Content-Type: text/html
Content-Length: 13

Hello, World!
```

## 易错点
- 以为每个报文都有正文；GET 请求通常没有，204 响应也没有
- 以为空行可有可无；它是头部和正文之间的分隔标志
- 把请求行和状态行混为一谈；前者描述请求，后者描述结果

## 追问
### [f1] Content-Length 有什么用？
它告诉接收方正文有多少字节，接收方才知道读到哪里算结束。
