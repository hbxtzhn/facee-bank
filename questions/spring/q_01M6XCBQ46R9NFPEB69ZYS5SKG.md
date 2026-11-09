---
id: q_01M6XCBQ46R9NFPEB69ZYS5SKG
title: MyBatis 怎么映射一对一关联？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [association-mapping]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
一对一关联就是在实体类里放一个关联对象属性，再在 resultMap 里用 `<association>` 指定属性名和类型，把查询结果装进去。

## 要点
- [kp1|3] 实体类里定义关联对象属性，如订单里放 `private Pay pay;`
- [kp2|3] resultMap 里用 `<association>` 映射这个关联属性
- [kp3|2] `property` 写实体里的属性名，`javaType` 写关联对象类型
- [kp4] `<association>` 内部可以直接映射关联对象的各个字段

## 详解
### 先搞懂：一个订单对应一条支付记录
订单和支付是典型的一对一：一个订单只有一条支付信息。查订单时，你希望拿到的订单对象里，直接带着支付对象，而不是再手动去查一次。

可以把它想成快递单：订单是外面的盒子，支付信息是盒子里的一个小袋子。MyBatis 要做的就是把查到的一行行数据，分别装进盒子和小袋子。

后文用到的术语：
- **resultMap**：告诉 MyBatis 查询结果的每一列怎么对应到对象属性。
- **`<association>`**：专门用来映射「对象里面的另一个对象」。

### 第一步：实体类里放关联对象
```java
public class Order {
    private Long id;
    private String orderNo;
    private Pay pay;   // 一对一关联的对象
}
```

### 第二步：resultMap 里用 association
`<association>` 里的 `property` 写 `Order` 里的属性名 `pay`，`javaType` 写它的类型 `Pay`。标签内部再用 `<id>`、`<result>` 把支付表的列对应到 `Pay` 的字段。

MyBatis 读到一行结果后，先装 `Order` 的字段，再创建一个 `Pay` 对象，装好后赋给 `order.pay`。

### 两种取关联数据的方式
上面是「内联映射」：一条联表 SQL 查出全部数据，在 resultMap 里一次装好。另一种是 `<association>` 加 `select` 属性，再发一条 SQL 查关联对象，这就是嵌套查询，后面的题会讲。

## 示例
```xml
<resultMap id="orderMap" type="Order">
  <id property="id" column="id"/>
  <result property="orderNo" column="order_no"/>
  <association property="pay" javaType="Pay">
    <id property="id" column="pay_id"/>
    <result property="amount" column="amount"/>
  </association>
</resultMap>

<select id="getOrder" resultMap="orderMap">
  select o.id, o.order_no, p.id as pay_id, p.amount
  from orders o left join pay p on p.order_id = o.id
  where o.id = #{id}
</select>
```

## 易错点
- 联表查询里两张表都有 `id` 列却不起别名；后者会覆盖前者，映射出错
- `property` 写成了表列名；它必须是实体类的属性名
- 用了 `<association>` 但 `select` 用的是 `resultType`；关联属性需要 `resultMap` 才能映射

## 追问
### [f1] `javaType` 能省略吗？
多数情况下 MyBatis 可以通过反射看属性类型，自动推断，所以能省略。写上更清晰，类型推断不出来时也必须写。
