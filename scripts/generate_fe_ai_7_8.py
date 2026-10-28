import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUESTIONS_DIR = os.path.join(BASE_DIR, 'questions')

DATA = [
    {
        "id": "fe-ai-061",
        "title": "如何设计AI前端项目的标准化目录结构？",
        "difficulty": "medium",
        "question": "如何设计一个AI前端项目的标准化目录结构，兼顾业务功能、共享组件、工具函数与类型定义？",
        "answer": """### 一句话总结

推荐采用**“功能特性切片（Feature-based Architecture）结合领域驱动分层”**。将代码组织从按技术类型（如把所有 components 堆在一起）升级为**按 AI 业务特性（`chat/`, `agent/`, `prompt-studio/`）自包含组织**；核心层抽象出独立的 `models/`（模型配置与 Provider 适配）、`tools/`（客户端执行工具集）与 `shared/`（纯 UI 与通用工具），保持高内聚低耦合。

---

### 详细回答

#### 1. 传统按技术类型组织的痛点
- 所有的 hooks、components、api 散落在全局目录中；
- 当 AI 功能包含独立的流式解析器、Markdown 特殊渲染卡片、状态机时，开发者需要在 10 个跨度极大的目录之间反复横跳，改一个 Agent 功能牵扯全仓。

#### 2. 标准生产级目录树规范
```text
src/
├── features/               # 业务特性切片（按业务域划分）
│   ├── chat/              # 聊天特性（包含该特性专属的 components/hooks/stores）
│   ├── agent-workflow/    # 智能体编排工作流
│   └── prompt-lab/        # Prompt 调试实验室
├── core/                   # AI 核心能力下沉层
│   ├── models/            # 厂商适配器（OpenAI, Anthropic, Ollama）
│   ├── tools/             # 客户端 Tool 注册表（计算器、地理位置、截图）
│   └── stream/            # SSE / WebSocket 传输层与流式解析器
├── components/ui/          # 通用设计系统（原子级按钮、弹窗、输入框）
├── types/                 # 跨模块共享 TS 类型与 Zod Schema
└── lib/                   # 纯工具函数（时间格式化、缓存助手）
```

---

### 核心代码片段（极简记法）

```text
// features/chat 内部实现完全自闭环：
features/chat/
├── components/MessageList.tsx
├── hooks/useStreamChat.ts
├── stores/chatStore.ts
└── index.ts               # 对外仅导出公共 API（Facade）
```

---

### 面试加分项

- **路径别名（Path Alias）与严格跨模块依赖规则**：在 `tsconfig.json` 中配置 `@/features/*`，并配合 ESLint 强行禁止 `features/chat` 内部代码直接深层引用 `features/prompt-lab` 的私有文件，跨模块必须走对方的 `index.ts` 导出，杜绝模块网状循环依赖。""",
        "followups": """## 追问 1：全局状态库（如 Zustand store）应该放在 src/stores 还是按 feature 存放？

**回答要点**：
特性专属的状态（如当前会话的流式中间 Buffer、单条消息展开折叠态）严格放在该 `features/chat/stores` 内部；仅有跨整个系统共享的全局状态（如当前登录用户 Profile、全局租户主题）才提取到 `src/stores`。

---

## 追问 2：目录结构如何适配微前端或者后续拆分为 Monorepo？

**回答要点**：
按 Feature-based 划分的代码天然具备**向独立子包抽离的独立性**。后续若要升级为 Monorepo，只需将 `features/agent-workflow` 目录直接物理剪切到 `packages/agent-workflow`，并在其内部添加 `package.json` 即可瞬间无缝拆分。"""
    },
    {
        "id": "fe-ai-062",
        "title": "请设计一套AI前端代码规范并集成Git Hooks自动检查",
        "difficulty": "medium",
        "question": "请设计一套AI前端代码规范（ESLint、Prettier、Commitlint），并集成Git Hooks自动检查。",
        "answer": """### 一句话总结

现代规范体系采用 **“ESLint Flat Config（语法与逻辑检查） + Prettier（无争议代码排版） + Commitlint（Angular 规范提交信息） + Husky / Simple-git-hooks”**。在 Git 提交（`pre-commit`）时利用 **`lint-staged` 仅对暂存区增量文件执行检查与自动修复**，在 `commit-msg` 阶段拦截不规范提交日志，实现本地秒级拦截并守死提交入口。

---

### 详细回答

#### 1. 工具分工明确（职责不越界）
- **ESLint**：管代码质量（变量未定义、禁用 `any`、React Hook 依赖项缺失、禁止在流式组件中滥用副作用）；
- **Prettier**：管代码格式（换行、单双引号、缩进、尾逗号）；
- **eslint-config-prettier**：关闭所有 ESLint 中与 Prettier 冲突的排版规则。

#### 2. Commitlint 规范（Angular 风格）
- 强制格式：`<type>(<scope>): <subject>`；
- 类型必须在：`feat`、`fix`、`docs`、`style`、`refactor`、`perf`、`test`、`chore` 之中。

#### 3. 为什么必须用 lint-staged？
- 如果每次 `git commit` 都全量扫描几十万行源码，提交一次要等 30 秒；
- `lint-staged` 只针对 `git add` 暂存区里的几十行改动文件执行 Lint，0.5 秒瞬间跑完。

---

### 核心代码片段（极简记法）

```json
// package.json 配置
{
  "scripts": {
    "prepare": "husky install"
  },
  "lint-staged": {
    "*.{ts,tsx,js}": [
      "eslint --fix",
      "prettier --write"
    ]
  }
}
```

---

### 面试加分项

- **ESLint 9 Flat Config 演进**：指出现代项目已全面拥抱 `eslint.config.js`（扁平化配置），基于纯 ES 模块导入，废弃了旧版复杂的 `.eslintrc.js` 及其隐藏的共享插件解析 Bug，配置速度与可读性大幅提升。""",
        "followups": """## 追问 1：如果有人在本地用 git commit --no-verify 强行跳过了本地的 Git Hooks 怎么办？

**回答要点**：
本地 Git Hooks 属于“防君子不防小人”。
团队必须在 **CI/CD 流水线（GitHub Actions / GitLab CI）上配置强制 Gatekeeper**：代码推送到远程时必须全量执行 `npm run lint` 和 `npm run type-check`，检查不通过直接锁死合并按钮（Block PR）。

---

## 追问 2：AI 自动生成（如 Copilot 补全）的大段代码经常报错违背 TS 规则，怎么快速规范？

**回答要点**：
在 VS Code 中配置 `"editor.codeActionsOnSave": { "source.fixAll.eslint": "explicit" }` 与 `"editor.formatOnSave": true`，保存瞬间让工具链自动修复所有 AI 生成的细小格式缺陷。"""
    },
    {
        "id": "fe-ai-063",
        "title": "如何用Husky、lint-staged与Commitizen打造自动化提交流水线？",
        "difficulty": "easy",
        "question": "如何用Husky、lint-staged、Commitizen打造AI项目的自动化提交与代码质量流水线？",
        "answer": """### 一句话总结

该流水线采用 **“交互式引导提交（Commitizen `git cz`） + Git 生命周期拦截（Husky） + 增量自动化修复（lint-staged）”**。开发者敲击 `cz` 通过方向键选择改动类型并填写工单号；提交触发 `pre-commit` 钩子自动格式化并修复语法隐患；`commit-msg` 钩子校验日志合法性，实现从写码到入仓全流程工业化标准化。

---

### 详细回答

#### 1. 三剑客各司其职
- **Commitizen（前端交互层）**：替代枯燥的 `git commit -m "..."`，提供友好命令行表单交互，引导输入标准 message；
- **Husky（钩子驱动层）**：在 `npm install` 时自动安装 Git 钩子脚本到 `.husky/`；
- **lint-staged（执行引擎）**：仅抓取本次提交的差异文件，自动执行 ESLint、Prettier 与单元测试。

#### 2. 标准搭建三步法
1. 安装依赖：`pnpm add -D husky lint-staged commitizen cz-conventional-changelog @commitlint/cli`；
2. 激活 Husky：`pnpm dlx husky-init`；
3. 挂载钩子：
   - `.husky/pre-commit` 写入 `npx lint-staged`；
   - `.husky/commit-msg` 写入 `npx --no -- commitlint --edit ${1}`。

---

### 核心代码片段（极简记法）

```bash
# .husky/pre-commit 钩子内容
npx lint-staged

# .husky/commit-msg 钩子内容
npx --no -- commitlint --edit "$1"
```

---

### 面试加分项

- **提交前同步执行类型检查（tsc）**：很多人忽略了 ESLint 默认不会检查静态类型错误。在 `lint-staged` 或 pre-commit 中加上 `tsc --noEmit`，坚决把任何类型不匹配的危险代码拦截在本地。""",
        "followups": """## 追问 1：lint-staged 能直接跑 tsc --noEmit 吗？会有什么坑？

**回答要点**：
有坑！
`tsc` 不支持只编译部分单文件，它必须读取全量项目工程文件。若将 `tsc` 挂在 `lint-staged` 的单文件匹配列表里会导致每个暂存文件全量跑一次 `tsc`（卡死电脑）。
正确做法是：在 `lint-staged` 运行完之后，单独在 `pre-commit` 脚本末尾追加一行单次的 `pnpm type-check`。

---

## 追问 2：新手觉得 git cz 命令太麻烦，只想用 VS Code Git 界面点击提交，Commitizen 会失效吗？

**回答要点**：
会失效。但因为配置了 Husky 的 `commit-msg` 强制校验，哪怕在 VS Code 界面点击提交，如果手写的日志不合规也会被直接打回并弹出报错，依然能够强力守护规范底线。"""
    },
    {
        "id": "fe-ai-064",
        "title": "设计AI前端CI/CD流水线：代码检查、单测、E2E与构建部署",
        "difficulty": "hard",
        "question": "设计一个AI前端项目的CI/CD流水线，包括代码检查、单元测试、E2E测试、构建优化、自动部署。",
        "answer": """### 一句话总结

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

- **PR 临时预览环境（Preview Deployments）**：结合 Vercel / Cloudflare Pages 为每一个 Pull Request 自动生成专属独立测试链接（如 `pr-42.preview.ai.com`），QA 和产品经理可以在真实设备上直接试用验收，验收通过才准许合并。""",
        "followups": """## 追问 1：AI 流式接口依赖真实大模型，跑 E2E 测试如果每次都调用真实 OpenAI 接口成本极高且经常超时，怎么破？

**回答要点**：
在 CI 自动化测试中**严禁依赖真实外部大模型！**
必须利用 `msw`（Mock Service Worker）或本地自建轻量 Node 脚本，模拟出按照每 50ms 吐一个 chunk 的可预测 Mock SSE 服务，既完全免费、毫秒级响应，又杜绝外部网络抖动导致的误报警。

---

## 追问 2：生产部署如何做到前端版本更新时，正在流式生成的用户页面不被意外刷新中断？

**回答要点**：
采用 **静态资源版本哈希（Hash Assets） + 多版本并存（Side-by-side Retention）**。新版本发布不删除 CDN 上的旧版 JS 文件；前端提供软更新弹窗提示：“检测到新版本，生成完成后点击刷新体验”，尊重正在进行的会话。"""
    },
    {
        "id": "fe-ai-065",
        "title": "如何用Docker容器化AI前端应用实现开发、测试、生产环境一致？",
        "difficulty": "medium",
        "question": "如何用Docker容器化AI前端应用，实现开发、测试、生产环境的一致性？",
        "answer": """### 一句话总结

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

- **SPA 单页应用 Nginx 路由兜底**：在 `nginx.conf` 中必须配置 `try_files $uri $uri/ /index.html;`，杜绝用户在前端路由（如 `/chat/123`）按下 F5 刷新时出现 Nginx 404 错误。""",
        "followups": """## 追问 1：打包出的 Docker 镜像如何实现“一份镜像，测试与生产环境不同接口地址配置”？

**回答要点**：
前端代码打包后是写死的静态文本。实现动态配置的工业界最佳解法：
在 Docker 启动脚本 `entrypoint.sh` 中，利用 `envsubst` 读取容器运行时的环境变量，动态替换 `index.html` 中注入的 `window.__APP_CONFIG__ = { API_URL: "$API_URL" }` 占位符。

---

## 追问 2：Docker 构建时每次都重新下载 pnpm 依赖非常耗时，怎么利用缓存加速？

**回答要点**：
开启 BuildKit 特性（`DOCKER_BUILDKIT=1`），并在 Dockerfile 中挂载缓存目录：
`RUN --mount=type=cache,id=pnpm,target=/root/.local/share/pnpm/store pnpm install`，复用宿主机依赖缓存。"""
    },
    {
        "id": "fe-ai-066",
        "title": "设计AI前端性能监控方案收集Core Web Vitals与Token/s等指标",
        "difficulty": "hard",
        "question": "请设计一个AI前端性能监控方案，收集FP、FCP、LCP、CLS等核心指标，并关联AI特定指标（如Token/s）。",
        "answer": """### 一句话总结

监控方案采用**“Web-Vitals 浏览器性能基线 + AI 专属业务指标探测器（TTFT、Token/s、打断率） + sendBeacon 批量异步聚合上报”**。结合 `PerformanceObserver` 采集首屏加载与布局抖动；重点度量 AI 对话独有的**首字时间（TTFT）与端到端推流速率**，将技术指标与用户提问 Token 规模多维交叉关联，建立可视化全链路监控大盘。

---

### 详细回答

#### 1. 传统前端指标 vs AI 专属性能指标
- **传统 Web Vitals**：
  - **FCP / LCP**：首屏最大内容绘制；
  - **CLS（Cumulative Layout Shift）**：由于流式文本不断撑开高度，AI 界面极易发生严重的 CLS 布局抖动，是重点监控对象；
- **AI 独有核心指标（必须度量）**：
  - **TTFT（Time To First Token）**：用户点击发送到首个汉字渲染出来的延迟（衡量模型思考与网关冷启动性能）；
  - **TPS（Tokens Per Second）**：流式推流速率；
  - **User Abort Rate（打断率）**：用户提前点击“停止”的比例（打断率高说明生成质量差或速度慢）。

#### 2. 上报架构设计
- 使用 Google 官方 `web-vitals` 库监听；
- 采集完成后，使用 `navigator.sendBeacon('/api/metrics', blob)` 异步非阻塞上报，不与主业务请求抢占带宽。

---

### 核心代码片段（极简记法）

```javascript
import { onLCP, onCLS } from 'web-vitals';

// 1. 监听基础指标
onLCP(metric => reportMetric('LCP', metric.value));
onCLS(metric => reportMetric('CLS', metric.value));

// 2. 测量 AI 首字延迟与生成速率
function trackAIPerformance(sessionId) {
  const t0 = performance.now();
  let firstTokenTime = null;
  let tokenCount = 0;

  return {
    onFirstToken: () => {
      firstTokenTime = performance.now() - t0;
      reportMetric('AI_TTFT', firstTokenTime, { sessionId }); // 毫秒
    },
    onToken: () => tokenCount++,
    onDone: () => {
      const totalTime = (performance.now() - t0) / 1000;
      const tps = tokenCount / totalTime;
      reportMetric('AI_TPS', tps, { sessionId, totalTokens: tokenCount });
    }
  };
}
```

---

### 面试加分项

- **动态采样率控制（Sampling Rate）**：大流量平台全量上报会冲垮监控后端。对成功会话按 5% 比例动态采样上报，对报错会话（Error / 500 / 429）执行 100% 强制全量上报，平衡监控覆盖度与服务器开销。""",
        "followups": """## 追问 1：前端统计的 Token/s 和后端大模型服务端的 Token/s 经常有偏差，原因是什么？

**回答要点**：
前端度量的是**“用户最终感知端到端速率”**，包含了：网络往返传输延迟（RTT）、反向代理流式分包缓冲、以及前端 JS 主线程 Markdown 解析与 DOM 绘制耗时；而服务端仅度量模型显卡推理速度。前端指标更能真实代表用户真实体感。

---

## 追问 2：流式文本不断追加导致的 CLS 飙升，前端怎么在布局上根治？

**回答要点**：
在聊天流的滚动容器上配置 CSS 原生属性：`overflow-anchor: auto`，并给外层容器设置 `contain: layout style`，浏览器会自动锁定视口锚定点，避免新增内容将视口上方已阅读的内容顶飞，将 CLS 牢牢压低在 0.05 以下。"""
    },
    {
        "id": "fe-ai-067",
        "title": "如何用Sentry监控AI前端异常，自动捕获输入与模型参数上下文？",
        "difficulty": "medium",
        "question": "如何用Sentry或Bugsnag监控AI前端异常，自动捕获错误上下文（用户输入、模型参数、网络状态）？",
        "answer": """### 一句话总结

采用 **Sentry 前端 SDK 结合 Scope 上下文注入与 Breadcrumbs（面包屑）自动录制**。在全局配置中通过 `Sentry.setContext()` 绑定当前激活的模型名称、网络协议（SSE/WS）与 Prompt 参数；利用自定义前置过滤器（`beforeSend`）在错误上报时对敏感个人隐私进行星号脱敏，配合 React ErrorBoundary 实现异常瞬时捕获与精准现场还原。

---

### 详细回答

#### 1. 为什么传统控制台错误在 AI 场景下极难排查？
- AI 错误通常依赖特定上下文（如：某个特定长度的中文 Prompt 在 Markdown 转义反引号时触发了正则死循环崩溃）；
- 传统 Sentry 只抓取调用栈，无法得知崩溃前用户输入了什么、当前使用的是哪个模型。

#### 2. Sentry Scope 维度上下文设计
- **`setTag('model_id', 'gpt-4o')`**：打上索引标签，在 Sentry 面板中一键筛选“所有特定模型的错误”；
- **`setContext('ai_request', { promptLength, temperature, streamActive: true })`**：记录结构化参数树；
- **Breadcrumbs 面包屑追踪**：记录最近 10 次的用户操作（如：点击选择文件 -> 输入 Prompt -> 收到首个 Chunk -> 发生解析异常）。

---

### 核心代码片段（极简记法）

```javascript
import * as Sentry from '@sentry/react';

// 发起 AI 请求前绑定上下文
Sentry.configureScope((scope) => {
  scope.setTag('ai_provider', 'openai');
  scope.setContext('generation_params', {
    model: 'gpt-4o',
    temperature: 0.7,
    promptLength: prompt.length
  });
  scope.addBreadcrumb({ category: 'ai.stream', message: 'SSE Connection opened' });
});

// 捕获异常
try {
  parseMarkdownChunk(badChunk);
} catch (err) {
  Sentry.captureException(err);
}
```

---

### 面试加分项

- **严苛的 PII 隐私合规拦截（beforeSend）**：绝不可将用户的完整身份证号、银行卡号或涉密商机 Prompt 明文发送到第三方 Sentry 平台。在 `beforeSend(event)` 钩子中编写正则表达式，将敏感内容替换为 `[REDACTED]` 后再外发，确保符合 GDPR / 网络安全合规。""",
        "followups": """## 追问 1：如果大模型正在推流时由于用户网络断开导致报错，如何防止 Sentry 产生海量无意义的网络噪点报警？

**回答要点**：
在 `ignoreErrors` 列表中配置过滤规则，或者在 `beforeSend` 中检查 `err.name === 'AbortError'` 或包含 `Failed to fetch` 且当前 `navigator.onLine === false`，判定为用户主动取消或断网事件，直接丢弃（返回 `null`），不占用 Sentry 配额。

---

## 追问 2：Sentry 录制的会话回放（Session Replay）在多轮长对话中会导致流量过大吗？

**回答要点**：
全量录制会导致体积过大。
生产中推荐采用 **`replaysOnErrorSampleRate: 1.0` + `replaysSessionSampleRate: 0.05`** 策略：正常会话仅低采样率抽查，只有在发生严重代码崩溃时才完整抓取崩溃前后 1 分钟的 DOM 录屏回放。"""
    },
    {
        "id": "fe-ai-068",
        "title": "设计AI前端日志系统结构化记录用户操作、请求耗时与回溯分析",
        "difficulty": "medium",
        "question": "设计一个AI前端日志系统，结构化记录用户操作、AI请求、响应时间、错误信息，便于回溯分析。",
        "answer": """### 一句话总结

日志系统采用**“客户端环形内存缓冲区（Ring Buffer） + 结构化日志 Schema + 分级批量刷盘”**架构。定义包含全局 `traceId`、时间戳、日志级别与分类的标准化 JSON 格式；日常将 `DEBUG`、`INFO` 存入内存队列（仅保留最近 200 条）；一旦触发 `ERROR` 异常，一次性将内存中的前序操作回溯日志打包连带上传，兼顾极低网络开销与事故现场完美复原。

---

### 详细回答

#### 1. 为什么不能每打印一行 `console.log` 就发一次请求？
- 流式生成高频调用，频繁网络上报会严重挤占带宽；
- 绝大多数正常日志无需长期上报沉淀，只有报错前后的“案发现场日志”才具有高价值。

#### 2. 结构化日志标准 Schema
```typescript
interface LogItem {
  traceId: string;       // 贯穿前端与后端的链路 ID
  sessionId: string;     // 会话 ID
  timestamp: number;     // 毫秒时间戳
  level: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR';
  category: 'USER_ACTION' | 'NETWORK' | 'STREAM' | 'RENDER';
  message: string;
  metadata?: Record<string, unknown>;
}
```

#### 3. 环形回溯缓冲区（Ring Buffer）
- 内存中维护固定容量数组（如 100 条）；
- 当写满时新日志覆盖最旧的日志；
- 当捕获到未处理的 Promise 拒绝或代码崩溃时，立即将这 100 条“历史轨迹”全部转存上报。

---

### 核心代码片段（极简记法）

```javascript
class RingLogBuffer {
  constructor(limit = 100) {
    this.limit = limit;
    this.buffer = [];
  }

  log(level, category, message, metadata = {}) {
    const entry = { time: Date.now(), level, category, message, metadata };
    if (this.buffer.length >= this.limit) this.buffer.shift();
    this.buffer.push(entry);

    if (level === 'ERROR') this.flush(); // 报错时立即全量刷盘上报！
  }

  flush() {
    const logs = [...this.buffer];
    navigator.sendBeacon('/api/logs/batch', JSON.stringify(logs));
  }
}
```

---

### 面试加分项

- **全链路 TraceId 贯通（Trace Context）**：在前端发起 Fetch 请求时，请求头注入 `x-trace-id: <uuid>`；后端微服务与模型推理网关在全链路日志中打印该 ID，排查疑难客诉时只需搜一个 ID 即可串联起从浏览器点击、Nginx、业务网关到 GPU 推理的完整链路。""",
        "followups": """## 追问 1：前端写到 IndexedDB 的离线日志，如果用户长时间不上报，怎么清理？

**回答要点**：
基于 TTL（Time-To-Live）机制：设置 7 天过期时间；每次系统初始化时异步触发一次清理事务，删除 `timestamp < Date.now() - 7 * 86400000` 的冷数据，保持存储健康。

---

## 追问 2：如何在生产环境动态开启某个特定用户的 DEBUG 级别日志？

**回答要点**：
基于“白名单指令通道”：客服让客诉用户在 URL 输入特定 Query（如 `?debug_mode=true`）或在控制台执行专属命令，前端检测到后动态将本地日志上报级别从 `ERROR` 临时提升为 `DEBUG`，实现无感定向排查。"""
    },
    {
        "id": "fe-ai-069",
        "title": "如何用Vite或Webpack优化AI前端构建性能？代码分割、TreeShaking与持久缓存",
        "difficulty": "medium",
        "question": "如何用Webpack或Vite优化AI前端构建性能，实现代码分割、Tree Shaking、预加载、持久缓存？",
        "answer": """### 一句话总结

构建优化采用**“动态异步导入按需分包（Dynamic Chunking） + ESM 深度 Tree Shaking + 构建与浏览器双层持久缓存”**。将巨型依赖（Monaco Editor 代码编辑器、Mermaid 架构图、KaTeX 数学排版）全部隔离为独立异步 Chunk，利用动态 `import()` 按需拉取；配置稳定的 `[contenthash]` 结合 Vite 底层的 Rollup 消除无用导出，将首屏主 JS 体积削减 70% 以上。

---

### 详细回答

#### 1. 痛点：AI 前端应用的“体积刺客”
- 一个完整的 AI 应用往往集成了：代码高亮库（Highlight.js / Prism）、富文本/语法树（Remark / Unified）、数学公式（KaTeX）、矢量绘图（Mermaid/ECharts）；
- 若全打包在 `index.js`，首屏体积轻松突破 5MB，弱网下加载需 10 秒以上。

#### 2. 代码分割最佳实践（manualChunks）
- 在 Vite 中通过 `rollupOptions.output.manualChunks` 明确分包：
  - 核心骨架（React + Zustand）：打入 `vendor`；
  - 语法高亮引擎：打入 `async-highlight`；
  - 图表引擎：打入 `async-charts`。

#### 3. 生产级持久缓存（Long-term Cache）
- 输出文件名规范：`[name].[contenthash:8].js`；
- Nginx 对带 hash 的静态文件配置永久强缓存：`Cache-Control: public, max-age=31536000, immutable`；
- `index.html` 配置协商缓存：`Cache-Control: no-cache`，发版后秒级生效。

---

### 核心代码片段（极简记法）

```javascript
// vite.config.js 深度分包配置
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'markdown-vendor': ['marked', 'dompurify'],
          'chart-vendor': ['mermaid', 'echarts'],
          'editor-vendor': ['monaco-editor']
        }
      }
    }
  }
});

// 组件内动态异步按需拉取
const HeavyMermaid = React.lazy(() => import('./HeavyMermaidBlock'));
```

---

### 面试加分项

- **预加载策略（Modulepreload）**：现代 Vite 默认会在 HTML 中注入 `<link rel="modulepreload">`。在首屏加载空闲时，浏览器会在后台静默预拉取 Markdown 解析器 Chunk，等用户真正收到首个 Token 时该模块已在内存就绪，消除动态 import 的网络等待。""",
        "followups": """## 追问 1：为什么有的库（比如某些 CommonJS 模块）无法被 Vite / Rollup 有效 Tree Shaking？

**回答要点**：
Tree Shaking 强依赖于 **ES6 静态模块结构（ESM，`import` / `export`）**。CommonJS 的 `require()` 是动态求值的，编译器无法在静态分析期安全判断哪些属性未被使用；必须引入 `@rollup/plugin-commonjs` 或优先选用官方提供 ESM 构建版本的库。

---

## 追问 2：Vite 在开发环境秒级启动的底层原理是什么？

**回答要点**：
基于 **浏览器原生 ESM + esbuild 预构建**。开发模式下 Vite 根本不对业务源码进行打包混淆，而是让浏览器直接请求原生 ES 模块，由 Vite 服务端拦截按需转译单文件，时间复杂度从 $O(N)$ 下降为 $O(1)$。"""
    },
    {
        "id": "fe-ai-070",
        "title": "请设计一个AI前端依赖管理策略，评估SDK更新与性能影响",
        "difficulty": "medium",
        "question": "请设计一个AI前端依赖管理策略，定期更新模型SDK、工具库，并评估兼容性与性能影响。",
        "answer": """### 一句话总结

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

- **对“重型库”保持克制与替代方案选型**：指出在前端工程中，避免为了简单的流式通信无脑引入几十 MB 的庞大 LangChain 全家桶；推荐使用原生的极简 Fetch Stream 或官方轻量 `@ai-sdk/react`（Vercel AI SDK），保持依赖极致纯粹。""",
        "followups": """## 追问 1：如果依赖树中某个第三方子依赖存在严重的高危安全漏洞（CVE），如何快速强制升级？

**回答要点**：
利用 pnpm 的 **`pnpm.overrides`** 配置项：在根目录 `package.json` 中指定强制覆写该深层子依赖的版本号（如 `"overrides": { "semver": "^7.5.4" }`），无需等待上层父包发布新版即可秒级修复。

---

## 追问 2：升级第三方 SDK 后，如何确保其没有偷偷引入全局变量污染或恶意抓包木马？

**回答要点**：
配置 `Socket.dev` 或通过 npm 的开源安全审计插件（`npm audit`）在 CI 阶段进行依赖行为静态分析，检测新引入的包是否包含可疑的安装后生命周期脚本（如 `postinstall` 恶意下载外部可执行文件）。"""
    },
    {
        "id": "fe-ai-071",
        "title": "如何用OpenAI Function Calling在前端实现AI工具调用？",
        "difficulty": "medium",
        "question": "如何用OpenAI Function Calling或Tools在前端实现AI工具调用（如计算器、搜索、数据库查询）？",
        "answer": """### 一句话总结

Function Calling（工具调用）的核心是**“前端向模型声明 JSON Schema 工具契约 + 模型决断调用参数 + 前端执行并将 Observation 结果回填”**。大模型本身不具备联网或运算能力，它仅根据用户意图输出结构化的 `{ name, arguments }`；前端的**工具分发中心（Tool Dispatcher）**匹配并执行本地代码，再发起二次请求将结果回传给模型输出最终结论。

---

### 详细回答

#### 1. 运作完整闭环四步走
1. **声明工具（Tools Definition）**：前端在请求头中传入工具清单及 JSON Schema 入参定义；
2. **模型决断（Decision）**：大模型判断是否需要调用工具，若需要，流式返回 `tool_calls` 片段；
3. **本地执行（Client Execution）**：前端拦截解析参数，调用真实 JS 函数（如获取经纬度、调用后端 API）；
4. **结果回填（Observation Feed）**：前端携带原始工具调用 ID 及返回的 JSON 结果再次请求大模型，由大模型总结润色输出给人看的话。

---

### 核心代码片段（极简记法）

```javascript
// 1. 声明工具定义 Schema
const tools = [{
  type: 'function',
  function: {
    name: 'calculate',
    description: '执行数学计算',
    parameters: {
      type: 'object',
      properties: { expression: { type: 'string' } },
      required: ['expression']
    }
  }
}];

// 2. 本地执行工具与回填
async function runTool(toolCall) {
  const { name, arguments: argsJson } = toolCall.function;
  const args = JSON.parse(argsJson);
  if (name === 'calculate') {
    return eval(args.expression); // 简写示意，生产应使用安全计算引擎
  }
}
```

---

### 面试加分项

- **流式参数拼接（Incremental JSON Parsing）**：大模型返回 `arguments` 是以流式字符串碎片逐步推过来的（如 `{"expr"` -> `": "1+1"` -> `"}"`）。前端在流式生成期间可以通过 `partial-json` 进行容错渐进式解析，提前在 UI 呈现“正在计算 1+1...”加载态。""",
        "followups": """## 追问 1：前端如何防止大模型输出恶意代码参数并在客户端执行破坏性操作？

**回答要点**：
1. 严禁使用未加保护的 `eval()` 或 `new Function()` 执行模型代码；
2. 涉及代码执行的工具必须在受限的 Web Worker 或独立的沙箱 iframe 中执行；
3. 高危操作必须强制弹出人工审批确认弹窗。

---

## 追问 2：如果大模型死循环连续多次调用同一个工具，怎么熔断？

**回答要点**：
前端在 Agent 循环中维护调用计数器与上下文深拷贝深度限制（如最大调用步数限制为 5 步）；一旦超限，强制切断工具分支，强行让模型在当前已有数据基础上给出最终回答。"""
    },
    {
        "id": "fe-ai-072",
        "title": "请设计一个模型性能监控面板实时展示耗时、成功率与成本",
        "difficulty": "medium",
        "question": "请设计一个模型性能监控面板，实时展示各模型的响应时间、成功率、Token消耗与成本。",
        "answer": """### 一句话总结

该面板采用**“指标采集探针（Metrics Probe） + 时间序列聚合 + ECharts / Tremor 可视化仪表盘”**。采集各模型的 TTFT 首字延迟、P95/P99 响应耗时、429/500 错误率以及 Prompt/Completion 实际消耗的 Token 数量；前端根据不同模型官方单价矩阵实时折算为美元/人民币成本，辅助工程团队对模型进行性价比选型与限流治理。

---

### 详细回答

#### 1. 核心四大维度的度量指标
- **吞吐与延迟**：
  - 首字延迟（TTFT，Time To First Token）；
  - 全文生成总耗时；
  - P95 / P99 极端长尾延迟分布；
- **稳定性**：
  - 接口成功率（`200 OK` 比例）；
  - 429 限流频率、504 网关超时频率；
- **资源与成本**：
  - 输入/输出 Token 累计用量；
  - 动态计费计算器：$\text{Cost} = \text{Tokens}_{\text{in}} \times P_{\text{in}} + \text{Tokens}_{\text{out}} \times P_{\text{out}}$。

#### 2. 前端面板交互与呈现
- **折线图（Time Series）**：实时展示过去 1 小时各模型的延迟波动曲线；
- **饼图/环形图**：展示团队各业务线对不同模型（Claude 3.5 vs GPT-4o vs DeepSeek）的调用量占比；
- **异常警报高亮**：若某模型近 5 分钟错误率超过 5%，面板卡片亮起红色呼吸告警，并展示“建议一键熔断切换为备选模型”操作开关。

---

### 核心代码片段（极简记法）

```javascript
// 计算各模型实时折算费用
const PRICE_PER_1K = {
  'gpt-4o': { prompt: 0.005, completion: 0.015 },
  'deepseek-chat': { prompt: 0.0001, completion: 0.0002 }
};

function calculateCost(model, promptTokens, completionTokens) {
  const p = PRICE_PER_1K[model];
  if (!p) return 0;
  return (promptTokens / 1000) * p.prompt + (completionTokens / 1000) * p.completion;
}
```

---

### 面试加分项

- **异常告警通知联动（Webhook）**：面板不仅能看，还能设置阈值规则（如 P99 超过 15 秒）。一旦触发，由前端通过飞书/钉钉 Webhook 自动发送群告警，实现工程监控闭环。""",
        "followups": """## 追问 1：监控面板自身的数据拉取会不会高频请求拖垮后台？

**回答要点**：
采用“时间切片聚合与降采样”：后端数据库（如 Prometheus 或 ClickHouse）预先将秒级数据聚合成 1 分钟、5 分钟粒度的统计桶（Buckets）；前端每 10~30 秒定时轮询或建立单个 SSE 长连接推流，数据体积仅几 KB。

---

## 追问 2：多租户场景下，如何防止租户 A 看到租户 B 的模型调用消耗数据？

**回答要点**：
基于租户 ID 进行严格的数据行级权限隔离（Row-Level Security）。前端所有请求头必须携带经由后端校验的 Tenant JWT，接口仅返回当前租户所属范围内的聚合指标数据。"""
    },
    {
        "id": "fe-ai-073",
        "title": "如何用LangChain.js在前端构建AI链串联Prompt、模型与工具？",
        "difficulty": "medium",
        "question": "如何用LangChain.js在前端构建AI链（Chain），串联多个Prompt、模型调用、工具执行？",
        "answer": """### 一句话总结

LangChain.js 核心基于 **LCEL（LangChain 表达式语言）与管道操作符 `.pipe()`**。将 `PromptTemplate`（模板插值）、`ChatModel`（模型调用抽象）与 `OutputParser`（输出解析器）像 UNIX 管道一样声明式串联成 Chain；统一支持流式推流（`.stream()`）、异步调用（`.invoke()`）与中途取消，使复杂的多步工作流逻辑高度模块化。

---

### 详细回答

#### 1. 为什么不用纯手写 Fetch 拼接？
- 当工作流包含“用户输入 -> 生成检索词 -> 检索知识库 -> 组装上下文 -> 模型总结 -> 结构化提取 JSON”多步时；
- 纯手写代码会变成深度嵌套的 Promise 回调地狱；
- LangChain 的 LCEL 提供统一的输入输出接口规范（Runnable Interface）。

#### 2. LCEL 声明式链的核心组成
- **PromptTemplate**：定义带占位符的模板；
- **ChatModel**：统一的模型 Provider 抽象（`new ChatOpenAI()`）；
- **OutputParser**：将模型返回的原始 Message 提取并解析为目标对象（如 `StringOutputParser`、`JsonOutputParser`）。

---

### 核心代码片段（极简记法）

```javascript
import { ChatOpenAI } from '@langchain/openai';
import { PromptTemplate } from '@langchain/core/prompts';
import { StringOutputParser } from '@langchain/core/output_parsers';

// 构建 LCEL 链：Prompt | Model | Parser
const prompt = PromptTemplate.fromTemplate('你是一个专家，请用一句话解释{topic}');
const model = new ChatOpenAI({ modelName: 'gpt-4o', temperature: 0.3 });
const chain = prompt.pipe(model).pipe(new StringOutputParser());

// 流式输出消费
const stream = await chain.stream({ topic: '前端微架构' });
for await (const chunk of stream) {
  process.stdout.write(chunk);
}
```

---

### 面试加分项

- **对前端引入 LangChain.js 的体积辩证思考**：指出在前端生产环境中，LangChain.js 依赖层级深、打包体积偏大。对于简单的单步或两步对话，**优先推荐使用原生 Fetch 或极致轻量的 Vercel AI SDK（`@ai-sdk`）**；仅在需要重度复用已有复杂 Agent 逻辑且体积不受限的桌面端/内部工具中选用 LangChain。""",
        "followups": """## 追问 1：在执行 LCEL 链的过程中，如何实现取消正在运行的流式生成？

**回答要点**：
在调用 `.invoke()` 或 `.stream()` 时，第二个可选配置参数传入包含 `signal` 的对象：
`await chain.stream({ topic: '...' }, { signal: abortController.signal })`，即可直接中断链路中的底层网络请求。

---

## 追问 2：链中的某个中间步骤（如知识库检索）如果抛错，整条链如何容错？

**回答要点**：
使用 LangChain 提供的 `.withFallbacks([fallbackChain])` 方法声明备选链，当主链中的节点执行崩溃时自动无缝降级到备选链继续执行。"""
    },
    {
        "id": "fe-ai-074",
        "title": "如何实现大模型调用的请求合并以提升吞吐并降低成本？",
        "difficulty": "hard",
        "question": "如何实现模型调用的“请求合并”，将多个用户的相似问题批量发送，提升吞吐并降低成本？",
        "answer": """### 一句话总结

请求合并采用**“微批处理队列（Micro-batching / DataLoader 模式）结合滑动时间窗口”**。前端或 BFF 中间层在收到零散的模型调用请求时，不立即发起网络传输，而是在微时间窗口（如 50ms）内将其积聚为一个批次，打包为单个 Batch 请求合并喂给大模型或向量模型，计算完毕后拆解回发给各自调用者，大幅提升并发吞吐量并均摊网络握手开销。

---

### 详细回答

#### 1. 适用场景：什么请求能合并？什么不能合并？
- **不能合并**：交互式实时流式多轮对话（用户等待极敏感，强依赖单人上下文）；
- **极度适合合并（吞吐敏感型）**：
  - 批量文本向量化（Batch Embeddings）；
  - 批量审核过滤（Batch Content Moderation）；
  - 多个小模块的轻量分类判断（如“判断这 5 个句子的情感倾向”）。

#### 2. 微批处理核心算法机制
1. **收集窗口**：利用 `setTimeout` 延迟 50ms，收集期间所有进入队列的单个任务 Promise；
2. **容量阈值**：若在 50ms 内收集数量达到最大容量（如 20 条），提前触发立即发车；
3. **单请求批量化**：调用 `openai.embeddings.create({ input: textsArray })`；
4. **结果派发**：根据原始序号将结果分别 resolve 给对应的待决 Promise。

---

### 核心代码片段（极简记法）

```javascript
class BatchEmbeddingQueue {
  constructor(batchSize = 10, delayMs = 50) {
    this.batchSize = batchSize;
    this.delayMs = delayMs;
    this.queue = [];
    this.timer = null;
  }

  add(text) {
    return new Promise((resolve, reject) => {
      this.queue.push({ text, resolve, reject });
      if (this.queue.length >= this.batchSize) this.flush();
      else if (!this.timer) this.timer = setTimeout(() => this.flush(), this.delayMs);
    });
  }

  async flush() {
    clearTimeout(this.timer);
    this.timer = null;
    const batch = this.queue.splice(0, this.batchSize);
    if (!batch.length) return;

    try {
      const results = await callBatchAPI(batch.map(b => b.text));
      batch.forEach((item, i) => item.resolve(results[i]));
    } catch (err) {
      batch.forEach(item => item.reject(err));
    }
  }
}
```

---

### 面试加分项

- **对 Token 成本的节省机制认知**：指出请求合并除了节省 HTTP 连接建立开销外，在使用大模型批量处理相同前置背景的问题时，能充分命中现代大模型推理引擎的 **Prefix Caching（前缀 KV 缓存共享）**，从而享受官方高达 50%~80% 的输入 Token 计费折扣。""",
        "followups": """## 追问 1：如果批次中的某一个请求由于特殊字符导致整体报错，如何避免影响整批的其他正常请求？

**回答要点**：
批次报错后启动二分降级重试（Bisection Retry）：将该批次切分为两个小批次分别重发；最终定位出恶意的单个畸形请求单独抛错，确保其他正常请求顺利成功。

---

## 追问 2：时间窗口（delayMs）设置多少最合适？

**回答要点**：
取决于业务 SLA。在纯后台异步分析场景可设为 100~300ms 以实现高批处理密度；在需要即时响应的交互式前端场景，通常设置为 16~50ms，在人类不可感知的极小延迟内实现最大化合并。"""
    },
    {
        "id": "fe-ai-075",
        "title": "如何用WebSocket实现双向流式通信支持模型推送与主动中断？",
        "difficulty": "medium",
        "question": "如何用WebSocket实现双向流式通信，支持AI模型主动推送进度更新、中断信号、工具调用请求？",
        "answer": """### 一句话总结

WebSocket 提供**原生全双工（Full-Duplex）单 TCP 管道**。在客户端建立标准协议帧通道，**下行链路**接收大模型的逐字流式 Chunk、后台异步进度推送与人机协同事件；**上行链路**可随时在流式生成中途无延迟发送中断信令（`STOP_GENERATION`）或即时追加补充要求，彻底避免 SSE 单向连接只能靠重建 HTTP 请求交互的笨拙限制。

---

### 详细回答

#### 1. 为什么全双工在复杂 AI Agent 中比 SSE 更有优势？
- **SSE 的局限**：纯单向从服务端推流到客户端；若客户端想要在模型生成途中通知“不要继续写了，改写这段”，必须另开一个 HTTP POST 请求发送中断通知，有额外的网络往返延迟；
- **WebSocket 优势**：同一个连接上双向自由交流，可以在接收 Chunk 的同时即时发送控制信号，且支持服务端主动向前端发起工具确认求助。

#### 2. 双向消息协议设计
- 客户端到服务端（Client -> Server）：
  - `{ type: 'PROMPT', payload: { text } }`；
  - `{ type: 'INTERRUPT' }`（即时终止）；
  - `{ type: 'TOOL_CONFIRM', toolId: 'pay', approved: true }`；
- 服务端到客户端（Server -> Client）：
  - `{ type: 'CHUNK', delta: '...' }`；
  - `{ type: 'AGENT_STATUS', step: 'searching_web' }`；
  - `{ type: 'DONE' }`。

---

### 核心代码片段（极简记法）

```javascript
const ws = new WebSocket('wss://api.ai.com/v1/chat');

// 1. 随时随刻发送即时中断信令
function stopGeneration() {
  ws.send(JSON.stringify({ action: 'INTERRUPT' }));
}

// 2. 统一分发各类双向事件
ws.onmessage = (event) => {
  const { type, payload } = JSON.parse(event.data);
  switch (type) {
    case 'CHUNK': renderDelta(payload.text); break;
    case 'AGENT_STATUS': updateProgressUI(payload.status); break;
    case 'DONE': finishChat(); break;
  }
};
```

---

### 面试加分项

- **心跳保活与自动重连（Heartbeat & Exponential Backoff）**：WebSocket 极易被途经的路由器或负载均衡器因空闲超时静默断开。客户端必须每 30 秒发送一次 `{ type: 'ping' }` 保活包，断线后结合带随机抖动的指数退避算法自动拉起重连。""",
        "followups": """## 追问 1：既然 WebSocket 功能这么全面，为什么绝大多数 AI 聊天（如 ChatGPT 官网）首选还是 SSE？

**回答要点**：
1. **运维与架构成本**：SSE 基于标准 HTTP，天然兼容现有的 CDN 缓存、代理鉴权、负载均衡与 HTTP/2 多路复用，对服务器状态无强长连接绑定；
2. **断网重连优势**：SSE 协议原生支持 `Last-Event-ID` 自动重连；
3. 对于普通“一问一答”场景，SSE 的架构复杂度远低于 WebSocket。

---

## 追问 2：浏览器关闭页面时，WebSocket 能确保把最后一条断开信令发出去吗？

**回答要点**：
不一定可靠。
在 `beforeunload` 时调用 `ws.send()`，由于浏览器进程即将被强制杀死，TCP 缓冲区可能未来得及刷新。高可靠场景需配合在 `pagehide` 中调用 `navigator.sendBeacon()` 作为保底上报。"""
    },
    {
        "id": "fe-ai-076",
        "title": "如何用Server-Sent Events实现模型输出的进度条与部分结果预览？",
        "difficulty": "medium",
        "question": "如何用Server-Sent Events实现模型输出的“进度条”与“部分结果预览”？",
        "answer": """### 一句话总结

利用 SSE 原生支持的 **多事件类型分发（Named Events，`event: <name>`）** 特性。服务端在同一个 HTTP 连接中推送不同类型的事件帧（如 `event: progress` 推送百分比与当前步骤说明，`event: preview` 推送部分草稿 AST，`event: chunk` 推送正式文本）；前端通过 `addEventListener` 按事件类型分别更新进度条组件与预览画布，实现层次分明的多维感知。

---

### 详细回答

#### 1. 为什么不用纯 data 混合解析？
- 如果把进度、状态、文本全塞在 `data: {"type": "..."}` 里面，客户端必须每次都进行 JSON 解析，且破坏了协议分层；
- SSE 标准规范天然原生支持针对事件类型进行订阅。

#### 2. SSE 多事件流线格式规范
```http
event: progress
data: {"percent": 40, "message": "正在检索企业本地向量知识库..."}

event: chunk
data: {"delta": "根据知识库检索结果，"}

event: preview_image
data: {"lowResUrl": "data:image/webp;base64,..."}

event: done
data: {}
```

#### 3. 前端消费与多组件解耦驱动
- 进度条组件只订阅 `progress` 事件；
- 文本渲染组件只订阅 `chunk` 事件；
- 图片预览卡片只订阅 `preview_image` 事件；
- 各组件数据流清晰互不干扰。

---

### 核心代码片段（极简记法）

```javascript
// 基于 fetch ReadableStream 分发具名事件
function parseSSEEvent(eventBlock, emitter) {
  const matchEvent = eventBlock.match(/event:\s*(\w+)/);
  const matchData = eventBlock.match(/data:\s*(.+)/);

  const eventName = matchEvent ? matchEvent[1] : 'message';
  const data = matchData ? JSON.parse(matchData[1]) : {};

  emitter.emit(eventName, data); // 对应触发 progress / chunk / preview
}
```

---

### 面试加分项

- **进度条平滑动画（Spring Animation）**：服务端下发的进度数据通常是阶梯式的（如从 20% 突跳到 60%）。前端进度条应使用 CSS `transition: width 0.5s ease-out` 或弹簧插值函数，让进度条优雅匀速流动，消除视觉突兀跳跃感。""",
        "followups": """## 追问 1：使用 fetch 读取 ReadableStream 时，如何区分多个不同名称的 event？

**回答要点**：
原生的 `EventSource` 会自动根据 `event: foo` 触发 `source.addEventListener('foo')`；
若使用自研的 `fetch` 流解析器，需自行编写基于空行 `\n\n` 分割的状态机，逐块提取 `event:` 行作为事件名进行回调分发。

---

## 追问 2：若中间丢包导致 80% 的进度事件丢失直接收到了 100%，进度条怎么表现？

**回答要点**：
直接快速过渡到 100% 即可，不能倒退也不能死等；并且在收到 `done` 事件时，强制无条件将进度条动画推进至 100% 并在 300ms 后淡出隐藏。"""
    },
    {
        "id": "fe-ai-077",
        "title": "如何用Web Workers并行调用多个模型实现模型投票与结果融合？",
        "difficulty": "hard",
        "question": "如何用Web Workers并行调用多个模型，实现“模型投票”或“结果融合”？",
        "answer": """### 一句话总结

该架构采用**“主线程调度中枢 + 多 Web Worker 独立沙箱推理 + 多数表决/评审融合仲裁机（Consensus Arbiter）”**。将请求同时派发给三个运行不同轻量模型或调用不同 API 的 Worker 并发生成；在主线程采用**文本相似度投票（Majority Voting）**或将各家结果合成提示词由第四个评判模型做最终裁决，极大压低单模型的幻觉率并产出最优答案。

---

### 详细回答

#### 1. 为什么需要“模型投票（Model Ensemble）”？
- 单个 AI 模型无论多强大，都存在固有的盲区与事实幻觉；
- 在高可靠性要求场景（如法律条款校验、复杂数学计算、医疗常识初筛），让多个模型独立作答并交叉比对，能显著提高输出的正确率。

#### 2. Worker 并发与主线程架构
- **Worker 池划分**：
  - `Worker 1`：运行轻量本地 Qwen 模型；
  - `Worker 2`：请求 DeepSeek 接口；
  - `Worker 3`：请求 Claude 接口；
- **并发触发**：`Promise.allSettled([w1.run(), w2.run(), w3.run()])`；
- **仲裁策略（Arbitration）**：
  - 若为分类/单选题：直接统计众数（Mode）；
  - 若为长文本开放题：使用 LCS（最长公共子序列）提取各模型的一致性事实，剔除孤立差异点。

---

### 核心代码片段（极简记法）

```javascript
async function ensembleQuery(prompt) {
  // 1. 并行派发给三个独立模型 Worker
  const results = await Promise.all([
    callModelWorker('model-a.js', prompt),
    callModelWorker('model-b.js', prompt),
    callModelWorker('model-c.js', prompt)
  ]);

  // 2. 仲裁融合（以文本相似度多数票决为例）
  const finalAnswer = arbitrateBestAnswer(results);
  return finalAnswer;
}
```

---

### 面试加分项

- **超时淘汰机制（Straggler Mitigation）**：多个模型并发时，必然有一个响应最慢（木桶效应）。配置动态阈值：只要前两个模型已返回且耗时已达设定上限，立即忽略最慢的长尾模型，直接基于前两个结果进行融合，防止整体延迟被个别慢模型拖死。""",
        "followups": """## 追问 1：多个 Web Worker 同时在前端做复杂的模型计算，会不会导致手机发烫或电池快速消耗？

**回答要点**：
会！
密集并发计算会占满所有 CPU 核心。在移动端必须做设备电量与散热探测（`navigator.getBattery?.()`）；若处于低电量模式，强制降级为单模型云端串行调用，禁止本地多 Worker 并发轰炸。

---

## 追问 2：模型投票的结果若各不相同（A、B、C 结果各得一票平局），如何决策？

**回答要点**：
基于“模型置信度加权（Weighted Confidence Voting）”：根据历史基准评测给不同模型分配固定权重（如 Claude 0.4、GPT 0.4、小模型 0.2）；平局时以权重最高的核心模型为主，或将三者的回答并排输出给用户自主挑选。"""
    }
]

for item in DATA:
    qdir = os.path.join(QUESTIONS_DIR, item['id'])
    os.makedirs(qdir, exist_ok=True)
    with open(os.path.join(qdir, 'question.md'), 'w', encoding='utf-8') as f:
        f.write(f"# {item['title']}\n\n{item['question']}\n")
    with open(os.path.join(qdir, 'answer.md'), 'w', encoding='utf-8') as f:
        f.write(item['answer'].strip() + '\n')
    with open(os.path.join(qdir, 'followups.md'), 'w', encoding='utf-8') as f:
        f.write(item['followups'].strip() + '\n')

print(f"Generated {len(DATA)} questions successfully (fe-ai-061 ~ fe-ai-077)!")
