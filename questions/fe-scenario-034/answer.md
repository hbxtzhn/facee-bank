### 一句话总结

**同一个父级域名下的不同子域名可以无缝共享（通过指定 `Domain=.example.com`）；而完全不同的顶级域名（如 a.com 与 b.com）由于浏览器沙箱安全隔离，在底层协议上绝对无法直接共享读取 Cookie**。跨完全不同域的会话共享必须借助 **SSO 单点登录（CAS / OAuth 重定向授权并携带 Token）** 或 **中间页借助 `postMessage` + `iframe` 跨源传输**。

---

### 详细回答

#### 1. 场景一：二级子域名共享（同主域）
- 场景：`oa.baidu.com` 和 `tieba.baidu.com`；
- **配置规则**：
  写入 Cookie 时显式设置 `Domain=.baidu.com; Path=/`；
  此时只要是以 `.baidu.com` 结尾的所有二级、三级子域名，在发请求时均会自动携带该 Cookie。

#### 2. 场景二：完全跨域（a.com 与 b.com）
- **协议死限制**：浏览器内核强制禁止 `a.com` 读取属于 `b.com` 的 Cookie（同源策略最核心防线，若能共享则黑客可秒级窃取全网登录态）；
- **成熟工程解法（SSO 单点登录）**：
  1. 访问 `b.com` 时发现未登录，自动 302 重定向到统一认证中心 `sso.com`；
  2. `sso.com` 验证自身 Cookie 发现已登录，签发一个带有一次性票据的授权码（Ticket）；
  3. 重定向回 `b.com?ticket=xyz`；
  4. `b.com` 后端用 ticket 兑换会话，并在 `b.com` 自身的域名下独立种下本站 Cookie。

---

### 核心代码片段（极简记法）

```javascript
// 子域名共享 Cookie 规范设置
document.cookie = "token=xyz123; Domain=.company.com; Path=/; Secure; SameSite=Lax";
```

---

### 面试加分项

- **跨域 iframe 写入 Cookie 的第三方限制（CHIPS / Partitioned Cookies）**：Chrome 正在全面废除传统的第三方跨站 Cookie（Third-Party Cookies）。如果必须在跨域 iframe 中嵌入携带自身 Cookie，必须声明新特性属性 `Partitioned`（独立分区 Cookie），否则会被新版 Chrome 直接丢弃。
