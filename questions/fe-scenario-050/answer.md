### 一句话总结

Context 导致全量重刷的核心根源是**“Context 消费端是基于引用的粗粒度穿透订阅，无法按需订阅局部属性”**。三大防线：**“拆分多个细粒度 Context（按读写频次分离）”**、**“通过 `children` 属性或 `React.memo` 将不需要更新的中间层级隔离开”**、以及在生产级复杂场景中**“改用基于 `useSyncExternalStore` 的外部原子化状态库（如 Zustand / Jotai）”**。

---

### 详细回答

#### 1. 误区剖析：为什么 React.memo 挡不住 Context？
- 如果子组件内部直接调用了 `useContext(MyContext)`；
- 只要 Provider 的 `value` 发生引用变动，**任何 `React.memo` 都会被直接穿透失效！**消费了该 Context 的组件必定强制执行重渲染。

#### 2. 防御策略一：通过 children 传参（组件组合解耦）
- 如果 Provider 内部有状态更新，包裹在其 JSX 标签内的子元素若是作为 `children` 传入的：
  ```javascript
  function MyProvider({ children }) {
    const [theme, setTheme] = useState('dark');
    return <ThemeContext.Provider value={theme}>{children}</ThemeContext.Provider>;
  }
  ```
- 此时 `children` 是在父级组件创建好的 React Element 引用，只要父级不重刷，`children` 对应的中间层组件直接跳过重绘！

#### 3. 防御策略二：读写分离（Context Splitting）
- 将高频变化的“状态（State）”与低频不变的“修改函数（Dispatch）”拆分为两个独立的 Context：
  `ThemeStateContext` 与 `ThemeDispatchContext`；
  仅需要触发点击操作的按钮只订阅 Dispatch，完全不因 State 的变动而触发重刷。

---

### 核心代码片段（极简记法）

```javascript
// 拆分为只读状态与操作动作两个 Context
const CountStateContext = createContext();
const CountDispatchContext = createContext();

function CounterProvider({ children }) {
  const [count, dispatch] = useReducer(reducer, 0);
  return (
    <CountStateContext.Provider value={count}>
      <CountDispatchContext.Provider value={dispatch}>
        {children} {/* 保持不变，中间层级不重刷 */}
      </CountDispatchContext.Provider>
    </CountStateContext.Provider>
  );
}
```

---

### 面试加分项

- **use-context-selector 提案实现**：原生 Context 不支持选择器（Selector）。可通过社区知名库 `use-context-selector`，让组件仅在 `useContextSelector(Ctx, state => state.user.name)` 关注的单一属性变化时才重刷，实现精准更新。
