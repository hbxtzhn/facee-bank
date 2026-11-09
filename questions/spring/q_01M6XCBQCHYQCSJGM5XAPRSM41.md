---
id: q_01M6XCBQCHYQCSJGM5XAPRSM41
title: MyBatis 怎么映射一对多关联？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [association-mapping]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
一对多关联就是在实体类里放一个 `List` 属性，再在 resultMap 里用 `<collection>` 指定属性名和元素类型，把多行结果装成一个集合。

## 要点
- [kp1|3] 实体类里定义集合属性，如分类里放 `List<Product> products`
- [kp2|3] resultMap 里用 `<collection>` 映射这个集合属性
- [kp3|2] `property` 写集合属性名，`ofType` 写集合里元素的类型
- [kp4] 联表查询会返回多行，MyBatis 靠 `<id>` 把多行合并成一个主对象

## 详解
### 先搞懂：一个分类下有很多商品
商品分类和商品是一对多：一个分类下有很多商品。查分类时，希望得到的分类对象里直接带着商品列表。

可以把它想成文件夹：分类是文件夹，商品是里面的文件。查出来的是一堆「文件夹加文件」的行，MyBatis 要把同一个文件夹的行合起来，文件放进同一个列表。

后文用到的术语：
- **`<collection>`**：映射「对象里面的一个集合」。
- **`ofType`**：集合里每个元素是什么类型。

### 第一步：实体类里放集合
```java
public class Category {
    private Long id;
    private String name;
    private List<Product> products;   // 一对多关联
}
```

### 第二步：resultMap 里用 collection
`<collection>` 的 `property` 写 `products`，`ofType` 写 `Product`。标签内部用 `<id>`、`<result>` 映射商品表的列。

联表查询时，一个分类有 3 个商品，就会查出 3 行，分类的列每行都重复。MyBatis 看分类的 `<id>` 值：值相同就认为是同一个分类，只创建一次，把每行里的商品追加进列表。

### association 和 collection 的区别
- `<association>` 的关联属性是单个对象，用 `javaType`。
- `<collection>` 的关联属性是集合，用 `ofType`。

## 示例
```xml
<resultMap id="categoryMap" type="Category">
  <id property="id" column="id"/>
  <result property="name" column="name"/>
  <collection property="products" ofType="Product">
    <id property="id" column="product_id"/>
    <result property="title" column="title"/>
  </collection>
</resultMap>

<select id="getCategory" resultMap="categoryMap">
  select c.id, c.name, p.id as product_id, p.title
  from category c left join product p on p.category_id = c.id
  where c.id = #{id}
</select>
```

## 易错点
- 主对象的 `<id>` 没写；MyBatis 没法判断哪些行属于同一个对象，可能拆成多个重复对象
- 把 `ofType` 写成 `javaType`；集合元素类型要用 `ofType`
- 联表查询时用 `limit` 分页；它按行截断，会把一个分类的商品截断，需要改用嵌套查询或先分页主表

## 追问
### [f1] 分类下没有商品时，`products` 是 null 还是空列表？
联表查不到商品时，MyBatis 一般会给出空集合，而不是 null。如果代码依赖这点，建议在测试里确认。
