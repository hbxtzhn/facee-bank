---
id: q_01M6XCC5FZ8C8RAM22B3HHH0SZ
title: MyBatis-Plus 的条件构造器是做什么的？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [orm, dynamic-sql]
prerequisites: [q_01M6XCC5803060MG58YDYQW03Z]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
条件构造器让你用链式的 Java 方法，如 `eq`、`like`、`orderByDesc`，拼出查询条件，MyBatis-Plus 会自动生成对应的 SQL 条件。

## 要点
- [kp1|3] 用 `QueryWrapper` 或 `LambdaQueryWrapper` 链式拼接条件
- [kp2|3] 常用方法有 `eq`、`ne`、`gt`、`like`、`in`、`between`、`orderByDesc`
- [kp3|2] 多个条件默认用 AND 连接，需要 OR 时调用 `or()`
- [kp4|2] `LambdaQueryWrapper` 用方法引用代替字符串列名，改名时编译期就能发现
- [kp5] 条件值以参数方式绑定，不是直接拼进 SQL

## 详解
### 先搞懂：为什么需要它
页面上有个筛选表单：姓名可以不填，年龄可以不填，状态可以选也可以不选。后台就要根据“用户填了什么”来拼 where 条件。

手写 SQL 要在 XML 里用一堆 `<if>` 判断。条件构造器就是把这件事变成 Java 代码：想加什么条件就调用什么方法，像搭积木一样。

- **链式调用**：一个方法返回对象本身，可以接着调用下一个方法。
- **where 条件**：SQL 里过滤数据的部分。

### 常用方法
| 方法 | 对应的 SQL |
|---|---|
| `eq("name", "张三")` | `name = '张三'` |
| `gt("age", 18)` | `age > 18` |
| `like("name", "张")` | `name like '%张%'` |
| `in("id", list)` | `id in (...)` |
| `orderByDesc("id")` | `order by id desc` |

条件之间默认是 AND。想用 OR，在两个条件之间加 `.or()`。

### 按条件决定是否生效
每个方法都有一个带布尔参数的版本，第一个参数为 `false` 时这个条件会被忽略。这样“用户没填就不加条件”不用写 `if`。

### Lambda 版本
`QueryWrapper` 的列名是字符串，写错了要运行时才发现。`LambdaQueryWrapper` 用 `User::getName` 这样的方法引用，列名写错编译就报错。

## 示例
```java
LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
wrapper.eq(User::getStatus, 1)
       .like(name != null, User::getName, name)   // name 为 null 时不加这个条件
       .orderByDesc(User::getId);

List<User> list = userMapper.selectList(wrapper);
```

## 易错点
- 用字符串写列名，字段改名后运行时才报错
- 以为 `eq` 之类能拼出任意复杂 SQL；多表关联还是要手写
- 把 `like` 的参数直接拼进列名位置；列名要固定，用户输入只能放在值的位置

## 追问
### [f1] 条件构造器会不会有 SQL 注入风险？
条件的值是以参数方式绑定的，一般安全。风险在于把用户输入当成列名或排序字段传进去，这类要先校验白名单。
