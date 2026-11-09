---
id: q_01M6XCBGRWDPSDMVC1HYFX55X8
title: 怎么定义和调用 Mapper 接口？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [mybatis-internals]
prerequisites: [q_01M6XCBGG2THFPCV9HY7RH11DQ]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
先定义 Mapper 接口方法，再让 XML 的 `namespace` 等于接口全名、语句 `id` 等于方法名，最后通过 `getMapper` 取得接口直接调用。

## 要点
- [kp1|3] 定义一个接口，每个方法对应一条 SQL
- [kp2|3] XML 的 `namespace` 写接口全限定名，语句 `id` 写方法名
- [kp3|2] 通过 `session.getMapper` 获取接口实现，直接调方法
- [kp4] 也可以不用接口，直接 `session.selectOne` 执行

## 详解
### 先搞懂：接口是点菜单，XML 是后厨
做项目时，你只调接口方法，没有写实现类。这像点菜：菜单（接口）上只有菜名，后厨（XML）里有每道菜的做法。菜名要完全对得上，后厨才知道做哪道。

后文用到的词：

- **Mapper 接口**：只有方法声明，没有实现类的接口。
- **全限定名**：带包名的完整类名，如 `com.example.UserMapper`。

### 三步写法
1. 写接口，方法名即语句名：`User findById(long id);`
2. 写 XML：`namespace` 写接口全限定名，`<select>` 的 `id` 写 `findById`；
3. 获取并调用：`session.getMapper(UserMapper.class)`，拿到对象后直接调用方法。

### 为什么不用写实现类
框架用动态代理为接口生成实现：调用方法时，代理按"接口全名加方法名"去找 SQL 并执行。所以对应关系只要有一个字写错，就会找不到语句。

## 示例
```java
public interface UserMapper {
    User findById(long id);
}
```

```xml
<mapper namespace="com.example.UserMapper">
    <select id="findById" resultType="com.example.User">
        SELECT id, name FROM user WHERE id = #{id}
    </select>
</mapper>
```

```java
UserMapper mapper = session.getMapper(UserMapper.class);
User user = mapper.findById(1L);
```

## 易错点
- `namespace` 少写包名，导致找不到语句
- 给接口自己写实现类；通常不需要，框架会生成代理

## 追问
### [f1] 接口方法可以重载吗？
不建议。语句靠方法名定位，同名方法会对应到同一个 `id`，容易出错。
