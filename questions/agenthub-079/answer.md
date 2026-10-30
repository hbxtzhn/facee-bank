### 一句话总结

会话认证、跨站请求防护和浏览器跨源读取策略职责不同，不能互相替代。

### 回答要点

1. Cookie 的 Secure、HttpOnly 和合适 SameSite 属性可降低部分风险，但仍需结合具体登录和跨站流程设计写操作保护。

2. CORS 主要控制浏览器脚本读取跨源响应，不是通用服务端鉴权；请求可能已经发送，非浏览器客户端也不受同样限制。

3. 写接口验证会话、资源权限和适合的 CSRF 或来源规则，避免 GET 执行状态变更。这里是网页安全原理题，不代指全部现有接口实现。

### 常见误区与边界

不要把 CORS 配置当成后台写操作的访问控制。

### 资料核对

[OWASP：CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)。官方资料用于核对通用 API 语义，不证明任何项目已启用相应能力。

### 关联复习

[同专题关联题](../agenthub-080/question.md)
