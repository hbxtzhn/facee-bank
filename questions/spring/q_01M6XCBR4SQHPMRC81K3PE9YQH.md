---
id: q_01M6XCBR4SQHPMRC81K3PE9YQH
title: 延迟加载是怎么实现的（CGLIB 代理与拦截）？
type: concept
difficulty: medium
importance: 2
category: spring
tags: [association-mapping, dynamic-proxy]
prerequisites: [q_01M6XCBQWWQPY8ASY7VYDWPJ9R]
source: { name: FaceE, license: CC-BY-4.0 }
references:
  - { title: "MyBatis 3 文档：配置 - settings（proxyFactory 等）", url: "https://mybatis.org/mybatis-3/configuration.html" }
  - { title: "MyBatis 源码：JavassistProxyFactory", url: "https://github.com/mybatis/mybatis-3/blob/master/src/main/java/org/apache/ibatis/executor/loader/javassist/JavassistProxyFactory.java" }
estimatedMinutes: 3
---

## 一句话
MyBatis 给结果对象生成一个代理子类，你调用关联属性的 getter 时，代理拦截下来，先执行预先保存好的关联 SQL，把结果赋给对象，再放行原方法。

## 要点
- [kp1|3] 查询时关联属性先留空，同时把关联 SQL 的信息保存起来
- [kp2|3] 返回给你的不是原对象，而是它的代理子类
- [kp3|2] 调用到需要懒加载的 getter 时被拦截，执行关联查询并赋值
- [kp4] 代理工具默认是 Javassist，也可以配置成 CGLIB

## 详解
### 先搞懂：你拿到的其实是个「替身」
查订单时，MyBatis 返回的不是普通的 `Order`，而是一个继承了 `Order` 的代理对象，外表和 `Order` 一样。

可以把它想成秘书：老板（订单）的某些资料不在手边，你问秘书，秘书先去档案室取出来，再回答你。你全程只对秘书说话，感觉不到中间多了一步。

后文用到的术语：
- **代理对象**：运行时生成的子类，能在方法被调用前后插入自己的逻辑。
- **拦截器**：代理里负责「半路截住方法调用」的那段代码。

### 创建阶段：留空并记账
开启 `lazyLoadingEnabled` 后，MyBatis 映射结果对象时，遇到延迟的关联属性，不去执行关联 SQL。它只把这条 SQL 的信息（语句 id、参数）记下来，关联属性保持为 null，并把整个对象换成代理对象返回。

### 访问阶段：拦截、查询、赋值、放行
1. 你调用 `order.getPay()`，实际进入代理的拦截器。
2. 拦截器检查这个属性是不是有待加载的记录。
3. 有，就执行记下来的关联 SQL，查到结果后用 set 方法赋给对象。
4. 最后放行原方法，`getPay()` 返回的就是刚查到的值。
5. 这个属性之后不再待加载，下次调用直接返回。

### 为什么用代理，不直接改代码
关联属性是你自己定义的普通字段，MyBatis 没法改你的类，也不想让你每个 getter 都手写查询逻辑。代理在运行时动态加一层，业务代码完全不用感知。

### 进阶：代理工具和触发方法（基础薄弱可先跳过）
- `proxyFactory` 设置可选 CGLIB 或 JAVASSIST，较新版本默认是 JAVASSIST，CGLIB 自 3.5.10 起已标记弃用。
- 代理是子类，所以实体类不能是 `final`，要延迟加载的方法也不能是 `final`。
- `lazyLoadTriggerMethods` 指定哪些方法会触发整体加载，默认是 `equals`、`clone`、`hashCode`、`toString`。
- `aggressiveLazyLoading` 为 true 时，调用任何一个属性就加载所有延迟属性；新版本默认为 false。

## 易错点
- 把代理对象当成原类对象，用 `getClass() == Order.class` 判断；代理是子类，判断会失败
- 实体类写成 `final`；子类没法继承，延迟加载无法生效
- 以为拦截发生在查询阶段；实际是第一次调用 getter 时才触发

## 追问
### [f1] 延迟加载的结果会缓存吗？
赋值之后就保存在对象里，之后再调用 getter 不会再发 SQL。同一个 SqlSession 里相同的查询，还可能命中一级缓存。
