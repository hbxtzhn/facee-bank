### 一句话总结

离线优先 AI 应用采用 **TanStack Query（React Query）结合 `persistClient` 插件与离线突变队列（Offline Mutation Queue）**。以本地 IndexedDB 作为持久化二级缓存，在离线断网状态下由缓存即时响应会话历史；网络恢复后自动触发后台增量同步与失败任务自动回放。

---

### 详细回答

#### 1. 为什么 TanStack Query 契合离线优先？
- 内置开箱即用的网络状态感知：`networkMode: 'offlineFirst'`；
- 当网络断开时，请求不会报错，而是自动进入暂停挂起状态（`paused`）；
- 一旦浏览器触发 `online` 事件，自动无缝恢复请求。

#### 2. 持久化插件：createSyncStoragePersister
- 配置 `persistQueryClient`：将 React Query 内存中的 Query Cache 同步镜像写入 IndexedDB；
- 哪怕用户在飞机离线模式下冷启动页面，React Query 瞬间从 IndexedDB 载入上次的对话数据，实现零秒秒开。

#### 3. 离线提问暂存（Offline Mutations）
- 用户断网时输入问题并点击发送；
- 突变（Mutation）将提问追加至本地缓存中渲染，同时将网络任务存入离线持久化队列；
- 联网瞬间按顺序依次将队列任务推送到服务端。

---

### 核心代码片段（极简记法）

```javascript
import { QueryClient } from '@tanstack/react-query';
import { persistQueryClient } from '@tanstack/react-query-persist-client';
import { createIDBPersister } from './idbPersister';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      networkMode: 'offlineFirst', // 离线优先读取本地
      gcTime: 1000 * 60 * 60 * 24 * 7 // 保留7天本地缓存
    }
  }
});

// 持久化到 IndexedDB
persistQueryClient({ queryClient, persister: createIDBPersister() });
```

---

### 面试加分项

- **数据冲突仲裁（Last-Write-Wins vs 向量时钟）**：当用户在离线状态下编辑了某条消息，而在另一台联网设备上也修改了同一会话，重新联网时根据版本号和时间戳进行自动合并或提示冲突解决。
