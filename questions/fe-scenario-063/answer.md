### 一句话总结

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

- **对 $parent / $children / $refs 强耦合反模式的警惕**：指出虽然可以通过 `ref` 或 `$parent` 直接强行修改父组件或子组件的内部私有变量，但这是严重的**反模式（Anti-pattern）**，严重破坏了单向数据流与组件封装独立性，一旦出 Bug 调用链根本无法追踪，严禁在正规通用组件中滥用。
