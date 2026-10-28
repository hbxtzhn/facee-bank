### 一句话总结

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

- **类组件目前依然无可替代的唯一场景**：指出目前 React 中唯一的例外是**“错误边界（Error Boundary）”**。React 官方至今尚未提供任何能捕获子组件渲染崩溃的 Hook，实现 `componentDidCatch` 和 `getDerivedStateFromError` 依然**必须手写类组件**。
