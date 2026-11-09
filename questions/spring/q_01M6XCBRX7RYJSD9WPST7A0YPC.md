---
id: q_01M6XCBRX7RYJSD9WPST7A0YPC
title: 为什么推荐嵌套结果，并怎么配合 fetchType 使用？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [association-mapping]
prerequisites: [q_01M6XCBRN0N32SHJMNVYYM7BA7]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
references:
  - { title: "MyBatis 3 文档：Mapper XML 文件（association 的 fetchType 与嵌套查询）", url: "https://mybatis.org/mybatis-3/sqlmap-xml.html" }
  - { title: "MyBatis 3 文档：配置（settings：lazyLoadingEnabled）", url: "https://mybatis.org/mybatis-3/configuration.html" }
---

## 一句话
数据总是要用的时候，选嵌套结果，一条 SQL 避免 N+1；关联数据不一定用到时，选嵌套查询加 `fetchType` 延迟加载，按需再查。

## 要点
- [kp1|3] 嵌套结果一次联表查完，避免 N+1，但不能延迟加载
- [kp2|3] `fetchType` 只对带 `select` 的嵌套查询生效，取值 lazy 或 eager
- [kp3|2] 关联总是要用就用嵌套结果，不一定用到才用延迟加载
- [kp4] 标签上的 `fetchType` 优先于全局的 `lazyLoadingEnabled`

## 详解
### 先搞懂：两个工具解决的是不同的问题
嵌套结果解决的是「查询次数太多」：一次联表，不再逐条查。`fetchType` 解决的是「查了没用上」：关联数据暂时不查，用到再查。

可以把它想成备菜：确定客人一定会点的菜，提前一起做好（嵌套结果）；不确定会不会点的菜，等客人点了再做（延迟加载）。

后文用到的术语：
- **`fetchType`**：写在 `<association>` 或 `<collection>` 上，取值 `lazy`（延迟）或 `eager`（立即）。

### 先纠正一个常见误解
很多人以为嵌套结果可以配合 `fetchType` 延迟加载。实际上不行：嵌套结果是一条联表 SQL，数据一次全部回来了，没有「晚一点再查」的空间。`fetchType` 只对用 `select` 属性的嵌套查询有效。

### 方案对比：怎么选
| 方案 | 查询次数 | 延迟加载 | 适合 |
|---|---|---|---|
| 嵌套结果 | 1 次 | 不支持 | 关联数据总是要用 |
| 嵌套查询加 `lazy` | 用到才查，最多 N+1 | 支持 | 关联数据不一定用到 |
| 嵌套查询加 `eager` | 主查询加 N 次 | 不延迟 | 少数场景，一般不推荐 |

结论：默认用嵌套结果；只有关联数据大、而且经常用不上，才用嵌套查询加延迟加载。

### 为什么两者要放在一起讲
实际项目里经常两种都有：列表页的用户信息总是要展示，用嵌套结果；详情页里很重的明细数据，用嵌套查询加延迟加载。这样既不会处处 N+1，也不会把用不到的大数据全查出来。

### fetchType 的使用位置
全局开关 `lazyLoadingEnabled` 默认关闭。在某个关联上写 `fetchType="lazy"`，可以只让这一个关联延迟，不影响其他关联。反过来，全局打开后，也可以用 `fetchType="eager"` 让某个关联保持立即加载。

## 示例
```xml
<resultMap id="orderMap" type="Order">
  <id property="id" column="id"/>
  <!-- 总是要用：嵌套结果 -->
  <association property="user" javaType="User">
    <id property="id" column="user_id"/>
    <result property="name" column="user_name"/>
  </association>
  <!-- 不一定用：嵌套查询加延迟 -->
  <collection property="items" column="id"
              select="selectItems" fetchType="lazy"/>
</resultMap>
```

## 易错点
- 在嵌套结果的标签上写 `fetchType`；它不起作用，因为数据已经一次查完
- 以为延迟加载一定比嵌套结果快；全部用到时反而是 N+1，更慢
- 没打开全局开关，只写了 `fetchType="eager"`，却期待延迟；默认就是立即加载

## 追问
### [f1] 列表页每行都要用关联数据，该用哪种？
用嵌套结果，一次联表查完。若是一对多又要分页，可以先分页查主表，再用 `in` 批量查关联，避免联表分页截断数据。
