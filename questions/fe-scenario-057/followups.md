## 追问 1：如何确保外部用户传入的 ref 能够精准绑定到你的通用组件内部的真实原生 DOM 上？

**回答要点**：
使用 **`React.forwardRef`** 进行 Ref 转发；若需要向外部暴露定制的受控方法（如 `formRef.current.validate()`），配合 **`useImperativeHandle`** 进行安全的方法精简暴露。

---

## 追问 2：组件库如何做自动化视觉回归测试（Visual Regression Testing）？

**回答要点**：
基于 Storybook 配合 Playwright / Chromatic，在 CI 流水线中自动为每个组件状态截取像素图，与基线截图逐像素比对（Pixel Diff），变动超过 0.1% 立即报错拦截阻断合并。
