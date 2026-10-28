### 一句话总结

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

- **为什么必须搭配 Reflect.get / set 使用？** 必须指出 Reflect 内部接收的 `receiver` 参数至关重要：当对象内部存在 getter 访问器属性且内部调用了 `this.otherProp` 时，传给 `Reflect.get` 的 receiver 能够确保 `this` 正确指向当前创建的 Proxy 代理对象，而不是原始对象，从而杜绝依赖收集发生遗漏丢失！
