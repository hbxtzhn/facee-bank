### 一句话总结

展开收起的核心是**“内容多行截断展示 + 精准探测是否真正发生了文本溢出”**。纯展示可使用 CSS 的 `-webkit-line-clamp`；交互上通过对比 **`scrollHeight > clientHeight`（或 Range 测量）** 动态决定是否展示“展开”按钮，展开时移除截断类名或通过 CSS Grid 实现丝滑的高度过渡动画。

---

### 详细回答

#### 1. 核心判断：到底该不该显示“展开”按钮？
- 如果文本本身只有 2 行，却依然显示了“展开”按钮，是严重的 UI Bug；
- **判断逻辑**：
  在元素被截断状态下，比较真实内容高度与可视高度：
  `const isOverflow = element.scrollHeight > element.clientHeight;`
  仅当 `isOverflow === true` 时才显示展开按钮。

#### 2. CSS 多行文本截断规范写法
```css
.clamped-text {
  display: -webkit-box;
  -webkit-line-clamp: 3; /* 限制展示 3 行 */
  -webkit-box-orient: vertical;
  overflow: hidden;
}
```

#### 3. 丝滑高度展开动画（CSS Grid 奇技淫巧）
- 传统 `max-height` 动画高度写死不精准；
- 现代最优解使用 CSS Grid 的 `grid-template-rows: 0fr -> 1fr` 过渡，无需 JS 计算具体像素即可实现任意高度的丝滑展开收起。

---

### 核心代码片段（极简记法）

```javascript
function useTextOverflow(ref, text) {
  const [canExpand, setCanExpand] = useState(false);

  useLayoutEffect(() => {
    const el = ref.current;
    if (el) {
      setCanExpand(el.scrollHeight > el.clientHeight); // 判断是否溢出
    }
  }, [text]);

  return canExpand;
}
```

---

### 面试加分项

- **浮动环绕（Float）实现展开按钮无缝嵌入文本尾部**：如果不希望展开按钮另起一行，而是像小说 App 一样紧跟在省略号 `...` 后面，可利用 CSS `float: right` 配合伪元素制造异形环绕排版。
