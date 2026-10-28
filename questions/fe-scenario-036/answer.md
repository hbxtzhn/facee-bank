### 一句话总结

折叠面板的核心难点是**“从 `height: 0` 到自适应内容 `height: auto` 之间无法直接应用 CSS transition 动画”**。最现代的纯 CSS 方案是采用 **CSS Grid 的 `grid-template-rows: 0fr -> 1fr` 魔法过渡**；JS 方案采用获取 `scrollHeight` 动态赋固定像素高；语义化场景亦可直接利用 HTML5 原生 `<details>` 与 `<summary>` 标签零 JS 实现。

---

### 详细回答

#### 1. 传统高度动画的痛点
- 如果写 `transition: height 0.3s; height: 0 -> height: auto;`，浏览器**根本不会产生任何动画**，而是生硬地瞬间闪现；
- 旧解法是设一个很大的 `max-height: 500px`，但会导致展开和收起时动画速度极其不匀速、存在明显滞后卡顿。

#### 2. 现代纯 CSS 最优解：CSS Grid 0fr 转 1fr
- 外层包裹容器设为 Grid 布局：
  ```css
  .accordion-content {
    display: grid;
    grid-template-rows: 0fr;
    transition: grid-template-rows 0.3s ease-out;
  }
  .accordion-content.expanded {
    grid-template-rows: 1fr; /* 丝滑过渡到内容实际撑开高度！ */
  }
  .accordion-inner {
    overflow: hidden; /* 内部子元素必须 overflow: hidden */
  }
  ```

#### 3. HTML5 原生语义化标签：`<details>`
- 浏览器自带展开收起行为，无需任何 JS 状态维护；
- 现代 Chrome 120+ 原生支持给 `details::details-content` 添加过渡动画。

---

### 核心代码片段（极简记法）

```html
<!-- 原生无需一行 JS 的手风琴折叠卡片 -->
<details>
  <summary>点击展开查看常见问题</summary>
  <p>这里是折叠的详细内容，浏览器原生支持...</p>
</details>
```

---

### 面试加分项

- **手风琴互斥模式（Accordion Mutex）**：若要求“同一时刻最多只能展开一个面板，展开 A 时自动折叠 B”，原生 `<details>` 仅需加上 `name="faq-group"` 属性，同名 details 标签由浏览器内核原生自动互斥互锁，体验绝佳。
