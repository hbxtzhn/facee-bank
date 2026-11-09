---
id: q_01M6XCC25YT1149WJN4PRWJZZR
title: 怎么复用 SQL 片段（sql 和 include）？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [dynamic-sql]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
用 `<sql>` 标签把重复出现的 SQL 片段定义一次，再用 `<include>` 在各条语句里引用，避免到处复制粘贴。

## 要点
- [kp1|3] `<sql id="...">` 定义可复用的片段，如字段列表、公共条件
- [kp2|3] `<include refid="..."/>` 在语句中引用，id 要对上
- [kp3|2] `<include>` 里可以用 `<property>` 给片段传参，片段内用 `${}` 取
- [kp4] 引用别的映射文件里的片段，`refid` 写 `namespace.id`

## 详解
### 先搞懂：为什么要复用 SQL 片段
一个用户表有十几个字段，`selectById`、`selectByName`、`selectAll` 都要写一遍同样的字段列表。以后加一列，就得改好几个地方，漏一处就出 bug。

复用就像写文章时的“引用”：把常用的一段话放在附录里，正文里只写“见附录”。

- **SQL 片段**：一段可以被多次引用的 SQL 文本。
- **refid**：引用的片段的 id。

### 定义和引用
先在映射文件里用 `<sql>` 起个 id，写上字段列表或公共条件。然后在 `<select>`、`<update>` 等语句里用 `<include refid="id"/>`，MyBatis 解析时会把片段原样放进去。

适合抽取的内容：字段列表、常用的 where 条件、公共的排序或表名。

### 给片段传参
片段里可以用 `${变量}`，引用处用 `<property name="变量" value="值"/>` 提供。这在多张表共用相似片段时有用，比如表别名不同。

注意 `${}` 是直接拼进 SQL 的文本，只放你自己写死的值，不要放用户输入。

## 示例
```xml
<sql id="userCols">id, name, age</sql>

<select id="selectById" resultType="com.example.User">
    select <include refid="userCols"/>
    from user where id = #{id}
</select>
```

## 易错点
- `refid` 写错或片段不在同一映射文件，又没带 namespace，启动时报找不到
- 片段里把用户输入用 `${}` 拼接，会有 SQL 注入风险
- 片段抽得太碎，读 SQL 时要来回跳，反而难维护

## 追问
### [f1] sql 片段能嵌套吗？
可以。片段里还能再 `<include>` 别的片段，但嵌套太深可读性差，一般一两层就够了。
