---
id: q_01M6XBP98KY9K9AZK8HKB9VM2N
title: Spring 是怎么通过三级缓存解决循环依赖的？
type: concept
difficulty: hard
importance: 3
category: spring
tags: [bean-lifecycle]
prerequisites: [q_01M6XBH8EVVJ781F6BQC0TEHFV]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 5
references:
  - { title: "Spring Framework 源码：DefaultSingletonBeanRegistry（三级缓存字段、getSingleton、addSingleton）", url: "https://github.com/spring-projects/spring-framework/blob/main/spring-beans/src/main/java/org/springframework/beans/factory/support/DefaultSingletonBeanRegistry.java" }
  - { title: "Spring Framework 源码：AbstractAutowireCapableBeanFactory（doCreateBean 中的提前曝光）", url: "https://github.com/spring-projects/spring-framework/blob/main/spring-beans/src/main/java/org/springframework/beans/factory/support/AbstractAutowireCapableBeanFactory.java" }
---

## 一句话
Spring 创建单例时，对象刚实例化就把“生产它的工厂”放进三级缓存；循环依赖时，对方从缓存里拿到这个半成品先用着，等它创建完整再放进一级缓存。

## 要点
- [kp1|3] 三级缓存：一级成品池，二级早期对象，三级对象工厂
- [kp2|3] 实例化后、注入属性前，先把 ObjectFactory 放进三级缓存
- [kp3|2] 依赖方按一级、二级、三级顺序查找，在三级通过工厂拿到早期引用并升到二级
- [kp4|2] 对象创建完整后放入一级缓存，并清理二、三级
- [kp5] 只有 setter 或字段注入的环才有机会走通这个流程

## 详解
### 先搞懂：先把“半成品”摆出来
假设 A、B 互相依赖。就像两个人合作做菜：A 先把锅架上（对象创建出来但没放料），告诉大家“我在这儿，料稍后补”；B 要用 A 时，先拿着这口还没做好的锅，等 A 补好料，B 手里的其实就是同一口锅。

后文术语：
- **实例化**：调用构造方法 new 出对象，此时属性还是空的。
- **属性注入**：给对象的依赖字段赋值。
- **初始化**：执行初始化回调、后置处理等，AOP 代理通常在这一步之后生成。
- **ObjectFactory**：一个小工厂，调用它能得到这个 Bean 的“早期引用”。

### 三级缓存各放什么
| 缓存 | 字段名 | 里面放什么 |
|---|---|---|
| 一级 | `singletonObjects` | 完全创建好的单例，也就是成品池 |
| 二级 | `earlySingletonObjects` | 已提前曝光的早期对象（半成品） |
| 三级 | `singletonFactories` | 能生产早期引用的 ObjectFactory |

### 以 A、B 互相依赖为例，按顺序走一遍
1. 创建 A：先实例化 A（属性为空），把 A 的 ObjectFactory 放进三级缓存。
2. 给 A 注入属性，发现要 B，B 还不存在，转去创建 B。
3. 创建 B：实例化 B，同样把 B 的工厂放进三级缓存。
4. 给 B 注入属性，发现要 A，去缓存找：一级没有，二级没有，在三级找到 A 的工厂。调用工厂得到 A 的早期引用，放进二级缓存，并从三级移除。
5. B 拿到 A 的半成品，完成注入和初始化，放进一级缓存。
6. 回到 A，注入 B（已完成），A 完成初始化，放进一级缓存，二级缓存里的 A 随之清理。

这样 B 手里的 A 与最终的 A 是同一个对象，等 A 完成后，两边都是完整的。

### 进阶：为什么放的是工厂而不是对象
工厂在被调用时，才会决定早期引用是原始对象还是 AOP 代理（通过 `getEarlyBeanReference`）。这样没有循环依赖的 Bean 不用提前生成代理，仍然在初始化之后生成。这部分在“为什么需要三级缓存”一题里展开。

## 易错点
- 以为三级缓存能解决构造器注入的环；构造器注入时对象无法提前实例化
- 以为二级缓存放的是成品；它放的是半成品
- 以为每个 Bean 都会用到三级和二级缓存；没有循环依赖的 Bean 只是放入三级、最后进一级

## 追问
### [f1] B 拿到的 A 是半成品，会不会出问题？
不会，因为拿到的是同一个对象引用；只要 B 在创建期间不去调用 A 里还没注入好的功能，等 A 创建完成后，B 持有的就是完整的 A。

### [f2] 三级缓存的数据什么时候被清掉？
对象完全创建好放入一级缓存时，会同时把二级、三级缓存中同名的条目移除。
