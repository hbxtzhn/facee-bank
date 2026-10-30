# AgentHub 项目面试题库 · 120 题

这组题按多端 Agent 知识平台的项目经历组织，针对 TypeScript、工具调用、Cloudflare、D1、FTS5、权限和可靠性交付准备项目深挖。每题包含场景、参考答案、两道有答案的追问、常见误区及同专题关联题。

## 使用边界

- 参考答案是机制说明与答题提纲，不是个人经历证明。只把自己确实完成且能解释的部分说成个人贡献。
- 题目同时包含现有设计所引出的原理题，以及明确标注的扩展题；混合检索、共享熔断、读副本、缓存等不能直接写成已上线功能。
- 本次只依据所提供的简历项目截图和本地项目材料整理，不代表审核了完整个人简历、线上数据或全部贡献归属。
- 公共题库不包含私有源码、源码位置、生产日志、运行配置、个人标识和原始聊天。核对资料留在独立本地记录；以下场景均采用原创抽象表述。
- 简历中的规模数据应按原统计日期和口径陈述；不把累计量当准确率，不编造性能提升、故障经历或个人完成量。

## 按简历亮点安排复习

| 简历亮点 | 先复习的题号 | 面试必须讲清楚 |
|---|---|---|
| 模型容错与安全备用 | 021–050 | 意图、执行、发送和确认是不同事实；为什么写后超时不能直接重放 |
| 前置检索与知识回答 | 051–070 | FTS5 边界、预检索触发、证据组织、权限过滤与质量评测 |
| 多群权限和隐私发布 | 071–090 | 可信身份、本群与全局权限、来源资格、落盘与派生公开边界 |
| TypeScript / Worker / D1 | 011–020、091–110 | 运行时差异、异步接口、协调状态、事务能力、迁移与回滚 |
| 运行记录和故障复盘 | 111–120 | 从实际证据还原时序、定位不确定状态、验证修复而不虚构事故 |
| 项目介绍与技术取舍 | 001–010 | 业务价值、个人职责、现状与目标架构、数字统计口径 |

## 建议复习顺序

第一轮先练 001、003、007、011、014、023、027、031、033、034、035、039、041、042、043、045、046、050、052、053、056、058、062、064、066、071、072、073、076、078、081、083、084、086、091、092、093、098、100、105、108、111、114、116、117、118、119、120。先能不看答案讲出关键因果，再扩展其余题。

第二轮每题用三到五分钟解释：输入与身份是什么，状态如何转移，在哪些条件下拒绝，失败后如何处理，用什么测试证明。随后练两道追问，检查是否只是背术语。

第三轮按第 120 题做四十五分钟模拟面试。选一个亲自处理的真实问题，准备正常流程、反例、回归测试和剩余限制；没有实测的数据明确说未验证。

## 全题索引

### 01 · 项目架构与表达

- [001 · 如何用两分钟介绍一个多端 Agent 知识服务平台？](../questions/agenthub-001/question.md)（简单）
- [002 · 这个平台与普通聊天机器人相比，系统边界有什么不同？](../questions/agenthub-002/question.md)（中等）
- [003 · 如何区分 Agent 核心与 QQ、网页、Worker 等宿主能力？](../questions/agenthub-003/question.md)（中等）
- [004 · 为什么网页通道和私聊记忆范围不能使用同一个字段表达？](../questions/agenthub-004/question.md)（中等）
- [005 · 为什么不能仅凭对话量和知识条数评价项目价值？](../questions/agenthub-005/question.md)（简单）
- [006 · 为什么 Agent 在线问答和长时间后台任务适合采用不同执行方式？](../questions/agenthub-006/question.md)（中等）
- [007 · 如何让公开知识中的结论能够追溯到真实讨论？](../questions/agenthub-007/question.md)（中等）
- [008 · 如何解释为什么先使用 FTS5，而不是直接建设向量数据库？](../questions/agenthub-008/question.md)（中等）
- [009 · 怎样向面试官说明技术债和架构演进，而不把目标架构当成现状？](../questions/agenthub-009/question.md)（中等）
- [010 · 如果群聊规模扩大十倍，你会如何判断先优化哪一层？](../questions/agenthub-010/question.md)（困难）

### 02 · TypeScript 与异步

