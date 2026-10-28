### 一句话总结

Vue 3 是一次脱胎换骨的架构重写，核心优势凝聚为四点：**“更好的代码组织与逻辑复用（Composition API 终结了 Mixin 命名冲突与来源模糊地狱）”**、**“更极致的运行与打包性能（Proxy 代理响应式、虚拟 DOM 静态提升 PatchFlags、按需摇树 Tree-shaking 使包体积缩减约 50%）”**、**“原生 100% 强类型 TypeScript 支持”**、以及**“更强大的原生新特性（Fragment 支持多根节点、Teleport 任意传送门、Suspense）”**。

---

### 详细回答

#### 1. 逻辑复用：Composition API vs Options API
- **Vue 2 (Options API)**：一个业务功能被硬生生割裂撕碎在 `data`、`methods`、`computed`、`mounted` 四处，代码超过 500 行后上下翻滚查找痛不欲生；
- **Vue 3 (Composition API)**：将同一业务功能相关的所有响应式变量与函数聚合在一个自定义组合式函数（`useUser()`）中，按功能模块独立收拢与随意复用。

#### 2. 编译与运行性能大飞跃
- **静态提升（Hoist Static）**：模板中永远不变的静态纯 HTML 节点在编译期提升到渲染函数外部，每次重绘直接复用同一引用，零重构开销；
- **补丁标记（PatchFlags）**：Diff 算法只针对带有标记的动态节点（如只包含文本动态变动、只包含动态 class）进行靶向比对，完全跳过所有静态 DOM 比对。

#### 3. 架构解耦：自定义渲染器（createRenderer）
- Vue 3 核心与平台渲染逻辑彻底解耦，开发者可以轻松使用 Vue 语法去渲染 Canvas 图元、微信小程序、甚至 iOS/Android 原生 UI。

---

### 核心代码片段（极简记法）

```vue
<!-- Vue 3 <script setup> 现代极简开发范式 -->
<script setup>
import { ref, onMounted } from 'vue';

const count = ref(0);
const increment = () => count.value++;
</script>

<template>
  <!-- 原生支持多根节点 Fragment -->
  <h1>计数器: {{ count }}</h1>
  <button @click="increment">+1</button>
</template>
```

---

### 面试加分项

- **Tree-shaking 友好的底层重构**：指出在 Vue 2 中，`Vue.nextTick`、`Vue.observable` 等 API 全部挂载在 Vue 全局构造函数原型上，即使你一行没写，打包器也无法将它们剪掉；而在 Vue 3 中，几乎所有 API 均改为具名导出 `import { nextTick } from 'vue'`，未使用的功能在打包期被彻底剪切摇掉，极致纯净。
