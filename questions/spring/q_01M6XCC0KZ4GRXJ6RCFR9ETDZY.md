---
id: q_01M6XCC0KZ4GRXJ6RCFR9ETDZY
title: Mapper 方法的返回值类型怎么影响执行结果？
type: concept
difficulty: medium
importance: 1
category: spring
tags: [mybatis-internals, sql-mapping]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MyBatis 源码：MapperMethod.java", url: "https://raw.githubusercontent.com/mybatis/mybatis-3/master/src/main/java/org/apache/ibatis/binding/MapperMethod.java" }
  - { title: "MyBatis 3 文档：Java API（SqlSession、ExecutorType、Mapper 注解）", url: "https://mybatis.org/mybatis-3/java-api.html" }
estimatedMinutes: 3
---

## 一句话
Mapper 方法的返回值类型决定 MyBatis 调用 SqlSession 的哪个方法：返回列表走 selectList，单个对象走 selectOne，Map 走 selectMap，Cursor 走 selectCursor。

## 要点
- [kp1|3] 返回 `List` 或数组，调用 `selectList`，结果转成对应集合
- [kp2|3] 返回单个对象，调用 `selectOne`，多于一行会抛异常
- [kp3|2] 返回 `Map` 需要 `@MapKey`，调用 `selectMap`
- [kp4|2] 返回 `Cursor` 调用 `selectCursor`，边读边处理
- [kp5] 返回 `void` 并带 `ResultHandler` 参数时，结果交给回调处理

## 详解
### 先搞懂：同样是查询，要的“货”不同
你去超市买东西，可能想要一箱、一个，或者按名字索引的一排。店员要先问清你要什么，才知道怎么拿。

Mapper 方法的返回类型就是这个“要什么”：返回列表、单个对象，还是 Map，MyBatis 要调用不同的方法去取，再按你要的形式交给你。

后文用到的词：

- **selectList**：执行查询，返回所有行组成的列表。
- **selectOne**：执行查询，只要一个结果。
- **Cursor**：游标，一行一行读取，不会一次性装入内存。

### 各种返回类型的处理
这些判断发生在 `MapperMethod` 里，只对 SELECT 语句生效：

- **返回 List、数组、Collection**：调用 `selectList`，再根据声明转换成对应形式，比如转成数组。
- **返回 Map**：要在方法上加 `@MapKey`，指定用哪个属性做 key，调用 `selectMap`。
- **返回 Cursor**：调用 `selectCursor`，适合大结果集，边迭代边读取。使用完要关闭。
- **返回单个对象**：调用 `selectOne`，本质是 `selectList` 之后取一个：没有行返回 null，多于一行抛出 `TooManyResultsException`。
- **返回 Optional**：同 `selectOne`，再用 `Optional` 包起来。
- **void 且参数里有 ResultHandler**：每读到一行就回调一次，不返回集合。

### 增删改的返回值
INSERT、UPDATE、DELETE 的返回类型用来接收影响行数：

- 返回 `int` 或 `long`：直接是影响的行数；
- 返回 `boolean`：影响行数大于 0 就是 true；
- 返回 `void`：不关心结果。

### 为什么这样设计
返回类型本身已经表达了开发者想要的形态，MyBatis 据此选择最合适的方法，开发者不用在代码里手动转换。

## 示例
```java
public interface UserMapper {
    List<User> findAll();                       // selectList
    User findById(Long id);                     // selectOne
    @MapKey("id")
    Map<Long, User> findMap();                  // selectMap，用 id 做 key
    Cursor<User> scanAll();                     // selectCursor，用完要关闭
    int updateName(Long id, String name);       // 返回影响行数
}
```

## 易错点
- 返回单个对象但查询结果有多行，抛出 `TooManyResultsException`
- 返回 Map 却没写 `@MapKey`，不知道用哪个属性做 key
- 用完 Cursor 不关闭，数据库资源被占用
- 返回基本类型但查询无结果，得到 null 转换失败

## 追问
### [f1] 返回单个对象但查不到会怎样？
返回 null。如果方法返回的是 `int`、`long` 这类基本类型，null 无法转换，会抛出异常，所以可空的结果建议用包装类型或 `Optional`。

### [f2] Cursor 和 List 的区别是什么？
`List` 一次性把所有行读进内存；`Cursor` 按需一行一行读，适合很大的结果集，但需要在事务或会话未关闭时使用。
