---
id: q_01M6XCBEWTXT97DJVTJA1PAT5G
title: MyBatis 的 XML 映射文件是做什么的？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [mybatis-internals, sql-mapping]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
XML 映射文件把 SQL 从 Java 代码里单独拿出来集中存放，实现 SQL 与代码分离，改 SQL 时不用动 Java 代码。

## 要点
- [kp1|3] 映射文件用来存放 SQL 语句，让 SQL 与 Java 代码分离
- [kp2|3] `namespace` 对应 Mapper 接口全名，语句 `id` 对应方法名
- [kp3|2] 在里面配置参数类型和结果映射
- [kp4] 动态 SQL 标签也写在这里

## 详解
### 先搞懂：SQL 像菜谱，不要夹在炒菜动作里
做项目时，如果 SQL 全拼在 Java 字符串里，改一个条件就要改代码、重新编译。这像把菜谱手写在锅铲上：想改配方得换锅铲。把菜谱单独写在一本书里（映射文件），改配方只需改这本书。

后文用到的词：

- **映射文件**：一个 XML 文件，里面存放某个 Mapper 对应的所有 SQL。
- **Mapper 接口**：Java 接口，每个方法对应一条 SQL。

### 映射文件里有什么
- `<select>`、`<insert>`、`<update>`、`<delete>`：各自对应一条 SQL；
- `parameterType`：参数类型；
- `resultType` 或 `resultMap`：结果映射成什么对象；
- `<if>`、`<where>` 等标签：写动态 SQL。

### 它和接口怎么对上
映射文件根标签 `<mapper>` 的 `namespace` 写 Mapper 接口的全限定名，里面每条语句的 `id` 写接口的方法名。这样调用接口方法时，框架就能找到对应的 SQL。

### 好处
SQL 集中管理，便于阅读和维护；DBA 或其他同事可以直接审查和优化 SQL，而不用翻 Java 代码。

## 示例
```xml
<mapper namespace="com.example.UserMapper">
    <select id="findById" resultType="com.example.User">
        SELECT id, name FROM user WHERE id = #{id}
    </select>
</mapper>
```

## 易错点
- 以为 SQL 只能写在 XML 里；简单语句也可以用注解
- `namespace` 或 `id` 写错，调用时会提示找不到对应语句

## 追问
### [f1] 一个映射文件对应几个 Mapper 接口？
通常一对一：一个映射文件的 `namespace` 对应一个 Mapper 接口，里面放这个接口全部方法的 SQL。
