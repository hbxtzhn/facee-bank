### 一句话总结

状态快照系统采用**“状态树纯 JSON 序列化 + 不可序列化对象（如 AbortController）解耦映射 + 版本迁移适配器”**。将整个会话的状态、参数、消息列表提取为纯数据 Schema 存入 IndexedDB/文件导出；恢复时通过反序列化工厂函数重建非纯数据逻辑对象，实现跨设备导出导入和意外刷新瞬时恢复。

---

### 详细回答

#### 1. 核心挑战：非纯数据对象的剥离
- 会话状态中包含大量的函数、网络句柄和不可序列化对象（如 `AbortController`、`EventSource` 实例、`AudioContext`）；
- 快照设计原则：**存储只存纯数据（State），逻辑和网络连接由运行时（Runtime）按需重建**。

#### 2. 快照结构体设计
```typescript
interface ChatSnapshotV1 {
  version: 1;
  snapshotId: string;
  createdAt: number;
  sessionMeta: { id: string; model: string; temperature: number };
  messages: Array<{ id: string; role: string; content: string; status: 'completed' | 'interrupted' }>;
}
```

#### 3. 版本迁移升级（Migration Pipeline）
随着业务迭代，快照 Schema 可能会改变（如新增了 `tools` 字段）。设计版本迁移函数管道：
若读取到 `version === 1`，自动经过 `migrateV1ToV2(snapshot)` 转换为最新结构，防止旧版本会话导入崩溃。

---

### 核心代码片段（极简记法）

```javascript
// 导出快照（过滤掉非纯数据）
function createSnapshot(storeState) {
  return JSON.stringify({
    version: 2,
    timestamp: Date.now(),
    messages: storeState.messages.map(m => ({ id: m.id, role: m.role, text: m.text })),
    settings: storeState.settings
  });
}

// 恢复快照
function restoreSnapshot(jsonStr, store) {
  const data = JSON.parse(jsonStr);
  const validData = runMigrations(data); // 执行版本升级校验
  store.setState({ messages: validData.messages, settings: validData.settings });
}
```

---

### 面试加分项

- **流式中断恢复状态机**：如果保存快照时某条消息恰好处于流式生成一半的状态，快照将其标记为 `status: 'interrupted'`，恢复后界面渲染“生成中断”卡片并显示“继续生成”按钮，点击后自动发起断点续传。