- [011 · TypeScript 静态类型为什么不能替代工具参数的运行时校验？](../questions/agenthub-011/question.md)（简单）
- [012 · 如何用可辨识联合类型建模 Agent 事件和投递结果？](../questions/agenthub-012/question.md)（中等）
- [013 · 为什么工具副作用声明适合绑定对象身份，而不是只绑定工具名称？](../questions/agenthub-013/question.md)（中等）
- [014 · AsyncLocalStorage 如何隔离并发请求的身份和会话范围？](../questions/agenthub-014/question.md)（中等）
- [015 · 单线程 JavaScript 为什么仍然会出现竞态条件？](../questions/agenthub-015/question.md)（中等）
- [016 · Promise.all 和 Promise.allSettled 在工具并发中应该如何选择？](../questions/agenthub-016/question.md)（中等）
- [017 · 为什么 setTimeout 不能保证 Agent 恰好在指定时刻中止？](../questions/agenthub-017/question.md)（中等）
- [018 · 如何防止 AbortSignal 监听器在多轮 Agent 调用中泄漏？](../questions/agenthub-018/question.md)（中等）
- [019 · 为什么跨 Node 和 Worker 的公共 SQL 接口应保持异步且精简？](../questions/agenthub-019/question.md)（中等）
- [020 · 如何设计可测试的时钟、模型、工具和宿主依赖？](../questions/agenthub-020/question.md)（困难）

### 03 · Agent 与工具执行

- [021 · Agent、普通模型调用和固定工作流有什么区别？](../questions/agenthub-021/question.md)（简单）
- [022 · Function Calling 中模型和工具执行器各自负责什么？](../questions/agenthub-022/question.md)（中等）
- [023 · 怎样为不同角色构造最小工具集合？](../questions/agenthub-023/question.md)（中等）
- [024 · 如何设计 Agent 循环的停止条件？](../questions/agenthub-024/question.md)（中等）
- [025 · 为什么外部网页和检索文本必须作为数据处理？](../questions/agenthub-025/question.md)（中等）
- [026 · 工具结果过大时，如何避免挤爆上下文和掩盖重要证据？](../questions/agenthub-026/question.md)（中等）
- [027 · 怎样用执行状态区分模型请求、工具开始和工具完成？](../questions/agenthub-027/question.md)（困难）
- [028 · 如何设计工具调用的错误分类和反馈？](../questions/agenthub-028/question.md)（中等）
- [029 · 模型提供商之间的工具协议差异应如何封装？](../questions/agenthub-029/question.md)（中等）
- [030 · 如何在 Agent 框架升级时守住业务约束？](../questions/agenthub-030/question.md)（困难）

### 04 · 模型容错与副作用

- [031 · 为什么模型备用切换不能简单实现为 catch 后重新调用？](../questions/agenthub-031/question.md)（中等）
- [032 · 只读、外部只读、写入和未知工具应该如何区分？](../questions/agenthub-032/question.md)（简单）
- [033 · 为什么后续成功的只读工具不能清除早先写工具的风险？](../questions/agenthub-033/question.md)（困难）
- [034 · 并行只读工具尚未全部结束时，为什么不能立刻切换模型？](../questions/agenthub-034/question.md)（困难）
- [035 · 为什么发送开始后，模型层应停止备用切换？](../questions/agenthub-035/question.md)（中等）
- [036 · 模型故障、额度不足、认证失败和内容拒绝如何影响备用策略？](../questions/agenthub-036/question.md)（中等）
- [037 · 重试、备用模型、熔断和降级之间有什么区别？](../questions/agenthub-037/question.md)（中等）
- [038 · 如何设计熔断器的半开探测，避免恢复瞬间惊群？](../questions/agenthub-038/question.md)（困难）
- [039 · 备用模型为什么还要检查上下文容量和最小剩余时间？](../questions/agenthub-039/question.md)（中等）
- [040 · 为什么应用与 AI Gateway 的重试必须统一预算？](../questions/agenthub-040/question.md)（困难）

### 05 · 取消与可靠交付

