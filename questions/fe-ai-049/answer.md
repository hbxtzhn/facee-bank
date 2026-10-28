### 一句话总结

该架构采用**“短暂临时令牌（Ephemeral Ephemeral Token）机制 + 反向鉴权代理网关”**。前端绝不可明文硬编码任何大模型主 API Key；用户发起会话前先请求后端 BFF，后端核销用户套餐额度后下发**单次带签名且限制生效时间（如 5 分钟）的临时访问 Token**，前端携带该 Token 直连代理网关推流，兼具极速低延迟与绝对资金安全。

---

### 详细回答

#### 1. 为什么前端不能直接保存官方 API Key？
- 无论代码如何打包混淆，任何在前端客户端中暴露的 OpenAI / Anthropic 密钥，都会在 1 分钟内被黑客通过 Network 抓包提取，直接导致数十万元的盗刷欠费事故。

#### 2. 安全代理流转架构
1. **获取授权凭证**：前端向自身后端发送 `POST /api/auth/token`；
2. **后端鉴权与预扣费**：后端核验用户身份与余额，签发一份带有 HMAC 防伪签名的短效 JWT；
3. **直连边缘网关（Cloudflare Workers 等）**：
   - 前端直连代理 URL，在 Header 中携带短效 JWT；
   - 边缘网关验证签名并扣减使用配额后，在网关层动态注入真实的大模型 API 密钥并透明转发给大模型；
   - 模型响应通过 SSE 直连推流回前端。

---

### 核心代码片段（极简记法）

```javascript
// 1. 先向自身业务后端申请临时推流凭证
const { tempToken, gatewayUrl } = await fetch('/api/token').then(r => r.json());

// 2. 前端携带临时凭据直连网关，安全直推
const res = await fetch(gatewayUrl, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${tempToken}`, // 临时 Token，泄漏自动过期
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ prompt: '你好' })
});
```

---

### 面试加分项

- **前端客户端密钥模式（BYOK - Bring Your Own Key）**：如果是面向开发者的开源或本地工具，允许用户在设置中填入自己的 API Key。前端仅将密钥加密保存在用户的本地 LocalStorage 中，每次请求直接直连官方接口，零经过第三方服务器，打消用户隐私顾虑。
