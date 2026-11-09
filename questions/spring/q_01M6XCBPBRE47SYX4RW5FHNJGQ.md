---
id: q_01M6XCBPBRE47SYX4RW5FHNJGQ
title: 怎么用 foreach 拼接 IN 条件？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [dynamic-sql]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
`<foreach>` 遍历集合，用 `open`、`close`、`separator` 拼成 `(1, 2, 3)` 的样子，既能做 IN 条件，也能做批量插入。

## 要点
- [kp1|3] `<foreach>` 遍历传入的集合，每个元素生成一段 SQL
- [kp2|3] `open` 和 `close` 写括号，`separator` 写元素之间的分隔符
- [kp3|2] `item` 是当前元素的变量名，在循环体里用 `#{item}` 引用
- [kp4] 同样的写法也能拼批量插入的多组 values

## 详解
### 先搞懂：IN 里的个数是不固定的
页面勾选了几个订单，要查它们：`where id in (1, 2, 3)`。勾了三个，括号里是三个；勾了五个，就是五个。个数不固定，不能提前写死。

`<foreach>` 就是做这件事的：给它一个集合，它把每个元素按你给的格式拼起来。这像是排队点名：一个一个念，念完加上括号和逗号。

术语说明：

- **集合**：传进来的 `List`、数组等一组数据；
- **`item`**：循环时，代表当前元素的临时变量名；
- **`separator`**：每两个元素之间要插入的内容。

### foreach 的几个属性
- `collection`：要遍历谁，也就是参数集合的名字；
- `item`：当前元素叫什么，循环体内用 `#{item}` 引用；
- `open`：整体开头加什么，IN 条件里是 `(`；
- `close`：整体结尾加什么，是 `)`；
- `separator`：元素之间用什么分隔，是 `,`。

最终效果：传入 1、2、3，拼成 `(1, 2, 3)`，每个值仍是 `?` 占位符，安全。

### 批量插入
同样的办法，也能一次插入多行：遍历对象列表，每个元素生成一组 `(#{u.name}, #{u.age})`，用逗号隔开，一条 SQL 插入多行。

### 使用时注意
集合很大时，SQL 会变得很长，可能超出数据库对语句长度或参数个数的限制，要分批处理。集合为空时，`in ()` 是语法错误，调用前要先判断。

## 示例
```xml
<select id="findByIds" resultType="Order">
  select * from orders where id in
  <foreach collection="ids" item="id" open="(" close=")" separator=",">
    #{id}
  </foreach>
</select>
```

```java
List<Order> findByIds(@Param("ids") List<Long> ids);
```

## 易错点
- 集合为空时拼出 `in ()`，数据库报语法错误，需提前判空
- `collection` 的名字写得和参数名不一致，会提示找不到参数
- 一次传入太多元素，SQL 过长，应分批执行

## 追问
### [f1] 批量插入用 foreach 有什么要注意的？
一条 SQL 的长度和参数个数有上限，数据量大时要分批，比如每批几百条。也可以考虑使用 JDBC 批处理模式。
