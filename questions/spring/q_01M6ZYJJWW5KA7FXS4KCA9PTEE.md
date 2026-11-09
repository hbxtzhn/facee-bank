---
id: q_01M6ZYJJWW5KA7FXS4KCA9PTEE
title: 怎么把一个类交给 Spring 容器管理，并注入使用（@Component、@Service、@Autowired）？
type: concept
difficulty: easy
importance: 3
category: spring
tags: [ioc-di]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
在类上加 `@Component`（或 `@Service` 等衍生注解），Spring 扫描到就会把它创建成 Bean 放进容器；用到它的地方再用 `@Autowired` 按类型注入。

## 要点
- [kp1|3] `@Component` 把类注册为 Bean，`@Service` 等是它的衍生注解
- [kp2|3] 类要在被扫描的包范围内，注解才会生效
- [kp3|2] `@Autowired` 按类型注入，可用于字段、构造器、setter
- [kp4|2] 同类型有多个 Bean 时，用 `@Qualifier` 或 `@Primary` 指定
- [kp5] 推荐构造器注入；只有一个构造器时可以省略 `@Autowired`

## 详解
### 先搞懂：让 Spring 管对象是什么意思
平时你自己 `new UserService()`，对象的创建和依赖都由你手动管。用了 Spring 后，改成你告诉 Spring：“这个类交给你管”，需要时它递给你。

这像去餐厅：你不用自己买菜做饭，说一声要什么，服务员端来。

- **Bean**：由 Spring 容器创建和管理的对象。
- **容器**：存放和管理所有 Bean 的地方。
- **依赖注入**：Spring 把一个对象需要的其他对象自动递给它。

### 注册：@Component 和它的衍生注解
在类上加 `@Component`，Spring 启动扫描到后，会创建一个对象放进容器，Bean 名字默认是类名首字母小写。

衍生注解只是换了名字表达分层，功能基本一致：

- `@Controller`：接口层；
- `@Service`：业务层；
- `@Repository`：数据访问层；
- `@Component`：不好归类的通用组件。

扫描范围要覆盖到这些类。Spring Boot 的启动类默认扫描它所在的包及子包。

### 注入：@Autowired
`@Autowired` 告诉 Spring：这里需要一个某类型的对象，请从容器里找一个放进来。

- 加在字段上最简洁，但不利于测试；
- 加在构造器上，依赖一目了然，也能做成 `final`，更推荐；
- 只有一个构造器时，Spring 会自动用它，可以不写 `@Autowired`。

### 同一类型有多个怎么办
`@Autowired` 先按类型找。找到多个时，会再按名字匹配；仍有歧义就报错。这时可用 `@Qualifier("beanName")` 指定名字，或在其中一个上加 `@Primary` 作为首选。

## 示例
```java
@Service
public class UserService {
    private final UserMapper userMapper;

    public UserService(UserMapper userMapper) {   // 构造器注入
        this.userMapper = userMapper;
    }
}

@RestController
public class UserController {
    @Autowired
    private UserService userService;               // 字段注入
}
```

## 易错点
- 类上加了注解，但不在扫描的包内，注入时找不到 Bean
- 自己 `new` 出来的对象不受 Spring 管理，里面的 `@Autowired` 不会生效
- 同类型有多个 Bean 又没指定，启动时报“期望一个但找到多个”

## 追问
### [f1] @Autowired 和 @Resource 有什么区别？
`@Autowired` 是 Spring 的注解，默认按类型找；`@Resource` 是 Java 标准注解，默认按名字找。多数项目选一种统一使用即可。
