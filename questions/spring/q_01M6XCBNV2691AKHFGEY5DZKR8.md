---
id: q_01M6XCBNV2691AKHFGEY5DZKR8
title: choose、when、otherwise 标签是做什么的？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [dynamic-sql]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
`<choose>` 像 Java 的 switch：多个 `<when>` 按顺序判断，第一个成立的生效，都不成立就走 `<otherwise>`。

## 要点
- [kp1|3] `<choose>` 里的多个分支只会有一个生效
- [kp2|3] `<when test>` 按书写顺序依次判断，命中第一个就停
- [kp3|2] `<otherwise>` 是兜底分支，全部 when 不成立才执行
- [kp4] 和多个并列 `<if>` 不同，`<if>` 会各自独立判断

## 详解
### 先搞懂：几个条件里只选一个
搜索订单时，规则可能是：如果传了订单号，就按订单号查；否则如果传了手机号，就按手机号查；两个都没传，就只查今天的订单。这是“多选一”，不是“都拼上”。

多个 `<if>` 做不到：每个 `<if>` 自己独立判断，两个条件都成立时，两段都会拼进去。需要“只取其一”，就要用 `<choose>`。

术语说明：

- **`<choose>`**：外层标签，包住一组备选分支；
- **`<when>`**：一个分支，带 `test` 条件；
- **`<otherwise>`**：兜底分支，没有条件。

### 它怎么工作
MyBatis 从上到下检查每个 `<when>` 的 `test`：

1. 遇到第一个成立的，把它里面的 SQL 拼进去，其余分支全部跳过；
2. 如果所有 `<when>` 都不成立，就拼入 `<otherwise>` 里的内容；
3. 没写 `<otherwise>` 又全不成立，什么都不拼。

所以分支的顺序有意义，要把优先级高的放前面。

### 和 if 的区别
| 标签 | 是否互斥 | 全不成立时 |
|---|---|---|
| 多个 `<if>` | 否，各自独立 | 什么都不拼 |
| `<choose>` | 是，只取一个 | 走 `<otherwise>` |

要“可以同时满足多个条件”，用 `<if>`；要“只能走一条路”，用 `<choose>`。

## 示例
```xml
<select id="search" resultType="Order">
  select * from orders
  <where>
    <choose>
      <when test="orderNo != null">order_no = #{orderNo}</when>
      <when test="phone != null">phone = #{phone}</when>
      <otherwise>create_date = current_date</otherwise>
    </choose>
  </where>
</select>
```

## 易错点
- 以为多个 `<when>` 都会生效，其实命中第一个就停止
- 把优先级低的条件写在前面，导致高优先级条件永远走不到
- 误以为 `<otherwise>` 必写，其实可省，不写则全不成立时不拼任何内容

## 追问
### [f1] choose 和 if 怎么选？
条件互相排斥、只选一个，用 `choose`；条件可以叠加、满足几个拼几个，用 `if`。
