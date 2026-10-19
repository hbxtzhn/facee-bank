## 追问 1：OAuth2PasswordBearer 校验了什么？

它提取请求头中的 Bearer token，并让 OpenAPI 知道 token 获取地址；签名、exp、issuer/audience 及用户状态需后续依赖验证。常见 JWT 为签名而非加密格式，不能把 payload 当成保密容器。

## 追问 2：如何提前失效？

可采用短期 access token 配合可轮换的 refresh token、用户 token_version 或按 jti 保存带 TTL 的吊销记录。策略取决于一致性与状态成本；它不是所有系统都必须采用的唯一“黑名单标准”。检查必须在正常验签与声明验证之后进行。