- [041 · 为什么端到端截止时间比每层单独超时更重要？](../questions/agenthub-041/question.md)（中等）
- [042 · AbortController 能否保证正在执行的工具停止并回滚？](../questions/agenthub-042/question.md)（中等）
- [043 · 上下文 epoch 如何阻止重置前的旧答案晚到发送？](../questions/agenthub-043/question.md)（困难）
- [044 · 如何区分模型无进展和工具执行较慢？](../questions/agenthub-044/question.md)（中等）
- [045 · 消息发送超时为什么必须保留“结果不明”状态？](../questions/agenthub-045/question.md)（困难）
- [046 · 如何区分消息准入去重和回答投递去重？](../questions/agenthub-046/question.md)（中等）
- [047 · 迟到 ACK 应该更新哪些状态，为什么不能继续补发？](../questions/agenthub-047/question.md)（困难）
- [048 · 长答案分段发送为什么会让交付正确性更复杂？](../questions/agenthub-048/question.md)（中等）
- [049 · 每群串行队列如何兼顾上下文一致性和跨群并发？](../questions/agenthub-049/question.md)（中等）
- [050 · 从外部平台收消息到发送回答，能否保证端到端 exactly-once？](../questions/agenthub-050/question.md)（困难）

### 06 · FTS5 与搜索

- [051 · FTS5 倒排索引与普通 B-tree 索引分别适合什么查询？](../questions/agenthub-051/question.md)（简单）
- [052 · FTS5 trigram 为什么适合部分中文技术检索，又有哪些限制？](../questions/agenthub-052/question.md)（中等）
- [053 · 如何防止用户输入改变 FTS5 查询语法？](../questions/agenthub-053/question.md)（中等）
- [054 · 为什么某些检索接口不适合用 LIKE 百分号包围关键词？](../questions/agenthub-054/question.md)（中等）
- [055 · 只提取一个最长关键词作为检索词有什么取舍？](../questions/agenthub-055/question.md)（中等）
- [056 · 全文索引更新为什么必须与业务内容保持一致？](../questions/agenthub-056/question.md)（困难）
- [057 · BM25、召回和重排分别解决什么问题？](../questions/agenthub-057/question.md)（中等）
- [058 · 客户端传回“我刚才看过这些搜索结果”时为什么还要重新鉴权？](../questions/agenthub-058/question.md)（困难）
- [059 · 两字关键词检索应如何避免退化成跨租户全表扫描？](../questions/agenthub-059/question.md)（中等）
- [060 · 如何为项目设计一组可复现的检索回归用例？](../questions/agenthub-060/question.md)（困难）

### 07 · RAG 与质量评测

- [061 · 一个完整的 RAG 问答链路包含哪些步骤？](../questions/agenthub-061/question.md)（简单）
- [062 · 为什么要在调用模型前做一次确定性的公开检索？](../questions/agenthub-062/question.md)（中等）
- [063 · 检索结果为什么不应该混入“最近聊天记录”区块？](../questions/agenthub-063/question.md)（中等）
- [064 · 来源链接补充与引用真实性有什么区别？](../questions/agenthub-064/question.md)（中等）
- [065 · 如何处理过期知识和带时间边界的回答？](../questions/agenthub-065/question.md)（中等）
- [066 · 如何构建检索增强问答的离线评测集？](../questions/agenthub-066/question.md)（困难）
- [067 · Recall@K、MRR 与答案支持率分别说明什么？](../questions/agenthub-067/question.md)（中等）
- [068 · 无检索结果、检索失败和低相关结果应该如何区分？](../questions/agenthub-068/question.md)（中等）
- [069 · 如果要扩展混合检索，如何比较关键词与向量召回？](../questions/agenthub-069/question.md)（困难）
- [070 · 如何设计 RAG 缓存键和撤回失效策略？](../questions/agenthub-070/question.md)（中等）

### 08 · 权限与多租户

- [071 · 认证、授权、RBAC 和资源范围有什么区别？](../questions/agenthub-071/question.md)（简单）
- [072 · 为什么可信身份不能来自昵称、引用消息或转发内容？](../questions/agenthub-072/question.md)（中等）
- [073 · 本群管理员和全局维护者的权限边界如何设计？](../questions/agenthub-073/question.md)（中等）
- [074 · 如何防止 IDOR，即修改资源 ID 访问别人的内容？](../questions/agenthub-074/question.md)（困难）
- [075 · 工具列表过滤和执行点鉴权为什么需要同时存在？](../questions/agenthub-075/question.md)（中等）
- [076 · TOCTOU 在长时间 Agent 调用中如何出现？](../questions/agenthub-076/question.md)（困难）
- [077 · 多租户隔离为什么需要贯穿记忆、队列、图片和缓存？](../questions/agenthub-077/question.md)（中等）
- [078 · 群问答准入和群内容公开为什么必须独立配置？](../questions/agenthub-078/question.md)（中等）
- [079 · Cookie、CSRF 与 CORS 在网页管理接口中分别解决什么问题？](../questions/agenthub-079/question.md)（中等）
- [080 · 如何设计多群权限回归矩阵？](../questions/agenthub-080/question.md)（困难）

