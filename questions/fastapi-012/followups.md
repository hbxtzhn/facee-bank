## 追问 1：OAuth2PasswordBearer(tokenUrl='token') 这个依赖项到底做了什么？它会帮我们校验 Token 签名吗？

不会！这是很多初学者的最大误区。OAuth2PasswordBearer 唯一的作用是：在 OpenAPI Swagger 文档中右上角点亮那个小绿锁输入框，并在收到 HTTP 请求时，从 Authorization Header 里把 Bearer <token> 这一串原始字符串抓取出来返回而已。解密、验签、校验过期时间全部必须由开发者在随后的依赖项里自己写代码完成。

## 追问 2：如果想让已经颁发的 JWT Token 提前失效（如用户点击登出、修改密码），怎么处理？

JWT 是无状态的，默认在到达 exp 过期时间前一直合法。若需提前吊销，行业标准做法是引入 Redis 黑名单：登出时把该 token 的唯一标识 jti（或完整 token）作为 key 存入 Redis，TTL 设为剩余有效时长。鉴权依赖项在解析完 JWT 之后，查一次 Redis 确认不在黑名单中。
