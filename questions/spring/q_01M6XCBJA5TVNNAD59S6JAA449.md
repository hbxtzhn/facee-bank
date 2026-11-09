---
id: q_01M6XCBJA5TVNNAD59S6JAA449
title: Mapper 方法有多个参数时，怎么用 @Param 传参？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [sql-mapping]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
在 Mapper 方法的每个参数前加 `@Param("名字")`，SQL 里就用 `#{名字}` 引用它，比按位置对号入座直观得多。

## 要点
- [kp1|3] 参数前写 `@Param("名字")`，给参数起一个明确的名字
- [kp2|3] SQL 里用 `#{名字}` 引用，名字要和注解括号里的一致
- [kp3|2] 它不依赖参数顺序，调整方法签名不会让 SQL 悄悄出错
- [kp4] 参数不多时推荐使用，参数很多就改用 JavaBean

## 详解
### 先搞懂：给参数贴名字
你查订单时传两个值：用户 ID 和订单状态。SQL 里有两个 `#{}`，MyBatis 要知道谁是谁。这就像发快递，两个包裹各贴一张写着收件人的标签，快递员就不会送错。

`@Param` 就是这张标签。术语说明：

- **`#{名字}`**：SQL 里的占位符，运行时会被换成对应的参数值；
- **`@Param`**：MyBatis 提供的注解，用来给 Mapper 方法的参数命名。

### @Param：写名字，按名字取
接口里这样写：参数前加注解，括号里写名字。XML 里写 `#{userId}`，MyBatis 就会去找名字叫 `userId` 的参数。

不用注解时，只能写 `#{param1}`、`#{param2}` 这类按位置的名字。读 SQL 的人要回头数第几个参数，方法里换个顺序，SQL 里的数字就对不上了。

用了 `@Param`，SQL 自己就能读懂：`where user_id = #{userId}`，一眼知道取的是谁。

### 使用时的几点
- 注解里的名字和 `#{}` 里的名字必须一样，大小写也要一致；
- 每个参数都建议加，不要有的加有的不加，否则风格混乱；
- 只有一个简单类型参数时可以不加，但统一加上更不容易出错。

## 示例
```java
public interface OrderMapper {
    List<Order> findByUserAndStatus(@Param("userId") Long userId,
                                    @Param("status") Integer status);
}
```

```xml
<select id="findByUserAndStatus" resultType="Order">
  select * from orders
  where user_id = #{userId} and status = #{status}
</select>
```

## 易错点
- 注解里写 `userId`，SQL 里写 `#{userid}`，名字对不上会报错
- 把 JavaBean 参数加了 `@Param` 后，仍直接写属性名，要改成“名字.属性”
- 以为不加注解也一定能按真实参数名取值，这取决于编译参数，不能依赖

## 追问
### [f1] 参数是 JavaBean 又加了 @Param，SQL 怎么引用？
要写成 `#{名字.属性}`，例如 `@Param("q") OrderQuery q`，SQL 里写 `#{q.userId}`。不加注解且只有一个 JavaBean 参数时，直接写属性名即可。
