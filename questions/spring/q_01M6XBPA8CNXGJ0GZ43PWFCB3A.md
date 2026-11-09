---
id: q_01M6XBPA8CNXGJ0GZ43PWFCB3A
title: JDK 动态代理和 CGLIB 代理有什么区别？
type: concept
difficulty: medium
importance: 3
category: spring
tags: [dynamic-proxy]
prerequisites: [q_01M6XBP9ZWJJVYTDKK8GKBAAVQ]
appliesTo: ["Spring Boot >= 2.0（默认使用 CGLIB）"]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
references:
  - { title: "Spring Framework 参考文档：Proxying Mechanisms（JDK 与 CGLIB 的选择、proxyTargetClass、CGLIB 限制）", url: "https://docs.spring.io/spring-framework/reference/core/aop/proxying.html" }
  - { title: "Spring Boot 参考文档：Aspect-Oriented Programming（默认使用 CGLIB 代理）", url: "https://docs.spring.io/spring-boot/reference/features/aop.html" }
  - { title: "Spring Boot 2.0 Migration Guide：Default Proxying Strategy", url: "https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-2.0-Migration-Guide" }
---

## 一句话
JDK 动态代理要求目标类有接口，生成的代理实现这些接口；CGLIB 通过继承生成目标类的子类，不需要接口，但不能代理 final 类和 final 方法。

## 要点
- [kp1|3] JDK 代理基于接口，代理类实现目标的接口
- [kp2|3] CGLIB 基于继承，生成目标类的子类并覆盖方法
- [kp3|2] CGLIB 无法代理 final 类，也无法增强 final 和 private 方法
- [kp4|2] Spring Boot 2.0 起默认优先用 CGLIB
- [kp5] JDK 代理出来的对象不能转成目标实现类

## 详解
### 先搞懂：两种“做替身”的方式
JDK 代理像是“照着合同（接口）找个能签同样合同的人”：只要合同一样，调用方就分不出区别。CGLIB 像是“找个目标的亲戚（子类）”，继承目标的一切，再改写其中几个行为。

后文术语：
- **接口**：只规定有哪些方法，不写具体做法。
- **子类**：继承父类，可以覆盖父类的方法。
- **final**：被它修饰的类不能被继承，方法不能被覆盖。

### 方案对比：JDK 动态代理与 CGLIB
| 维度 | JDK 动态代理 | CGLIB |
|---|---|---|
| 实现方式 | 生成实现目标接口的代理类 | 生成目标类的子类 |
| 是否需要接口 | 必须有接口 | 不需要 |
| final 类和方法 | 不涉及（只看接口方法） | final 类不能代理，final 方法不能增强 |
| 来源 | JDK 自带 | 第三方库，Spring 内部已打包 |
| 注入时的类型 | 只能用接口类型接收 | 可以用目标类型接收 |

结论：有接口时两者都可以；需要按类注入或没有接口时用 CGLIB。Spring Boot 默认选 CGLIB，省去类型转换的麻烦。

### Spring 怎么选
Spring Framework 本身的规则是：目标类实现了接口，用 JDK 代理；没有接口，用 CGLIB。设置 `proxyTargetClass=true` 可以强制用 CGLIB。Spring Boot 2.0 起把这个值默认设为 true，所以 Boot 项目默认用 CGLIB。

### 进阶：CGLIB 的限制
CGLIB 要覆盖方法，所以 final 方法和 private 方法无法被拦截。Spring 借助 Objenesis 创建 CGLIB 代理实例，目标类的构造器不会被调用两次。

## 易错点
- 以为 JDK 代理也能把对象转成目标实现类；它只实现了接口，转换会报错
- 以为 CGLIB 能代理一切；final 类和 final 方法不行
- 以为 Spring 永远用 JDK 代理；Boot 项目默认是 CGLIB
- 凭印象说某一种更快；没有测试依据不要下结论

## 追问
### [f1] 为什么 final 方法不能被 CGLIB 增强？
CGLIB 靠在子类中覆盖方法来拦截，final 方法不能被覆盖，调用会直接走父类原方法，增强逻辑不会执行。
