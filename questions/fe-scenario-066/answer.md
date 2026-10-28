### 一句话总结

最本质区别在于**“攻击媒介与信任借用方向不同”**：**XSS 是黑客利用漏洞在你的网站里注入并运行了恶意 JS 代码，借此盗取用户的 Cookie 凭据或篡改页面（信任泄露）**；而 **CSRF 是黑客根本拿不到你的任何代码和 Cookie，而是通过引诱用户在第三方钓鱼网站点击链接，诱骗浏览器自动带上本站受信任的 Cookie 发起越权恶意请求（借刀杀人）**。

---

### 详细回答

#### 1. XSS（跨站脚本攻击）
- **分类**：
  - 存储型（最危险，注入留言板入库保存）；
  - 反射型（注入 URL 参数直接返回）；
  - DOM 型（前端 JS 读 URL 盲目赋值 `innerHTML`）。
- **防御核心三板斧**：
  1. **输入输出转义过滤**：严禁直接拼接 HTML 字符串，对富文本使用安全白名单库（`DOMPurify.sanitize()`）；
  2. **Cookie 安全标记**：敏感登录 Token 的 Cookie 必须打上 **`HttpOnly`** 标记（禁止任何前端 JS 通过 `document.cookie` 窃取）；
  3. **CSP（内容安全策略）**：配置 HTTP 响应头 `Content-Security-Policy`，只允许加载可信域名的脚本。

#### 2. CSRF（跨站请求伪造）
- **攻击过程**：用户已登录银行网站 `bank.com`；用户在未登出情况下访问了黑客的钓鱼网站 `evil.com`；钓鱼网站暗中发出一张图片 `<img src="bank.com/transfer?money=1000&to=hacker">`，浏览器会自动为该请求带上银行网站的 Cookie，服务器误以为是用户本人操作。
- **防御核心三板斧**：
  1. **SameSite 属性**：现代浏览器最强防线！将 Cookie 的 `SameSite` 设为 `Lax` 或 `Strict`，跨站请求直接禁止携带 Cookie；
  2. **CSRF Token**：请求体中携带一个由服务端下发的随机动态 Token，黑客跨站发起请求时根本拿不到该 Token；
  3. **验证码与双重确认**：转账等核心敏感操作强制要求二次短信或验证码核验。

---

### 核心代码片段（极简记法）

```javascript
// 1. 防御 XSS：富文本净化
import DOMPurify from 'dompurify';
const cleanHtml = DOMPurify.sanitize(userDirtyInput);

// 2. 防御 CSRF：请求头显式注入独立 Token
axios.post('/api/pay', data, {
  headers: { 'X-CSRF-Token': getCsrfTokenFromMeta() }
});
```

---

### 面试加分项

- **JWT 存放在 LocalStorage 还是 Cookie 更安全？** 这是一个经典高频面试题。必须指出：
  - 存 LocalStorage：天然完全免疫 CSRF，但**一旦发生 XSS 会被一锅端秒级窃取**；
  - 存带有 `HttpOnly; Secure; SameSite=Lax` 的 Cookie：JS 彻底无法窃取（防 XSS 窃取），同时 SameSite 几乎彻底锁死了 CSRF，综合安全性最高。
