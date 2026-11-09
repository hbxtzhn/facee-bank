---
id: q_01M6XCBN2T0CJ7P58KFVTQGDS3
title: 怎么让 MyBatis 把下划线字段自动映射成驼峰属性？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [sql-mapping, configuration]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MyBatis 3 文档：配置 - settings（mapUnderscoreToCamelCase）", url: "https://mybatis.org/mybatis-3/configuration.html" }
estimatedMinutes: 2
---

## 一句话
在 settings 里开启 `mapUnderscoreToCamelCase`，`user_name` 这样的下划线列就会自动映射到 `userName` 属性。

## 要点
- [kp1|3] 开启 `mapUnderscoreToCamelCase` 为 `true`，按驼峰规则自动映射
- [kp2|3] 它把 `user_name` 对应到 `userName`，不用再写别名
- [kp3|2] 这个设置默认关闭，需要手动打开
- [kp4] 只处理下划线转驼峰，其他命名差异仍要用别名或 resultMap

## 详解
### 先搞懂：数据库和 Java 习惯不一样
数据库的列习惯用小写加下划线，如 `user_name`、`create_time`。Java 属性习惯用驼峰，如 `userName`、`createTime`。两边都是各自的好习惯，可是 MyBatis 默认按名字完全一样才映射，所以对不上。

这就像中文名“张三”和拼音“Zhang San”：说的是同一个人，需要一个规则让它们互相认出来。驼峰开关就是这条规则。

术语说明：

- **下划线命名**：单词用 `_` 连接，全小写；
- **驼峰命名**：第一个单词小写，之后每个单词首字母大写。

### 怎么开启
配置文件里加一项设置，把 `mapUnderscoreToCamelCase` 设为 `true`。开启后，MyBatis 在做自动映射时，会把列名里的下划线去掉并把后面的字母大写，再去找对应的属性。

所以 `user_name` 会匹配到 `userName`，`create_time` 会匹配到 `createTime`，不需要手写别名，也不需要为此写 resultMap。

### 它管不到的情况
- 列名和属性名意思不同，比如 `order_no` 对 `code`，开关不起作用；
- 属性名里没有大写字母的情况下，需要整个名字去掉下划线后一致，才会匹配；
- 复杂的关联映射，仍要用 resultMap。

## 示例
```yaml
# Spring Boot 配置文件
mybatis:
  configuration:
    map-underscore-to-camel-case: true
```

```xml
<!-- 传统 XML 配置 -->
<settings>
  <setting name="mapUnderscoreToCamelCase" value="true"/>
</settings>
```

## 易错点
- 以为默认就是开启的，结果属性全是 null，其实默认关闭
- 以为开了就能解决所有名字不一致，其实只处理下划线转驼峰
- 在 resultMap 里已经显式映射的字段，不受这个开关影响

## 追问
### [f1] 开启后还需要给列写别名吗？
大多数下划线转驼峰的列不需要了。只有名字本身不同的，比如列叫 `code`、属性叫 `orderNo`，才需要别名或 resultMap。
