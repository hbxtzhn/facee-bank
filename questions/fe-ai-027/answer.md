### 一句话总结

对话历史版本控制采用**“有向无环图（DAG）/ 对话树结构”**建模。每个消息节点维护唯一 `id`、`parentId` 与 `childrenIds`；“重新生成”或“分支编辑”本质是在父节点上创建子分支，前端通过**指针（Current Leaf Pointer）**追踪当前活跃的会话路径，实现类似 Git 的时光倒流、分支切换与对比合并。

---

### 详细回答

#### 1. 传统线性数组建模的致命缺陷
- 绝大多数应用将消息存为数组 `Message[]`；
- 当用户对第 3 条消息点击“重新生成”时，旧回答会被粗暴覆盖，用户无法查看之前的回答，也无法进行多分支探索。

#### 2. 对话树（Tree-based Architecture）核心设计
- **节点定义**：
  ```typescript
  interface Node {
    id: string;
    parentId: string | null;
    content: string;
    children: string[]; // 支持多个子分支
  }
  ```
- **当前路径回溯**：
  给定当前叶子节点 ID，自底向上通过 `parentId` 递归查找，即可在线性时间 $O(D)$ 内提取出当前分支的完整对话上下文。

#### 3. 分支切换交互
- 在拥有多个分支的节点下方展示翻页器组件：`< 2 / 3 >`；
- 点击切换时，更新当前激活的叶子节点指针，视图瞬间切换为对应分支。

---

### 核心代码片段（极简记法）

```javascript
// 获取当前激活分支的线性消息列表
function getActiveBranchMessages(nodesMap, currentLeafId) {
  const branch = [];
  let curr = nodesMap[currentLeafId];

  while (curr) {
    branch.unshift(curr);
    curr = curr.parentId ? nodesMap[curr.parentId] : null;
  }
  return branch; // 返回给 UI 渲染的平铺数组
}
```

---

### 面试加分项

- **分支 Diff 对比视图**：允许用户选择同一个问题的两个不同模型生成分支，双栏并排渲染，直观对比不同 Prompt 或不同模型的生成质量。
