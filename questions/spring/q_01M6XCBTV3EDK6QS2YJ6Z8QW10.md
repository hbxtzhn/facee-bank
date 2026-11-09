---
id: q_01M6XCBTV3EDK6QS2YJ6Z8QW10
title: 为什么更新操作会让二级缓存失效？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [mybatis-cache, cache-consistency]
prerequisites: [q_01M6XCBSNWRWKD6XSZ1X4ZS2CS]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
更新操作成功提交后会清空所在 namespace 的二级缓存，这样之后的查询就必须重新访问数据库，不会读到更新之前的旧数据。

## 要点
- [kp1|3] 对应 namespace 里的 insert、update、delete 会清空它的二级缓存
- [kp2|3] 清空是为了让后续查询重新从数据库读最新数据
- [kp3|2] 清空的是整个 namespace，不是只删被改的那一行
- [kp4] 增删改语句默认 `flushCache` 为 true，可以改成 false

## 详解
### 先搞懂：改了数据，缓存里的就成了过期货
缓存里存着「用户 1 的名字叫张三」。你把名字改成李四。如果缓存不清，别人再查，读到的还是张三，和数据库对不上。

可以把它想成菜单：菜价调整了，就必须撤掉旧菜单、换新菜单，不然客人照着旧价格点单。

后文用到的术语：
- **缓存一致性**：缓存里的数据和数据库里的数据保持一致。

### 为什么清整个 namespace
MyBatis 不解析 SQL 内容，无法判断一条更新影响了缓存里的哪几项。比如 `update user set status = 1 where age > 30` 可能影响很多个缓存的查询结果。

最简单可靠的办法是：只要这个 namespace 有增删改，就把这个 namespace 的缓存全部清空。清空之后，后面的查询重新从数据库加载，结果自然是最新的。

### 清空发生在什么时候
增删改语句默认带有 `flushCache="true"`。和查询结果入缓存一样，清空也是通过事务暂存机制处理的：事务提交之后，清空才真正生效。

### 可以关掉吗
可以在某条更新语句上写 `flushCache="false"`，这样这条更新不清缓存。但这等于接受缓存可能过期，只适合你能确定这次更新不影响任何缓存查询的场景。

### 联表的盲区
更新只清自己 namespace 的缓存。如果另一个 Mapper 的缓存里存着联了这张表的结果，它不会被清，仍可能读到旧数据。这时可以用 `<cache-ref>` 让两个 Mapper 共享缓存。

## 示例
```xml
<update id="updateName" flushCache="true">
  update user set name = #{name} where id = #{id}
</update>
```

## 易错点
- 以为只清被修改的那一条缓存；实际清整个 namespace
- 在其他 Mapper 里更新了相关的表，却以为本 Mapper 的缓存也会清；不会
- 随意给更新语句设置 `flushCache="false"`；之后查询可能读到旧数据

## 追问
### [f1] 事务回滚了，二级缓存会怎样？
二级缓存的写入和清空都先放在暂存区，只有提交才生效。事务回滚时，暂存的内容被丢弃，二级缓存不受影响。
