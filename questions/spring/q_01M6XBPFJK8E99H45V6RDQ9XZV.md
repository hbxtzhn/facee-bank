---
id: q_01M6XBPFJK8E99H45V6RDQ9XZV
title: 多个参数的几种传参方式各有什么优缺点？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [sql-mapping]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
多参数传参有顺序传参、`@Param`、Map、JavaBean 四种：参数少用 `@Param`，参数多或要复用就封装成 JavaBean。

## 要点
- [kp1|3] 顺序传参靠位置引用，参数一多就容易看不懂、写错
- [kp2|3] `@Param` 给每个参数起名，SQL 里按名字引用，最直观
- [kp3|2] Map 传参灵活但 key 靠字符串约定，没有类型检查
- [kp4|2] JavaBean 传参结构清楚，适合参数多、需要复用的场景

## 详解
### 先搞懂：多个参数怎么让 SQL 认出来
比如查订单，要传“用户 ID”和“状态”两个值。Java 方法能接收两个参数，但 SQL 里只写 `#{...}`，MyBatis 得知道哪个占位符对应哪个值。这就像快递员送两个包裹，包裹上要贴名字，不然分不清给谁。

四种方式，本质是用不同方法给参数“贴名字”：

- **顺序传参**：不贴名，按位置对号入座；
- **`@Param`**：在参数前贴一个明确的名字；
- **Map**：把所有值放进一个 Map，key 就是名字；
- **JavaBean**：把值装进一个对象，属性名就是名字。

### 四种方式各是什么样
顺序传参，SQL 里写 `#{param1}`、`#{param2}` 这类按位置的名字。参数少时能用，但读 SQL 的人要回头对着方法签名数第几个，改参数顺序还会悄悄出错。

`@Param` 在接口参数前写注解，SQL 里直接用注解里的名字。名字清楚，改顺序不受影响。

Map 传参要调用方自己拼 Map，SQL 里用 key 取值。key 写错只有运行时才发现。

JavaBean 传参是定义一个类，SQL 里用属性名引用。类型明确，能复用，还能直接承载查询条件。

### 方案对比：四种传参方式
| 方案 | 可读性 | 灵活性 | 维护性 | 适合 |
|---|---|---|---|---|
| 顺序传参 | 差，要对位置 | 低 | 改顺序易出错 | 临时、一两个参数 |
| `@Param` | 好，名字明确 | 中 | 好 | 参数不多的常规查询 |
| Map 传参 | 一般，看 key | 高，随意增减 | 差，key 无检查 | 条件不固定的临时场景 |
| JavaBean 传参 | 好，字段有类型 | 中 | 好，可复用 | 参数多、查询条件对象 |

结论：参数在三四个以内默认用 `@Param`；参数更多或要在多处复用时换成 JavaBean，Map 尽量少用。

## 示例
```java
// @Param 写法
List<Order> find(@Param("userId") Long userId, @Param("status") Integer status);

// JavaBean 写法
List<Order> find(OrderQuery query);
```

```xml
<select id="find" resultType="Order">
  select * from orders where user_id = #{userId} and status = #{status}
</select>
```

## 易错点
- 多个参数不加任何名字，直接在 SQL 写属性名，会报找不到参数
- 用 Map 传参时 key 拼错，不会编译报错，只在运行时才出错
- 同时用 JavaBean 和 `@Param` 混传时，引用要写成“名字.属性”

## 追问
### [f1] 参数很多时，选 JavaBean 还是 Map？
选 JavaBean。它有类型、有属性名，IDE 能提示和重构；Map 的 key 全靠字符串，容易写错且没人检查。
