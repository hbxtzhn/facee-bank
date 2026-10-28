### 一句话总结

核心区别在于**“表单数据的驱动源头与控制权在谁手里”**。**受控组件**的数据完全由 React 组件的 `state` 强控，输入改变必须通过 `onChange` 更新 state 反哺回输入框，是 **“单一事实来源（Single Source of Truth）”**；而**非受控组件**的数据完全由浏览器原生 DOM 节点自己管理内部状态，React 仅在需要提交时通过 `ref` 获取当前原生 DOM 的实时值。

---

### 详细回答

#### 1. 受控组件（Controlled Component）
- **特征**：`<input value={name} onChange={e => setName(e.target.value)} />`；
- **优势**：
  1. 能够对每一次用户击键做即时校验、格式化（如只能输入数字、输入手机号自动加空格）；
  2. 根据当前输入内容即时控制“提交按钮”是否置灰禁用；
- **劣势**：每一次打字都会触发 React 组件的一次重新渲染。

#### 2. 非受控组件（Uncontrolled Component）
- **特征**：`<input defaultValue="Jack" ref={inputRef} />`；
- **优势**：
  1. 打字输入完全由浏览器底层原生驱动，零 React 重新渲染，极高性能；
  2. 极度适合接入旧版第三方 jQuery 插件或处理大表单；
- **强制必须使用非受控组件的场景**：文件上传输入框 `<input type="file" />`，因为由于浏览器安全限制，文件路径是只读的，React 无法程序化给其赋 `value`。

---

### 核心代码片段（极简记法）

```javascript
// 1. 受控组件：React State 驱动
const [val, setVal] = useState('');
<input value={val} onChange={e => setVal(e.target.value)} />

// 2. 非受控组件：DOM Ref 读取
const inputRef = useRef(null);
<input defaultValue="初始值" ref={inputRef} />
// 提交时直接读取：const currentVal = inputRef.current.value;
```

---

### 面试加分项

- **大型重型表单性能治理（react-hook-form 的哲学）**：指出在几百个表单项的企业级复杂大表单中，全受控组件会导致打字极度卡顿。现代主流库（如 `react-hook-form`）全面转向**基于非受控组件 + Ref 订阅**架构，大幅削减重绘次数，性能极度炸裂。
