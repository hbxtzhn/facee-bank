### 一句话总结

依赖治理策略采用**“版本锁定规范（Strict Lockfile） + 自动化安全审计（Renovate / Dependabot） + 性能预算红线（Bundle Size Budget）”**。在 `package.json` 中采用精准锁定语义化版本；通过 CI 自动化 PR 进行依赖渐进式升级，并在 CI 中配置 **Bundle-analyzer 体积波动警戒线**，杜绝升级大模型 SDK 导致打包体积失控膨胀或出现破坏性 Breaking Changes。

---

### 详细回答

#### 1. 痛点：AI 生态依赖更新极度激进
- OpenAI / LangChain 等 SDK 每周发布数个小版本，API 频繁废弃（Deprecated）；
- 若随意使用 `^1.0.0`，团队成员在不同时间 `npm install` 极易构建出不同代码，导致诡异线上故障。

#### 2. 治理四步法
1. **统一包管理器与锁定文件**：
   全团队强制使用 `pnpm`，提交 `pnpm-lock.yaml`，CI 部署强制 `--frozen-lockfile`；
2. **自动化依赖升级工具（Renovate）**：
   配置规则每周一自动发起依赖更新 PR，自动合并测试通过的小版本（Patch Updates）；
3. **体积预算防护（Bundle Size Check）**：
   在 CI 中集成 `size-limit`，如果某个 SDK 升级导致包体积单次增加超过 50KB，自动阻断 PR 合并并报警；
4. **沙箱回归单测覆盖**：
   对封装的大模型 API 客户端编写完整的接口适配器单测，升级后运行单测自动校验新旧接口入参返回值兼容性。

---

### 核心代码片段（极简记法）

```json
// .size-limit.json 体积预算约束
[
  {
    "path": "dist/assets/index-*.js",
    "limit": "200 KB"
  },
  {
    "path": "dist/assets/markdown-vendor-*.js",
    "limit": "150 KB"
  }
]
```

---

### 面试加分项

- **对“重型库”保持克制与替代方案选型**：指出在前端工程中，避免为了简单的流式通信无脑引入几十 MB 的庞大 LangChain 全家桶；推荐使用原生的极简 Fetch Stream 或官方轻量 `@ai-sdk/react`（Vercel AI SDK），保持依赖极致纯粹。
