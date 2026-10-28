## 追问 1：打包出的 Docker 镜像如何实现“一份镜像，测试与生产环境不同接口地址配置”？

**回答要点**：
前端代码打包后是写死的静态文本。实现动态配置的工业界最佳解法：
在 Docker 启动脚本 `entrypoint.sh` 中，利用 `envsubst` 读取容器运行时的环境变量，动态替换 `index.html` 中注入的 `window.__APP_CONFIG__ = { API_URL: "$API_URL" }` 占位符。

---

## 追问 2：Docker 构建时每次都重新下载 pnpm 依赖非常耗时，怎么利用缓存加速？

**回答要点**：
开启 BuildKit 特性（`DOCKER_BUILDKIT=1`），并在 Dockerfile 中挂载缓存目录：
`RUN --mount=type=cache,id=pnpm,target=/root/.local/share/pnpm/store pnpm install`，复用宿主机依赖缓存。
