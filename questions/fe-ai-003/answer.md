### 一句话总结

利用 TypeScript 4.1+ 的**模板字面量类型（Template Literal Types）结合条件类型递归推导**，从模板字符串中静态提取 `{variable}` 占位符联合类型；配合高阶函数与 Proxy，在编译期强制要求必须传入所有匹配的插值参数，漏传或错传时直接静态报错。

---

### 详细回答

#### 1. 静态提取占位符：模板字面量递归
- 定义泛型类型 `ExtractParams<T>`：
  - 模式匹配 `${string}{${infer Param}}${infer Rest}`；
  - 递归提取所有 `{param}` 并组成联合类型，例如模板 `"Hello {name}, your role is {role}"` 静态推导出 `'name' | 'role'`。

#### 2. 参数类型绑定与必填校验
- 将推导出的联合类型转化为 Record 对象：`Record<ExtractParams<T>, string | number>`；
- 在函数签名中强约束入参，漏填任何一个参数在 VS Code 中立刻红线报错。

#### 3. 运行时正则替换与默认值处理
- 运行时通过正则 `/\{(\w+)\}/g` 遍历匹配，若传入参数中包含该 key 则替换，若未传入则尝试使用预置默认值字典，否则抛出运行时异常。

---

### 核心代码片段（极简记法）

```typescript
// 1. 静态递归提取 {variable}
type ExtractParams<T extends string> = 
  T extends `${string}{${infer Param}}${infer Rest}` 
    ? Param | ExtractParams<Rest> 
    : never;

// 2. 类型安全的渲染函数
function renderPrompt<T extends string>(
  template: T,
  vars: Record<ExtractParams<T>, string | number>
): string {
  return template.replace(/\{(\w+)\}/g, (_, key) => String((vars as any)[key]));
}

// ✅ 编译通过
renderPrompt("我是{role}，帮我分析{topic}", { role: "前端架构师", topic: "性能优化" });

// ❌ 编译报错：缺少属性 'topic'
// renderPrompt("我是{role}，帮我分析{topic}", { role: "前端架构师" });
```

---

### 面试加分项

- **支持默认值语法推导**：可扩展类型支持 `{name=默认值}` 语法，通过条件类型解析提取出可选参数类型 `Partial<ExtractDefaultParams<T>>`，实现更强大的工业级模板引擎。
