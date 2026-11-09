---
id: q_01M6XCBP37JZHV5JB5XDH4G73H
title: trim、where、set 标签有什么区别？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [dynamic-sql]
prerequisites: [q_01M6XCBNK1F0XM77F4682VE0WA]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
`<where>` 管查询条件，去掉多余的 AND/OR；`<set>` 管更新赋值，去掉多余逗号；`<trim>` 是它们的通用版，可自定义前后缀。

## 要点
- [kp1|3] `<where>` 去掉开头多余的 AND/OR，没有条件时连 where 也省掉
- [kp2|3] `<set>` 去掉末尾多余的逗号，用在动态 update 语句里
- [kp3|2] `<trim>` 可自定义前缀、后缀，以及要去掉的前缀、后缀
- [kp4] `<where>` 和 `<set>` 本质上是 `<trim>` 的两种固定用法

## 详解
### 先搞懂：条件拼出来时容易多出东西
动态 SQL 里，条件是按需拼入的。查询时，第一个条件没成立，剩下的是 `and status = ?`，拼上 `where` 就成了 `where and status = ?`，语法错误。更新时，每个字段后面都带逗号，最后一个字段后面多一个逗号，也是语法错误。

这就像写清单：每行结尾都带分号，最后一行多出一个分号。三个标签就是帮你把这个多余的东西修掉。

术语说明：

- **前缀**：拼出来的片段最前面加的内容，如 `where`；
- **后缀**：片段最后面加的内容。

### where：管查询条件
- 里面有内容时，自动加上 `where`；
- 开头的 `and` 或 `or` 会被自动去掉；
- 里面一条条件也没有时，整个 `where` 都不会出现。

所以所有条件都是动态的查询，都可以放心包在 `<where>` 里。

### set：管更新赋值
- 自动加上 `set` 关键字；
- 去掉末尾多余的逗号。

这样每个字段写成 `name = #{name},`，不用担心最后一个逗号。

### trim：什么都能自定义
`<trim>` 有四个常用属性：

- `prefix`：要加的前缀；
- `suffix`：要加的后缀；
- `prefixOverrides`：要去掉的开头内容；
- `suffixOverrides`：要去掉的结尾内容。

用 `<trim>` 可以写出和 `<where>`、`<set>` 一样的效果，也可以处理别的情况，比如拼 `insert` 的列清单。

### 方案对比：三个标签
| 标签 | 加前缀 | 去除内容 | 典型场景 |
|---|---|---|---|
| `<where>` | `where` | 开头的 AND/OR | 动态查询条件 |
| `<set>` | `set` | 末尾的逗号 | 动态更新字段 |
| `<trim>` | 自己指定 | 自己指定前后缀 | 自定义拼接 |

结论：查询用 `<where>`，更新用 `<set>`，两者覆盖不了的情况再用 `<trim>`。

## 示例
```xml
<update id="updateUser">
  update user
  <set>
    <if test="name != null">name = #{name},</if>
    <if test="age != null">age = #{age},</if>
  </set>
  where id = #{id}
</update>
```

## 易错点
- `<set>` 里一个字段都没传，会拼出不合法的 SQL，要保证至少更新一列
- `<where>` 只处理开头的 AND/OR，写在条件末尾的 and 不会被去掉
- 以为 `<trim>` 和前两个完全无关，其实它们只是 `<trim>` 的固定用法

## 追问
### [f1] 用 trim 怎么写出和 where 一样的效果？
`<trim prefix="where" prefixOverrides="and |or ">`，即加前缀 where，并去掉开头的 and 或 or。
