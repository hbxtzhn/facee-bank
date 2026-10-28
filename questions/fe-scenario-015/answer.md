### 一句话总结

高定制拖拽推荐采用**“鼠标事件模拟（`mousedown` 记录起点 $	o$ `document.onmousemove` 计算偏移 $	o$ `document.onmouseup` 释放解绑）”**。移动过程中利用 **CSS `transform: translate3d`** 修改坐标以触发 GPU 合成层加速，杜绝修改 `top/left` 引发的高频回流；监听必须绑定在 `document` 上以防止鼠标快速移动时脱轨脱标。

---

### 详细回答

#### 1. 原生 HTML5 Drag & Drop API 的缺陷
- 专为文件拖入或跨应用拖放设计；
- 拖拽过程中会自带半透明的系统默认幽灵残影（Ghost Image），样式极难深度定制；
- 拖动时无法实时平滑获取鼠标绝对像素坐标做复杂吸附与碰撞检测。

#### 2. 鼠标事件三部曲（最佳实战）
1. **`mousedown`（在目标元素上）**：
   记录鼠标按下时的起始坐标 $(startX, startY)$ 与元素当前偏移量；
2. **`mousemove`（必须绑定在 `document` 上）**：
   - 为什么不绑在元素上？若鼠标移动过快划出元素边缘，事件会瞬间断档失效；
   - 计算偏移差值 $\Delta X = clientX - startX$；
   - 更新位移：`el.style.transform = \`translate3d(\${x}px, \${y}px, 0)\``；
3. **`mouseup`（必须绑定在 `document` 上）**：
   清理并注销 `document` 上的 mousemove 与 mouseup 监听器，释放内存。

---

### 核心代码片段（极简记法）

```javascript
function makeDraggable(el) {
  el.addEventListener('mousedown', (e) => {
    let startX = e.clientX - el.offsetLeft;
    let startY = e.clientY - el.offsetTop;

    function onMove(moveEvent) {
      el.style.left = `${moveEvent.clientX - startX}px`;
      el.style.top = `${moveEvent.clientY - startY}px`;
    }

    function onUp() {
      document.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseup', onUp);
    }

    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
  });
}
```

---

### 面试加分项

- **边界约束与磁吸对齐（Snapping）**：在计算坐标时，通过 `Math.max(0, Math.min(x, maxBound))` 限制拖动不能超出屏幕可视区；当元素距离屏幕边缘小于 10px 时自动将坐标吸附至边缘，提供极致工业设计细节。
