---
id: q_01M6XCBM2N3DCJM5FXCN0582EB
title: ${} 是做什么的，什么时候会用到？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [sql-mapping]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
`${}` 把参数值原样拼进 SQL 字符串，不经过预编译，所以只用在动态表名、列名、排序字段上，且参数必须提前校验。

## 要点
- [kp1|3] `${}` 把参数值当文本直接替换进 SQL，不走预编译
- [kp2|3] 它用于 `#{}` 做不到的位置：表名、列名、排序字段
- [kp3|2] 参数来自用户时有 SQL 注入风险，必须提前校验
- [kp4] 校验最稳妥的做法是白名单，只放行事先约定好的值

## 详解
### 先搞懂：有些位置只能“改文字”，不能“填空”
`#{}` 好比表格里的空格，只能填内容。但有的需求不是填内容，而是要改表格的结构。例如：按月分表，今天查 `order_202611`，下个月查 `order_202612`。表名是 SQL 的结构，不是值，没法用空格填。

这时只能直接改文字，就是 `${}`。可是谁都能改文字，也就意味着坏人也能改，所以要特别小心。

术语说明：

- **字符串替换**：MyBatis 在发 SQL 前，先把 `${}` 换成参数的文本；
- **白名单**：只允许预先列好的几个取值通过，别的一律拒绝。

### ${}：什么时候必须用
- **动态表名**：按月、按年分表，或多租户分表；
- **动态列名**：让调用方选择查哪一列；
- **排序**：`order by ${column} ${direction}`，列名和升降序都不能用占位符。

这些位置在 SQL 里不是“值”，所以预编译帮不上忙。

### 用的时候怎么保证安全
1. 参数不要直接来自前端输入；
2. 在 Java 代码里用白名单，把用户选项映射成固定的列名或表名；
3. 校验不通过就拒绝，不要尝试“过滤危险字符”。

过滤字符很容易漏，白名单才可靠。

## 示例
```xml
<select id="listByTable" resultType="Order">
  select * from ${tableName} where user_id = #{userId}
</select>
```

```java
// 调用前用白名单校验，不能把用户输入直接传给 ${}
private static final Set<String> TABLES = Set.of("order_202611", "order_202612");

String table = TABLES.contains(input) ? input : "order_202611";
mapper.listByTable(table, userId);
```

## 易错点
- 把用户输入直接放进 `${}`，等于让用户能改写整条 SQL
- 条件值也用 `${}`，既不安全，字符串值还要自己手写引号
- 只做关键词过滤，容易被绕过，应使用白名单

## 追问
### [f1] `${}` 传入的字符串需要自己加引号吗？
需要。它是原样替换，不会加引号。所以条件值应该用 `#{}`，让 MyBatis 自动处理类型和转义。
