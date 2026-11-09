---
id: q_01M6XCBPVTD1W07TKKJXNCSG0G
title: OGNL 表达式在动态 SQL 中是怎么取值的？
type: concept
difficulty: medium
importance: 1
category: spring
tags: [dynamic-sql, reflection]
prerequisites: [q_01M6XCBNK1F0XM77F4682VE0WA]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
MyBatis 动态 SQL 里的 `test` 条件交给 OGNL 计算，OGNL 按属性名从参数对象里取值，再算出 true 或 false 决定这段 SQL 要不要拼。

## 要点
- [kp1|3] `<if test>`、`<when test>` 等条件由 OGNL 表达式引擎计算
- [kp2|3] 表达式里的变量名就是参数对象的属性名或 Map 的 key
- [kp3|2] 表达式只在拼 SQL 时算一次，结果决定片段是否保留
- [kp4] 多参数不加 `@Param` 时，属性名对不上会报错

## 详解
### 先搞懂：按条件拼 SQL，条件怎么判断
做商品搜索时，用户可能填标题，也可能不填。填了就加 `title like ...`，没填就不加。这个「填没填」的判断，写在 `<if test="title != null">` 里。

可以把它想成点餐单上的勾选框：你勾了才上这道菜，没勾就跳过。`test` 里的表达式就是判断「勾没勾」的规则。

后文用到的术语：
- **OGNL**：一种表达式语言，能写属性访问、比较、逻辑运算。
- **参数对象**：你传给 Mapper 方法的那个参数，可以是实体、Map 或单个值。
- **动态 SQL**：运行时按条件拼出来的 SQL。

### 取值：按属性名找，找的是 getter
假设 Mapper 方法的参数是一个 `Article` 对象，里面有 `title` 属性。表达式 `title != null` 里的 `title`，就是去参数对象上取 `title`。

取值走的是反射：OGNL 通过 getter 方法（或直接读字段）拿到属性值，所以属性名要和 getter 对得上。参数如果是 `Map`，`title` 就是 Map 里的 key。

多层属性也能写，比如 `user.name != null`，意思是先取 `user`，再取它的 `name`。

### 计算：拼 SQL 的时候算一次
MyBatis 解析映射文件时，会把 SQL 拆成一个个节点，`<if>` 就是其中一种节点。真正执行时，每个 `<if>` 节点把 `test` 交给 OGNL 去算。

算出 true，这段 SQL 文本追加到最终语句里。算出 false，这段直接丢掉。所以最终发给数据库的 SQL，只包含条件成立的那些片段。

OGNL 的表达式会被缓存，同一个表达式不用每次重新解析，只是每次重新取值。

### 常用写法
- 判空：`title != null and title != ''`，用 `and`、`or` 连接，不用 `&&` 也可以，但 XML 里 `&&` 要转义，所以习惯写 `and`。
- 比较：`age > 18`，`status == 1`。
- 调方法：`list != null and list.size() > 0`。
- 取整个参数：单个简单类型参数时，可以用 `_parameter` 指代它。

### 进阶：绑定变量和源码入口（基础薄弱可先跳过）
- `<bind>` 可以先算出一个变量，后面的 `test` 和 `#{}` 都能用。
- 源码里表达式由 `ExpressionEvaluator` 计算，内部调用 OGNL，上下文是 `DynamicContext`，参数对象放在其中。
- 多个参数没写 `@Param` 时，MyBatis 会把它们放进一个 Map，key 是 `param1`、`param2` 等，直接写属性名会取不到。

## 示例
```xml
<select id="search" resultType="Article">
  select * from article
  <where>
    <if test="title != null and title != ''">
      and title like concat('%', #{title}, '%')
    </if>
    <if test="authorId != null">
      and author_id = #{authorId}
    </if>
  </where>
</select>
```

## 易错点
- 把 Integer 属性写成 `id != ''`；OGNL 会把空串当成数字 0 比较，导致值为 0 时条件被误判为假
- 属性名拼错或没有 getter；运行时会抛出找不到属性的异常，而不是当作 null
- 多个参数不加 `@Param`，直接写 `title`；取不到值，要写 `param1` 或加注解
- 以为 `test` 里的表达式是 Java 代码；它是 OGNL，语法相近但规则不完全相同

## 追问
### [f1] `<if>` 判断 String 为空，为什么常写 `title != null and title != ''`？
只判 null 会放过空串，拼出 `like '%%'` 这种没意义的条件。两个都判，才能保证用户没有真正输入时，条件不生效。

### [f2] 参数是 Map 时，表达式里怎么取值？
直接写 key 名即可，`title` 就是 `map.get("title")`。如果 key 不存在，结果是 null，不会报错。
