### 一句话总结

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

- **Vue 3 新增的 watchEffect 与 watch 的区别**：指出 `watch` 需要显式指定监听哪几个变量；而 `watchEffect` 无需显式传入依赖，它会在回调执行时**自动追踪并收集用到的所有响应式变量**，且默认初次即刻无条件执行一次，语法更加紧凑现代化。