### 09 · 隐私与知识公开

- [081 · 为什么敏感数据要在进入持久化前控制，而不是写完再脱敏？](../questions/agenthub-081/question.md)（中等）
- [082 · 公开 DTO 为什么适合按白名单重建，而不是删除几个敏感字段？](../questions/agenthub-082/question.md)（中等）
- [083 · 私有知识引用为什么会影响回答记录和后续公开资格？](../questions/agenthub-083/question.md)（困难）
- [084 · 知识审核为什么需要独立于内容生成？](../questions/agenthub-084/question.md)（中等）
- [085 · 审核批次格式错误为什么应拆分隔离，而不是无限重试或默认通过？](../questions/agenthub-085/question.md)（困难）
- [086 · 来源撤回后，怎样处理派生条目、搜索索引和缓存？](../questions/agenthub-086/question.md)（中等）
- [087 · 化名为什么适合在响应生成时应用？](../questions/agenthub-087/question.md)（中等）
- [088 · 埋点和可观测日志如何遵守数据最小化？](../questions/agenthub-088/question.md)（中等）
- [089 · 附件读取如何守住路径、大小和会话范围边界？](../questions/agenthub-089/question.md)（困难）
- [090 · 怎样把私有项目经验整理成可公开的面试题？](../questions/agenthub-090/question.md)（中等）

### 10 · Cloudflare 与分布式

- [091 · Workers、Durable Objects、D1 和 R2 在这类项目中如何分工？](../questions/agenthub-091/question.md)（中等）
- [092 · 按群划分 Durable Object 为什么仍需要显式控制异步执行顺序？](../questions/agenthub-092/question.md)（困难）
- [093 · Durable Object 的内存状态为什么不能当作永久事实？](../questions/agenthub-093/question.md)（中等）
- [094 · 路由协调器为什么不应该等待整轮模型生成结束？](../questions/agenthub-094/question.md)（中等）
- [095 · WebSocket 心跳、重连退避和业务 ACK 分别解决什么问题？](../questions/agenthub-095/question.md)（中等）
- [096 · WebSocket Hibernation 如何影响连接与状态管理？](../questions/agenthub-096/question.md)（中等）
- [097 · 事件至少一次与发送最多一次为什么可以同时存在？](../questions/agenthub-097/question.md)（中等）
- [098 · D1 原子 batch 如何与条件更新一起守住一次性消费？](../questions/agenthub-098/question.md)（困难）
- [099 · D1 开启读副本后，如何理解读后写和会话一致性？](../questions/agenthub-099/question.md)（困难）
- [100 · 为什么 Node 单元测试通过后仍需要在 workerd 中验证？](../questions/agenthub-100/question.md)（中等）

### 11 · 数据迁移与发布

- [101 · 为什么完整会话日志适合放对象存储，索引摘要放关系数据库？](../questions/agenthub-101/question.md)（中等）
- [102 · 为什么读取对象存储列表必须处理分页？](../questions/agenthub-102/question.md)（中等）
- [103 · 内容同步为什么既需要增量差异，也需要定期对账？](../questions/agenthub-103/question.md)（中等）
- [104 · 如何防止上游读取失败被误认为批量删除？](../questions/agenthub-104/question.md)（困难）
- [105 · 从本地 SQLite 迁移到 D1，如何设计可回滚切换？](../questions/agenthub-105/question.md)（困难）
- [106 · 数据库变更为什么适合采用 expand-contract 思路？](../questions/agenthub-106/question.md)（中等）
- [107 · UPSERT 和唯一约束如何帮助实现可恢复导入？](../questions/agenthub-107/question.md)（中等）
- [108 · 为什么回滚时必须保留发送账本和持久去重状态？](../questions/agenthub-108/question.md)（困难）
- [109 · 影子模式与灰度切换如何避免双发送？](../questions/agenthub-109/question.md)（中等）
- [110 · 题库发布为什么需要同时校验版本、目录和最终 ZIP？](../questions/agenthub-110/question.md)（中等）

