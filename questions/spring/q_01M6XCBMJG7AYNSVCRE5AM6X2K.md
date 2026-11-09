---
id: q_01M6XCBMJG7AYNSVCRE5AM6X2K
title: 插入数据后，怎么拿到自动生成的主键？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [sql-mapping]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
在 `<insert>` 上设置 `useGeneratedKeys="true"` 和 `keyProperty`，插入后数据库生成的主键会自动写回参数对象。

## 要点
- [kp1|3] `useGeneratedKeys="true"` 让 MyBatis 向数据库取回自动生成的主键
- [kp2|3] `keyProperty` 指定把主键写回参数对象的哪个属性
- [kp3|2] 插入完成后，用参数对象的 getter 就能读到主键
- [kp4] 需要数据库和驱动支持，如 MySQL 的自增主键

## 详解
### 先搞懂：主键是数据库给的，你事先不知道
新增一个订单，表里的 `id` 是自增的，你插入时不传它，数据库自己生成。插入完，你却需要这个 `id`：要用它去写订单明细、返回给前端。怎么拿到？

这像去银行取号：你没法事先知道是几号，办完后柜员把号码交给你。回填主键，就是让 MyBatis 把这个号写回你手里的对象。

术语说明：

- **自增主键**：数据库在插入时自动生成的递增编号；
- **主键回填**：插入后，把生成的主键写进传入的 Java 对象属性。

### 用法：两个属性搭配
在 `<insert>` 标签上：

- `useGeneratedKeys="true"`：告诉 MyBatis 要取回数据库生成的主键；
- `keyProperty="id"`：取回来的值放到参数对象的 `id` 属性里。

插入执行后，`order.getId()` 就是新生成的主键。注意主键写回到你传入的那个对象上，不是方法的返回值，插入方法返回的仍是影响的行数。

### 几点说明
- 参数必须是对象，有对应的属性和 setter，单独传一个数字无处可写；
- 全局设置里也有 `useGeneratedKeys`，默认是关闭的，所以在语句上显式写更稳妥；
- 不支持自增的数据库，比如依赖序列的 Oracle，要改用 `selectKey` 标签。

## 示例
```xml
<insert id="insert" useGeneratedKeys="true" keyProperty="id">
  insert into orders (order_no, user_id) values (#{orderNo}, #{userId})
</insert>
```

```java
Order order = new Order();
order.setOrderNo("A001");
order.setUserId(1L);
orderMapper.insert(order);
Long id = order.getId(); // 主键已回填
```

## 易错点
- 以为主键是方法返回值，其实返回值是影响的行数
- 写了 `useGeneratedKeys` 却漏了 `keyProperty`，主键没有地方回填
- 传多个散参数且没有对象，主键没地方写，需要封装对象

## 追问
### [f1] Oracle 这类用序列的数据库怎么拿主键？
用 `<selectKey>` 标签，在插入前或后执行一条查询序列的 SQL，把结果写到指定属性里。
