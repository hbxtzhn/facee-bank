### 一句话总结

采用 **Docker 多阶段构建（Multi-stage Build）结合 Alpine 极轻量镜像**。构建阶段（Builder）使用完整的 Node 环境安装依赖并执行编译打包；运行阶段（Runner）丢弃全部源代码和 Node 运行时，仅将打包产物 `dist/` 复制到只有 20MB 的 **Nginx Alpine 基础镜像**中，配置静态路由与反向代理，实现镜像体积缩减 95% 且具备极致启动速度与生产安全性。

---

### 详细回答

#### 1. 为什么不能直接跑 `node dist/index.js`？
- 纯前端静态应用跑在 Node.js 镜像里，会额外携带几百 MB 的 Node 运行时，浪费服务器内存且存在未经打补丁的容器安全漏洞；
- 生产环境静态文件必须由高性能的 **Nginx 或 Caddy** 托管，原生支持 HTTP/2、Brotli 压缩与长效 Cache-Control。

#### 2. 多阶段构建（Dockerfile）结构
- **阶段 1（deps）**：`pnpm install` 依赖并利用 Docker 层缓存；
- **阶段 2（builder）**：注入环境变量，执行 `pnpm build`；
- **阶段 3（runner）**：基于 `nginx:alpine`，挂载自定义 `nginx.conf`，拷贝 `dist` 目录。

---

### 核心代码片段（极简记法）

```dockerfile
# 阶段 1：构建产物
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm i -g pnpm && pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

# 阶段 2：轻量生产服务（仅 20MB）
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

### 面试加分项

- **SPA 单页应用 Nginx 路由兜底**：在 `nginx.conf` 中必须配置 `try_files $uri $uri/ /index.html;`，杜绝用户在前端路由（如 `/chat/123`）按下 F5 刷新时出现 Nginx 404 错误。
