### 一句话总结

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
  2. 函数作为 props 传递给了被 `React.memo` 优化过的重量级子组件，或者该函数被列入了另一个 `useEffect` 的依赖数组中作为触发源。
