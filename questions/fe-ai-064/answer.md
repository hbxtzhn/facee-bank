### 一句话总结

CI/CD 采用**“并行门禁校验（Parallel Gateways） + 容器化流水线 + 边缘无感知蓝绿部署”**。代码提 PR 触发并行运行 **TypeCheck + ESLint + Vitest 单元测试 + Playwright 无头浏览器 E2E 真实流式对话仿真**；全绿合并至 main 后触发 Docker 极速构建，产物上传全球 CDN 并原子化切换路由，实现 5 分钟内高质量交付。

---

### 详细回答

#### 1. 流水线阶段设计（GitHub Actions 范式）
- **Stage 1：Lint & TypeCheck（并行执行，1分钟）**：
  检查语法规范与 TS 静态类型；
- **Stage 2：Unit Test（Vitest，1分钟）**：
  测试 SSE 流式解析器、Markdown 补齐状态机、Token 计算纯函数；
- **Stage 3：E2E 仿真测试（Playwright，2分钟）**：
  启动本地前端与 Mock 模型服务，模拟用户在输入框打字、点击发送、断网断线重连、点击停止生成的真实端到端完整链路；
- **Stage 4：Build & Artifacts（2分钟）**：
  Turborepo 远程缓存加速构建，生成优化后的静态资源包；
- **Stage 5：Deploy（秒级）**：
  推送到 Cloudflare Pages / Vercel 或 Kubernetes 生产集群。

---

### 核心代码片段（极简记法）

```yaml
# .github/workflows/ci.yml 核心骨架
name: AI Web CI
on: [pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v3
      - run: pnpm install --frozen-lockfile
      - run: pnpm type-check
      - run: pnpm lint
      - run: pnpm test:unit
      - run: pnpm test:e2e # Playwright 无头自动化仿真
```

---

### 面试加分项

- **PR 临时预览环境（Preview Deployments）**：结合 Vercel / Cloudflare Pages 为每一个 Pull Request 自动生成专属独立测试链接（如 `pr-42.preview.ai.com`），QA 和产品经理可以在真实设备上直接试用验收，验收通过才准许合并。
