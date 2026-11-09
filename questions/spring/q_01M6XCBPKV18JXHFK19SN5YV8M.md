---
id: q_01M6XCBPKV18JXHFK19SN5YV8M
title: foreach 的 collection 属性在不同参数类型下怎么写？
type: concept
difficulty: easy
importance: 1
category: spring
tags: [dynamic-sql]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
`collection` 要写对参数的名字：单个 List 且没加 `@Param` 写 `list`，数组写 `array`，加了 `@Param` 就写注解里的名字。

## 要点
- [kp1|3] 单个 List 参数且没加注解时，`collection` 写 `list`
- [kp2|3] 单个数组参数且没加注解时，`collection` 写 `array`
- [kp3|2] 加了 `@Param` 后，`collection` 写注解里的名字
- [kp4|2] 传多个参数时，要给集合参数加 `@Param`，或封装进 Map、对象

## 详解
### 先搞懂：foreach 要知道“遍历谁”
`<foreach>` 的 `collection` 属性，告诉 MyBatis 去参数里找哪一个集合来遍历。写错了，MyBatis 找不到，就会报参数不存在的错误。

这像是对着一堆包裹说“把第三箱的东西拿出来”：你得说对箱子的名字。可是 MyBatis 有时会替你把参数改名，所以要知道规则。

术语说明：

- **参数名**：Mapper 方法的参数在 SQL 里使用的名字；
- **`@Param`**：给参数指定名字的注解。

### 几种情况怎么写
1. **单个 `List`，没加 `@Param`**：MyBatis 会把它包起来，名字固定为 `list`，所以写 `collection="list"`。
2. **单个数组，没加 `@Param`**：名字固定为 `array`，写 `collection="array"`。
3. **加了 `@Param("ids")`**：名字就是你起的，写 `collection="ids"`。
4. **有多个参数**：没有统一规则，最稳妥的做法是给集合参数加 `@Param`，名字写进 `collection`；也可以把所有参数装进一个 `Map` 或对象，用 key 或属性名引用。
5. **集合是对象的属性**：写成“对象名.属性名”。

### 推荐做法
无论几个参数，都给集合参数加 `@Param`。这样 `collection` 写的就是你自己起的名字，不用记“`list`、`array`”这些固定叫法，换参数个数也不会出错。

## 示例
```java
// 1. 单个 List，不加注解
List<User> findByIds(List<Long> ids);
// <foreach collection="list" ...>

// 2. 加 @Param，推荐
List<User> findByIds(@Param("ids") List<Long> ids);
// <foreach collection="ids" ...>
```

```xml
<foreach collection="ids" item="id" open="(" close=")" separator=",">
  #{id}
</foreach>
```

## 易错点
- 单个 List 没加注解，却把 `collection` 写成变量名，会提示找不到参数
- 多个参数时没给集合加 `@Param`，导致名字对不上
- 把数组写成 `list`，或把 List 写成 `array`，名字搞反了

## 追问
### [f1] 为什么推荐统一加 @Param？
统一加了，`collection` 就永远是你起的名字，不用区分 List、数组或参数个数。代码更好读，参数增减也不会让 SQL 悄悄出错。
