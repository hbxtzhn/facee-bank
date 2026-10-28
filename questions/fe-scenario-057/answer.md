### 一句话总结

设计优秀通用组件遵循**“SOLID 原则与高内聚低耦合”**，核心贯穿六大维度：**“合理的 API 接口设计（受控与非受控兼顾、Props 命名符合心智直觉） + 极致的扩展性（插槽 Slot / Compound 组件复合模式） + 健全的无障碍无感体验（A11y 键盘导航） + 纯净样式与换肤隔离（Tailwind/CSS Module/CSS Vars） + 严格的 TypeScript 类型推导 + 完备的单元测试与文档”**。

---

### 详细回答

#### 1. 维度一：Props 契约设计（受控/非受控双模态）
- 同时支持 `value`（受控模式）与 `defaultValue`（非受控模式）；
- 内部封装 `useControllableValue` 统一抽象，向业务使用者提供极致灵活度。

#### 2. 维度二：复合组件设计模式（Compound Pattern）
- 拒绝搞出有 50 个 Props 的“配置膨胀巨石怪组件”；
- 采用父子复合拆分模式（类似 HTML 原生 `<select>` 与 `<option>`）：
  ```javascript
  <Modal>
    <Modal.Header title="提示" />
    <Modal.Body>{/* 自定义内容 */}</Modal.Body>
    <Modal.Footer />
  </Modal>
  ```

#### 3. 维度三：无障碍访问（A11y）与交互鲁棒性
- 弹窗必须支持 `Esc` 键自动退出；
- 支持 Tab 键在弹窗内部元素的焦点捕获与焦点锁定（Focus Trap）；
- 点击遮罩蒙层外部（Click Outside）自动收起。

---

### 核心代码片段（极简记法）

```typescript
// 通用组件标准 TypeScript Props 设计规范
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  icon?: React.ReactNode;
}
```

---

### 面试加分项

- **Headless UI（无头组件设计哲学）**：指出近些年国际顶尖开源界（如 Radix UI / TanStack Table）最前沿的架构趋势是 **Headless UI**：组件库**只封装核心复杂交互逻辑、状态机与 A11y 键盘规范，完全不写死任何 CSS 样式与 DOM 标签**，将样式控制权 100% 交由业务开发者自定义，彻底解决传统组件库样式难以覆盖魔改的痛点。
