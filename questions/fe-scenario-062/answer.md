### 一句话总结

二者混用会造成**“执行优先级混乱引发的巨大渲染性能浪费甚至语法报错 Bug”**。**Vue 2 中 `v-for` 优先级高于 `v-if`**，导致即使全列表只需展示 1 项，Vue 也会把全量 1000 项无脑遍历一遍再逐个判断是否显示，性能极度浪费；而在 **Vue 3 中颠倒为 `v-if` 优先级高于 `v-for`**，导致执行 `v-if` 时循环变量根本尚未生成，直接抛出 `ReferenceError: item is not defined` 崩溃。最佳实践是**使用 `computed` 提前过滤数据列表，或外层包裹 `<template>` 标签解耦**。

---

### 详细回答

#### 1. Vue 2 的惨痛代价（性能黑洞）
- 开发者意图：只渲染已完成的任务；
  ```html
  <li v-for="item in 10000_items" v-if="item.isDone">{{ item.name }}</li>
  ```
- **编译结果**：编译生成的渲染函数中，循环包裹着条件判断。必须执行 10000 次虚拟节点创建与判断，首屏严重卡顿掉帧。

#### 2. Vue 3 的反转与报错
- Vue 3 调整了规则：`v-if` 拥有更高优先级；
- 当 `v-if="item.isDone"` 执行时，`item` 此时还在后面的 `v-for` 中未定义，控制台直接疯狂报错报红。

#### 3. 官方推荐两大约束正解
- **解法一：优先使用 computed 过滤（终极推荐）**：
  ```javascript
  const doneItems = computed(() => items.value.filter(item => item.isDone));
  ```
  然后在模板中直接纯净循环：`<li v-for="item in doneItems" :key="item.id">`。
- **解法二：外层 template 解耦分级**：
  若只是想控制整张列表是否展示，在外层包裹 `<template v-if="showList">`。

---

### 核心代码片段（极简记法）

```html
<!-- ✅ 优雅规范解耦：使用 template 标签包裹分层 -->
<template v-if="shouldShowList">
  <div v-for="item in list" :key="item.id">
    {{ item.name }}
  </div>
</template>
```

---

### 面试加分项

- **ESLint 工业化拦截规范**：在团队工程中配置官方插件 `eslint-plugin-vue`，开启规则 `'vue/no-use-v-if-with-v-for': 'error'`，在研发保存代码时直接通过 AST 静态语法树拦截报警，从工程工具链路杜绝该低级错误流入代码库。
