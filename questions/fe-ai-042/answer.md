### 一句话总结

基于 **pnpm Workspaces + Turborepo（或 Nx）** 搭建现代 Monorepo 工程。将代码拆分为 `apps/web`（前端界面）、`apps/node-gateway`（BFF 计费鉴权中间层）与 `packages/shared-types`（模型与 Prompt 共享契约）；通过 workspace 软链接实现**“类型一处改动，前后端实时联动编译提示”**，配合 Turborepo 全局缓存实现秒级极速构建。

---

### 详细回答

#### 1. 痛点：多仓分离（Multi-repo）的维护灾难
- AI 模型接口迭代极快（字段频繁新增/弃用）；
- 前端与 Node BFF 跨仓维护时，TS 接口必须双边手动复制同步，经常因拼写漏更导致生产环境运行时报错。

#### 2. Monorepo 目录规划标准
```text
my-ai-project/
├── apps/
│   ├── web/               # Next.js / React 前端
│   └── gateway/           # NestJS / Fastify 模型中间层 (BFF)
├── packages/
│   ├── api-client/        # 前端调用 BFF 的 SDK
│   ├── shared-types/      # 核心领域实体、Zod Schema 与 TS 类型
│   └── ui/                # 共享 Design System 组件库
└── pnpm-workspace.yaml
```

#### 3. Turborepo 任务流拓扑编排
- 在根目录 `turbo.json` 中配置 pipeline：
  `"build": { "dependsOn": ["^build"], "outputs": [".next/**", "dist/**"] }`
- 当构建 `web` 时，Turborepo 会自动先编译依赖的 `shared-types`，并智能跳过未改动包的构建（Remote Caching）。

---

### 核心代码片段（极简记法）

```json
// pnpm-workspace.yaml
packages:
  - "apps/*"
  - "packages/*"
```

```json
// apps/web/package.json 引入内部公共类型包
"dependencies": {
  "@org/shared-types": "workspace:*"
}
```

---

### 面试加分项

- **Changesets 自动化版本与发版**：在 Monorepo 中配合 `@changesets/cli`，针对每个 Pull Request 自动生成改动日志，合并后自动化打 tag 发布独立 npm 包。
