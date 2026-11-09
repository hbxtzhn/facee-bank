---
id: q_01M6XCC2YVJTT354C8HHPZCNPW
title: 在 Spring 项目里，怎么让 Mapper 接口被扫描并注入使用？
type: concept
difficulty: easy
importance: 2
category: spring
tags: [mybatis-internals, ioc-di]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
用 `@MapperScan` 或 `MapperScannerConfigurer` 指定 Mapper 接口所在的包，Spring 就会把这些接口注册成 Bean，之后用 `@Autowired` 直接注入。

## 要点
- [kp1|3] `@MapperScan("包名")` 加在配置类或启动类上，扫描 Mapper 接口
- [kp2|3] XML 项目可用 `MapperScannerConfigurer` 做同样的事
- [kp3|2] 扫描到的接口会被注册成 Bean，背后是 MyBatis 生成的代理对象
- [kp4] 每个接口单独加 `@Mapper` 也能被识别，但要逐个加

## 详解
### 先搞懂：接口为什么也能当 Bean
Mapper 只是一个接口，没有实现类。按理说 Spring 不知道怎么创建它。

MyBatis 的做法是：运行时为接口生成一个代理对象，调用接口方法就等于执行对应的 SQL。mybatis-spring 再把这个代理对象交给 Spring 容器管理，别的类就能像注入普通 Bean 一样注入它。

- **代理对象**：运行时自动生成的“替身”，替你实现接口的方法。
- **扫描**：Spring 去指定的包下找符合条件的类或接口。

### 怎么让接口被发现
你要告诉 Spring：Mapper 接口在哪个包。

- **`@MapperScan`**：写在配置类或启动类上，参数填包名，可以填多个。
- **`MapperScannerConfigurer`**：在 XML 或 Java 配置里声明成 Bean，设置 `basePackage` 属性，作用相同。
- **`@Mapper`**：每个接口单独加。在 Spring Boot 里，如果没写 `@MapperScan`，starter 会自动找带 `@Mapper` 的接口。

扫描到的每个接口，会被注册成一个 `MapperFactoryBean`，由它负责生产代理对象。

### 注入使用
扫描完成后，在 Service 里直接 `@Autowired` 或用构造器注入 Mapper 接口即可。注入的就是那个代理对象。

## 示例
```java
@SpringBootApplication
@MapperScan("com.example.mapper")
public class App { }

@Service
public class UserService {
    private final UserMapper userMapper;

    public UserService(UserMapper userMapper) {
        this.userMapper = userMapper;
    }
}
```

## 易错点
- 包名写错或漏写，运行时报“找不到 UserMapper 类型的 Bean”
- 扫描范围写得太大，把不相关的接口也注册成 Mapper
- 以为接口要写实现类；Mapper 不需要，代理会处理

## 追问
### [f1] @Mapper 和 @MapperScan 该用哪个？
接口少时 `@Mapper` 够用。接口多、集中放在一个包里，`@MapperScan` 一次扫描更省事，不会漏加。
