### 一句话总结

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

- **ESLint 规则与 React 为什么不采用基于函数名的 Key 寻址？** 指出官方推出了 `eslint-plugin-react-hooks` 在编译写码时进行强制 AST 静态检测。React 团队之所以不用命名 Map 存储 Hook，是为了避免命名冲突、强制开发者遵守原子化拆分，并杜绝每次调用传递额外命名参数的运行时开销。
