## 追问 1：有时候希望某些属性（比如边框 1px border）保持绝对物理 1 像素，不要被转成 rem，怎么配置？

**回答要点**：
1. 在样式属性中书写大写字母单位，如 `border: 1PX solid #ccc;`（PostCSS 默认只匹配小写 px，大写会被智能跳过）；
2. 或者在插件配置的 `propList` 中排除 `border` 相关属性。

---

## 追问 2：用户的安卓系统设置了“超大辅助字体”，导致计算出来的 rem 界面排版全乱挤爆，怎么防守？

**回答要点**：
安卓微信等内置环境会强行放大网页根字号。
防守代码：在设置完 `html.style.fontSize` 后，立即通过 `window.getComputedStyle(document.documentElement).fontSize` 测量实际渲染字号；若发现实际字号 > 设定字号，除以该缩放比例做反向除法抵消。
