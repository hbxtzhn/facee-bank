import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUESTIONS_DIR = os.path.join(BASE_DIR, 'questions')

DATA = [
    {
        "id": "fe-scenario-001",
        "title": "如何判断用户设备？",
        "difficulty": "easy",
        "question": "如何判断用户设备（PC端、移动端、平板、iOS、Android等）？有哪些方案和最佳实践？",
        "answer": """### 一句话总结

判断用户设备首选**“用户代理（User-Agent / Client Hints） + 屏幕与交互特征（Media Query / Pointer / Touch）”**的组合策略。对于服务端渲染（SSR）路由跳转，通过请求头中的 `User-Agent` 或现代 `sec-ch-ua` 进行快速粗筛；对于前端样式与交互适配，坚决以 **CSS 媒体查询与触摸特性探测（`window.matchMedia`）** 为主，杜绝仅靠 UA 字符串导致新设备误判。

---

### 详细回答

#### 1. 方案一：User-Agent 字符串探测（服务端分流与兼容）
- 通过正则匹配 `navigator.userAgent` 关键特征词：
  - iOS：`/(iPhone|iPad|iPod)/i.test(ua)`；
  - Android：`/Android/i.test(ua)`；
  - Mobile 通用：`/Mobi|Android|iPhone|iPad/i.test(ua)`。
- **缺点**：UA 极易被用户或浏览器伪装篡改；新版 Chrome 正在逐步冻结并缩减 UA 字符串（User-Agent Reduction）。

#### 2. 方案二：现代 Client Hints API（最新标准）
- 现代浏览器支持 `navigator.userAgentData`：
  ```javascript
  if (navigator.userAgentData) {
    const isMobile = navigator.userAgentData.mobile;
    const platform = navigator.userAgentData.platform;
  }
  ```

#### 3. 方案三：特性探测（交互与屏幕）—— 前端推荐
- 不关心具体是哪个牌子的手机，只关心**“是否有触摸屏”与“屏幕宽度”**：
  ```javascript
  const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  const isSmallScreen = window.matchMedia('(max-width: 768px)').matches;
  ```

---

### 核心代码片段（极简记法）

```javascript
// 综合判断设备类型
function getDeviceType() {
  const ua = navigator.userAgent;
  if (/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua)) return 'tablet';
  if (/Mobile|iP(hone|od)|Android|BlackBerry|IEMobile|Kindle|NetFront|Silk-Accelerated/i.test(ua)) return 'mobile';
  return 'desktop';
}

// 基于特性判断是否支持触摸交互
const canTouch = window.matchMedia('(pointer: coarse)').matches;
```

---

### 面试加分项

- **iPadOS 桌面模式的巨坑**：从 iPadOS 13 开始，Safari 默认将 UA 伪装成 macOS 桌面版（包含 `Macintosh; Intel Mac OS X` 且无 `iPad` 标识）。精准识别 iPad 必须配合特性检查：
  `const isIPad = /Macintosh/i.test(ua) && navigator.maxTouchPoints > 1;`。""",
        "followups": """## 追问 1：响应式布局（Responsive）和按设备拆分不同域名（PC 与 H5）各有什么优缺点？如何选择？

**回答要点**：
- **响应式（同一套代码）**：适合官网、展示页、业务逻辑轻量的页面；维护成本低，SEO 友好；但在复杂业务下会包含多余的 PC/移动端互斥代码，包体积大。
- **分域跳转（PC web 与 独立 H5）**：适合电商、大型管理台等交互差异极大的复杂业务；各自轻装上阵、性能极致，但需额外维护两套工程及跨端分流跳转逻辑。

---

## 追问 2：如何在服务端（SSR / Node.js）优雅判断并实现无白屏重定向？

**回答要点**：
在 Nginx 或 Node BFF 层读取 HTTP `User-Agent` 请求头，在返回 HTML 之前直接执行 302 重定向到移动端页面，杜绝前端加载完 JS 后才通过 `window.location.href` 跳转造成的严重二次白屏闪烁。"""
    },
    {
        "id": "fe-scenario-002",
        "title": "如何将Git多次提交压缩成一次提交？",
        "difficulty": "easy",
        "question": "在前端日常开发与分支合并时，如何将多次冗余的小提交压缩（Squash）成一次规范提交？",
        "answer": """### 一句话总结

最常用的方案是 **`git rebase -i HEAD~N`（交互式变基，将后续提交标记为 `squash` 或 `s`）**；或使用 **`git reset --soft <base-commit>` 一键将所有改动撤回暂存区后统一 `git commit`**；在向主干合并 PR 时，也可直接通过 GitHub/GitLab 网页端勾选 **Squash and merge** 实现一键压缩。

---

### 详细回答

#### 1. 方案一：交互式变基（git rebase -i，最经典可控）
- 执行命令查看最近 3 次提交：`git rebase -i HEAD~3`；
- 在弹出的 Vim 编辑器中，保留第一个提交为 `pick`，将其余后续提交的指令改为 `squash`（或简写为 `s`）：
  ```text
  pick a1b2c3d feat: 完成用户登录组件骨架
  squash e4f5g6h fix: 修复输入框样式
  squash i7j8k9l style: 调整按钮边距
  ```
- 保存退出后，编辑最终合并后的单一 Commit Message 并保存。

#### 2. 方案二：git reset --soft（极速无脑方案）
- 将 HEAD 指针重置回最初的分支基线，但**完全保留工作区与暂存区的所有代码变更**：
  ```bash
  git reset --soft origin/main
  git commit -m "feat: 完成用户登录全套功能与样式规范"
  ```

#### 3. 方案三：git merge --squash（合并时压缩）
- 在 master 分支执行：`git merge --squash feature-branch`，将特性分支的所有提交打平为一个未提交的改动，手动 commit 即可。

---

### 核心代码片段（极简记法）

```bash
# 极速压缩最近 3 次 commit
git reset --soft HEAD~3
git commit -m "feat: 规范合并后的完整提交说明"
```

---

### 面试加分项

- **黄金安全法则（Public Branch Rule）**：压缩提交本质是在**改写 Git 提交历史**。绝对不要在已经推送到公共主干分支（如 `main` / `master`）的代码上执行 `rebase` 或 `reset` 并强推（`--force`），这会导致协同其他开发者的本地历史全部错乱！只允许在个人的私有特性分支（Feature Branch）上使用。""",
        "followups": """## 追问 1：如果变基过程中遇到冲突（Conflict），该如何解决？

**回答要点**：
手动打开冲突文件解决冲突并保存；执行 `git add <file>` 标记已解决；然后运行 `git rebase --continue` 继续变基流程；若想完全放弃此次变基恢复原样，运行 `git rebase --abort`。

---

## 追问 2：git reset --soft 和 git reset --mixed 以及 --hard 的核心区别是什么？

**回答要点**：
- `--soft`：仅移动 HEAD 指针，暂存区和工作区代码全保留；
- `--mixed`（默认）：移动 HEAD 指针并清空暂存区，工作区代码仍保留（变为未 add 状态）；
- `--hard`：彻底丢弃暂存区和工作区的所有改动，代码永久丢失，极度危险。"""
    },
    {
        "id": "fe-scenario-003",
        "title": "介绍下navigator.sendBeacon方法",
        "difficulty": "medium",
        "question": "介绍下navigator.sendBeacon方法？它的使用场景、优缺点以及与传统XHR/Fetch的区别是什么？",
        "answer": """### 一句话总结

`navigator.sendBeacon` 是浏览器专门为**“页面卸载/跳出时异步可靠上报数据（如埋点、停留时长、报错日志）”**设计的原生 API。它以 **POST** 方式异步排队发送请求，**完全脱离当前页面的生命周期限制**，即使页面被瞬间关闭，浏览器后台也会保证数据包可靠送达服务器，且绝不阻塞页面卸载与新页面导航。

---

### 详细回答

#### 1. 传统页面离开上报方式的致命缺陷
- **同步 XHR（`xhr.open(..., false)`）**：会严重卡死浏览器主线程，用户感知到明显的关闭卡顿，现代浏览器已在 unload 事件中将其全面废弃；
- **普通异步 fetch / 异步 XHR**：页面销毁时，浏览器为释放资源会**直接强制掐断未决的网络连接**，导致高达 30%~50% 的离开埋点丢失；
- **同步构造空图片（`new Image().src = ...`）**：在旧版浏览器中能短暂卡住页面，但在新版 Chrome 中同样会被强制取消。

#### 2. sendBeacon 的核心优势
- **后台脱钩排队**：请求交由浏览器底层进程托管，页面无论多快关闭都不影响请求发送；
- **非阻塞性能**：完全异步执行，对用户感知零卡顿，不影响跳出跳转流畅度；
- **API 极简**：返回布尔值 `true` / `false` 表示浏览器是否成功将任务塞入发送队列。

#### 3. 局限性与避坑点
- **只能发 POST 请求**；
- **无法读取响应结果**：无法获取服务器返回的 Response 数据（纯单向投递）；
- **Payload 体积受限**：浏览器对排队中的 beacon 数据施加了 64KB 的配额上限，超出直接返回 `false` 拒绝排队。

---

### 核心代码片段（极简记法）

```javascript
// 在 visibilitychange 或 pagehide 事件中可靠上报
window.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'hidden') {
    const data = JSON.stringify({ event: 'page_exit', duration: 42 });
    const blob = new Blob([data], { type: 'application/json' });
    navigator.sendBeacon('/api/analytics', blob);
  }
});
```

---

### 面试加分项

- **fetch keepalive 替代方案**：现代 Fetch API 提供了 `{ keepalive: true }` 配置（如 `fetch('/api', { method: 'POST', body, keepalive: true })`），其行为与 sendBeacon 完全一致，但支持自定义复杂的请求头并能发送更多 HTTP Method，是目前最新的标准实践。""",
        "followups": """## 追问 1：监听 sendBeacon 时，为什么推荐使用 visibilitychange 而不是 unload / beforeunload？

**回答要点**：
在移动端浏览器（尤其是 iOS Safari）中，当用户切换应用或划掉后台时，`unload` 和 `beforeunload` **根本不会触发**；W3C 官方明确建议将 `visibilitychange`（结合 `document.visibilityState === 'hidden'`）作为页面生命周期结束的最可靠唯一点。

---

## 追问 2：如果服务端接口只支持 application/json，sendBeacon 默认是 text/plain 怎么办？

**回答要点**：
将数据包装为指定 MIME 类型的 `Blob` 对象：
`const blob = new Blob([jsonString], { type: 'application/json' });`
再传入 `navigator.sendBeacon(url, blob)`，浏览器请求头会自动带上 `Content-Type: application/json`。"""
    },
    {
        "id": "fe-scenario-004",
        "title": "滚动跟随导航（电梯导航）该如何实现？",
        "difficulty": "medium",
        "question": "滚动跟随导航（电梯导航 / 楼层导航）该如何实现？有哪些实现方式和性能优化点？",
        "answer": """### 一句话总结

电梯导航包含**“双向联动（滚动页面高亮导航菜单 + 点击菜单平滑滚动至对应楼层）”**。推荐采用 **`IntersectionObserver`（交叉观察器）替代传统滚动事件监听**，零主线程监听开销实现高精度的视口楼层探测；点击时通过 `element.scrollIntoView({ behavior: 'smooth' })` 驱动平滑过渡，并在过渡期间加锁防止滚动监听相互干扰。

---

### 详细回答

#### 1. 传统方案的痛点（scroll 事件）
- 传统做法：在 `window.onscroll` 中遍历每个楼层的 `offsetTop`，计算与 `scrollTop` 的相对位置；
- **痛点**：高频触发滚动事件，频繁读取 `offsetTop` 会导致**强制同步布局（Forced Synchronous Layout / 页面重排）**，滚动出现明显掉帧。

#### 2. 现代最优解：IntersectionObserver
- 创建一个观察器，配置 `rootMargin`（例如 `"-30% 0px -70% 0px"` 将判定线收拢在屏幕上部 1/3 区域）；
- 楼层只要触碰到该观察线，浏览器异步通知回调，自动获取当前处于活跃状态的楼层 ID，设置对应导航 Tab 高亮。

#### 3. 点击导航跳动防打架（加锁机制）
- 用户点击导航菜单 Tab 3 时，页面会平滑向下飞滚；
- 飞滚过程中会途径楼层 1 和楼层 2，若未加锁，导航栏高亮会快速在 1、2、3 之间乱跳；
- **解决**：点击时设置标志位 `isClickScrolling = true`，滚动动画结束或延迟 500ms 后再恢复滚动联动。

---

### 核心代码片段（极简记法）

```javascript
// 1. 高性能视口监听高亮
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      setActiveNavId(entry.target.id); // 激活对应导航
    }
  });
}, { rootMargin: '-20% 0px -70% 0px' });

document.querySelectorAll('.floor-section').forEach(el => observer.observe(el));

// 2. 点击平滑跳转
function scrollToFloor(id) {
  document.getElementById(id).scrollIntoView({ behavior: 'smooth' });
}
```

---

### 面试加分项

- **吸顶效果的 CSS 纯声明式实现**：电梯导航菜单自身的粘性吸顶，直接使用纯 CSS `position: sticky; top: 0;` 即可，完全不需要任何 JS 监听高度动态切换 `fixed`，代码极简且性能极致。""",
        "followups": """## 追问 1：如果页面最底部最后一个楼层内容高度很矮（比如只有 200px），怎么滚它都无法到达视口顶部判定线，怎么让它高亮？

**回答要点**：
边界处理：当检测到滚动条已经触底（`scrollTop + clientHeight >= scrollHeight - 5`）时，强制无条件将最后一个导航菜单标记为高亮状态。

---

## 追问 2：CSS 的 scroll-behavior: smooth 在旧版浏览器兼容性不佳怎么办？

**回答要点**：
引入开源微型 Polyfill（如 `smoothscroll-polyfill`），或基于 `requestAnimationFrame` 自研结合缓动曲线（Easing function）的平滑位移动画函数。"""
    },
    {
        "id": "fe-scenario-005",
        "title": "退出浏览器之前，发送积压的埋点数据请求，该如何做？",
        "difficulty": "medium",
        "question": "退出浏览器之前，发送积压的埋点数据请求，该如何做？有哪些成熟可靠的兜底策略？",
        "answer": """### 一句话总结

核心采用**“`visibilitychange` 事件监听 + `navigator.sendBeacon`（或 `fetch keepalive`）后备通道 + 本地 IndexedDB 离线暂存”**。在页面切换为不可见（`hidden`）瞬间，将内存中积压的埋点队列批量通过 `sendBeacon` 脱机投递；若因断网发送失败，落盘存入 IndexedDB，待用户下次冷启动应用时自动读取补报。

---

### 详细回答

#### 1. 为什么不能等到 unload 阶段？
- 移动端划掉 App、按 Home 键切后台或锁屏时，**`unload` 和 `beforeunload` 不保证触发**；
- W3C 标准与各大浏览器推荐将 **`visibilitychange`（`document.visibilityState === 'hidden'`）** 作为保存状态与发送统计的黄金切入点。

#### 2. 可靠发送通道选型阶梯
- **首选**：`navigator.sendBeacon(url, data)`，请求由浏览器底层网络线程托管，不阻塞页面销毁；
- **备选**：`fetch(url, { method: 'POST', body: data, keepalive: true })`，功能更全面；
- **极端兜底（本地持久化）**：若离线断网，将积压数组序列化存入 `localStorage` 或 IndexedDB。

---

### 核心代码片段（极简记法）

```javascript
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'hidden' && eventQueue.length > 0) {
    const payload = JSON.stringify(eventQueue);
    const success = navigator.sendBeacon('/api/track', payload);
    if (success) {
      eventQueue.length = 0; // 清空积压队列
    } else {
      localStorage.setItem('OFFLINE_TRACK_LOGS', payload); // 失败落盘
    }
  }
});
```

---

### 面试加分项

- **冷启动回放机制**：应用入口初始化时，检查 `localStorage` 中是否存在上一次未发送成功的离线埋点数据。若有，补发请求并上报附带标记 `is_retroactive: true`，确保数据完整性达到 99.9% 以上。""",
        "followups": """## 追问 1：sendBeacon 一次性最多能发多大的数据包？

**回答要点**：
规范限制排队中的 Beacon 请求总大小不能超过 **64KB**。
因此埋点上报必须在日常做好定期定量批量发送（例如累积 20 条或每 5 秒发送一次），严禁把上百兆的大数据堆积到最后关头一次性上报。

---

## 追问 2：用户在离开页面时，如果想要弹出确认框提示“有未保存内容”，应该用什么事件？

**回答要点**：
必须使用原生的 `window.addEventListener('beforeunload', (e) => { e.preventDefault(); e.returnValue = ''; })`。浏览器会拦截并弹出原生的确认提示框，用户选择“留在此页”后页面不会关闭。"""
    },
    {
        "id": "fe-scenario-006",
        "title": "如何统计页面的Long Task（长任务）？",
        "difficulty": "medium",
        "question": "如何统计页面的long task（长任务）？它的定义标准是什么？如何上报与归因排查？",
        "answer": """### 一句话总结

长任务（Long Task）是指**在浏览器主线程上连续执行超过 50 毫秒的任何 JavaScript 任务**。统计标准是利用浏览器原生提供的 **`PerformanceObserver` 监听 `longtask` 条目类型**；通过采集长任务的耗时（`duration`）、发生起点（`startTime`）与归属容器（`attribution`），在上报监控平台后用于量化页面卡顿与计算 TBT（总阻塞时间）指标。

---

### 详细回答

#### 1. 为什么 50ms 是长任务的分水岭？
- 根据 Google RAIL 性能模型，人脑对 100ms 以内的交互无感知；
- 浏览器为了保证在用户点击或按键后能在 100ms 内给出视觉反馈，留给主线程响应交互的时间大约是 50ms；
- 若单个 JS 任务霸占主线程超过 50ms，用户的输入事件就会排队等待，引发明显掉帧卡顿。

#### 2. PerformanceObserver 核心采集
- 实例监听 `entryTypes: ['longtask']`；
- 每个 entry 返回字段：
  - `entry.duration`：阻塞主线程的总耗时（单位毫秒）；
  - `entry.startTime`：相对于 `timeOrigin` 的发生时间戳；
  - `entry.attribution`：指示长任务是来源于主页面还是某个特定的 `iframe`。

#### 3. 计算核心指标：TBT（Total Blocking Time）
- 每一个长任务超出 50ms 的部分被称为阻塞时间：$\text{BlockingTime} = \text{duration} - 50$；
- 在 FCP 到 TTI 之间所有长任务的阻塞时间累加和，即为衡量首屏流畅度的核心指标 TBT。

---

### 核心代码片段（极简记法）

```javascript
const observer = new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    console.warn(`检测到长任务！耗时: ${entry.duration.toFixed(2)}ms`);
    // 异步上报监控服务
    reportMetric('LONG_TASK', {
      duration: entry.duration,
      startTime: entry.startTime,
      name: entry.name
    });
  }
});

// 开始监听长任务
observer.observe({ entryTypes: ['longtask'] });
```

---

### 面试加分项

- **长任务定位到源码调用栈（Long Animation Frames API）**：`longtask` 无法获知具体的 JS 函数名。Chrome 123+ 推出了全新的 **LoAF（Long Animation Frames）API**（`entryTypes: ['long-animation-frame']`），能精准采集到具体是哪一个 JS 脚本文件、哪一行代码函数的执行造成了长任务，堪称前端卡顿治理神器。""",
        "followups": """## 追问 1：发现页面存在 200ms 的长任务，前端有哪些立竿见影的优化手段？

**回答要点**：
1. **时间切片（Time Slicing）**：用 `requestIdleCallback`、`MessageChannel` 或 `scheduler.yield()` 将大循环拆成小片段；
2. **多线程卸载**：把耗时的数据处理、复杂加解密移入 Web Worker；
3. **防抖节流**：避免高频事件触发连环重算。

---

## 追问 2：PerformanceObserver 监听时，如果长任务发生在 observer 初始化之前，能捕获到吗？

**回答要点**：
在配置项中开启 **`buffered: true`**：
`observer.observe({ type: 'longtask', buffered: true })`；
浏览器会将初始化之前已经在缓冲区里记录的历史长任务一并回放给回调函数。"""
    },
    {
        "id": "fe-scenario-007",
        "title": "PerformanceObserver如何测量页面性能？",
        "difficulty": "medium",
        "question": "PerformanceObserver如何测量页面性能？与传统performance.timing相比有哪些优势？",
        "answer": """### 一句话总结

`PerformanceObserver` 是现代浏览器标准的**“性能事件异步观察器”**。它废弃了旧版轮询查询 `performance.timing` 的被动模式，以**事件驱动（Event-driven）异步订阅性能时间线条目（`navigation`, `resource`, `paint`, `largest-contentful-paint`, `longtask` 等）**；不仅零轮询开销、不污染主线程，还能精准捕获 SPA 路由切换与动态加载资源的实时性能流水线。

---

### 详细回答

#### 1. 传统 `performance.timing` 的硬伤
- **静态快照**：只记录页面首次冷启动的单一时间点，SPA 单页应用后续的路由跳转完全无法体现；
- **主线程轮询开销**：必须写 `setInterval` 去轮询某些指标是否生成，极易阻塞主线程；
- **已被 W3C 标准全面废弃（Deprecated）**。

#### 2. PerformanceObserver 核心工作流
1. 实例化 `new PerformanceObserver(callback)`；
2. 调用 `observe({ type: '...', buffered: true })` 开启订阅；
3. 浏览器在特定性能事件发生时，异步批量回调传递条目列表；
4. 按需断开 `observer.disconnect()`。

#### 3. 常见监听类型清单
- `navigation`：DNS、TCP、TTFB、DOM 解析耗时；
- `paint`：FP（首次绘制）、FCP（首次内容绘制）；
- `largest-contentful-paint`：LCP 最大内容绘制；
- `first-input`：FID 首次输入延迟；
- `resource`：每一个图片、JS、CSS 资源的下载流水线。

---

### 核心代码片段（极简记法）

```javascript
// 异步捕获 FCP 与 LCP 指标
const observer = new PerformanceObserver((entryList) => {
  for (const entry of entryList.getEntries()) {
    if (entry.name === 'first-contentful-paint') {
      console.log('FCP 耗时:', entry.startTime);
    }
  }
});

// buffered: true 确保捕获已经发生过的事件
observer.observe({ type: 'paint', buffered: true });
```

---

### 面试加分项

- **`buffered: true` 的不可替代性**：如果监控 SDK 是异步延迟加载的，当 SDK 执行时，FP 和 FCP 早就发生完毕了。声明 `buffered: true` 会指示浏览器去自身的内部时间轴缓存区中提取并补发过去的性能条目，杜绝数据遗漏。""",
        "followups": """## 追问 1：PerformanceObserver 监听 resource 资源耗时时，跨域的 CDN 静态脚本拿不到详细的 TCP/DNS 时间，全是 0，为什么？

**回答要点**：
浏览器的安全隐私保护限制（Timing-Allow-Origin）。
若 CDN 响应头中未配置 `Timing-Allow-Origin: *`，浏览器出于安全原因会将资源请求细分的 redirect、DNS、TCP、SSL 等敏感网络耗时字段全部抹零，只暴露总时长。

---

## 追问 2：PerformanceObserver 本身会占用主线程性能吗？

**回答要点**：
开销极低。
浏览器底层会在 C++ 内核层异步排队收集指标，仅在每帧渲染间隙或空闲时批量触发一次 JS 回调，相比手动高频计算 `performance.getEntries()` 节约数倍 CPU。"""
    },
    {
        "id": "fe-scenario-008",
        "title": "移动端如何实现下拉滚动加载（顶部加载/下拉刷新）？",
        "difficulty": "medium",
        "question": "移动端如何实现下拉滚动加载（顶部加载/下拉刷新）？有哪些手势与视觉交互考量？",
        "answer": """### 一句话总结

下拉刷新采用**“触摸手势监听（touchstart/touchmove/touchend） + CSS 阻尼位移（Transform） + 异步请求完成弹性回弹”**。在容器处于顶部（`scrollTop === 0`）时捕获下划手势；通过对位移应用对数阻尼算法实现越拉越沉的跟手质感；释放后吸附在临界高度展示 Loading 动效，数据返回后平滑过渡归零。

---

### 详细回答

#### 1. 触发的前置条件判定
- 只有当滚动容器当前**处于最顶部（`el.scrollTop <= 0`）且手指是向下滑动时**才允许触发下拉动效；
- 若容器已滚至中间，必须放行浏览器原生滚动，严禁拦截。

#### 2. 阻尼手势算法（Damping Formula）
- 不能让手指拉动多少像素 DOM 就移动多少像素（无阻尼体验极差、像塑料玩具）；
- 真实物理阻尼位移公式：
  $$\Delta Y_{\text{actual}} = \Delta Y_{\text{touch}} \times \left(1 - \frac{\Delta Y_{\text{touch}}}{\text{MaxDistance} \times 2}\right)$$
  或者简易算法：$\Delta Y_{\text{actual}} = \Delta Y_{\text{touch}} \times 0.4$。

#### 3. 动画与回弹状态流转
- **拉动阶段**：更新 `transform: translateY(y px)`，不加 CSS 过渡动画（保持极致跟手）；
- **释放阶段**：
  - 若 $Y < \text{Threshold}$：添加 `transition: transform 0.3s`，瞬间弹回 0；
  - 若 $Y \ge \text{Threshold}$：吸附在 50px 处，展示菊花旋转动画，触发 `onRefresh()`；
  - 请求完成：重置为 0，隐藏 Loading。

---

### 核心代码片段（极简记法）

```javascript
let startY = 0;
let distance = 0;

container.addEventListener('touchstart', (e) => {
  if (container.scrollTop === 0) startY = e.touches[0].pageY;
});

container.addEventListener('touchmove', (e) => {
  const currentY = e.touches[0].pageY;
  if (currentY > startY && container.scrollTop === 0) {
    distance = (currentY - startY) * 0.4; // 阻尼系数
    header.style.transform = `translateY(${distance}px)`;
  }
});

container.addEventListener('touchend', async () => {
  if (distance > 50) {
    await fetchData(); // 刷新数据
  }
  header.style.transform = 'translateY(0)'; // 平滑回弹
});
```

---

### 面试加分项

- **CSS 原生方案（overscroll-behavior）**：在移动端容器上加上 `overscroll-behavior-y: contain;`，能彻底解决 iOS Safari 橡皮筋回弹导致的整个页面被带跑偏的恶劣滚动穿透 Bug。""",
        "followups": """## 追问 1：手指横向滑动轮播图时，容易误触发下拉刷新，怎么避免手势冲突？

**回答要点**：
在 `touchmove` 中计算 X 轴与 Y 轴的移动绝对值差量：
若 `Math.abs(deltaX) > Math.abs(deltaY)`，说明用户意图是横向滑动，立即放弃下拉刷新逻辑，完全交给横向手势处理。

---

## 追问 2：移动端使用 transform 位移实现下拉，如何利用 GPU 硬件加速？

**回答要点**：
使用 `transform: translate3d(0, y, 0)` 或在元素样式中声明 `will-change: transform`，强制提升为独立的 GPU 合成层（Compositing Layer），杜绝主线程重排，保持 60fps 丝滑。"""
    },
    {
        "id": "fe-scenario-009",
        "title": "如何判断页签是否为活跃状态？",
        "difficulty": "easy",
        "question": "如何判断页签是否为活跃状态（当前正在被用户查看）？有哪些应用场景？",
        "answer": """### 一句话总结

最标准可靠的原生 API 是 **Page Visibility API（监听 `visibilitychange` 事件结合 `document.visibilityState`）**。当值等于 `'visible'` 时代表页签处于激活可见状态，`'hidden'` 代表页签被切到后台、最小化或被遮挡；亦可辅助结合 `window.onfocus` 与 `window.onblur` 判断焦点切换。

---

### 详细回答

#### 1. Page Visibility API（标准方案）
- **`document.hidden`**：只读布尔值；
- **`document.visibilityState`**：
  - `'visible'`：页面在当前屏幕上至少部分可见；
  - `'hidden'`：页面完全不可见（用户切换了 Tab、浏览器最小化或电脑锁屏）；
- **事件监听**：`document.addEventListener('visibilitychange', () => { ... })`。

#### 2. focus / blur 与 visibilitychange 的关键差异
- 用户在双显示器环境下，在主屏幕看网页，鼠标点击了副屏幕的聊天工具；
- 此时网页触发了 `blur`（失去焦点），但页面仍然在屏幕上是**完全可见的**！
- 若用 `blur` 暂停视频播放会导致极差体验，因此**度量页面是否被看始终以 `visibilitychange` 为准**。

#### 3. 常见实战应用场景
- **暂停耗电任务**：页面切后台时立即暂停 Canvas 复杂动画、停止视频播放、调低 WebSocket 心跳频率；
- **唤醒即时轮询**：用户切回页面瞬间，立即向服务器发起一次增量拉取，秒级同步最新未读红点。

---

### 核心代码片段（极简记法）

```javascript
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') {
    resumeAnimation(); // 切回前台：恢复动画/拉取最新数据
    startHeartbeat();
  } else {
    pauseAnimation();  // 切到后台：暂停定时器以节省 CPU
    stopHeartbeat();
  }
});
```

---

### 面试加分项

- **浏览器切后台定时器降频（Timer Throttling）**：指出浏览器出于省电考虑，会对处于 `hidden` 状态的页签中的 `setInterval` 强制施加最低 1000ms（甚至更长）的休眠惩罚。重要定时器切后台时必须有心理准备，不可依赖其精准计时。""",
        "followups": """## 追问 1：在 Chrome 中，多个独立的系统窗口并排展示时，visibilityState 会是 hidden 吗？

**回答要点**：
不会。
只要当前页签在物理显示器上有哪怕 1 像素露出，它的 `visibilityState` 都是 `'visible'`，只有当它被完全盖住、折叠最小化或切换 Tab 时才会变成 `'hidden'`。

---

## 追问 2：页面切后台时，如何修改标题吸引用户切回（如展示「您有一条新消息」）？

**回答要点**：
在 `visibilitychange` 为 `hidden` 且有新消息时，启动轻量定时器交替修改 `document.title`（如 `document.title = '【新消息】您收到一条回复'`）；切回 `visible` 时立即还原原始标题。"""
    },
    {
        "id": "fe-scenario-010",
        "title": "在网络带宽一定的情况下，切片上传和整体上传消耗时间差不多吗？",
        "difficulty": "medium",
        "question": "在网络带宽一定的情况下，切片上传感觉和整体上传消费的时间应该是差不多的这种说法正确吗？为什么？",
        "answer": """### 一句话总结

**这种说法是不准确的，通常切片上传反而可能耗费稍多的纯传输时间，但其核心价值在于“容错重传成本极低”与“通过并发打满带宽通道”**。切片上传会产生额外的 TCP 握手与 HTTP 请求头开销；但在弱网环境下，一旦发生网络抖动，整体上传必须从 0% 重新再来，而切片上传仅需重传单个失败切片，工程上的最终成功耗时与体验远胜整体上传。

---

### 详细回答

#### 1. 理论传输开销分析（为什么切片可能会更慢？）
- **额外的 HTTP 协议头开销**：每个切片都需要独立的 Request / Response 头部信息；
- **TCP 连接与慢启动（Slow Start）**：如果不使用 HTTP/2 多路复用，每个切片可能经历新的 TCP 握手和拥塞控制慢启动过程；
- **分片与 Hash 计算开销**：前端切割文件（`file.slice()`）与计算 Hash 占用本地 CPU 时间。

#### 2. 为什么工业界依然首选切片上传？
- **断点续传（关键优势）**：上传 10GB 文件到 99% 时断网，整体上传前功尽弃，实际耗时直接翻倍；切片上传仅需续传最后 1% 的切片；
- **并发突破浏览器单连接限速**：针对高带宽场景，并发上传 3~6 个切片能更充分压榨利用上行链路带宽；
- **秒传机制（Instant Upload）**：基于 Hash 比对，若服务端已存在该文件，传输耗时直接从数分钟变为 0 毫秒！

---

### 核心代码片段（极简记法）

```javascript
// 切片上传的核心：并发控制 + 失败单片重试
async function uploadChunksWithLimit(chunks, limit = 3) {
  const pool = new Set();
  for (const chunk of chunks) {
    const task = uploadSingleChunk(chunk).finally(() => pool.delete(task));
    pool.add(task);
    if (pool.size >= limit) await Promise.race(pool); // 并发控制
  }
  await Promise.all(pool);
}
```

---

### 面试加分项

- **HTTP/2 多路复用的加速效应**：指出在开启 HTTP/2 的现代架构下，多个切片请求可以复用同一条 TCP 底层连接，彻底消除了 TCP 握手和慢启动惩罚，切片的额外开销几乎可以忽略不计。""",
        "followups": """## 追问 1：切片大小设置太小（比如每个切片只有 10KB）会带来什么灾难？

**回答要点**：
请求风暴！
若 1GB 文件切成 10KB，会产生 10 万个 HTTP 请求。不仅浏览器请求队列完全挤死、主线程卡顿，还会直接冲垮后端的接入层网关（DDOS 级压力）。

---

## 追问 2：如果服务端合并切片非常耗时，前端应该怎么配合？

**回答要点**：
切片全部上传完成后，前端发送合并请求；服务端异步执行合并并返回一个 `taskId`；前端通过轮询或 WebSocket 监听合并完成通知，避免 HTTP 请求一直挂起直至 504 网关超时。"""
    },
    {
        "id": "fe-scenario-011",
        "title": "大文件切片上传的时候，确定切片数量有哪些考量因素？",
        "difficulty": "medium",
        "question": "大文件切片上传的时候，确定切片数量的时候，有那些考量因素？",
        "answer": """### 一句话总结

确定切片数量的核心是**“在单次重传代价与 HTTP 握手损耗之间寻找平衡点”**。通常采取**“动态分片策略（文件 < 100MB 按固定 5MB 分片；超大文件限制切片总数在 100~500 个区间）”**，受**浏览器最大并发连接数（同域名限制 6 个）**、**网络环境稳定性**及**服务端合并压力**三维制约。

---

### 详细回答

#### 1. 考量维度一：网络损耗 vs 重传代价
- **切片过小（如 100KB）**：请求次数过多，HTTP 头部传输开销甚至超过内容本身，且极易触发浏览器队列堵塞；
- **切片过大（如 500MB）**：一旦网络轻微丢包超时，单个切片重试耗时极长，失去了断点续传的灵活性。

#### 2. 考量维度二：浏览器最大并发数（6个通道）
- 浏览器针对同一个域名同时最多维持 6 个活跃 TCP 连接；
- 切片并发度通常控制在 3~4 个，留出 2 个通道保障页面正常业务请求不受阻。

#### 3. 动态自适应切片算法（业界标准方案）
- 文件体积 $< 50\text{MB}$：不分片或切片大小固定为 $2\text{MB}$；
- 文件体积 $50\text{MB} \sim 1\text{GB}$：切片大小固定为 $5\text{MB} \sim 10\text{MB}$；
- 文件体积 $> 1\text{GB}$：将切片总数固定在 100 份以内，动态计算切片大小：$\text{ChunkSize} = \text{FileSize} / 100$。

---

### 核心代码片段（极简记法）

```javascript
function calculateChunkSize(fileSize) {
  const DEFAULT_SIZE = 5 * 1024 * 1024; // 默认 5MB
  const MAX_CHUNKS = 100; // 最大限制 100 块

  if (fileSize / DEFAULT_SIZE > MAX_CHUNKS) {
    return Math.ceil(fileSize / MAX_CHUNKS); // 动态扩大单片大小
  }
  return DEFAULT_SIZE;
}
```

---

### 面试加分项

- **动态网速自适应调整（Adaptive Chunking）**：在上传过程中根据前 3 个切片的实际传输耗时动态评估当前带宽。若网速飞快（> 10MB/s），自动动态调大切片体积；若处于弱网环境，调小后续切片体积以降低超时失败概率。""",
        "followups": """## 追问 1：如何计算超大文件的 MD5 避免前端内存溢出崩溃？

**回答要点**：
不能直接读取整个文件 `readAsArrayBuffer(file)`。
必须使用 `FileReader` 配合 `file.slice()` 分块流式读取，结合 `spark-md5` 的 `spark.append()` 逐块累加计算 Hash，并在 Web Worker 中执行。

---

## 追问 2：抽样 Hash（Sampling Hash）是怎么做到秒算几十 GB 文件指纹的？

**回答要点**：
大文件仅提取特定特征块：文件头部 2MB、尾部 2MB、以及中间均匀抽取 10 个 100KB 切片，将这些特征块拼接计算 Hash，准确率达 99.999% 且能在 1 秒内算完。"""
    },
    {
        "id": "fe-scenario-012",
        "title": "页面关闭时执行方法，该如何做？",
        "difficulty": "medium",
        "question": "页面关闭时执行方法，该如何做？有哪些事件可用以及注意事项？",
        "answer": """### 一句话总结

页面关闭监听分为**“UI 交互阻拦（使用 `beforeunload`）”**与**“无感知状态上报与资源清理（优先使用 `visibilitychange` 与 `pagehide` 配合 `sendBeacon`）”**两类。现代浏览器已废弃在关闭事件中发起同步网络请求或弹窗，任何网络通信必须交由底层的 `navigator.sendBeacon` 或 `fetch keepalive` 托管。

---

### 详细回答

#### 1. 场景 A：弹出“确定要离开吗？有内容未保存”
- **唯一合法事件**：`beforeunload`；
- **标准实现**：调用 `e.preventDefault()` 并设置 `e.returnValue = ''`；
- **注意**：现代浏览器出于安全防骚扰，已彻底禁止开发者自定义弹窗中的文字内容，一律展示系统默认警告。

#### 2. 场景 B：静默发送离线埋点与保存数据
- **推荐事件**：`visibilitychange`（`document.visibilityState === 'hidden'`）或 `pagehide`；
- **为什么不用 unload？** 移动端 Safari 等环境直接划走应用时 `unload` 经常不触发；
- **网络发送方式**：必须使用 `navigator.sendBeacon(url, data)`。

---

### 核心代码片段（极简记法）

```javascript
// 1. 阻止用户误触关闭（二次确认）
window.addEventListener('beforeunload', (event) => {
  if (hasUnsavedChanges) {
    event.preventDefault();
    event.returnValue = ''; // 触发浏览器原生确认弹窗
  }
});

// 2. 可靠执行离线统计与清理
window.addEventListener('pagehide', () => {
  navigator.sendBeacon('/api/leave', JSON.stringify({ userId: 123 }));
});
```

---

### 面试加分项

- **区分“刷新”与“关闭”**：在浏览器底层两个动作触发相同事件。可通过比较 `performance.navigation.type === 1`（或全新 `performance.getEntriesByType('navigation')[0].type === 'reload'`）在页面加载时精准识别上一次是刷新还是初次进入。""",
        "followups": """## 追问 1：在 beforeunload 回调函数中执行一个耗时 2 秒的 while 同步死循环能阻止页面关闭吗？

**回答要点**：
不能！
现代浏览器引擎内置了强制杀死超时进程的看门狗机制（Watchdog）。若在卸载钩子中卡住，浏览器会直接强行杀掉该 Render 进程并关闭窗口。

---

## 追问 2：pagehide 和 unload 有什么细微差别？

**回答要点**：
`pagehide` 事件在页面进入浏览器的往返缓存（BFCache / Back-Forward Cache）时也会触发，且其事件对象包含 `e.persisted` 属性标识页面是否被缓存以便后续秒开。"""
    },
    {
        "id": "fe-scenario-013",
        "title": "如何统计用户PV访问的发起请求数量？",
        "difficulty": "medium",
        "question": "如何统计用户单次PV访问期间发起的网络请求数量？有哪些实现思路？",
        "answer": """### 一句话总结

统计单次 PV 内网络请求数有两种通用路径：**“底层网络原生条目扫描（`performance.getEntriesByType('resource')`）”**用于统计所有静态资源与 Ajax 请求总数；或者**“全局 Monkey Patch 拦截（统一劫持 Axios / Fetch / XMLHttpRequest）”**统计业务接口并绑定当前的全局 `pv_id`，在页面跳出或下次切换路由时汇总上报。

---

### 详细回答

#### 1. 方案一：PerformanceObserver 原生被动监听（全覆盖）
- 浏览器底层会忠实记录每一个发出的请求（HTML、CSS、JS、IMG、Fetch、XHR）；
- 通过 `performance.getEntriesByType('resource').length` 即可秒级获取全站资源总请求数。

#### 2. 方案二：全局拦截器（聚焦业务 API 统计）
- 通常产品关心的不是加载了几个图标，而是**“这次 PV 究竟调用了多少次后端接口”**；
- 在全局 Axios 拦截器或 `window.fetch` 代理中打点自增：
  - 发起请求：`reqCount++`；
  - 携带统一标记：请求头注入 `X-PV-ID: <current_pv_id>`，方便后端精准串联聚合。

#### 3. SPA 单页应用的 PV 切换边界
- 在单页应用中，路由切换（`hashchange` / `popstate` / History API）代表产生了一次新的 PV；
- 每次路由变更时：归档上一个 PV 的请求计数并上报，重置计数器并生成全新 `pv_id`。

---

### 核心代码片段（极简记法）

```javascript
let currentPvRequestCount = 0;

// 劫持原生 fetch 自动计数
const originalFetch = window.fetch;
window.fetch = async (...args) => {
  currentPvRequestCount++;
  return originalFetch.apply(this, args);
};

// 路由离开时统计上报并重置
function onPvEnd(pvId) {
  reportPvStats({ pvId, totalApiRequests: currentPvRequestCount });
  currentPvRequestCount = 0; // 重置
}
```

---

### 面试加分项

- **请求健康度衍生指标**：除了单纯统计总数，还可以统计**请求并发峰值（Max Concurrent Requests）**与**接口报错率（Failed API Ratio）**，一旦某个 PV 内接口调用次数突增 10 倍，往往意味着代码陷入了死循环轮询 Bug。""",
        "followups": """## 追问 1：如果页面有 iframe，iframe 内发出的请求会被宿主页面的 fetch 拦截器捕获吗？

**回答要点**：
不会。
iframe 拥有自己完全独立的 `window` 上下文。要统计 iframe 内请求，必须将探针脚本注入到 iframe 内部，或通过 `postMessage` 汇总给宿主页面。

---

## 追问 2：如何过滤掉由埋点 SDK 自身发出的统计请求，防止无限套娃自增？

**回答要点**：
在拦截器中增加白名单 URL 匹配：若请求地址命中 `/api/track` 或包含特定内部标记头，直接放行且计数器不自增。"""
    },
    {
        "id": "fe-scenario-014",
        "title": "长文本溢出，展开/收起如何实现？",
        "difficulty": "medium",
        "question": "长文本溢出，展开/收起效果该如何实现？有哪些纯CSS与JS方案？",
        "answer": """### 一句话总结

展开收起的核心是**“内容多行截断展示 + 精准探测是否真正发生了文本溢出”**。纯展示可使用 CSS 的 `-webkit-line-clamp`；交互上通过对比 **`scrollHeight > clientHeight`（或 Range 测量）** 动态决定是否展示“展开”按钮，展开时移除截断类名或通过 CSS Grid 实现丝滑的高度过渡动画。

---

### 详细回答

#### 1. 核心判断：到底该不该显示“展开”按钮？
- 如果文本本身只有 2 行，却依然显示了“展开”按钮，是严重的 UI Bug；
- **判断逻辑**：
  在元素被截断状态下，比较真实内容高度与可视高度：
  `const isOverflow = element.scrollHeight > element.clientHeight;`
  仅当 `isOverflow === true` 时才显示展开按钮。

#### 2. CSS 多行文本截断规范写法
```css
.clamped-text {
  display: -webkit-box;
  -webkit-line-clamp: 3; /* 限制展示 3 行 */
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```

#### 3. 丝滑高度展开动画（CSS Grid 奇技淫巧）
- 传统 `max-height` 动画高度写死不精准；
- 现代最优解使用 CSS Grid 的 `grid-template-rows: 0fr -> 1fr` 过渡，无需 JS 计算具体像素即可实现任意高度的丝滑展开收起。

---

### 核心代码片段（极简记法）

```javascript
function useTextOverflow(ref, text) {
  const [canExpand, setCanExpand] = useState(false);

  useLayoutEffect(() => {
    const el = ref.current;
    if (el) {
      setCanExpand(el.scrollHeight > el.clientHeight); // 判断是否溢出
    }
  }, [text]);

  return canExpand;
}
```

---

### 面试加分项

- **浮动环绕（Float）实现展开按钮无缝嵌入文本尾部**：如果不希望展开按钮另起一行，而是像小说 App 一样紧跟在省略号 `...` 后面，可利用 CSS `float: right` 配合伪元素制造异形环绕排版。""",
        "followups": """## 追问 1：窗口大小变化（Resize）导致文本行数改变时，如何自动重新计算是否溢出？

**回答要点**：
使用 `ResizeObserver` 监听该文本容器的大小变动；一旦宽度发生改变，重新比对 `el.scrollHeight > el.clientHeight`，动态切换按钮可见性。

---

## 追问 2：如果文本里包含图片，图片异步加载完毕后撑开高度导致判定失效怎么办？

**回答要点**：
图片在加载完成前高度为 0。
给图片标签声明固定的宽高比或监听容器内图片的 `onload` 事件，完成后重新触发一次溢出检测。"""
    },
    {
        "id": "fe-scenario-015",
        "title": "如何实现鼠标拖拽？",
        "difficulty": "medium",
        "question": "在前端如何实现流畅的鼠标拖拽元素？原生Drag API与鼠标事件模拟各有什么优缺点？",
        "answer": """### 一句话总结

高定制拖拽推荐采用**“鼠标事件模拟（`mousedown` 记录起点 $\to$ `document.onmousemove` 计算偏移 $\to$ `document.onmouseup` 释放解绑）”**。移动过程中利用 **CSS `transform: translate3d`** 修改坐标以触发 GPU 合成层加速，杜绝修改 `top/left` 引发的高频回流；监听必须绑定在 `document` 上以防止鼠标快速移动时脱轨脱标。

---

### 详细回答

#### 1. 原生 HTML5 Drag & Drop API 的缺陷
- 专为文件拖入或跨应用拖放设计；
- 拖拽过程中会自带半透明的系统默认幽灵残影（Ghost Image），样式极难深度定制；
- 拖动时无法实时平滑获取鼠标绝对像素坐标做复杂吸附与碰撞检测。

#### 2. 鼠标事件三部曲（最佳实战）
1. **`mousedown`（在目标元素上）**：
   记录鼠标按下时的起始坐标 $(startX, startY)$ 与元素当前偏移量；
2. **`mousemove`（必须绑定在 `document` 上）**：
   - 为什么不绑在元素上？若鼠标移动过快划出元素边缘，事件会瞬间断档失效；
   - 计算偏移差值 $\Delta X = clientX - startX$；
   - 更新位移：`el.style.transform = \`translate3d(\${x}px, \${y}px, 0)\``；
3. **`mouseup`（必须绑定在 `document` 上）**：
   清理并注销 `document` 上的 mousemove 与 mouseup 监听器，释放内存。

---

### 核心代码片段（极简记法）

```javascript
function makeDraggable(el) {
  el.addEventListener('mousedown', (e) => {
    let startX = e.clientX - el.offsetLeft;
    let startY = e.clientY - el.offsetTop;

    function onMove(moveEvent) {
      el.style.left = `${moveEvent.clientX - startX}px`;
      el.style.top = `${moveEvent.clientY - startY}px`;
    }

    function onUp() {
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
    }

    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  });
}
```

---

### 面试加分项

- **边界约束与磁吸对齐（Snapping）**：在计算坐标时，通过 `Math.max(0, Math.min(x, maxBound))` 限制拖动不能超出屏幕可视区；当元素距离屏幕边缘小于 10px 时自动将坐标吸附至边缘，提供极致工业设计细节。""",
        "followups": """## 追问 1：拖拽时鼠标移动如果经过了文字区域，会导致文字被大面积蓝色高亮选中，怎么解决？

**回答要点**：
在 `mousedown` 回调开始时调用 `e.preventDefault()` 阻止默认选择行为，并在容器样式上加上 `user-select: none;`。

---

## 追问 2：如何同时兼容移动端触摸屏（Touch）拖拽？

**回答要点**：
使用 W3C 现代标准的 **Pointer Events API**（`onpointerdown`, `onpointermove`, `onpointerup`），配合 `el.setPointerCapture(e.pointerId)`，一套代码通吃鼠标、触控笔与手指触摸。"""
    },
    {
        "id": "fe-scenario-016",
        "title": "统计全站每一个静态资源加载耗时，该如何做？",
        "difficulty": "medium",
        "question": "统计全站每一个静态资源（JS/CSS/图片等）的加载耗时，该如何做？",
        "answer": """### 一句话总结

全站资源统计采用浏览器原生的 **`PerformanceObserver` 监听 `resource` 性能条目**。通过条目自动提取资源名称（`name`）、文件类型（`initiatorType`）、传输大小（`transferSize`）以及完整的网络瀑布流各阶段耗时（DNS、TCP、TTFB、Download）；通过按类型聚合分析，精准抓取拖慢页面的超大慢资源。

---

### 详细回答

#### 1. 核心属性与耗时计算
每个 PerformanceResourceTiming 包含微秒级高精时间戳：
- **总耗时（Duration）**：`entry.duration`；
- **DNS 查询耗时**：`entry.domainLookupEnd - entry.domainLookupStart`；
- **TCP 连接与 SSL 耗时**：`entry.connectEnd - entry.connectStart`；
- **TTFB 等待响应首字节**：`entry.responseStart - entry.requestStart`；
- **内容下载耗时**：`entry.responseEnd - entry.responseStart`。

#### 2. 识别资源是否命中缓存
- 若 `entry.transferSize === 0 && entry.decodedBodySize > 0`：代表命中本地强缓存（disk / memory cache）；
- 若体积很小且状态码为 304：代表命中协商缓存。

---

### 核心代码片段（极简记法）

```javascript
const observer = new PerformanceObserver((list) => {
  list.getEntries().forEach((res) => {
    console.log(`[资源耗时] ${res.name} | 类型: ${res.initiatorType} | 耗时: ${res.duration.toFixed(1)}ms`);
    if (res.duration > 1000) {
      reportSlowResource({ url: res.name, time: res.duration }); // 上报大于1秒的慢资源
    }
  });
});

observer.observe({ type: 'resource', buffered: true });
```

---

### 面试加分项

- **Timing-Allow-Origin 跨域响应头**：必须指出，部署在独立 CDN 上的静态资源，若服务端没有在响应头添加 `Timing-Allow-Origin: *`，浏览器会隐蔽保护敏感时间线，导致重定向、DNS、TCP、TTFB 细分耗时全被清零，只能读取总 `duration`。""",
        "followups": """## 追问 1：页面动态使用 new Image() 预加载或者动态注入 script，也能被监听到吗？

**回答要点**：
完全可以！
只要请求走的是浏览器的网络栈，无论是静态 HTML 标签还是动态 JS 发起的资源拉取，都会被记入 `resource` 时间线并被 observer 捕获。

---

## 追问 2：全站资源成百上千个，全部上报会消耗巨大带宽，生产上如何治理？

**回答要点**：
1. **阈值过滤**：仅上报耗时超出阈值（如 > 1.5s）的慢资源；
2. **抽样上报**：按 1% 采样率上报全量明细；
3. **本地汇总压缩**：在离开页面前，将资源按类型聚合（如 JS 耗时总均值、图片均值）只上报一份聚合统计对象。"""
    },
    {
        "id": "fe-scenario-017",
        "title": "防止前端页面重复请求",
        "difficulty": "medium",
        "question": "在前端如何防止重复提交请求（如连续猛击按钮、网络缓慢时重复提交订单）？",
        "answer": """### 一句话总结

防止重复请求必须构建**“UI 交互禁用 + 请求层唯一 Key 拦截（AbortController 取消或锁定时序） + 服务端幂等 Token 兜底”**三层防御。对于提交类操作在点击瞬间通过状态变量禁用按钮；在 Axios / Fetch 拦截器中根据“请求方法+URL+参数”生成唯一 Hash 键，若前序相同请求未完成直接中止后发请求或自动取消旧请求。

---

### 详细回答

#### 1. 视图层（UI 禁用 / Loading 锁）
- 点击提交按钮后，按钮立即设为 `disabled` 并展示旋转 Spinner；
- 必须放在 `finally` 中解锁，确保无论成功或报错都能恢复可点击状态。

#### 2. 请求拦截层（Axios CancelToken / AbortController 拦截器）
- **策略 A（保旧废新，适合表单提交）**：前序请求正在进行中，新的相同请求直接被拦截抛弃；
- **策略 B（弃旧迎新，适合搜索框输入防抖查询）**：前序请求还没返回，用户输入了新关键字，使用 `AbortController.abort()` 掐断上一个请求，只保留最新请求。

#### 3. 生产级唯一请求 Hash 判定
- 生成规则：`key = [method, url, JSON.stringify(params), JSON.stringify(data)].join('&')`；
- 维护内存 `pendingRequests = new Map()`；发起前 `has(key)` 判定拦截，响应后 `delete(key)`。

---

### 核心代码片段（极简记法）

```javascript
const pendingMap = new Map();

function generateReqKey(config) {
  return `${config.method}:${config.url}:${JSON.stringify(config.data)}`;
}

// Axios 请求拦截器防重
axios.interceptors.request.use((config) => {
  const reqKey = generateReqKey(config);
  if (pendingMap.has(reqKey)) {
    // 拦截重复请求
    return Promise.reject(new Error('请勿频繁重复提交！'));
  }
  pendingMap.set(reqKey, true);
  return config;
});

// 响应拦截器清理释放
axios.interceptors.response.use(
  (res) => { pendingMap.delete(generateReqKey(res.config)); return res; },
  (err) => { pendingMap.delete(generateReqKey(err.config)); return Promise.reject(err); }
);
```

---

### 面试加分项

- **服务端分布式幂等 Token（Idempotency Key）**：指出黑客可以直接跨过前端界面调用接口。对于金融支付和创建订单，进入表单页面时先向后端申请一个唯一的 `idempotent_token`，提交时携带，后端通过 Redis 分布式锁拦截重复 Token，实现 100% 幂等。""",
        "followups": """## 追问 1：为什么用防抖（Debounce）不能完全替代请求层的并发锁？

**回答要点**：
防抖只能限制高频连续触发的点击间隔（比如 300ms）。
如果后端接口由于数据库死锁慢查询耗时 3 秒才返回，防抖时间过后用户再次点击，仍然会发出第二个重复请求导致二次扣款，因此必须配合基于状态完成态的异步锁。

---

## 追问 2：如果参数包含随机时间戳，生成的 Request Key 不一致导致防重拦截失效怎么办？

**回答要点**：
在生成请求指纹时，执行字段白名单或黑名单过滤：主动剔除 `timestamp`、`nonce`、`_t` 等动态防缓存参数后再做字符串拼接哈希。"""
    },
    {
        "id": "fe-scenario-018",
        "title": "ResizeObserver作用是什么？",
        "difficulty": "easy",
        "question": "ResizeObserver的作用是什么？与传统的window.onresize相比有哪些核心优势？",
        "answer": """### 一句话总结

`ResizeObserver` 是浏览器提供的专门用于**高精、高性能监听“特定 DOM 元素尺寸变化”**的观察器。它摆脱了传统只能监听整个浏览器窗口（`window.onresize`）的局限，能够精准感知**由内容动态增加、CSS 动画、折叠面板展开引起的局部容器尺寸微变**，且天然经过浏览器底层的渲染循环批处理，杜绝循环依赖与死循环回流。

---

### 详细回答

#### 1. 传统 `window.onresize` 的局限
- 只能监听页面顶层窗口变化；
- 若窗口大小不变，仅仅是左侧侧边栏折叠导致右侧主画布宽度被动撑大，`window.onresize` 毫无反应；
- 传统做法是用定时器轮询检测元素的 `offsetWidth`，极其消耗 CPU。

#### 2. ResizeObserver 核心特性
- **细粒度元素级监听**：`observer.observe(targetElement)`；
- **多种盒模型尺寸报告**：
  - `contentBoxSize`：内容盒尺寸；
  - `borderBoxSize`：包含边框和内边距的边框盒尺寸；
  - `devicePixelContentBoxSize`：物理像素真实大小（用于 Canvas 消除模糊）。

#### 3. 典型应用场景
- **自适应图表（ECharts / Highcharts）**：容器变大自动调用 `chart.resize()`；
- **虚拟列表与富文本**：动态测量每个 Markdown 块的实际高度；
- **响应式容器查询（Container Queries）Polyfill**。

---

### 核心代码片段（极简记法）

```javascript
const observer = new ResizeObserver((entries) => {
  for (const entry of entries) {
    const { width, height } = entry.contentRect;
    console.log(`元素新尺寸: ${width} x ${height}`);
  }
});

// 开始监听特定 DOM 元素
observer.observe(document.querySelector('.chart-container'));
```

---

### 面试加分项

- **控制台报错「ResizeObserver loop limit exceeded」成因与解法**：当在 ResizeObserver 的回调函数内部又同步修改了该元素的样式或 DOM 结构导致其尺寸再次改变时，浏览器检测到了循环更新并在当前帧终止继续派发以防浏览器假死。解法是将回调内的样式修改用 `requestAnimationFrame` 推迟到下一帧执行。""",
        "followups": """## 追问 1：组件销毁时，如何正确释放 ResizeObserver？

**回答要点**：
调用 `observer.unobserve(targetElement)` 取消特定元素监听，或调用 `observer.disconnect()` 彻底清空所有监听器，防止闭包引发组件内存泄漏。

---

## 追问 2：Canvas 在高清屏（Retina）上缩放容易发虚模糊，ResizeObserver 怎么解决？

**回答要点**：
利用 `entry.devicePixelContentBoxSize`：直接获取物理像素级别的宽度和高度设置给 `canvas.width` 和 `canvas.height`，彻底消除由于 DPR 换算舍入误差带来的图像模糊。"""
    },
    {
        "id": "fe-scenario-019",
        "title": "要实时统计用户浏览器窗口大小，该如何做？",
        "difficulty": "easy",
        "question": "要实时统计用户浏览器窗口大小，该如何做？有哪些性能防刷考量？",
        "answer": """### 一句话总结

实时统计窗口大小采用 **`window.addEventListener('resize', throttledHandler)` 结合 `window.innerWidth` / `innerHeight`**。由于拖拽调整浏览器边框时每秒可能触发数百次 resize 事件，必须使用 **`requestAnimationFrame` 或 100ms 节流（Throttle）** 控制执行频率；若需将数据持久上报至后台，则必须结合 **防抖（Debounce）** 在用户停止调整窗口 1 秒后再执行网络提交。

---

### 详细回答

#### 1. 采集字段标准（视口宽高的选择）
- **`window.innerWidth / innerHeight`**：包含滚动条的可视视口大小（响应式布局最核心参考标准）；
- **`document.documentElement.clientWidth / clientHeight`**：不包含滚动条的页面根元素实际排版宽度；
- **`window.screen.width / height`**：显示器物理分辨率大小（全屏尺寸，不变）。

#### 2. 高频事件的性能灾难与治理
- 用户拖拽窗口边角时，resize 事件是以屏幕刷新率（60Hz~144Hz）疯狂派发的；
- 若在回调函数中频繁读取 DOM 或执行复杂布局重算，主线程会剧烈掉帧；
- **治理法则**：
  - 本地 UI 响应：用 `requestAnimationFrame` 限制为最高 60fps 单帧一次；
  - 远程统计上报：用 `debounce(reportApi, 1000)`，仅在用户拖拽停下后上报一次最终尺寸。

---

### 核心代码片段（极简记法）

```javascript
// 基于 requestAnimationFrame 实现极致流畅的节流监听
let isTicking = false;

window.addEventListener('resize', () => {
  if (!isTicking) {
    window.requestAnimationFrame(() => {
      const w = window.innerWidth;
      const h = window.innerHeight;
      console.log(`当前视口: ${w} x ${h}`);
      isTicking = false;
    });
    isTicking = true;
  }
});
```

---

### 面试加分项

- **移动端软键盘弹起的避坑（VisualViewport API）**：在移动端，用户点击输入框唤醒软键盘时，`window.innerHeight` 在某些 Android 机型上会剧烈变小，在 iOS 上则可能不变。现代标准推荐使用 **`window.visualViewport.height`** 监听真实的视觉视口变化，完美应对键盘弹起遮挡问题。""",
        "followups": """## 追问 1：在 React 组件中如何封装一个通用的 useWindowSize Hook？

**回答要点**：
基于 `useSyncExternalStore`（React 18 最优解）或 `useState` + `useEffect`；在 `useEffect` 中监听 `resize` 事件并在清理函数中执行 `removeEventListener`。

---

## 追问 2：SSR（服务端渲染如 Next.js）下执行 window.innerWidth 报错 window is not defined 怎么破？

**回答要点**：
在服务端渲染期间 `window` 对象不存在。
必须在初始化状态时提供默认安全兜底值（如 `{ width: 1920, height: 1080 }`），并在客户端挂载后的 `useEffect` 中才读取真实的 `window.innerWidth` 更新状态。"""
    },
    {
        "id": "fe-scenario-020",
        "title": "当项目报错定位是哪个commit引入的错误时，该怎么做？",
        "difficulty": "medium",
        "question": "当线上项目突然报错，代码历史中有数百个提交，你想精确定位是哪个commit引入的错误时，该怎么做？",
        "answer": """### 一句话总结

最快且最专业的工业级方案是使用 **Git 二分查找调试法（`git bisect`）**。指定一个已知正常的基线提交（`good`）和一个当前报错的提交（`bad`）；Git 会自动采用**二分查找算法（Binary Search）**在提交树中检出中间 Commit，由开发者（或编写自动化测试脚本）标记每次结果，仅需 $\log_2(N)$ 步（在 1000 个提交中只需 10 次）即可秒级锁定罪魁祸首提交。

---

### 详细回答

#### 1. 传统挨个排查的痛点
- 线上项目代码提交繁多，如果从最新的 commit 逐一 `git checkout` 往前试，排查几百个提交要耗费一整天，且极易看漏。

#### 2. `git bisect` 交互式排查四步走
1. 启动二分调试：`git bisect start`；
2. 标记坏点（当前报错）：`git bisect bad`；
3. 标记好点（上个月发布的稳定 tag）：`git bisect good v1.0.0`；
4. Git 自动切换到中间提交，运行项目检查：
   - 若报错：输入 `git bisect bad`；
   - 若正常：输入 `git bisect good`；
5. 重复几轮后，Git 会明确打印出：`<hash> is the first bad commit`；
6. 结束并回到原分支：`git bisect reset`。

---

### 核心代码片段（极简记法）

```bash
git bisect start
git bisect bad                 # 当前最新 commit 报错
git bisect good v2.1.0         # 已知 v2.1.0 正常

# 进阶：传入自动化测试脚本，全自动秒级揪出 bug commit！
git bisect run npm test
```

---

### 面试加分项

- **`git bisect run` 自动化全速排查**：如果为该 Bug 编写了一个最小复现的测试脚本（如 `npm run test:reproduce`，报错退出码为非 0，正常退出码为 0）。一行 `git bisect run` 命令敲下去，Git 会全程无人值守自动二分运行并在 10 秒内输出定位结果，极显资深工程师素养。""",
        "followups": """## 追问 1：如果二分过程中切到的某一个中间 commit 恰好有另一个无关的构建编译报错（编译不过去无法测试），怎么跳过？

**回答要点**：
输入 `git bisect skip`！
Git 会智能在当前提交的相邻节点重新选择一个替代 Commit 进行检出测试，绕过无法编译的脏提交。

---

## 追问 2：找到那个引入 Bug 的 commit 之后，该如何安全回滚修复？

**回答要点**：
若该分支已推送到公共主干，绝对不要用 `git reset` 强推！
使用 **`git revert <commit-id>`** 创建一个反向补偿提交，安全冲正代码，不破坏团队已有提交历史。"""
    },
    {
        "id": "fe-scenario-021",
        "title": "如何移除一个指定的commit？",
        "difficulty": "medium",
        "question": "在 Git 历史中，如何移除一个指定的 commit？在不同场景下（公共分支 vs 个人分支）有哪些最佳实践？",
        "answer": """### 一句话总结

移除指定的 commit 取决于该分支是否已经公开共享：对于**已推送到公共主干（main/master）的分支，唯一安全的方式是使用 `git revert <commit-id>`** 生成一个反向抵消提交；对于**仅在本地或个人私有特性分支上的提交，可以使用 `git rebase -i` 交互式变基，将目标行直接删除（或改成 `drop`）**，彻底将该 commit 从历史树中抹去。

---

### 详细回答

#### 1. 场景 A：公共分支安全移除（git revert，强烈推荐）
- **原理**：不改写过去的提交历史，而是计算指定 commit 的 Diff 并反向应用，生成一个全新的撤销提交；
- **命令**：`git revert <commit-id>`；
- **优势**：协作成员 pull 代码时平滑合并，绝不引起代码树分叉冲突，适合生产应急。

#### 2. 场景 B：个人私有分支彻底清除（git rebase -i）
- **原理**：物理改写 Git 树状历史；
- **步骤**：
  1. `git rebase -i <commit-id>^`（查看目标提交之前的历史）；
  2. 在文本编辑器中找到那一行，将 `pick` 改为 `drop`，或者直接将该整行代码删除；
  3. 保存退出，Git 自动跳过该 commit 并重新拼接后续提交。

---

### 核心代码片段（极简记法）

```bash
# 方案一：安全反向冲正（推荐生产公共分支）
git revert a1b2c3d

# 方案二：私有分支物理抹除
git rebase -i a1b2c3d^
# 将该行开头的 pick 改为 drop 并保存退出
```

---

### 面试加分项

- **撤销合并提交（Merge Commit）的坑**：如果要 revert 的是一个合并提交（包含两个父节点），直接 `git revert` 会报错拒绝。必须显式传入 `-m` 参数指定保留哪一条主线分支：
  `git revert -m 1 <merge-commit-id>`。""",
        "followups": """## 追问 1：如果移除的那个 commit 后面还有很多代码依赖它的改动，rebase 出现大面积冲突怎么办？

**回答要点**：
如果冲突过于繁杂难以理清，说明该提交的代码已经被深度耦合。强行物理移除成本太高，此时应立刻 `git rebase --abort` 退出，改为用普通的补丁代码手动修改并提交修复。

---

## 追问 2：已经强推（git push -f）覆盖了远程分支后，发现误删了别的同事的代码，怎么自救？

**回答要点**：
立即使用 **`git reflog`**！
Git 本地会忠实记录 HEAD 指针每一次变动的物理日志；找到强推前的那个提交 Hash，执行 `git reset --hard <old-hash>` 瞬间原地满血复活，重新推回远程。"""
    },
    {
        "id": "fe-scenario-022",
        "title": "如何还原用户操作流程？",
        "difficulty": "hard",
        "question": "当线上用户反馈出现偶发性Bug却无法复现时，如何还原用户的操作流程（用户轨迹与录屏回溯）？",
        "answer": """### 一句话总结

还原用户流程采用**“轻量行为轨迹探针（Breadcrumbs 面包屑链） + 基于 DOM 快照的录屏回放（如 rrweb）”**。全局拦截点击、路由跳转、网络请求并存入环形缓冲区；更极致的方案是利用 **rrweb 监听 DOM 树的 MutationObserver 增量突变**，将页面交互序列化为时间轴事件流，在后台像播放视频一样 1:1 动态还原用户点击与报错现场。

---

### 详细回答

#### 1. 方案一：行为轨迹日志（Breadcrumbs，开销极低）
- 拦截用户所有交互行为并在本地内存维护一个固定容量（如 50 条）的队列：
  - 点击事件：记录点击的元素标签、类名、按钮文案；
  - 路由跳转：记录从 `/list` 跳转到 `/detail/10`；
  - 接口调用：记录发送的请求与返回的状态码；
- 当报错触发时，将这 50 条足迹随错误报告一并上报，排查人员按步骤点击复现。

#### 2. 方案二：真实 DOM 录屏回放（rrweb，极致排查）
- **绝不是用 Canvas 或截图转视频**（那样做体积几十兆、卡死浏览器且暴露隐私）；
- **rrweb 核心原理**：
  1. 首屏全量 DOM 序列化为轻量 JSON 树快照；
  2. 使用 `MutationObserver` 监听后续每一个微小的 DOM 增删改差量事件；
  3. 捕获鼠标移动、滚动、点击坐标轨迹；
  4. 压缩后体积每分钟仅几十 KB，后台通过 `rrweb-player` 完美重放真实 DOM 渲染！

---

### 核心代码片段（极简记法）

```javascript
import { record } from 'rrweb';

let events = [];

// 监听并录制所有 DOM 变化与用户鼠标轨迹
record({
  emit(event) {
    events.push(event);
    if (events.length > 200) events.shift(); // 仅保留最近轨迹
  },
  maskAllInputs: true // 自动遮罩所有输入框密码与手机号
});

// 报错时上报录像
window.onerror = () => {
  sendBeacon('/api/replay', JSON.stringify({ events }));
};
```

---

### 面试加分项

- **严苛的隐私数据脱敏（Data Masking）**：生产落地录屏必须通过合规审计。在录制配置中开启 `maskAllInputs: true`，将所有输入框文字全部替换为 `***`；对敏感区域添加特定类名 `.rr-mask`，rrweb 在录制阶段直接将其置灰遮罩，坚决杜绝密码与个人隐私泄漏。""",
        "followups": """## 追问 1：rrweb 录制会不会对用户的电脑造成性能卡顿？

**回答要点**：
开销很小，因为只记录纯 DOM 数据变更。
但对于高频 DOM 变化的场景（如 60fps 的 Canvas 复杂动效或超大表格滚动），需在配置中忽略非关键节点的监听，避免短时间产生过多 Mutation 事件。

---

## 追问 2：如果报错发生在页面已经崩溃死锁的极端情况下，录像怎么上报？

**回答要点**：
将事件流实时写入 IndexedDB 作为本地临时草稿，页面若意外白屏或刷新，在下次用户打开系统时自动检测并弹窗询问“检测到上次异常退出，是否上报诊断日志”。"""
    },
    {
        "id": "fe-scenario-023",
        "title": "可有办法将请求的调用源码地址包括代码行数也上报上去？",
        "difficulty": "hard",
        "question": "在前端网络请求监控中，可有办法将该请求是由哪一个源文件、哪一行代码发起的（文件路径与代码行数）也自动采集并上报？",
        "answer": """### 一句话总结

最优雅的核心思路是**“在全局请求拦截器中就地 `new Error().stack` 提取调用栈并正则解析行号”**，结合 **构建工具插件（Babel / Vite Plugin）在编译期 AST 自动注入文件名**。在发起 Fetch / Axios 时实例化 Error 对象读取堆栈，向上回溯跳过 Axios 内部封装层，精准定位到业务组件的调用行，结合 SourceMap 在后台还原出原始 TS 源码位置。

---

### 详细回答

#### 1. 运行时方案：利用 Error 调用栈追溯（零构建侵入）
- 当你在 JS 中执行 `new Error().stack` 时，V8 引擎会瞬间捕获当前函数执行的调用栈帧；
- 打印出的堆栈长这样：
  ```text
  Error
      at Object.get (/utils/request.js:12:15)
      at fetchUserProfile (/services/user.ts:45:10)  <-- 真实的业务发起点！
      at UserProfile.vue:88:5
  ```
- 编写简单的正则表达式，跳过通用的封装拦截文件，直接提取第一行属于业务目录的文件路径与行列号。

#### 2. 编译期方案：Babel / Vite 编译宏注入（零运行时性能损耗）
- 编写 Vite 插件，在 AST 语法树遍历时识别所有 `api.call(...)` 函数；
- 自动向函数隐式追加调用元数据参数：
  `api.get('/users', { __caller: 'src/pages/User.tsx:42' })`。

---

### 核心代码片段（极简记法）

```javascript
// 在 Axios 拦截器中动态提取发起代码位置
axios.interceptors.request.use((config) => {
  const stack = new Error().stack || '';
  const lines = stack.split('\n');
  // 跳过前几层 axios 内部堆栈，找到业务层调用行
  const callerLine = lines.find(line => !line.includes('axios') && !line.includes('request.js')) || '';
  
  config.headers['X-Request-Source'] = callerLine.trim(); // 注入请求头或监控字段
  return config;
});
```

---

### 面试加分项

- **生产环境代码混淆与 SourceMap 还原**：生产代码经过打包后全是 `bundle.min.js:1:3485`。必须结合后端的 **SourceMap Consumer 还原服务**：上报行列号后，在监控后台根据发版时的隐藏 SourceMap 文件，将其还原为如 `src/components/PayButton.tsx:28` 的真实人类可读行号。""",
        "followups": """## 追问 1：每次发请求都 new Error().stack 会不会严重拖慢网络性能？

**回答要点**：
生成堆栈涉及 V8 引擎捕获当前调用帧，单次耗时约 0.1~0.5 毫秒。
对于普通业务频率完全可忽略；但对于每秒数百次的高频网络请求场景，建议开启**动态采样率（如仅对 5% 的请求采集源码行号）**或仅在测试/灰度环境下开启。

---

## 追问 2：如果请求是由某个第三方 npm 依赖包内部发出的，堆栈会表现怎样？

**回答要点**：
堆栈中会包含 `node_modules/<pkg-name>`。过滤逻辑中可判定若包含 `node_modules`，则提取该依赖包名及版本，便于区分是自身业务缺陷还是第三方库发出的异常请求。"""
    },
    {
        "id": "fe-scenario-024",
        "title": "请求失败弹出toast，如何保证批量请求失败只弹出一个toast？",
        "difficulty": "medium",
        "question": "页面加载时并发调用了 5 个接口，若此时服务器故障全部返回 500，界面如何保证只弹出一个 Toast 提示，而不是连续重叠弹出 5 次？",
        "answer": """### 一句话总结

核心采用**“微任务/时间窗口批处理防抖（Debounce Window）”**或**“单例活跃锁（Active Toast Mutex）”**。在全局 Axios 响应拦截器中拦截报错时，不直接调用 `toast.error()`，而是将错误投递到带有 50~100ms 延迟的时间窗口中去重合并；或者维护全局布尔标志位，只要当前屏幕上已有错误弹窗处于展示状态，后续同类错误全部静默吞吐。

---

### 详细回答

#### 1. 为什么不用简单的 Lodash debounce？
- 单纯的防抖函数会延迟执行最后一次，并且若报错信息各不相同（如接口 A 报 401，接口 B 报 500），简单防抖可能会把关键的 401 给吞掉。

#### 2. 最优解：消息队列批处理与归并（Message Batching）
- 当第一个错误到达时，开启一个短暂的时间切片（如 50ms）；
- 期间到达的所有报错全部压入当前批次数组；
- 时间窗口结束时统一决断：
  - 若包含登录失效 401，只弹一个“登录已过期，请重新登录”；
  - 若全是普通网络异常，弹出一个统合提示“网络异常，部分数据加载失败”；
  - 彻底杜绝 5 个黑色弹窗像扑克牌一样层叠刷屏。

---

### 核心代码片段（极简记法）

```javascript
let toastTimer = null;
const errorPool = new Set();

function showSafeToast(errMsg) {
  errorPool.add(errMsg);

  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    const combinedMessage = Array.from(errorPool).join('；') || '请求失败，请稍后重试';
    Toast.error(combinedMessage);
    errorPool.clear(); // 清空错误池
  }, 100); // 100ms 窗口内的错误全部聚合合并
}
```

---

### 面试加分项

- **组件库原生单例模式（destroyOnClose）**：像 Ant Design 等优秀的组件库本身支持全局单例覆盖：`message.error({ content: '...', key: 'global_error_toast' })`。只需声明固定的 `key`，连续调用 5 次也只会更新同一个 DOM 节点的文本，从组件库底层天然杜绝多重弹窗。""",
        "followups": """## 追问 1：如果 5 个并发请求中，有 1 个极其重要（比如订单状态），其余 4 个是无关紧要的打点，如何保证重要提示不被合并覆盖？

**回答要点**：
基于“错误优先级加权（Priority Level）”：为关键接口在请求配置中声明 `priority: 'high'`。在错误池合并决策时，若存在高优先级错误，立即清空低优先级提示并强制优先展示该关键错误。

---

## 追问 2：如果并发请求中触发了 401 导致连续 5 次尝试跳转登录页，怎么防重？

**回答要点**：
维护一个路由跳转单例锁 `isRedirectingToLogin`。第一个 401 触发时置为 `true` 并调用 `router.push('/login')`，后续 401 发现锁已被占用直接丢弃，防止页面产生多次死循环跳转历史。"""
    },
    {
        "id": "fe-scenario-025",
        "title": "如何减少项目里面if-else？",
        "difficulty": "medium",
        "question": "在前端业务代码中，大量的 if-else / switch-case 会导致代码圈复杂度极高且难以维护，如何优雅减少与重构？",
        "answer": """### 一句话总结

减少 if-else 的核心是**“由面向过程的过程判断升级为面向对象的规则驱动”**。最立竿见影的四大重构武器是：**对象映射表（Map / Dictionary 策略模式）**替代条件分支、**责任链模式（Pipeline / Middleware）**处理多级复杂校验、**多态（Polymorphism）与组合**消灭类型判断，以及**早期返回（Guard Clauses / 提前 return）**减少深层嵌套。

---

### 详细回答

#### 1. 武器一：表驱动法 / 对象映射（Strategy Pattern，最常用）
- **反例**：
  ```javascript
  if (type === 'text') renderText();
  else if (type === 'image') renderImage();
  else if (type === 'audio') renderAudio();
  ```
- **正解**：建立对象策略字典，将逻辑复杂度从 $O(N)$ 降到 $O(1)$：
  ```javascript
  const RENDER_MAP = {
    text: renderText,
    image: renderImage,
    audio: renderAudio
  };
  (RENDER_MAP[type] || defaultRender)();
  ```

#### 2. 武器二：卫语句（Guard Clauses / 提前 Return）
- 将多层嵌套的嵌套条件拍平，优先判断异常情况并立即 return，使主干业务代码永远保持在最外层 0 缩进。

#### 3. 武器三：配置驱动与策略函数
- 将复杂的联动判断转换为数组规则过滤：`rules.find(r => r.predicate(input))?.execute()`。

---

### 核心代码片段（极简记法）

```javascript
// 策略模式取代几十个 if-else 分支
const statusHandlers = {
  PENDING: () => console.log('处理等待中'),
  APPROVED: () => console.log('审核通过'),
  REJECTED: () => console.log('已拒绝')
};

function handleStatus(status) {
  const handler = statusHandlers[status] || statusHandlers.PENDING;
  handler();
}
```

---

### 面试加分项

- **可选链（Optional Chaining `?.`）与空值合并（Nullish Coalescing `??`）**：在数据解构取值时，一行 `user?.profile?.address ?? '默认地址'` 可以瞬间消灭传统代码中五六层冗长判空的 `if (user && user.profile && ...)` 丑陋代码。""",
        "followups": """## 追问 1：策略映射表如果每个分支的执行逻辑非常庞大（上百行），全写在一个文件里会导致文件膨胀，怎么拆？

**回答要点**：
采用工厂模式将各个策略拆分为独立文件：
`strategies/textStrategy.ts`、`strategies/imageStrategy.ts`；
通过动态路由导出或在一个注册中心集中导入，保证各策略单元高内聚并可独立单元测试。

---

## 追问 2：如果条件判断不是简单的等值比对，而是区间范围（如 分数 >= 90 为优秀，>= 80 为良好），策略字典怎么表示？

**回答要点**：
采用“规则数组过滤法（Rule Chain）”：
`const rules = [[s => s >= 90, '优秀'], [s => s >= 80, '良好']];`
通过 `const [_, label] = rules.find(([judge]) => judge(score)) || [null, '不及格'];` 依然实现无 if-else 的声明式匹配。"""
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

print(f"Generated {len(DATA)} questions successfully (fe-scenario-001 ~ fe-scenario-025)!")
