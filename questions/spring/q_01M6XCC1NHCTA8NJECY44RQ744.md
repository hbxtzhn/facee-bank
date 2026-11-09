---
id: q_01M6XCC1NHCTA8NJECY44RQ744
title: resultMap 怎么继承已有映射（extends）？
type: concept
difficulty: easy
importance: 1
category: spring
tags: [sql-mapping]
prerequisites: [q_01M6XCBJTBNNSR25Y1ABPDPBEH]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
在 `<resultMap>` 上写 `extends`，引用另一个已有的 resultMap，就能复用它的字段映射，只需再补充新增的字段。

## 要点
- [kp1|3] `<resultMap id="子" type="..." extends="父">` 引用父 resultMap
- [kp2|3] 子 resultMap 自动拥有父的映射，只需写新增或要覆盖的字段
- [kp3|2] 子里写了与父同名的字段映射，以子的为准
- [kp4] 父在别的 namespace 时，`extends` 要写完整的 `namespace.id`

## 详解
### 先搞懂：为什么需要继承
假设有 `User` 表和 `UserDetail` 表。基础查询要映射 id、name、age，详细查询除了这些，还要映射地址、电话。

如果每个 resultMap 都把前三个字段再写一遍，改一个字段名就得改好几处。继承就像“复制粘贴”的代替品：先写一个基础映射，其他的在它之上补充。

- **resultMap**：描述“数据库列怎么对应 Java 属性”的一张对照表。
- **extends**：声明“我是在另一张对照表上扩展的”。

### 怎么写
先写基础映射，再写子映射。子映射只写新增部分，父里已有的字段不用重复写。

子映射的 `type` 可以是父类型的子类，这样查询出来的对象会有更多属性。

### 覆盖规则
如果子里重新映射了同一个属性，以子的为准。这样可以在不改父的前提下，局部调整某个字段。

## 示例
```xml
<resultMap id="baseMap" type="com.example.User">
    <id property="id" column="id"/>
    <result property="name" column="name"/>
</resultMap>

<resultMap id="detailMap" type="com.example.UserDetail" extends="baseMap">
    <result property="address" column="address"/>
    <result property="phone" column="phone"/>
</resultMap>
```

## 易错点
- 把 `extends` 写成了 `<extends>` 子标签；它是 `<resultMap>` 的属性
- 子映射又把父的字段全部抄一遍，等于没有复用
- 父在其他映射文件里，却只写了短 id，会找不到

## 追问
### [f1] extends 和 include 有什么区别？
`extends` 用来复用 resultMap，也就是列到属性的映射；`<include>` 用来复用 `<sql>` 片段，也就是 SQL 文本。两者复用的东西不同。
