---
id: q_01M6XCBNK1F0XM77F4682VE0WA
title: 什么是动态 SQL？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [dynamic-sql]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
动态 SQL 是在 XML 里用 `<if>`、`<where>`、`<set>` 等标签，根据参数有没有值来决定拼不拼某段 SQL，不用在 Java 里手工拼字符串。

## 要点
- [kp1|3] 动态 SQL 按参数值，决定哪些 SQL 片段拼入语句
- [kp2|3] `<if test="...">` 条件成立才拼入其中的片段
- [kp3|2] `<where>`、`<set>` 能自动处理多余的 AND、OR 和逗号
- [kp4] 它替代了在 Java 里用字符串拼接 SQL 的做法

## 详解
### 先搞懂：搜索条件有时填、有时不填
订单列表页有三个筛选框：用户、状态、日期。用户可能只填其中一个，也可能都不填。SQL 需要随之变化：只填状态，就只拼 `status = ?`；都不填，就不加 `where`。

以前的做法是在 Java 里拼字符串，判断一个加一段，又乱又容易出错，还容易拼出注入漏洞。动态 SQL 把这件事交给 XML 标签来做。这就像填表时“如果有这项就写，没有就跳过”的指引。

术语说明：

- **动态 SQL**：运行时按条件决定 SQL 内容；
- **`test`**：`<if>` 标签里写判断条件的属性。

### 最基础的标签：if
`<if test="title != null">` 里面放一段 SQL。当条件成立时，这段会被拼进语句；不成立就整段忽略。

例如：

- 传了 `status`，就拼上 `and status = #{status}`；
- 没传，这一段就不出现。

多个 `<if>` 并列，就能组成灵活的 `where` 条件。

### 一个小麻烦与它的解法
如果第一个条件没成立，拼出来的 SQL 可能变成 `where and status = ?`，多了个 `and`；或者所有条件都不成立，只剩一个孤零零的 `where`。

`<where>` 标签就是处理这个问题的：它会去掉开头多余的 `and`/`or`，没有条件时连 `where` 一起省掉。更新语句里的多余逗号，用 `<set>` 处理。

## 示例
```xml
<select id="search" resultType="Order">
  select * from orders
  <where>
    <if test="userId != null">and user_id = #{userId}</if>
    <if test="status != null">and status = #{status}</if>
  </where>
</select>
```

## 易错点
- `<if>` 里用 `test` 判断字符串时，只判 null 不够，空字符串也会通过
- 不加 `<where>`，直接写 `where 1 = 1` 来绕开多余的 and，不够整洁
- `test` 里引用的是参数名或属性名，写错了会在运行时才报错

## 追问
### [f1] 动态 SQL 能防止注入吗？
`<if>` 本身不影响安全性。只要条件值仍用 `#{}` 传入，就是预编译的；用 `${}` 拼进去的值才有注入风险。
