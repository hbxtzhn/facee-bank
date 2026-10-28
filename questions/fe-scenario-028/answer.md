### 一句话总结

划词菜单的核心是**“利用 `window.getSelection()` 获取当前选区对象与坐标范围，并在 `contextmenu`（右键）或 `mouseup`（划选完毕）事件中弹出绝对定位操作框”**。通过 `selection.getRangeAt(0).getBoundingClientRect()` 获取选中文字在视口中的精确位置，结合 `e.preventDefault()` 阻止浏览器默认右键菜单，实现高仿 Medium / 飞书的划词悬浮菜单。

---

### 详细回答

#### 1. 核心 API 链路
1. **`window.getSelection()`**：获取浏览器全局的 Selection 选区对象；
2. **`selection.toString().trim()`**：判定用户是否真正选中了有效文字（若为空字符串说明用户只是普通点击，不弹菜单）；
3. **`range.getBoundingClientRect()`**：提取选中文字矩形区域的 `top`, `bottom`, `left`, `width` 物理视口像素坐标；
4. **阻止原生右键**：在 `contextmenu` 事件中调用 `e.preventDefault()`。

#### 2. 定位计算逻辑
- 弹窗菜单通常居中展示在选中文字的上方：
  - `menuTop = rect.top + window.scrollY - menuHeight - 8;`
  - `menuLeft = rect.left + window.scrollX + (rect.width / 2) - (menuWidth / 2);`

---

### 核心代码片段（极简记法）

```javascript
document.addEventListener('contextmenu', (e) => {
  const selection = window.getSelection();
  const selectedText = selection.toString().trim();

  if (selectedText) {
    e.preventDefault(); // 阻止浏览器原生右键菜单
    const range = selection.getRangeAt(0);
    const rect = range.getBoundingClientRect();

    // 绝对定位弹出自定义划词菜单
    showCustomMenu({
      x: rect.left + rect.width / 2,
      y: rect.top - 10,
      text: selectedText
    });
  }
});
```

---

### 面试加分项

- **边界碰撞保护（Viewport Collision）**：如果用户划选的是屏幕最顶部或最左侧的文字，菜单如果继续往上弹会被浏览器窗口截断隐藏。必须编写边界碰撞检测：若 `rect.top < menuHeight`，自动反转菜单弹出方向（翻转显示在选中文字的下方）。
