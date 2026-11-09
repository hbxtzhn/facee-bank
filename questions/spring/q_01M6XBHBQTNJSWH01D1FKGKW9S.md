---
id: q_01M6XBHBQTNJSWH01D1FKGKW9S
title: Nacos 和 Eureka 在注册中心上有什么区别？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [microservice, consensus]
prerequisites: [q_01M6XBHABRAHKWVM804H2CPYRR, q_01M6XBPBGP3MDZM5R1301Z138C]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "Netflix Eureka Wiki：首页（Eureka 2.0 停止、1.x 维护）", url: "https://github.com/Netflix/eureka/wiki" }
  - { title: "Eureka Wiki：Server Self Preservation Mode", url: "https://github.com/Netflix/eureka/wiki/Server-Self-Preservation-Mode" }
  - { title: "Nacos 文档：Instance Lifecycle（临时实例与持久实例）", url: "https://nacos.io/en/docs/latest/manual/user/naming/instance-lifecycle/" }
estimatedMinutes: 4
---

## 一句话
Eureka 只做注册中心且偏重可用性（AP），Netflix 已不再推进其新版本；Nacos 同时提供注册中心和配置中心，既支持 AP 也支持 CP，新项目一般首选 Nacos。

## 要点
- [kp1|3] Eureka 是 AP 型：网络出问题时优先保证服务可用，数据可能短暂不一致
- [kp2|3] Nacos 支持 AP 和 CP 两种模式，按实例类型选择
- [kp3|2] Nacos 同时是配置中心；Eureka 只做注册发现
- [kp4|2] Eureka 2.x 已停止开发，1.x 只做维护；Nacos 社区更活跃

## 详解
### 先搞懂：注册中心为什么还要谈一致性
注册中心的数据，是各服务实例的地址列表，一般部署成多台组成集群。网络出故障时，集群里的机器可能互相联系不上，这时每台机器手里的列表可能不一样。

这时有两种选择，好比两家分店的菜单价格不能互相通气时：
- 宁可让每家店继续营业，哪怕菜单暂时不一致（保证**可用性**）；
- 宁可暂停营业，等对齐后再说（保证**一致性**）。

对注册中心来说，列表稍微旧一点通常还能调通，而完全不可用却会让整个系统找不到服务，所以多数注册中心偏向可用性。

后文用到的术语：
- **AP**：网络分区时优先保证可用性，允许短暂不一致。
- **CP**：网络分区时优先保证一致性，可能暂时拒绝服务。
- **自我保护**：Eureka 在短时间内大量实例没有续约时，不再剔除实例，避免因网络问题误删。

### 方案对比：Nacos 和 Eureka
| 维度 | Nacos | Eureka |
|---|---|---|
| 一致性取向 | 临时实例走 AP，持久实例走 CP（可切换） | AP |
| 健康检查 | 临时实例靠客户端心跳；持久实例由服务端主动探测 | 客户端心跳续约，另有自我保护 |
| 配置管理 | 自带配置中心 | 没有，需配合其他组件 |
| 变更感知 | 服务端可以向客户端推送变化 | 客户端定时拉取注册信息 |
| 维护状态 | 社区持续维护更新 | 2.x 已停止开发，1.x 仅维护 |
| 周边能力 | 命名空间、分组、权重、元数据等 | 功能相对精简 |

结论：新项目优先选 Nacos，一个组件同时解决注册和配置问题；如果已有 Spring Cloud Netflix 老系统在稳定运行，也不必急着迁移。

### 临时实例和持久实例
Nacos 里实例默认是**临时实例**：靠客户端定时发心跳保活，超时没心跳就被剔除，数据同步走 AP 协议。**持久实例**则由服务端主动检查健康，不会因为心跳超时被自动剔除，数据一致性走 CP 协议。需要保留服务信息、不希望被自动删除的场景可以用持久实例。

### 选型时怎么想
- 只需要简单注册发现、不关心配置中心，并且是老 Netflix 栈：Eureka 也能用。
- 想把注册和配置统一，或需要持久实例、权重、分组等功能：选 Nacos。

## 易错点
- 以为 Nacos 只能是 CP 或只能是 AP；它按实例类型分别支持两种
- 以为 Eureka 的自我保护是 bug；它是为了避免网络波动时把存活的实例误删
- 以为 Eureka 的 Spring Cloud 集成已被官方全面移除；它仍可使用，只是 Netflix 不再推进新版本

## 追问
### [f1] Eureka 的自我保护机制是什么？
Eureka 在短时间内收不到大量实例的心跳时，会认为可能是自己网络有问题，于是停止剔除实例。好处是不误删存活实例，代价是列表里可能残留已经宕机的实例，调用方要自己做好重试。

### [f2] Nacos 为什么需要同时支持 AP 和 CP？
临时的、频繁变化的服务实例，更适合 AP，保证随时能注册和查询；需要长期保存、不能丢的服务数据，更适合 CP，保证各节点数据一致。