### 12 · 排障与模拟面试

- [111 · Agent 系统的 trace 至少应该能回答哪些诊断问题？](../questions/agenthub-111/question.md)（中等）
- [112 · 如何用历史事件评估备用模型的时间分配？](../questions/agenthub-112/question.md)（中等）
- [113 · 如何定义 Agent 的 SLI、SLO 和错误预算？](../questions/agenthub-113/question.md)（中等）
- [114 · 如何设计覆盖重复写入和迟到回包的故障注入测试？](../questions/agenthub-114/question.md)（困难）
- [115 · 网页流式回答如何处理断开、终态和服务端取消？](../questions/agenthub-115/question.md)（中等）
- [116 · 排查“备用回答成功但出现两条公告”应该按什么顺序取证？](../questions/agenthub-116/question.md)（困难）
- [117 · 如何排查“搜索能命中，但回答没有使用知识库”？](../questions/agenthub-117/question.md)（困难）
- [118 · 如何回答“你遇到的最难故障是什么”，又不虚构事故经历？](../questions/agenthub-118/question.md)（中等）
- [119 · 如果从零重做一次，你会保留什么，优先改什么？](../questions/agenthub-119/question.md)（困难）
- [120 · 如何在四十五分钟项目深挖中串起架构、难点和证据？](../questions/agenthub-120/question.md)（困难）

## 官方资料与核对范围

资料访问与事实核对日期：2026-10-30。链接用于核对通用原理和 API 边界；原创场景、恢复策略和架构取舍不是官方文档对某个项目的背书。平台文档会更新，面试前需核对具体版本。

| 相关题号 | 官方资料 | 核对内容 |
|---|---|---|
| 012 | [TypeScript Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html) | 可辨识联合与类型收窄 |
| 014 | [Node.js Async Context](https://nodejs.org/api/async_context.html) | AsyncLocalStorage 的传播与使用边界 |
| 018、042 | [MDN AbortController](https://developer.mozilla.org/en-US/docs/Web/API/AbortController) | 取消信号，不保证远端回滚 |
| 051–057 | [SQLite FTS5](https://www.sqlite.org/fts5.html) | trigram、查询语法、BM25；部分题为原创检索设计分析 |
| 071、074、075 | [OWASP Authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html) | 默认拒绝、逐请求授权和资源访问控制 |
| 079 | [OWASP CSRF](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html) | Cookie 场景下的跨站请求防护 |
| 092 | [DO Rules](https://developers.cloudflare.com/durable-objects/best-practices/rules-of-durable-objects/) | 协调、异步行为与平台约束 |
| 093 | [DO In-memory State](https://developers.cloudflare.com/durable-objects/reference/in-memory-state/) | 实例内存不是永久持久状态 |
| 096 | [DO WebSockets](https://developers.cloudflare.com/durable-objects/best-practices/websockets/) | 休眠接口、连接恢复与自动响应 |
| 019、098 | [D1 Database](https://developers.cloudflare.com/d1/worker-api/d1-database/) | batch 原子性及能力边界 |
| 099 | [D1 Read Replication](https://developers.cloudflare.com/d1/best-practices/read-replication/) | Sessions API 与副本使用条件 |
| 100 | [Workers Testing](https://developers.cloudflare.com/workers/testing/) | 在目标运行时验证真实适配层 |
| 102 | [R2 Workers API](https://developers.cloudflare.com/r2/api/workers/workers-api-reference/) | 对象列表游标、截断和分页 |
| 106 | [D1 Migrations](https://developers.cloudflare.com/d1/reference/migrations/) | 迁移文件与执行记录；发布顺序由项目约束决定 |
| 107 | [SQLite UPSERT](https://sqlite.org/lang_upsert.html) | 冲突目标与唯一约束 |
| 115 | [MDN SSE](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events) | 事件流与客户端能力；业务终态和恢复为原创设计分析 |

## 学习结果自检

能讲清为什么这么设计、什么情况下不成立、如何复现失败以及测试观察了什么，才算掌握。参考答案没有证明任何线上指标；本次新增内容没有运行真实模型、真实群发送或完整 App 端到端验证。
