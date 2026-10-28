### 一句话总结

微前端跨应用状态共享采用**“主应用全局发布订阅中心（EventBus / Actions） + 跨应用 CustomEvent 或 BroadcastChannel”**解耦通信。主应用作为单一真实数据源（SSOT）下发当前模型版本，子应用通过微前端生命周期 props 注入响应式 store 引用或监听全局事件，实现无框架绑定的跨技术栈即时联动。

---

### 详细回答

#### 1. 常见方案选型对比
- **方案 A：Qiankun 的 `initGlobalState`（官方标准）**：
  主应用提供全局状态管理，子应用通过 `onGlobalStateChange` 监听变化，`setGlobalState` 触发更新；
- **方案 B：CustomEvent 自定义事件（零依赖通用）**：
  基于 `window.dispatchEvent(new CustomEvent('ai:model_change', { detail }))` 广播，兼容任意框架；
- **方案 C：BroadcastChannel API（支持跨标签页）**：
  同源下多应用、多 Tab 均能瞬间感知模型版本切换。

#### 2. 数据流治理：防止死循环广播
- 规定：**模型版本的最终修改权由主应用收敛**。子应用若想变更模型，发起请求通知主应用更新，由主应用统一向下广播，避免多个子应用互相广播产生死循环更新。

---

### 核心代码片段（极简记法）

```javascript
// 主应用初始化全局模型状态
import { initGlobalState } from 'qiankun';

const actions = initGlobalState({ currentModel: 'gpt-4o' });

// 子应用内部监听变化
export async function mount(props) {
  props.onGlobalStateChange((state, prev) => {
    if (state.currentModel !== prev.currentModel) {
      updateLocalModelConfig(state.currentModel);
    }
  });
}
```

---

### 面试加分项

- **共享状态版本对齐（TypeScript 契约）**：跨应用的全局通信事件载荷容易产生字段拼写偏差。通过在 Monorepo 中发布 `@org/micro-events` 契约包，对 `detail` 参数进行编译期强类型约束。
