---
id: q_01M6XCC1D7NXNJ48ST5PCMY9RT
title: XML 映射文件里的 namespace 是做什么的？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [mybatis-internals, mybatis-cache]
prerequisites: [q_01M6XCBEWTXT97DJVTJA1PAT5G]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
`namespace` 是 Mapper 映射文件的“身份标识”：它指向对应的 Mapper 接口，同时也是语句 id 和二级缓存的作用范围。

## 要点
- [kp1|3] `namespace` 要写成 Mapper 接口的全限定名，两者靠它绑定
- [kp2|3] 语句的完整 id 是 `namespace.语句id`，接口方法名对应语句 id
- [kp3|2] 二级缓存按 `namespace` 划分，一个 namespace 一份缓存
- [kp4] 不同映射文件的同名语句靠 `namespace` 区分，不会冲突

## 详解
### 先搞懂：为什么需要“命名空间”
一个项目有几十个 Mapper，很多都有 `selectById`、`insert` 这类名字。如果没有区分，MyBatis 就不知道你要的是哪个。

这就像公司里有两个叫“小王”的人，得加上部门才分得清。`namespace` 就是这个“部门”。

- **全限定名**：包名加类名，如 `com.example.mapper.UserMapper`。
- **语句 id**：映射文件里 `<select id="selectById">` 的 id。
- **二级缓存**：多个会话共享的缓存，作用范围比单个会话大。

### 绑定接口：让接口方法找到 SQL
你调用 `userMapper.selectById(1)`，MyBatis 会用“接口全限定名 + 方法名”拼出 `com.example.mapper.UserMapper.selectById`，再去找同名语句。

所以映射文件的 `namespace` 必须等于接口的全限定名，方法名必须等于语句 id。对不上就会报“找不到语句”。这套绑定靠的是动态代理：接口没有实现类，调用被代理对象转成对 SQL 语句的执行。

### 缓存范围：一个 namespace 一份缓存
开启二级缓存后，缓存是挂在 `namespace` 上的。同一个 namespace 里的查询共用一份缓存，而这个 namespace 里的增删改会清空这份缓存。

如果两个 Mapper 需要共用缓存，可以用 `<cache-ref namespace="..."/>` 引用对方的缓存。

## 示例
```xml
<mapper namespace="com.example.mapper.UserMapper">
    <select id="selectById" resultType="com.example.User">
        select * from user where id = #{id}
    </select>
</mapper>
```

## 易错点
- `namespace` 写成了随便取的名字，用接口调用时找不到语句
- 以为二级缓存对所有 Mapper 全局共享；其实默认每个 namespace 各用各的
- 改了接口的包名或类名，忘了同步改 `namespace`

## 追问
### [f1] 两个 Mapper 的表有关联，改了其中一个的数据，另一个的缓存会过期吗？
不会。缓存按 namespace 隔离，只有本 namespace 的增删改才会清空自己的缓存。这是二级缓存可能读到脏数据的原因之一，需要的话用 `<cache-ref>` 让它们共用一份。
