## 追问 1：Vue 3 的 ref 和 reactive 在底层有什么区别？

**回答要点**：
- `reactive` 底层直接使用 `Proxy` 只能代理引用对象类型；
- `ref` 专门为了处理基础原始类型（数字、字符串），底层封装了一个包含 `get value()` 与 `set value()` 的类对象（Object Accessor），若是对象则内部再转调 `reactive`。

---

## 追问 2：Proxy 的唯一缺点是什么？

**回答要点**：
完全无法在不支持 ES6 的低版本旧浏览器（IE11）中通过 Polyfill 进行向下兼容（因为 Proxy 是语言语法底层的宿主代理，没有任何 ES5 语法能完美模拟它的拦截能力）。
