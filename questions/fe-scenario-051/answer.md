### 一句话总结

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

- **React 18+ 官方实验性 <Activity>（Offscreen）**：指出 React 团队正在研发底层并发原生支持的 `<Activity mode={isActive ? 'visible' : 'hidden'}>`。当切换为 hidden 时，React 不仅将 DOM display 设为 none，更会在 Fiber 调度层直接**降低该子树的任务优先级并暂停所有副作用触发**，是真正意义上的官方 Keep-Alive。
