## 追问 1：infer 和直接索引访问 T['choices'][0]['delta']['content'] 相比，优势在哪？

**回答要点**：
直接索引访问要求结构完全已知且中间每一层都必须非空，如果 `choices` 为空数组或者格式可能是其他分支，索引访问直接报错；而 `infer` 配合条件类型具有**模式匹配容错性**，匹配失败会优雅走 `never` 兜底，不会导致编译崩溃。

---

## 追问 2：infer 在提取函数返回值的 Promise 泛型时怎么用？

**回答要点**：
编写 `type UnpackPromise<T> = T extends Promise<infer U> ? U : T`，或者直接使用内置的 `Awaited<T>`，底层原理完全相同。
