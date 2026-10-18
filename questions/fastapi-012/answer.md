## 1. 鉴权闭环全流程时序图

```text
【登录阶段】
客户端 ──POST /token (username, password)──> FastAPI 路由
                                                   │
                                            从 DB 验证加盐哈希密码
                                                   │ 验证成功
                                            生成 JWT (包含 user_id, exp)
客户端 <──返回 {access_token: "xxx", token_type: "bearer"}──┘

【请求受保护接口】
客户端 ──GET /users/me [Header: Authorization: Bearer xxx]──> FastAPI
                                                                  │
                                                     oauth2_scheme 抓取 Token 字符串
                                                                  │
                                                     get_current_user 解密验签 JWT
                                                                  │
                                                     从 DB / 缓存获取完整 User 实体
                                                                  │
客户端 <──返回当前用户个人数据 (200 OK)───────────────────────── 路由执行
```

---

## 2. 生产级鉴权依赖设计范式

```python
from datetime import datetime, timedelta, timezone
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt

SECRET_KEY = "your-256-bit-secret"
ALGORITHM = "HS256"

# 1. 声明 OAuth2 Bearer 提取器（指定登录获取 Token 的路由 URL）
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()

# 2. 签发 JWT
def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=2)):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# 3. ★ 核心鉴权依赖：任意受保护路由只需 Depends(get_current_user)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="认证凭据无效或已过期",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    # 模拟从 DB 取出完整用户信息
    user = {"username": username, "role": "admin"}
    return user

# 4. 路由挂载
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # 校验账号密码（略）
    token = create_access_token(data={"sub": form_data.username})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    # 只要能进入此路由，current_user 必定是经过严密鉴权合法的用户
    return current_user
```
