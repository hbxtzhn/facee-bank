### 一句话总结

减少 if-else 的核心是**“由面向过程的过程判断升级为面向对象的规则驱动”**。最立竿见影的四大重构武器是：**对象映射表（Map / Dictionary 策略模式）**替代条件分支、**责任链模式（Pipeline / Middleware）**处理多级复杂校验、**多态（Polymorphism）与组合**消灭类型判断，以及**早期返回（Guard Clauses / 提前 return）**减少深层嵌套。

---

### 详细回答

#### 1. 武器一：表驱动法 / 对象映射（Strategy Pattern，最常用）
- **反例**：
  ```javascript
  if (type === 'text') renderText();
  else if (type === 'image') renderImage();
  else if (type === 'audio') renderAudio();
  ```
- **正解**：建立对象策略字典，将逻辑复杂度从 $O(N)$ 降到 $O(1)$：
  ```javascript
  const RENDER_MAP = {
    text: renderText,
    image: renderImage,
    audio: renderAudio
  };
  (RENDER_MAP[type] || defaultRender)();
  ```

#### 2. 武器二：卫语句（Guard Clauses / 提前 Return）
- 将多层嵌套的嵌套条件拍平，优先判断异常情况并立即 return，使主干业务代码永远保持在最外层 0 缩进。

#### 3. 武器三：配置驱动与策略函数
- 将复杂的联动判断转换为数组规则过滤：`rules.find(r => r.predicate(input))?.execute()`。

---

### 核心代码片段（极简记法）

```javascript
// 策略模式取代几十个 if-else 分支
const statusHandlers = {
  PENDING: () => console.log('处理等待中'),
  APPROVED: () => console.log('审核通过'),
  REJECTED: () => console.log('已拒绝')
};

function handleStatus(status) {
  const handler = statusHandlers[status] || statusHandlers.PENDING;
  handler();
}
```

---

### 面试加分项

- **可选链（Optional Chaining `?.`）与空值合并（Nullish Coalescing `??`）**：在数据解构取值时，一行 `user?.profile?.address ?? '默认地址'` 可以瞬间消灭传统代码中五六层冗长判空的 `if (user && user.profile && ...)` 丑陋代码。
