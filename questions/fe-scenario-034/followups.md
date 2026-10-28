## 追问 1：前端如果在 a.com 的 JS 里手动写 document.cookie = "token=123; Domain=b.com"，会发生什么？

**回答要点**：
浏览器会直接静默忽略该操作（写入失败）！
浏览器安全机制严格规定：页面只能将 Cookie 的 Domain 设置为当前域名本身或其公共父级域名，禁止向任何无关域名种 Cookie。

---

## 追问 2：SameSite 属性设为 Strict、Lax、None 分别代表什么？

**回答要点**：
- `Strict`：最严格，任何第三方网站发起的请求（包括点击超链接）绝不携带该 Cookie；
- `Lax`（现代默认）：导航类跨站（如直接点击 a 链接跳转）放行携带，跨站 POST/iframe 请求禁止携带；
- `None`：任何跨站请求均可携带，但必须同时开启 `Secure`（必须走 HTTPS）。
