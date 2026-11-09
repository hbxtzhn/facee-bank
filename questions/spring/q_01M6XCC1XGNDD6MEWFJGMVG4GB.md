---
id: q_01M6XCC1XGNDD6MEWFJGMVG4GB
title: resultMap 的鉴别器 discriminator 是做什么的？
type: concept
difficulty: medium
importance: 1
category: spring
tags: [sql-mapping]
prerequisites: [q_01M6XCBJTBNNSR25Y1ABPDPBEH]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
`discriminator`（鉴别器）根据某一列的值，选择不同的 resultMap 来映射这一行，让同一条查询映射成不同的子类对象。

## 要点
- [kp1|3] `<discriminator>` 放在 `<resultMap>` 里，按 `column` 的值分支
- [kp2|3] 每个 `<case value="...">` 对应一种值，指向各自的 resultMap
- [kp3|2] `javaType` 指定判断列的 Java 类型
- [kp4|2] 常和 `extends` 搭配：各子类 resultMap 继承基础映射
- [kp5] 没有匹配的 `case` 时，用外层 resultMap 本身映射

## 详解
### 先搞懂：同一张表里存着不同种类的数据
假设有一张 `vehicle` 表，里面既有汽车，也有卡车，用 `type` 列区分。汽车有“车门数”，卡车有“载重”。

查出来的每一行，都要看 `type` 是什么，再决定映射成 `Car` 还是 `Truck`。这就像快递分拣：看一眼标签，扔进不同的篮子。鉴别器干的就是这个分拣的活。

- **鉴别器**：按某列的值决定用哪套映射。
- **case**：鉴别器里的一个分支，对应列的一个具体值。

### 怎么工作：逐行看值，再选映射
MyBatis 处理每一行结果时，先读取鉴别器指定的 `column` 的值，再找到匹配的 `<case>`，改用该 case 指向的 resultMap 来映射。

不同行可以映射成不同的类。所以返回类型一般写成它们共同的父类，如 `List<Vehicle>`，列表里实际装的是 `Car` 和 `Truck` 对象。

### 搭配 extends：公共字段只写一次
各子类都有 id、name 这类公共字段，没必要每个 case 都写一遍。常见做法是：基础 resultMap 写公共字段，各子类 resultMap 用 `extends` 继承它，再加自己独有的字段。

如果没有任何 `case` 匹配，就用外层 resultMap 自己的映射，不会报错。

## 示例
```xml
<resultMap id="vehicleMap" type="com.example.Vehicle">
    <id property="id" column="id"/>
    <result property="name" column="name"/>
    <discriminator javaType="int" column="type">
        <case value="1" resultMap="carMap"/>
        <case value="2" resultMap="truckMap"/>
    </discriminator>
</resultMap>

<resultMap id="carMap" type="com.example.Car" extends="vehicleMap">
    <result property="doors" column="doors"/>
</resultMap>
```

## 易错点
- 只写 `case` 不继承基础映射，结果里 id、name 都是空的
- `case` 的 `value` 类型与 `javaType` 不一致，匹配不上
- 查询的 SQL 里没有查出鉴别列，鉴别器无法判断

## 追问
### [f1] 不用鉴别器还有什么办法处理这种“一表多类型”？
可以先查出通用对象，在 Java 代码里按类型转换；或者按类型分别写查询。鉴别器的好处是一条 SQL 就能返回正确的子类。
