import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUESTIONS_DIR = os.path.join(BASE_DIR, 'questions')

DATA = [
    {
        "id": "fe-scenario-051",
        "title": "React中如何实现Keep-Alive缓存？",
        "difficulty": "hard",
        "question": "React 原生没有 Vue 那样的 <KeepAlive> 标签，在 React 中如何优雅实现组件状态缓存（Keep-Alive）？有哪些主流实现方案？",
        "answer": """### 一句话总结

React 实现 Keep-Alive 主要有两大方案：**“基于 CSS `display: none` 隐藏真实 DOM 节点以保留组件树（轻量简单但无法彻底卸载子树）”**，以及**“利用 React Portal 传送门将组件持久化挂载在屏幕外的离屏容器中，激活时再传送回目标视口（主流开源方案如 `react-activation`）”**。此外，React 官方正在研发实验性的原生 `<Activity>`（即 `<Offscreen>`）API 来原生支持该能力。

---

### 详细回答

#### 1. 方案一：CSS display: none 样式切换（伪卸载）
- 父级组件不销毁子组件，仅根据当前活动 Tab 控制对应包裹层的 `style={{ display: active ? 'block' : 'none' }}`；
- **优点**：逻辑极简，完全保留 DOM 树、表单输入和组件内部所有 State；
- **缺点**：若缓存的 Tab 数量很多，所有隐藏页面的 DOM 节点依然堆积在当前 DOM 树上，持续消耗浏览器内存和重绘性能。

#### 2. 方案二：React Portal 传送门解法（react-activation 核心原理）
- 创建一个全局常驻的隐藏根节点 `KeepAliveContainer`；
- 当页面需要被缓存时，利用 `ReactDOM.createPortal` 将组件真实渲染在该独立离屏容器中；
- 目标页面切换时，通过 DOM 操作将该离屏容器内的 DOM 节点直接插入到当前的占位容器中；
- **优点**：组件生命周期和 State 始终保持存活，且脱离当前页面的卸载逻辑。

#### 3. 方案三：状态外提与持久化（数据层 Keep-Alive）
- 将页面所有表单状态、滚动条位置提取存入全局 Store（Zustand / Redux）；
- 组件即使正常 unmount 销毁，再次 mount 时从 Store 回填初始值，实现“轻量级假存活”。

---

### 核心代码片段（极简记法）

```javascript
// 基于状态外提或条件渲染的简版 KeepAlive 占位容器
function KeepAliveTabs({ activeTab, tabs }) {
  return (
    <div>
      {tabs.map(tab => (
        <div key={tab.id} style={{ display: tab.id === activeTab ? 'block' : 'none' }}>
          {tab.component}
        </div>
      ))}
    </div>
  );
}
```

---

### 面试加分项

- **React 18+ 官方实验性 <Activity>（Offscreen）**：指出 React 团队正在研发底层并发原生支持的 `<Activity mode={isActive ? 'visible' : 'hidden'}>`。当切换为 hidden 时，React 不仅将 DOM display 设为 none，更会在 Fiber 调度层直接**降低该子树的任务优先级并暂停所有副作用触发**，是真正意义上的官方 Keep-Alive。""",
        "followups": """## 追问 1：被 Keep-Alive 缓存的组件，原本绑定的 useEffect 会被触发清理吗？

**回答要点**：
如果采用 display: none 方案，组件根本没有真正 unmount，因此不会触发 `useEffect` 的清理函数；
需要自定义生命周期 Hook（如 `useActivate` / `useDeactivate`）通过事件驱动模拟页面的进入与离开。

---

## 追问 2：缓存页面重新激活时，如何准确恢复页面原先的滚动条位置？

**回答要点**：
在离开页面时监听 `scroll` 事件记录当时的 `window.scrollY`；
重新激活时在 `requestAnimationFrame` 回调中调用 `window.scrollTo(0, cachedScrollY)` 丝滑还原。"""
    },
    {
        "id": "fe-scenario-052",
        "title": "React类组件与函数组件的区别是什么？",
        "difficulty": "easy",
        "question": "React 类组件（Class Component）与函数组件（Function Component）的核心区别是什么？为什么现代 React 全面倒向函数组件？",
        "answer": """### 一句话总结

类组件与函数组件最根本的哲学区别是：**“类组件基于面向对象，通过 `this` 实例访问不断变化的最新状态；函数组件基于函数式编程与闭包，拥有‘捕获渲染值（Capture values）’的特性，每一次 render 都是一次独立的状态快照”**。函数组件配合 Hooks 彻底解决了类组件逻辑复用繁琐（HOC/Render Props 嵌套地狱）与 `this` 指向易踩坑的痼疾。

---

### 详细回答

#### 1. 核心特性对比矩阵
- **状态与逻辑**：
  - 类组件：依赖 `this.state` 与 `this.setState`，生命周期方法（`componentDidMount` 等）将不相关的逻辑强行捆绑在同一个函数里；
  - 函数组件：通过 `useState`、`useEffect` 等原子化 Hooks 组合，按业务功能聚拢逻辑。
- **心智负担与 this**：
  - 类组件必须手动 `bind(this)` 或写箭头函数，经常引发 `this` 指向丢失；
  - 函数组件纯粹为普通 JavaScript 函数，完全没有 `this` 心智负担。
- **打包体积与编译优化**：
  - 类组件编译后会生成大量冗余的 ES5 辅助函数（`_classCallCheck`），难以被打包器 Tree-shaking 彻底优化；
  - 函数组件结构纯净，压缩率与优化空间极佳。

#### 2. Dan Abramov 经典论断：捕获特性（Capture Value）
- 在类组件中若发起一个 3 秒后的异步请求，3 秒内用户点击修改了状态，回调执行时 `this.state` 会直接读取到**最新的状态**；
- 在函数组件中，闭包会**锁定发起请求那一瞬间的 props 与 state 快照**，有效杜绝异步状态竞态错乱。

---

### 核心代码片段（极简记法）

```javascript
// 函数组件：状态通过 Hook 独立拆分与闭包捕获
function UserProfile({ id }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    fetchUser(id).then(setUser);
  }, [id]);

  return <div>{user?.name}</div>;
}
```

---

### 面试加分项

- **类组件目前依然无可替代的唯一场景**：指出目前 React 中唯一的例外是**“错误边界（Error Boundary）”**。React 官方至今尚未提供任何能捕获子组件渲染崩溃的 Hook，实现 `componentDidCatch` 和 `getDerivedStateFromError` 依然**必须手写类组件**。""",
        "followups": """## 追问 1：如果想在函数组件里拿到类似类组件 this 那样永远最新的引用值，该怎么做？

**回答要点**：
使用 **`useRef`**！
`useRef` 返回一个在组件整个生命周期中保持恒定不变的引用容器对象 `{ current: val }`，修改其 `.current` 不会触发重渲染，且随时随刻都能读取到最新值。

---

## 追问 2：为什么 React 官方没有废弃类组件，而是选择向前兼容？

**回答要点**：
为了保护社区与超大型存量遗留系统的资产。全球有无数数百万行代码的成熟商业项目依然运行在类组件上，强行破坏性废弃会割裂生态，但新代码已 100% 推荐纯函数组件开发。"""
    },
    {
        "id": "fe-scenario-053",
        "title": "React中setState是同步还是异步的？",
        "difficulty": "medium",
        "question": "React 中 setState 到底是同步还是异步的？React 18 的批处理（Automatic Batching）带来了什么根本改变？",
        "answer": """### 一句话总结

在 React 源码底层，**`setState` 本身始终是纯同步代码执行**。所谓的“异步”是指 React 会**将多次状态变更合并并延迟推迟到批处理（Batching）阶段统一刷新组件，以达到避免重复渲染的性能优化目的**。在 **React 18 之前**，原生事件与 `setTimeout` 中的 setState 会逃逸出批处理表现为同步；而在 **React 18+** 中，引入了**全自动批处理（Automatic Batching）**，无论在 Promise、定时器还是原生事件中，一律全场景默认执行批处理（表现为异步）。

---

### 详细回答

#### 1. 为什么 React 要设计成“表现为异步”？
- 若每次调用 `setState` 立即同步执行一次完整 DOM Diff 与渲染，连续调用 3 次就会触发 3 次昂贵重绘；
- React 收集一轮事件处理函数中的所有修改，一次性只渲染一次（批量合并）。

#### 2. React 17 及以前的分界线
- **在 React 合成事件与生命周期中**：处于 React 的执行上下文中，合并批处理，表现为**异步**；
- **在 `setTimeout`、`Promise.then` 或原生 `addEventListener` 中**：脱离了 React 上下文，**表现为同步**（调用后下一行代码立即能拿到最新 state）。

#### 3. React 18 的重大升级：全自动批处理
- React 18 基于根容器 `createRoot`，将批处理范围扩大到了**全宇宙所有场景**；
- 哪怕在 `setTimeout` 内部连续两次 `setState`，也只会合并触发一次渲染！

---

### 核心代码片段（极简记法）

```javascript
// React 18 全自动批处理演示
setTimeout(() => {
  setCount(c => c + 1);
  setFlag(f => !f);
  // React 18 中，以上两行合并为 1 次重绘！(React 17 会触发 2 次)
}, 1000);

// 若在 React 18 中强行要求立即同步渲染，使用 flushSync
import { flushSync } from 'react-dom';
flushSync(() => { setCount(c => c + 1); }); // 立即同步更新 DOM
```

---

### 面试加分项

- **对 setState 传入函数 vs 传入对象的区别**：连续调用 `setCount(count + 1)` 3 次，因为每次读取的都是同一个作用域里的固定快照值，结果只增加 1；而连续调用 `setCount(c => c + 1)` 3 次，React 会将这些 Updater 函数放入执行队列串行累加，最终结果正确增加 3。""",
        "followups": """## 追问 1：如何拿到 setState 之后更新完毕的最新 DOM？

**回答要点**：
- 函数组件：在依赖项包含该 state 的 **`useEffect`** 中获取；
- 类组件：在 `this.setState(newState, callback)` 的第 2 个参数回调函数中获取。

---

## 追问 2：为什么 React 官方坚决不在函数组件的 useState 中提供像类组件那样的第 2 个 callback 参数？

**回答要点**：
因为在并发渲染（Concurrent Mode）下，渲染任务可能被挂起或中断，回调时机变得难以预测；且函数组件推崇声明式响应，所有“状态改变后的副作用”统一在 `useEffect` 中处理符合架构纯洁性。"""
    },
    {
        "id": "fe-scenario-054",
        "title": "React中useCallback与useMemo的区别是什么？",
        "difficulty": "easy",
        "question": "React 中 useCallback 与 useMemo 的核心区别是什么？它们在底层有什么联系？如何避免过度优化反受其害？",
        "answer": """### 一句话总结

核心区别：**`useMemo` 缓存的是“函数的计算结果（返回值）”，而 `useCallback` 缓存的是“函数实例本身（引用稳定）”**。在底层，`useCallback(fn, deps)` 仅仅是 **`useMemo(() => fn, deps)` 的语法糖**。它们的核心使命是配合 `React.memo` 防止因父组件重绘导致子组件无谓渲染，滥用它们反而会增加额外的内存与依赖比对开销。

---

### 详细回答

#### 1. 两者本质对比
- **`useMemo`**：用于缓存**高开销的计算属性**（如万条数据的过滤排重计算），仅当依赖项变动时才重新计算：
  ```javascript
  const sortedList = useMemo(() => heavySort(list), [list]);
  ```
- **`useCallback`**：用于保持**函数引用的稳定性**，防止每次组件重新渲染时都生成一个全新的函数内存地址：
  ```javascript
  const handleClick = useCallback(() => doSomething(id), [id]);
  ```

#### 2. 底层等价关系
- React 官方源码中：
  ```javascript
  function useCallback(callback, deps) {
    return useMemo(() => callback, deps);
  }
  ```

#### 3. 常见误区：过度滥用（Anti-pattern）
- 给普通组件里的每个简单事件处理函数无脑套上 `useCallback`；
- **代价**：定义内联函数、分配依赖数组、每次重绘逐项进行浅比对；其本身的开销往往远高于直接创建一个普通内联函数！

---

### 核心代码片段（极简记法）

```javascript
// 唯一真正需要 useCallback 的经典场景：传给被 React.memo 包裹的子组件
const MemoChild = React.memo(Child);

function Parent() {
  // 保持引用稳定，确保 MemoChild 命中浅比对缓存，不触发二次渲染
  const onSave = useCallback(() => save(), []);
  return <MemoChild onSave={onSave} />;
}
```

---

### 面试加分项

- **何时使用它们的黄金法则**：指出只有在两种情况下才真正需要它们：
  1. 涉及昂贵的 CPU 密集型纯数据计算；
  2. 函数作为 props 传递给了被 `React.memo` 优化过的重量级子组件，或者该函数被列入了另一个 `useEffect` 的依赖数组中作为触发源。""",
        "followups": """## 追问 1：如果 useCallback 的依赖项写空数组 []，但在函数内部读取了外部组件的 count 变量，会发生什么？

**回答要点**：
会发生**闭包陷阱（Stale Closure）**！
因为函数只在初次挂载时被创建一次，永远锁定了初次渲染时 `count = 0` 的快照值，后续无论外部 count 怎么变化，函数内部打印的永远是旧值 0。

---

## 追问 2：React Compiler（React 忘却编译器）会如何改变这一切？

**回答要点**：
React 19 推出的 React Compiler 能在构建期自动分析 AST 并精准注入依赖缓存，未来开发者将无需手动编写一行 `useMemo` 或 `useCallback`，从底层彻底根除心智负担。"""
    },
    {
        "id": "fe-scenario-055",
        "title": "为什么不能在条件语句或循环中写Hooks？",
        "difficulty": "medium",
        "question": "为什么 React 官方严格规定不能在条件语句（if）、循环或嵌套函数中调用 Hooks？底层数据结构原理是什么？",
        "answer": """### 一句话总结

React 内部使用**“严格按顺序单向链接的链表（Hook.next LinkedList）”**来追踪和管理组件中的每一个 Hook 状态。**Hooks 在初次 mount 建立链表顺序后，后续每一次 update 都绝对依赖完全一致的调用执行顺序来依次定位对应的 Fiber 节点**；一旦在 `if` 或循环中调用导致执行顺序被打乱或跳过，整个链表顺序就会发生错位，导致状态完全张冠李戴崩溃。

---

### 详细回答

#### 1. React Fiber 的 Hook 底层存储模型
- 每个函数组件的 Fiber 节点上有一个属性 `memoizedState`；
- 它指向一个由 Hook 对象组成的单向链表结构：
  `Hook1 (useState) -> Hook2 (useEffect) -> Hook3 (useState) -> null`；
- 每一个 Hook 只保存自己的数据，**完全没有所谓以名字为 key 的对象映射表（Key-Value Map）！**

#### 2. 如果写在 if 语句中会发生什么？（错位灾难）
- 第一次渲染（Mount）：
  1. `useState('Jack')`（链表第 1 个节点）
  2. `if (isVip) useState(999)`（链表第 2 个节点）
  3. `useState(true)`（链表第 3 个节点）
- 第二次渲染（Update，此时 `isVip` 突变为 false）：
  1. 依然读取第 1 个节点（获取 'Jack'，正常）；
  2. `if (isVip)` 被跳过！紧接着执行了第 3 个 Hook；
  3. **React 的游标走到第 2 个链表节点**，把本应是第 2 个 Hook 的数字 999 错误地赋给了第 3 个布尔值 Hook！
  4. 链表严重错位，数据全部混乱报错。

---

### 核心代码片段（极简记法）

```javascript
// ❌ 严禁：导致 Fiber 链表游标错位
if (condition) {
  useEffect(() => {}, []);
}

// ✅ 规范：Hook 顶层无条件执行，将判断逻辑放在 Hook 内部
useEffect(() => {
  if (!condition) return;
  // 业务逻辑
}, [condition]);
```

---

### 面试加分项

- **ESLint 规则与 React 为什么不采用基于函数名的 Key 寻址？** 指出官方推出了 `eslint-plugin-react-hooks` 在编译写码时进行强制 AST 静态检测。React 团队之所以不用命名 Map 存储 Hook，是为了避免命名冲突、强制开发者遵守原子化拆分，并杜绝每次调用传递额外命名参数的运行时开销。""",
        "followups": """## 追问 1：如果一个组件挂载了 5 个 Hook，组件重新渲染时 React 是怎么识别第 3 个 Hook 属于谁的？

**回答要点**：
React 内部维护了一个全局全局工作指针 `workInProgressHook`。组件开始渲染时指向 `firstHook`；每当调用一个 Hook，指针就顺着 `hook.next` 向前推进一步，精准读写当前链表节点。

---

## 追问 2：自定义 Hook（Custom Hook）内部可以调用其他 Hook 吗？规则是什么？

**回答要点**：
完全可以！
自定义 Hook 本质上只是普通 JS 函数的代码分发与抽离，它在运行时会被就地展开并入当前宿主组件的整体 Hook 链表中，因此自定义 Hook 也必须遵循“无条件顶层调用”的铁律。"""
    },
    {
        "id": "fe-scenario-056",
        "title": "受控组件和非受控组件的区别是什么？",
        "difficulty": "easy",
        "question": "React 中受控组件（Controlled）与非受控组件（Uncontrolled）的核心区别是什么？各自适用什么业务场景？",
        "answer": """### 一句话总结

核心区别在于**“表单数据的驱动源头与控制权在谁手里”**。**受控组件**的数据完全由 React 组件的 `state` 强控，输入改变必须通过 `onChange` 更新 state 反哺回输入框，是 **“单一事实来源（Single Source of Truth）”**；而**非受控组件**的数据完全由浏览器原生 DOM 节点自己管理内部状态，React 仅在需要提交时通过 `ref` 获取当前原生 DOM 的实时值。

---

### 详细回答

#### 1. 受控组件（Controlled Component）
- **特征**：`<input value={name} onChange={e => setName(e.target.value)} />`；
- **优势**：
  1. 能够对每一次用户击键做即时校验、格式化（如只能输入数字、输入手机号自动加空格）；
  2. 根据当前输入内容即时控制“提交按钮”是否置灰禁用；
- **劣势**：每一次打字都会触发 React 组件的一次重新渲染。

#### 2. 非受控组件（Uncontrolled Component）
- **特征**：`<input defaultValue="Jack" ref={inputRef} />`；
- **优势**：
  1. 打字输入完全由浏览器底层原生驱动，零 React 重新渲染，极高性能；
  2. 极度适合接入旧版第三方 jQuery 插件或处理大表单；
- **强制必须使用非受控组件的场景**：文件上传输入框 `<input type="file" />`，因为由于浏览器安全限制，文件路径是只读的，React 无法程序化给其赋 `value`。

---

### 核心代码片段（极简记法）

```javascript
// 1. 受控组件：React State 驱动
const [val, setVal] = useState('');
<input value={val} onChange={e => setVal(e.target.value)} />

// 2. 非受控组件：DOM Ref 读取
const inputRef = useRef(null);
<input defaultValue="初始值" ref={inputRef} />
// 提交时直接读取：const currentVal = inputRef.current.value;
```

---

### 面试加分项

- **大型重型表单性能治理（react-hook-form 的哲学）**：指出在几百个表单项的企业级复杂大表单中，全受控组件会导致打字极度卡顿。现代主流库（如 `react-hook-form`）全面转向**基于非受控组件 + Ref 订阅**架构，大幅削减重绘次数，性能极度炸裂。""",
        "followups": """## 追问 1：如果一个 input 没有写 onChange，只写了 value="abc"，会发生什么？

**回答要点**：
输入框会被锁死！用户在键盘上敲任何字符都无法输入，且 React 控制台会抛出明显的警告：“You provided a `value` prop to a form field without an `onChange` handler”。

---

## 追问 2： defaultValue 和 value 属性有何根本区别？

**回答要点**：
`defaultValue` 仅在组件初次 mount 时作为原生 DOM 的初始占位值赋值一次，后续它的变动不会影响输入框状态；而 `value` 始终与输入框当前显示的文本保持实时双向绑定。"""
    },
    {
        "id": "fe-scenario-057",
        "title": "如何设计一个工业级通用前端组件？",
        "difficulty": "hard",
        "question": "如何设计并落地一个高质量、企业级的通用前端组件（如通用 Modal / Table / Select）？有哪些设计原则与工程考量？",
        "answer": """### 一句话总结

设计优秀通用组件遵循**“SOLID 原则与高内聚低耦合”**，核心贯穿六大维度：**“合理的 API 接口设计（受控与非受控兼顾、Props 命名符合心智直觉） + 极致的扩展性（插槽 Slot / Compound 组件复合模式） + 健全的无障碍无感体验（A11y 键盘导航） + 纯净样式与换肤隔离（Tailwind/CSS Module/CSS Vars） + 严格的 TypeScript 类型推导 + 完备的单元测试与文档”**。

---

### 详细回答

#### 1. 维度一：Props 契约设计（受控/非受控双模态）
- 同时支持 `value`（受控模式）与 `defaultValue`（非受控模式）；
- 内部封装 `useControllableValue` 统一抽象，向业务使用者提供极致灵活度。

#### 2. 维度二：复合组件设计模式（Compound Pattern）
- 拒绝搞出有 50 个 Props 的“配置膨胀巨石怪组件”；
- 采用父子复合拆分模式（类似 HTML 原生 `<select>` 与 `<option>`）：
  ```javascript
  <Modal>
    <Modal.Header title="提示" />
    <Modal.Body>{/* 自定义内容 */}</Modal.Body>
    <Modal.Footer />
  </Modal>
  ```

#### 3. 维度三：无障碍访问（A11y）与交互鲁棒性
- 弹窗必须支持 `Esc` 键自动退出；
- 支持 Tab 键在弹窗内部元素的焦点捕获与焦点锁定（Focus Trap）；
- 点击遮罩蒙层外部（Click Outside）自动收起。

---

### 核心代码片段（极简记法）

```typescript
// 通用组件标准 TypeScript Props 设计规范
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: React.ReactNode;
}
```

---

### 面试加分项

- **Headless UI（无头组件设计哲学）**：指出近些年国际顶尖开源界（如 Radix UI / TanStack Table）最前沿的架构趋势是 **Headless UI**：组件库**只封装核心复杂交互逻辑、状态机与 A11y 键盘规范，完全不写死任何 CSS 样式与 DOM 标签**，将样式控制权 100% 交由业务开发者自定义，彻底解决传统组件库样式难以覆盖魔改的痛点。""",
        "followups": """## 追问 1：如何确保外部用户传入的 ref 能够精准绑定到你的通用组件内部的真实原生 DOM 上？

**回答要点**：
使用 **`React.forwardRef`** 进行 Ref 转发；若需要向外部暴露定制的受控方法（如 `formRef.current.validate()`），配合 **`useImperativeHandle`** 进行安全的方法精简暴露。

---

## 追问 2：组件库如何做自动化视觉回归测试（Visual Regression Testing）？

**回答要点**：
基于 Storybook 配合 Playwright / Chromatic，在 CI 流水线中自动为每个组件状态截取像素图，与基线截图逐像素比对（Pixel Diff），变动超过 0.1% 立即报错拦截阻断合并。"""
    },
    {
        "id": "fe-scenario-058",
        "title": "React 18的核心新特性有哪些？",
        "difficulty": "medium",
        "question": "React 18 带来了哪些颠覆性的核心新特性？并发渲染（Concurrent Mode）的底层原理与应用场景是什么？",
        "answer": """### 一句话总结

React 18 的最核心基石是**“并发渲染机制（Concurrent Rendering）”**，它彻底告别了过去的同步不可中断渲染，赋予了 React **按优先级暂停、中断、恢复渲染任务的能力**。基于并发机制衍生出了三大杀手级特性：**全自动批处理（Automatic Batching）**、**可中断状态过渡 Hook（`useTransition` / `useDeferredValue`）**、以及**流式服务端渲染（Streaming SSR with Suspense）**。

---

### 详细回答

#### 1. 并发模式（Concurrent Mode）的底层颠覆
- **旧版痛点**：JavaScript 是单线程的，如果渲染一个包含万条 DOM 的复杂组件树耗时 100ms，期间浏览器主线程被死死霸占，用户点击输入框、打字完全毫无反应（严重掉帧假死）；
- **React 18 并发机制**：将渲染工作拆解为微小的可中断切片。当用户输入高优先级交互发生时，React 会**立即暂停当前低优先级的后台渲染，优先响应用户输入，随后在空闲时再继续渲染**。

#### 2. 杀手级 Hook：useTransition（优先级降级）
- 将一个紧急任务（如即时打字回显）与一个非紧急任务（如根据输入内容过滤千条列表）解耦拆分：
  ```javascript
  const [isPending, startTransition] = useTransition();
  // 保持打字极其丝滑，后台计算列表被降级调度
  startTransition(() => { setFilteredList(heavyFilter(keyword)); });
  ```

#### 3. 流式 SSR（Streaming SSR）
- 结合 `<Suspense>`，服务端可以先将页面的骨架 HTML 瞬间流式输出给客户端；
- 慢速的数据模块（如评论区）在服务端异步加载完成后，再以 HTML 片段形式沿同一个 HTTP 流推送到前端就地拼装。

---

### 核心代码片段（极简记法）

```javascript
import { createRoot } from 'react-dom/client';

// 开启 React 18 并发特性的统一入口
const root = createRoot(document.getElementById('root'));
root.render(<App />);
```

---

### 面试加分项

- **Strict Mode（严格模式）在开发环境执行两次渲染的目的**：很多初级开发误以为这是 Bug。必须向面试官解释：React 18 为了验证组件是否对“并发可复用状态（Offscreen 卸载与重载）”具备纯净幂等性，特意在 Dev 环境故意执行两次 mount/unmount，帮助开发者提前暴露出在 `useEffect` 中未清理事件监听和定时器的内存泄漏 Bug。""",
        "followups": """## 追问 1：useTransition 和防抖（Debounce）有什么本质区别？

**回答要点**：
- 防抖依赖于固定死的人工延时（如延迟 300ms 触发），无论设备配置高低都必须干等 300ms；
- `useTransition` 没有人为死等，如果电脑性能强可能 5ms 瞬间完成，如果卡顿则智能让位给高优先级事件，是**硬件感知的自适应调度**。

---

## 追问 2：React 18 新增的 useId Hook 是为了解决什么痛点？

**回答要点**：
解决 SSR 服务端渲染与客户端水合（Hydration）之间的 ID 不匹配报错问题！
`useId` 生成全应用全局唯一的稳定层级 ID，在服务端和客户端生成的结果 100% 绝对一致，专为无障碍标签属性（如 `htmlFor`）而生。"""
    },
    {
        "id": "fe-scenario-059",
        "title": "Vue 2与Vue 3的响应式原理有何本质区别？",
        "difficulty": "medium",
        "question": "Vue 2 与 Vue 3 的响应式原理有什么本质区别？Object.defineProperty 为什么会被 Proxy 彻底取代？",
        "answer": """### 一句话总结

Vue 2 采用 **`Object.defineProperty` 深度遍历对象属性进行 getter/setter 拦截**；Vue 3 采用 **ES6 `Proxy` 直接对整个目标对象（及其集合如 Map/Set）进行全方位行为代理**。Proxy 彻底消除了 Vue 2 无法原生监听“数组索引下标修改、动态新增/删除属性”的先天硬伤，且实现了**“惰性深度代理（按需访问时才代理下一层）”**，在内存消耗与首屏初始化性能上完胜 Vue 2。

---

### 详细回答

#### 1. Vue 2 的三大硬伤缺陷
1. **动态新增属性无法感知**：`this.obj.b = 2` 不会触发更新，必须强依赖 `Vue.set(this.obj, 'b', 2)` 这种补丁语法；
2. **数组索引与长度修改无法感知**：`arr[0] = 9` 或 `arr.length = 0` 无法监听，Vue 2 不得不劫持并重写了 `push`、`splice` 等 7 个原生数组原型方法；
3. **初始化性能差**：如果数据对象嵌套极深，Vue 2 在一开始初始化时就会一次性递归到底为每个属性添加 getter/setter，极大拖慢首屏渲染。

#### 2. Vue 3 Proxy 的全面降维打击
1. **全方位原生监听**：支持直接监听动态属性添加、删除（`deleteProperty` 拦截器）、以及原生数组索引下标的直接赋值；
2. **原生支持 Set / Map / WeakMap** 等现代集合数据结构；
3. **按需惰性代理（Lazy Proxy）**：只有当用户真正读取到深层属性（`get` 触发）时，Vue 3 才会动态给下一层对象包裹 `reactive`，大幅降低内存开销。

---

### 核心代码片段（极简记法）

```javascript
// Vue 3 极简 Proxy 响应式原型
function reactive(target) {
  return new Proxy(target, {
    get(target, key, receiver) {
      track(target, key); // 收集依赖
      const res = Reflect.get(target, key, receiver);
      return typeof res === 'object' && res !== null ? reactive(res) : res; // 访问时才惰性代理！
    },
    set(target, key, value, receiver) {
      const res = Reflect.set(target, key, value, receiver);
      trigger(target, key); // 触发更新
      return res;
    }
  });
}
```

---

### 面试加分项

- **为什么必须搭配 Reflect.get / set 使用？** 必须指出 Reflect 内部接收的 `receiver` 参数至关重要：当对象内部存在 getter 访问器属性且内部调用了 `this.otherProp` 时，传给 `Reflect.get` 的 receiver 能够确保 `this` 正确指向当前创建的 Proxy 代理对象，而不是原始对象，从而杜绝依赖收集发生遗漏丢失！""",
        "followups": """## 追问 1：Vue 3 的 ref 和 reactive 在底层有什么区别？

**回答要点**：
- `reactive` 底层直接使用 `Proxy` 只能代理引用对象类型；
- `ref` 专门为了处理基础原始类型（数字、字符串），底层封装了一个包含 `get value()` 与 `set value()` 的类对象（Object Accessor），若是对象则内部再转调 `reactive`。

---

## 追问 2：Proxy 的唯一缺点是什么？

**回答要点**：
完全无法在不支持 ES6 的低版本旧浏览器（IE11）中通过 Polyfill 进行向下兼容（因为 Proxy 是语言语法底层的宿主代理，没有任何 ES5 语法能完美模拟它的拦截能力）。"""
    },
    {
        "id": "fe-scenario-060",
        "title": "Vue 3相比Vue 2有哪些全方位的优势与升级？",
        "difficulty": "medium",
        "question": "Vue 3 相比 Vue 2 有哪些全方位的重构与优势？为什么说 Composition API 彻底改变了大型项目开发？",
        "answer": """### 一句话总结

Vue 3 是一次脱胎换骨的架构重写，核心优势凝聚为四点：**“更好的代码组织与逻辑复用（Composition API 终结了 Mixin 命名冲突与来源模糊地狱）”**、**“更极致的运行与打包性能（Proxy 代理响应式、虚拟 DOM 静态提升 PatchFlags、按需摇树 Tree-shaking 使包体积缩减约 50%）”**、**“原生 100% 强类型 TypeScript 支持”**、以及**“更强大的原生新特性（Fragment 支持多根节点、Teleport 任意传送门、Suspense）”**。

---

### 详细回答

#### 1. 逻辑复用：Composition API vs Options API
- **Vue 2 (Options API)**：一个业务功能被硬生生割裂撕碎在 `data`、`methods`、`computed`、`mounted` 四处，代码超过 500 行后上下翻滚查找痛不欲生；
- **Vue 3 (Composition API)**：将同一业务功能相关的所有响应式变量与函数聚合在一个自定义组合式函数（`useUser()`）中，按功能模块独立收拢与随意复用。

#### 2. 编译与运行性能大飞跃
- **静态提升（Hoist Static）**：模板中永远不变的静态纯 HTML 节点在编译期提升到渲染函数外部，每次重绘直接复用同一引用，零重构开销；
- **补丁标记（PatchFlags）**：Diff 算法只针对带有标记的动态节点（如只包含文本动态变动、只包含动态 class）进行靶向比对，完全跳过所有静态 DOM 比对。

#### 3. 架构解耦：自定义渲染器（createRenderer）
- Vue 3 核心与平台渲染逻辑彻底解耦，开发者可以轻松使用 Vue 语法去渲染 Canvas 图元、微信小程序、甚至 iOS/Android 原生 UI。

---

### 核心代码片段（极简记法）

```vue
<!-- Vue 3 <script setup> 现代极简开发范式 -->
<script setup>
import { ref, onMounted } from 'vue';

const count = ref(0);
const increment = () => count.value++;
</script>

<template>
  <!-- 原生支持多根节点 Fragment -->
  <h1>计数器: {{ count }}</h1>
  <button @click="increment">+1</button>
</template>
```

---

### 面试加分项

- **Tree-shaking 友好的底层重构**：指出在 Vue 2 中，`Vue.nextTick`、`Vue.observable` 等 API 全部挂载在 Vue 全局构造函数原型上，即使你一行没写，打包器也无法将它们剪掉；而在 Vue 3 中，几乎所有 API 均改为具名导出 `import { nextTick } from 'vue'`，未使用的功能在打包期被彻底剪切摇掉，极致纯净。""",
        "followups": """## 追问 1：Vue 3 废弃了过滤器（Filters）特性，官方推荐用什么替代？

**回答要点**：
官方推荐直接使用普通的计算属性（`computed`）或简单的纯 JavaScript 方法函数调用（`format(text)`）替代，消除过滤器的特殊语法心智负担。

---

## 追问 2：Teleport 标签在业务开发中解决了什么棘手问题？

**回答要点**：
完美解决模态弹窗（Modal）和通知提示的挂载位置问题。
允许组件的逻辑和模板写在业务子组件内，但将其真实 DOM 瞬间“传送”挂载到外层的 `document.body` 节点下，彻底避免父级元素 `overflow: hidden` 或 `z-index` 的层级截断影响。"""
    },
    {
        "id": "fe-scenario-061",
        "title": "Vue中watch和computed的区别是什么？",
        "difficulty": "easy",
        "question": "Vue 中 watch 与 computed 的核心区别是什么？各自的底层原理与业务应用场景是什么？",
        "answer": """### 一句话总结

最根本的区别在于：**`computed`（计算属性）侧重于“衍生新数据且具备只读缓存特性”，只有当其依赖的响应式数据改变时才重新计算；而 `watch`（侦听器）侧重于“在数据变化时执行异步或昂贵的副作用操作”，不具备数据缓存能力**。

---

### 详细回答

#### 1. 核心属性横向对比
- **缓存机制（Cache）**：
  - `computed`：拥有**脏检查与惰性缓存**（`dirty` 标志）。只要依赖项没有变化，多次调用直接读取之前计算好的旧值，零重复执行开销；
  - `watch`：每次指定监听的数据变动，指定的回调函数必须立即或异步执行一次，无缓存。
- **返回值与副作用**：
  - `computed` 必须包含 `return` 返回值，用于在模板或代码中充当普通属性消费；严禁在内部执行发送网络请求等异步副作用；
  - `watch` 不需要返回值，核心使命就是在回调函数里发起 HTTP 请求、修改 LocalStorage、手动操作 DOM。

#### 2. 底层机制简析
- `computed` 内部维护一个 `ComputedRefImpl`，通过 `dirty` 布尔值控制是否重新执行计算；
- 当计算属性的依赖发生改变时，触发 `scheduler` 调度将 `dirty` 置为 true，但不会立即计算；只有当外部真正尝试读取其 `.value` 时才按需求值。

---

### 核心代码片段（极简记法）

```javascript
// 1. computed：用于衍生计算，自带缓存
const fullName = computed(() => `${firstName.value} ${lastName.value}`);

// 2. watch：用于监听变化，执行异步网络副作用
watch(keyword, async (newVal) => {
  const result = await fetchSearchData(newVal);
  list.value = result;
});
```

---

### 面试加分项

- **Vue 3 新增的 watchEffect 与 watch 的区别**：指出 `watch` 需要显式指定监听哪几个变量；而 `watchEffect` 无需显式传入依赖，它会在回调执行时**自动追踪并收集用到的所有响应式变量**，且默认初次即刻无条件执行一次，语法更加紧凑现代化。""",
        "followups": """## 追问 1：computed 里面如果写了异步代码（比如在里面 setTimeout 或 await fetch），能拿到计算值吗？

**回答要点**：
完全拿不到！
`computed` 必须是纯同步返回。若异步返回一个 Promise，模板里最终拿到的只是一个 Promise 对象而非真实数据；针对异步计算需求可使用社区开源库 `@vueuse/core` 中的 `asyncComputed`。

---

## 追问 2：watch 监听一个深度嵌套对象时，如果不开启 deep: true 会发生什么？

**回答要点**：
普通 watch 只进行浅层属性指针的比对。若修改了对象内部深层嵌套属性（如 `user.info.age = 20`），由于 `user` 自身的内存引用地址并未改变，watch 不会触发；必须显式声明 `{ deep: true }` 开启全量深度递归侦听。"""
    },
    {
        "id": "fe-scenario-062",
        "title": "Vue中v-if和v-for为什么强烈不建议一起使用？",
        "difficulty": "medium",
        "question": "为什么在 Vue 模板中强烈不建议在同一个标签上同时使用 v-if 和 v-for？Vue 2 与 Vue 3 在处理二者优先级上有何重大不同？",
        "answer": """### 一句话总结

二者混用会造成**“执行优先级混乱引发的巨大渲染性能浪费甚至语法报错 Bug”**。**Vue 2 中 `v-for` 优先级高于 `v-if`**，导致即使全列表只需展示 1 项，Vue 也会把全量 1000 项无脑遍历一遍再逐个判断是否显示，性能极度浪费；而在 **Vue 3 中颠倒为 `v-if` 优先级高于 `v-for`**，导致执行 `v-if` 时循环变量根本尚未生成，直接抛出 `ReferenceError: item is not defined` 崩溃。最佳实践是**使用 `computed` 提前过滤数据列表，或外层包裹 `<template>` 标签解耦**。

---

### 详细回答

#### 1. Vue 2 的惨痛代价（性能黑洞）
- 开发者意图：只渲染已完成的任务；
  ```html
  <li v-for="item in 10000_items" v-if="item.isDone">{{ item.name }}</li>
  ```
- **编译结果**：编译生成的渲染函数中，循环包裹着条件判断。必须执行 10000 次虚拟节点创建与判断，首屏严重卡顿掉帧。

#### 2. Vue 3 的反转与报错
- Vue 3 调整了规则：`v-if` 拥有更高优先级；
- 当 `v-if="item.isDone"` 执行时，`item` 此时还在后面的 `v-for` 中未定义，控制台直接疯狂报错报红。

#### 3. 官方推荐两大约束正解
- **解法一：优先使用 computed 过滤（终极推荐）**：
  ```javascript
  const doneItems = computed(() => items.value.filter(item => item.isDone));
  ```
  然后在模板中直接纯净循环：`<li v-for="item in doneItems" :key="item.id">`。
- **解法二：外层 template 解耦分级**：
  若只是想控制整张列表是否展示，在外层包裹 `<template v-if="showList">`。

---

### 核心代码片段（极简记法）

```html
<!-- ✅ 优雅规范解耦：使用 template 标签包裹分层 -->
<template v-if="shouldShowList">
  <div v-for="item in list" :key="item.id">
    {{ item.name }}
  </div>
</template>
```

---

### 面试加分项

- **ESLint 工业化拦截规范**：在团队工程中配置官方插件 `eslint-plugin-vue`，开启规则 `'vue/no-use-v-if-with-v-for': 'error'`，在研发保存代码时直接通过 AST 静态语法树拦截报警，从工程工具链路杜绝该低级错误流入代码库。""",
        "followups": """## 追问 1：为什么 Vue 3 决定把 v-if 的优先级调整为高于 v-for？

**回答要点**：
为了保护初学者和代码鲁棒性。很多人误以为写在同一个元素上的 `v-if` 是用来控制“整张列表是否该渲染”的开关；Vue 3 调高 `v-if` 优先级符合“先看外层开关是否开启、再决定要不要大动干戈执行循环遍历”的常理心智。

---

## 追问 2：<template> 标签在渲染后会生成真实 DOM 节点吗？

**回答要点**：
完全不会！
`<template>` 标签作为不可见的虚拟占位容器（Fragment），编译后仅负责组织逻辑与执行指令，不会在页面上留下任何真实的物理 HTML 标签，零多余层级开销。"""
    },
    {
        "id": "fe-scenario-063",
        "title": "Vue组件间通信有哪些方式？",
        "difficulty": "medium",
        "question": "Vue 组件间通信有哪些方式？父子、兄弟、跨层级以及全局通信各自的最优解是什么？",
        "answer": """### 一句话总结

Vue 组件通信根据组件层级拓扑关系精准选型：**父子通信采用“Props 下发 + Emits 事件上报（单向数据流）”**；**跨级深层通信采用“Provide / Inject 依赖注入”**；**无关系的跨组件/兄弟通信采用“全局事件总线（mitt）”**；而面对复杂的大规模共享状态，统一采用**现代官方状态管理中枢“Pinia”**。

---

### 详细回答

#### 1. 父子双向协作（最基础规范）
- **Props**：向下传递只读数据；
- **$emit**：向上传递事件与数据载荷；
- **v-model**（Vue 3 中升级为支持多个 `v-model:propName` 语法糖）。

#### 2. 跨多级祖孙通信（Dependency Injection）
- 祖先组件声明：`provide('theme', themeState)`；
- 任意深层后代直接提取：`const theme = inject('theme')`；
- 彻底告别 Props 一层一层痛苦透传的“Props Drilling”地狱。

#### 3. 兄弟与任意组件解耦通信
- Vue 2 中常用的全局 EventBus（`new Vue()`）在 Vue 3 中已被废弃；
- Vue 3 官方推荐引入极轻量开源库 **`mitt`**（仅 200 字节的发布订阅调度器）：
  `emitter.emit('event', data)` 与 `emitter.on('event', fn)`。

#### 4. 全局共享状态库：Pinia（Vuex 的终结者）
- 彻底废弃 Mutations，仅保留 `state`、`getters`、`actions`；
- 原生 100% 完美的 TypeScript 类型自动推导。

---

### 核心代码片段（极简记法）

```javascript
// Provide / Inject 跨级响应式依赖注入
// 祖先组件
provide('userKey', readonly(userState)); // 用 readonly 防御后代私自篡改

// 深层子组件消费
const user = inject('userKey', defaultFallback);
```

---

### 面试加分项

- **对 $parent / $children / $refs 强耦合反模式的警惕**：指出虽然可以通过 `ref` 或 `$parent` 直接强行修改父组件或子组件的内部私有变量，但这是严重的**反模式（Anti-pattern）**，严重破坏了单向数据流与组件封装独立性，一旦出 Bug 调用链根本无法追踪，严禁在正规通用组件中滥用。""",
        "followups": """## 追问 1：后代组件通过 inject 拿到对象后，能直接给对象的属性赋值修改吗？

**回答要点**：
在技术上如果传递的是响应式对象是可以修改的，但这**严重违背单向数据流**！
最佳实践：祖先组件在 provide 时同时下发一个专门的 `updateUser` 修改方法，后代若要改动必须显式调用该方法通知祖先统一变更，或者使用 `readonly()` 包裹锁定。

---

## 追问 2：Pinia 为什么不需要像 Vuex 那样区分 Mutation 和 Action？

**回答要点**：
因为在 Vue 3 现代架构与 Vue Devtools 中，时间旅行与状态追踪已经能深度捕获所有的异步与同步变化；合并后消除了冗余代码样板，写法极度清爽。"""
    },
    {
        "id": "fe-scenario-064",
        "title": "前端性能优化的常用手段有哪些？",
        "difficulty": "hard",
        "question": "前端全链路性能优化的核心手段有哪些？如何系统化从网络传输、资源解析、渲染运行到缓存策略全景落地？",
        "answer": """### 一句话总结

工业级性能优化遵循**“减少请求量、缩小资源体积、加速网络传输、优化渲染执行、榨干客户端缓存”**的五维矩阵：通过 **路由懒加载（Code Splitting）** 与 **Tree Shaking** 缩减体积，采用 **HTTP/2 多路复用 + CDN 加速** 跑满带宽，利用 **强缓存（Cache-Control） + Service Worker** 实现二次秒开，配合 **虚拟列表、防抖节流与 Web Vitals（LCP/CLS）监控** 保障 60FPS 丝滑交互。

---

### 详细回答

#### 1. 网络与传输层优化
- **静态资源上 CDN**：让用户就近从边缘节点拉取资源；
- **升级 HTTP/2 或 HTTP/3**：多路复用彻底消灭 HTTP/1.1 的队头阻塞（Head-of-Line Blocking）；
- **现代化压缩**：开启 Gzip / Brotli（Brotli 压缩比比 Gzip 再高 20%）。

#### 2. 资源与打包体积瘦身
- **路由级动态导入（Code Splitting）**：按路由分割 chunk，首屏仅下载当前页面必需的代码；
- **图片多维度优化**：全面拥抱新一代 WebP / AVIF 格式、配合 `loading="lazy"` 原生图片懒加载。

#### 3. 页面渲染与运行时优化
- **CSS 放头部 `<head>`，JS 脚本放底部或加上 `defer` / `async`**：防止脚本下载执行阻塞 DOM 树解析构建；
- **长列表虚拟滚动（Virtual List）**：万条数据只渲染视口可见的 10 个 DOM 节点；
- **合成图层硬件加速**：复杂位移使用 `transform` 与 `opacity` 代替 top/left，避免触发重排（Reflow）与重绘（Repaint）。

---

### 核心代码片段（极简记法）

```javascript
// 路由级代码分割（按需懒加载）
const Dashboard = React.lazy(() => import('./routes/Dashboard'));

// 强缓存标配响应头（带内容 Hash 的静态资源）
// Cache-Control: public, max-age=31536000, immutable
```

---

### 面试加分项

- **性能优化铁律：以真实数据衡量，拒绝凭空盲目揣测**：优化前必须以 **Lighthouse / WebPageTest** 报告及生产用户的真实监控指标（**RUM - Real User Monitoring**：LCP、INP、CLS）为基准度量。坚决杜绝“为了优化而优化”，必须以可量化的核心指标降幅（如 LCP 从 3.8s 压降到 1.2s）作为优化成效的唯一评判标准。""",
        "followups": """## 追问 1：script 标签的 defer 和 async 到底有什么区别？

**回答要点**：
- 两者都是异步并行下载脚本、不阻塞 HTML 解析；
- `defer`：脚本下载完成后**绝不立即执行**，而是静静等待整棵 DOM 树全部解析完毕，且严格按照标签在 HTML 中的书写先后顺序串行执行；
- `async`：只要脚本一旦下载完成，**立即强行中断 HTML 解析并立刻插队执行**，谁先下完谁先执行，顺序完全随机。

---

## 追问 2：什么是关键渲染路径（Critical Rendering Path）？

**回答要点**：
指浏览器从接收 HTML、CSS、JS 字节流到最终在屏幕上绘制出物理像素的完整五步过程：
`构建 DOM 树 -> 构建 CSSOM 树 -> 合并生成 Render Tree -> 布局（Layout/Reflow） -> 绘制（Painting/Composite）`。"""
    },
    {
        "id": "fe-scenario-065",
        "title": "首屏加载速度慢，如何系统化排查和优化？",
        "difficulty": "hard",
        "question": "当线上项目反馈首屏加载速度极慢（白屏时间长达 5 秒），你如何系统化排查瓶颈并实施针对性优化？",
        "answer": """### 一句话总结

首屏排查遵循**“先度量归因，再精准治理”**的标准排障 SOP：利用 Chrome DevTools 的 **Network 瀑布图与 Performance 性能录制面板**，结合 **`webpack-bundle-analyzer` / `rollup-plugin-visualizer`** 诊断包体积。治理实施核心四招：**“HTML 入口强力瘦身 $\to$ 大包拆解与公共库 CDN 外置 $\to$ 关键资源预加载（preload/prefetch） $\to$ 服务端渲染（SSR）或静态预渲染骨架屏秒开”**。

---

### 详细回答

#### 1. 第一步：精准归因瓶颈节点
- **白屏时间 TTFB（Time to First Byte）过长**：说明服务端响应慢、DNS 解析耗时、或没有 CDN 加速；
- **资源下载时间过长**：查看 Network 面板，发现一个 `app.js` 体积高达 8MB，说明完全没有配置路由懒加载；
- **执行时间长（Long Tasks）**：Performance 面板中 JS 脚本主线程执行占用超过 500ms，说明存在同步死循环、超大 JSON 递归反序列化。

#### 2. 第二步：四重工程落地重拳
1. **体积大开刀**：
   - 使用可视化插件分析，将体积巨大的 `moment.js` 替换为超轻量 `dayjs`；
   - 将 `echarts`、`xlsx` 等重量级库移出主 bundle，仅在对应图表路由中动态 `import()` 异步加载；
2. **消灭网络阻塞**：
   - 提取首屏核心关键 CSS 内联进 HTML `<style>`；
   - 使用 `<link rel="preload" href="vital.js" as="script">` 抢占高优先级带宽；
3. **视觉感知体验兜底**：
   - 在 `index.html` 的 `#app` 容器内直接内联写入轻量 SVG 骨架屏（Skeleton Screen），消除纯白屏焦虑。

---

### 核心代码片段（极简记法）

```html
<!-- HTML 头部关键资源预加载与骨架屏内联 -->
<link rel="preload" href="/assets/main-chunk.js" as="script">

<div id="root">
  <!-- JS 未加载完成前，用户瞬间看到的骨架屏 -->
  <div class="skeleton-shimmer"></div>
</div>
```

---

### 面试加分项

- **现代新架构破局： Islands 架构与 SSR**：指出对于内容型网站（如电商、门户、博客），纯单页应用（SPA）的首屏性能优化已达物理极限。现代最优解是直接转向 **Next.js / Nuxt / Astro** 的服务端渲染或**孤岛架构（Islands Architecture）**：首屏直接推送现成纯 HTML，交互部分实现细粒度水合（Partial Hydration），实现毫秒级瞬间首屏展现。""",
        "followups": """## 追问 1：资源预加载中，preload 和 prefetch 有什么区别？

**回答要点**：
- `preload`：针对**当前页面立刻就要用到的高优先级关键资源**，强制浏览器立即抢先下载；
- `prefetch`：针对**未来下一个页面可能会用到的低优先级资源**，仅在浏览器主线程处于空闲（Idle）时，在后台静默预下载存入缓存。

---

## 追问 2：为什么把大型公共库放在公共 CDN（如 cdnjs / unpkg）上在某些企业内网中反而变慢了？

**回答要点**：
公网公共 CDN 受制于不可控的外网波动、DNS 污染或企业内网安全防火墙策略拦截；企业级生产环境必须将公共库镜像同步并托管在**企业自建的专属私有 CDN 节点**上，才能保证绝对的可用性与高可用带宽。"""
    },
    {
        "id": "fe-scenario-066",
        "title": "XSS和CSRF的区别是什么？如何针对性防范？",
        "difficulty": "medium",
        "question": "Web 安全中，XSS（跨站脚本攻击）与 CSRF（跨站请求伪造）的本质区别是什么？各自完整的防御体系是怎样的？",
        "answer": """### 一句话总结

最本质区别在于**“攻击媒介与信任借用方向不同”**：**XSS 是黑客利用漏洞在你的网站里注入并运行了恶意 JS 代码，借此盗取用户的 Cookie 凭据或篡改页面（信任泄露）**；而 **CSRF 是黑客根本拿不到你的任何代码和 Cookie，而是通过引诱用户在第三方钓鱼网站点击链接，诱骗浏览器自动带上本站受信任的 Cookie 发起越权恶意请求（借刀杀人）**。

---

### 详细回答

#### 1. XSS（跨站脚本攻击）
- **分类**：
  - 存储型（最危险，注入留言板入库保存）；
  - 反射型（注入 URL 参数直接返回）；
  - DOM 型（前端 JS 读 URL 盲目赋值 `innerHTML`）。
- **防御核心三板斧**：
  1. **输入输出转义过滤**：严禁直接拼接 HTML 字符串，对富文本使用安全白名单库（`DOMPurify.sanitize()`）；
  2. **Cookie 安全标记**：敏感登录 Token 的 Cookie 必须打上 **`HttpOnly`** 标记（禁止任何前端 JS 通过 `document.cookie` 窃取）；
  3. **CSP（内容安全策略）**：配置 HTTP 响应头 `Content-Security-Policy`，只允许加载可信域名的脚本。

#### 2. CSRF（跨站请求伪造）
- **攻击过程**：用户已登录银行网站 `bank.com`；用户在未登出情况下访问了黑客的钓鱼网站 `evil.com`；钓鱼网站暗中发出一张图片 `<img src="bank.com/transfer?money=1000&to=hacker">`，浏览器会自动为该请求带上银行网站的 Cookie，服务器误以为是用户本人操作。
- **防御核心三板斧**：
  1. **SameSite 属性**：现代浏览器最强防线！将 Cookie 的 `SameSite` 设为 `Lax` 或 `Strict`，跨站请求直接禁止携带 Cookie；
  2. **CSRF Token**：请求体中携带一个由服务端下发的随机动态 Token，黑客跨站发起请求时根本拿不到该 Token；
  3. **验证码与双重确认**：转账等核心敏感操作强制要求二次短信或验证码核验。

---

### 核心代码片段（极简记法）

```javascript
// 1. 防御 XSS：富文本净化
import DOMPurify from 'dompurify';
const cleanHtml = DOMPurify.sanitize(userDirtyInput);

// 2. 防御 CSRF：请求头显式注入独立 Token
axios.post('/api/pay', data, {
  headers: { 'X-CSRF-Token': getCsrfTokenFromMeta() }
});
```

---

### 面试加分项

- **JWT 存放在 LocalStorage 还是 Cookie 更安全？** 这是一个经典高频面试题。必须指出：
  - 存 LocalStorage：天然完全免疫 CSRF，但**一旦发生 XSS 会被一锅端秒级窃取**；
  - 存带有 `HttpOnly; Secure; SameSite=Lax` 的 Cookie：JS 彻底无法窃取（防 XSS 窃取），同时 SameSite 几乎彻底锁死了 CSRF，综合安全性最高。""",
        "followups": """## 追问 1：使用了前端框架（如 React / Vue）之后，还会发生 XSS 吗？

**回答要点**：
仍然可能！
虽然 React `{data}` 和 Vue `{{data}}` 默认会自动进行 HTML 实体编码转义，但如果开发者使用了 **`dangerouslySetInnerHTML`**（React）或 **`v-html`**（Vue），或者直接将用户输入作为 `a` 标签的 `href="javascript:..."` 属性，依然会发生严重的 XSS 攻击。

---

## 追问 2：CSRF 攻击能否通过纯 GET 请求发起？

**回答要点**：
完全可以！
如果后端接口设计不规范，将转账或删除等写操作做成了 GET 接口，黑客只需在钓鱼页面放一个普通 `<img src="...">` 标签，浏览器拉取图片时就会静默触发该 GET 请求完成攻击。"""
    },
    {
        "id": "fe-scenario-067",
        "title": "HTTP与HTTPS的区别是什么？SSL/TLS握手过程是怎样的？",
        "difficulty": "medium",
        "question": "HTTP 与 HTTPS 有什么根本区别？SSL/TLS 1.2 的经典四次握手过程是怎样的？对称加密与非对称加密如何有机结合？",
        "answer": """### 一句话总结

HTTP 是明文传输协议，面临**“窃听、篡改、冒充”**三大安全隐患；HTTPS 是 **HTTP 运行在 SSL/TLS 加密层之上（身披安全铠甲）**，提供**机密性、完整性校验与身份认证**。其底层采用**“混合加密架构”**：在握手阶段利用**非对称加密（公钥/私钥）安全协商出临时的会话密钥**，在后续正式传输数据阶段全面改用高效的**对称加密（AES）**进行高速加密传输。

---

### 详细回答

#### 1. HTTP vs HTTPS 核心维度对比
- **端口**：HTTP 默认 80，HTTPS 默认 443；
- **传输安全**：HTTP 完全明文裸奔传输，中间路由器可随意抓包并插播广告；HTTPS 全程强加密；
- **身份防伪**：HTTPS 依赖权威 CA 机构签发的数字证书（Digital Certificate），确保你访问的确实是官方服务器而非钓鱼假冒站点。

#### 2. SSL/TLS 1.2 经典四次握手深度流程
1. **第一次握手（Client Hello）**：
   - 客户端向服务端打招呼，发送客户端支持的 TLS 版本号、密码套件列表、以及一个客户端生成的随机数 `Random_C`；
2. **第二次握手（Server Hello + 证书）**：
   - 服务端确定使用的加密套件、返回服务端的随机数 `Random_S`、并附带发送**服务器的 CA 数字证书（包含服务端公钥）**；
3. **第三次握手（客户端验证证书 + 预主密钥）**：
   - 客户端校验证书合法性（颁发机构是否受信任、域名是否匹配、是否过期）；
   - 客户端生成第三个随机数**“预主密钥（Pre-Master Secret）”**，用证书里的**公钥进行加密**后发送给服务端；
   - 此时客户端与服务端均集齐了 3 个随机数，各自在本地算出完全一致的**对称加密会话密钥（Master Secret）**；
4. **第四次握手（验证并结束）**：
   - 双方用计算出的对称密钥互相发送一段加密的校验信息，确认加密握手成功，后续全面开启对称加密通信！

---

### 核心代码片段（极简记法）

```
客户端                               服务端
  |  1. Client Hello (Random_C)        |
  | ---------------------------------> |
  |  2. Server Hello (Random_S + 证书)  |
  | <--------------------------------- |
  |  3. 预主密钥(用公钥加密) + Finished  |
  | ---------------------------------> |
  |  4. Finished (对称加密验证通过)     |
  | <--------------------------------- |
  | ======= 正式对称加密数据传输 ===== |
```

---

### 面试加分项

- **TLS 1.3 的 1-RTT 与 0-RTT 极速优化**：指出现代 TLS 1.3 废弃了过时加密算法，将握手时间从原来的 2-RTT（两个来回）直接砍半为 **1-RTT**；在恢复会话时甚至支持 **0-RTT（首个数据包直接携带加密业务数据）**，极大幅度缩短了 HTTPS 的连接延迟。""",
        "followups": """## 追问 1：为什么不全程都使用非对称加密传输数据，而要在后续换成对称加密？

**回答要点**：
因为性能开销差异巨大！
非对称加密（如 RSA / ECC）涉及极复杂的超大数质数数学运算，其 CPU 消耗比对称加密（如 AES）高出整整成百上千倍；若全量数据均用非对称加密，服务器和手机 CPU 会瞬间跑满过热，因此仅在协商密钥时使用一次。

---

## 追问 2：数字证书中的“数字签名”是如何防止黑客篡改证书内容的？

**回答要点**：
CA 机构先对证书内容做 Hash 生成摘要，然后**用 CA 自身的私钥进行加密生成数字签名**；
浏览器内置了全球受信任根 CA 的公钥，使用该公钥解密签名若能与证书当前计算的 Hash 完全吻合，即可物理证明证书未经任何中间人篡改。"""
    },
    {
        "id": "fe-scenario-068",
        "title": "Webpack和Vite的构建原理有什么本质区别？",
        "difficulty": "medium",
        "question": "Webpack 与 Vite 的底层构建原理有什么本质区别？为什么 Vite 在本地开发环境下能做到毫秒级极速冷启动？",
        "answer": """### 一句话总结

最本质区别在于**“先整体打包（Bundle-based）还是按需原生驱动（No-Bundle ESM）”**。**Webpack 必须在本地服务器启动前，深度递归扫描全工程并把所有模块完整编译打包成单体 Bundle 才能启动**（随着项目增大冷启动慢至数分钟）；而 **Vite 在开发环境充分利用了现代浏览器原生支持的 `Native ESM` 特性，跳过全量打包过程，只有当浏览器真正请求某个模块时才按需就地编译**，配合底层基于 Go 语言编写的 **esbuild** 预构建依赖，实现毫秒级瞬间秒开。

---

### 详细回答

#### 1. Webpack 本地启动模型（Bundle 模式）
- **流程**：入口 Entry $\to$ 逐个解析 AST 模块图谱 $\to$ Loader 递归转译 $\to$ 生成 Chunk $\to$ 输出 Bundle 内存盘 $\to$ 启动开发服务器；
- **痛点**：若项目有上万个文件，即使你只修改了其中一个按钮的颜色，每次启动和 HMR 重新构建的耗时都极其漫长。

#### 2. Vite 本地启动模型（No-Bundle + 原生 ESM）
- **流程**：利用 `esbuild` 耗时数十毫秒将三方依赖预打包为 ESM 缓存；瞬间启动本地 Dev Server；
- 当你在浏览器输入网址，浏览器解析到 `<script type="module" src="/src/main.ts">`；
- 浏览器向本地 Vite 服务器发起 HTTP 请求拉取 `/src/main.ts`；
- Vite 拦截该单文件 HTTP 请求，进行极速单个文件即时转译并返回给浏览器；
- **优势**：冷启动时间完全与项目规模大小（无论 10 个文件还是 10,000 个文件）完全脱钩！

#### 3. 生产打包环境的考量
- 在生产构建（`npm run build`）时，Vite 依然使用成熟的 **Rollup** 进行全局 Tree-shaking、代码分割和资源压缩打包，确保在复杂生产网络下的最佳加载性能。

---

### 核心代码片段（极简记法）

```html
<!-- Vite 本地开发利用浏览器原生模块化机制 -->
<script type="module" src="/src/main.ts"></script>
```

---

### 面试加分项

- **对生产环境下 Rollup vs 现代 Turbopack / Rolldown 演进的展望**：指出 Vite 目前开发（esbuild）与生产（Rollup）存在两套工具链的一致性隐患。目前尤雨溪团队正在全力打造基于 Rust 编写的纯原生打包器 **Rolldown**（100% 兼容 Rollup API 且拥有 Rust 极限性能），未来将实现开发与生产环境统一由 Rust 原生驱动，构建速度再跃迁一个数量级。""",
        "followups": """## 追问 1：为什么 Vite 在开发环境不直接让浏览器加载裸模块（如 import React from 'react'）？

**回答要点**：
因为浏览器原生 ESM 不支持裸模块导入路径（Bare Module Imports），直接写 `import React from 'react'` 会报错；
Vite 在预构建阶段会重写路径为带有具体相对路径的 `/node_modules/.vite/deps/react.js`。

---

## 追问 2：热模块替换（HMR）在 Vite 中为什么能做到恒定毫秒级更新？

**回答要点**：
在 Webpack 中热更新需要重新计算整个关联的 Chunk 链；
而在 Vite 中，由于模块天然解耦，当修改一个文件时，Vite 只需要精确使当前这一个模块的原生浏览器缓存失效，并通知浏览器重新发起该单文件的 HTTP 请求，复杂度恒定为 $O(1)$。"""
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

print(f"Generated {len(DATA)} questions successfully (fe-scenario-051 ~ fe-scenario-068)!")
