## 1. 分清提取、验签与业务授权

OAuth2PasswordBearer 负责提取 Bearer 字符串并描述 OpenAPI 安全方案，不负责验证 JWT。常见 JWT 是签名的 JWS，内容可被解码，**验签不是解密**；敏感数据不要写进 payload。

登录必须先校验密码哈希，再签发有限有效期的 token；访问受保护路由时校验算法、签名、必需声明和用户状态。生产系统还需考虑 issuer/audience、限流、TLS、密钥轮换与吊销机制。

## 2. 可运行的教学应用

依赖：`fastapi python-multipart PyJWT pwdlib[argon2]`。运行前从环境设置至少 32 字节的随机 `JWT_SECRET_KEY`，不要把实际密钥写进源码。

下例**只提供教学内存账号** `demo` / `demo-password-change-me`，真实系统必须替换用户持久化与注册流程；没有把“省略密码校验”当成合法登录。

```python
import os
from datetime import datetime, timedelta, timezone
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
import jwt

SECRET_KEY = os.environ["JWT_SECRET_KEY"]
if len(SECRET_KEY.encode("utf-8")) < 32:
    raise RuntimeError("JWT_SECRET_KEY must contain at least 32 bytes")
ALGORITHM = "HS256"
password_hash = PasswordHash.recommended()
users = {"demo": {
    "username": "demo",
    "password_hash": password_hash.hash("demo-password-change-me"),
    "disabled": False,
}}
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def unauthorized():
    return HTTPException(status_code=401, detail="认证凭据无效或已过期",
                         headers={"WWW-Authenticate": "Bearer"})

def create_access_token(username: str):
    return jwt.encode({
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
    }, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/token")
def login(form: OAuth2PasswordRequestForm = Depends()):
    user = users.get(form.username)
    # 未知用户名也检查一个演示哈希，避免立即返回形成明显时差。
    candidate = user or users["demo"]
    valid = password_hash.verify(form.password, candidate["password_hash"])
    if not user or not valid or user["disabled"]:
        raise unauthorized()
    return {"access_token": create_access_token(user["username"]), "token_type": "bearer"}

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM],
                             options={"require": ["sub", "exp"]})
    except InvalidTokenError:
        raise unauthorized()
    username = payload.get("sub")
    user = users.get(username) if isinstance(username, str) else None
    if not user or user["disabled"]:
        raise unauthorized()
    return {"username": user["username"]}

@app.get("/users/me")
def read_me(user: dict = Depends(get_current_user)):
    return user
```

## 3. 协议选择边界

密码模式用于解释现有应用或受控教学场景，不应被当成所有新 OAuth2 系统的推荐模式；OAuth 2.0 安全最佳实践已禁止资源所有者密码凭据授权，新系统优先考虑授权码 + PKCE、OIDC 或成熟身份提供方。JWT 身份认证也不自动完成对象级/角色级授权。

参考：[FastAPI JWT 教程](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)、[RFC 9700 §2.4](https://www.rfc-editor.org/rfc/rfc9700.html#section-2.4)。
