## 追问 1：computed 里面如果写了异步代码（比如在里面 setTimeout 或 await fetch），能拿到计算值吗？

**回答要点**：
完全拿不到！
`computed` 必须是纯同步返回。若异步返回一个 Promise，模板里最终拿到的只是一个 Promise 对象而非真实数据；针对异步计算需求可使用社区开源库 `@vueuse/core` 中的 `asyncComputed`。

---

## 追问 2：watch 监听一个深度嵌套对象时，如果不开启 deep: true 会发生什么？

**回答要点**：
普通 watch 只进行浅层属性指针的比对。若修改了对象内部深层嵌套属性（如 `user.info.age = 20`），由于 `user` 自身的内存引用地址并未改变，watch 不会触发；必须显式声明 `{ deep: true }` 开启全量深度递归侦听。
