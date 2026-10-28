### 一句话总结

CSS 3D 翻牌的核心是**“3D 透视舞台（`perspective`） + 保留 3D 空间（`transform-style: preserve-3d`） + 背面隐藏（`backface-visibility: hidden`）”**。将卡片容器作为 3D 旋转体，正反两面通过绝对定位重叠并让背面预先 `rotateY(180deg)`；当 Hover 或激活时让容器 `rotateY(180deg)`，两面同时翻转，原本隐藏的背面顺理成章转到正面展现。

---

### 详细回答

#### 1. 核心三大 CSS 属性
- **`perspective: 1000px;`**：必须加在**最外层父级舞台**上，给视网膜提供“近大远小”的真实 3D 空间透视深度；
- **`transform-style: preserve-3d;`**：必须加在**旋转卡片容器**上，指示子元素要在 3D 空间中保持立体层级，否则子元素会被强制拍平成 2D 平面；
- **`backface-visibility: hidden;`**：必须加在**正面与反面子元素**上，当元素背面朝向观察者时自动隐形不可见。

#### 2. 结构与旋转逻辑
- 正面（Front）：默认 `transform: rotateY(0deg);`；
- 反面（Back）：默认 `transform: rotateY(180deg);`（背对用户被 hidden 隐藏）；
- 容器触发翻转：`transform: rotateY(180deg);`。

---

### 核心代码片段（极简记法）

```css
.card-wrapper {
  perspective: 1000px; /* 3D 透视 */
}
.card {
  position: relative;
  transition: transform 0.6s;
  transform-style: preserve-3d; /* 维持 3D 空间 */
}
.card:hover {
  transform: rotateY(180deg); /* 翻转触发 */
}
.front, .back {
  position: absolute;
  inset: 0;
  backface-visibility: hidden; /* 核心：背面隐藏 */
}
.back {
  transform: rotateY(180deg); /* 预先背对 */
}
```

---

### 面试加分项

- **旋转轴心与毛刺抗锯齿（Anti-aliasing）**：在翻转动画执行中，文本或边缘容易产生毛刺闪烁。加上 `transform: translateZ(0)` 或 `will-change: transform` 能触发 GPU 硬件合成渲染，保持旋转全程无微小抖动与模糊。
