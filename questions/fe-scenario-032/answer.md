### 一句话总结

rem 是相对于**页面根元素（`<html>`）的 `font-size` 的相对单位**。底层原理是**“动态根据屏幕宽度等比例修改根字号，使 1rem 始终代表屏幕宽度的固定百分比”**；在现代前端工程中，严禁人工口算，全部通过 **`postcss-pxtorem` 插件在打包编译期将 CSS 中的 px 自动转换为 rem**，开发者只需按设计稿像素无脑写 px。

---

### 详细回答

#### 1. 底层换算公式
- 假设设计稿宽度为 375px，约定标准根字号为 37.5px（即 $1	ext{rem} = 37.5	ext{px}$，正好是设计稿宽度的 1/10）；
- 元素在设计稿上量出宽度为 150px，则换算为：$150 / 37.5 = 4	ext{rem}$；
- 当页面运行在 414px 宽度的手机上时，通过 JS 将根字号动态更新为 $414 / 10 = 41.4	ext{px}$；
- 此时元素在界面上的渲染宽度为：$4	ext{rem} 	imes 41.4	ext{px} = 165.6	ext{px}$，实现了完美的等比自适应放大！

#### 2. 工程化自动化：postcss-pxtorem
- 开发者在代码里直接写：`width: 150px;`；
- PostCSS 自动转译为：`width: 4rem;`。

---

### 核心代码片段（极简记法）

```javascript
// postcss.config.js 自动化转换配置
module.exports = {
  plugins: {
    'postcss-pxtorem': {
      rootValue: 37.5, // 对应设计稿基准字号 (375宽度的1/10)
      propList: ['*'], // 所有 CSS 属性均转换
      selectorBlackList: ['.ignore'] // 忽略特定类名转换
    }
  }
};
```

---

### 面试加分项

- **纯 CSS 的 vw 方案替代 rem**：指出 rem 依赖 JS 动态修改 DOM 容易引起首屏字体闪烁。现代移动端推荐更直接的 **`postcss-px-to-viewport` 方案**：将 px 直接转为 `vw`，完全不需要执行任何 JS 代码，纯 CSS 实现原生视口等比缩放。
