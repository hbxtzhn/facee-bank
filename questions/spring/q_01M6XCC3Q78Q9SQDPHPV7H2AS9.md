---
id: q_01M6XCC3Q78Q9SQDPHPV7H2AS9
title: MyBatis 的类型别名是什么，有什么用？
type: concept
difficulty: easy
importance: 1
category: spring
tags: [configuration, sql-mapping]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
类型别名是给 Java 类起的短名字，在映射文件里写别名就行，不用每次写完整的包名加类名。MyBatis 还内置了 `int`、`string`、`map` 等常用别名。

## 要点
- [kp1|3] `typeAliases` 给类起别名，映射文件里用别名代替全限定名
- [kp2|3] MyBatis 内置了常见类型的别名，如 `string`、`int`、`map`、`list`
- [kp3|2] 用 `<package name="...">` 批量注册，别名默认是类的简单名
- [kp4] 在类上加 `@Alias` 可以自定义别名

## 详解
### 先搞懂：别名解决什么问题
映射文件里经常要写 `resultType="com.example.model.User"`。几十个语句里都写这么长一串，既啰嗦，改包名时又要全局替换。

别名就像给人起外号：叫“小王”比叫全名省事，大家都认得。

- **全限定名**：包名加类名。
- **别名**：全限定名的简写，MyBatis 解析配置时会还原。

### 自己注册别名
有两种常用方式：

- 逐个注册：`<typeAlias type="..." alias="user"/>`；
- 按包注册：`<package name="com.example.model"/>`，包下每个类的简单名就是别名，不区分大小写。

如果想换个名字，在类上加 `@Alias("xxx")`。Spring Boot 里用 `mybatis.type-aliases-package` 配包名即可。

### 内置别名
常见类型已经预设了别名，不用自己注册：

| 别名 | 对应的类型 |
|---|---|
| `string` | `String` |
| `int`、`integer` | `Integer` |
| `long`、`boolean`、`double` | 对应的包装类 |
| `_int`、`_long` | 基本类型 `int`、`long`（前面带下划线） |
| `map`、`list` | `Map`、`List` |
| `date` | `Date` |

结论：常用类型直接写内置别名，自己的实体类按包注册，既短又统一。

## 示例
```xml
<typeAliases>
    <package name="com.example.model"/>
</typeAliases>
```

```xml
<!-- 不用写全名，写简单名即可 -->
<select id="selectById" resultType="User">
    select * from user where id = #{id}
</select>
```

## 易错点
- 两个包下有同名类，按包注册时别名冲突，启动会报错
- 以为 `int` 和 `_int` 是一回事；`int` 对应包装类 `Integer`，`_int` 才是基本类型
- 别名只在 MyBatis 配置里生效，Java 代码里不能用

## 追问
### [f1] 用别名有什么坏处？
别名和类名对不上时，排查要多一步。类名多的项目里还可能冲突。所以团队要统一约定，要么都用别名，要么都写全名。
