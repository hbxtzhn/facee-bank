---
id: q_01M6XBP0ZWGWBKKVG1GTXG45DG
title: 如何打破双亲委派模型？
type: concept
difficulty: medium
importance: 2
category: jvm
tags: [class-loading]
prerequisites: [q_01M6XBGFKRNVJX1180XX4DZNDH]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
只想扩展查找类的方式，就重写 `findClass()`，不会破坏双亲委派；要改变先问父加载器的顺序，就重写 `loadClass()`，Tomcat 为了隔离不同的 Web 应用就是这样做的。

## 要点
- [kp1|3] 重写 `findClass()`：只定义怎么找类，仍然遵守双亲委派
- [kp2|3] 重写 `loadClass()`：可以改变委派顺序，才算打破双亲委派
- [kp3|2] Tomcat 让 Web 应用优先加载自己目录下的类，用来隔离不同应用的依赖版本
- [kp4] 打破双亲委派的另一个常见场景是 JDBC 等 SPI，通过线程上下文类加载器完成

## 详解
### 先搞懂：为什么要"不先问上级"
双亲委派规则是"先问上级"。大多数时候这没问题，但有些场景需要例外。比如同一台 Tomcat 服务器上跑着两个 Web 应用，A 应用用 Spring 5，B 应用用 Spring 6。如果都先问上级、共用一份，就会有冲突。需要让每个应用先用自己带的那份。

后文用到的术语：
- **`loadClass()`**：类加载器的入口方法，里面实现了双亲委派的流程。
- **`findClass()`**：真正去查找并读取类的方法，双亲委派失败后才会被调用。
- **SPI**：由规范方定义接口、由厂商提供实现的机制，如 JDBC。

### 做法一：重写 findClass()，不破坏
`loadClass()` 的流程已经是先委派，失败后才调用 `findClass()`。所以你只要重写 `findClass()`，写好怎么从自己的来源（文件、网络）读取字节码，就可以扩展加载能力，同时双亲委派依然有效。这是推荐的做法。

### 做法二：重写 loadClass()，才算打破
`loadClass()` 里写死了"先委派"的顺序。如果你重写它，改成先自己找、再问父加载器，就改变了顺序，等于打破了双亲委派。

### Tomcat 为什么要这样做
Tomcat 里每个 Web 应用有自己的类加载器，加载类时优先从自己的目录（应用的类和依赖）找，找不到再交给上级，这样不同的应用可以使用同一个库的不同版本，互不影响。JDK 的核心类仍然交给上级加载，不允许应用替换。

### 进阶：另一种打破方式（基础薄弱可先跳过）
JDBC 的接口在核心类库里，由启动类加载器加载，但具体实现在厂商的 jar 里，需要应用类加载器去加载。启动类加载器没法向下找，于是通过**线程上下文类加载器**让上层代码也能用到下层的加载器。

## 示例
```java
public class MyLoader extends ClassLoader {
    // 只重写 findClass：不破坏双亲委派
    @Override
    protected Class<?> findClass(String name) throws ClassNotFoundException {
        byte[] bytes = loadBytes(name);              // 从自己的来源读取字节码
        return defineClass(name, bytes, 0, bytes.length);
    }

    private byte[] loadBytes(String name) { /* 读文件或网络 */ return new byte[0]; }
}
```

## 易错点
- 以为重写 `findClass()` 也会打破双亲委派；它只在父加载器失败后才被调用
- 以为打破双亲委派后可以替换 `java.lang` 里的类；JVM 仍然会拒绝
- 以为只有 Tomcat 才破坏双亲委派；JDBC、OSGi 等也有类似做法

## 追问
### [f1] 为什么 JDBC 要破坏双亲委派？
接口在核心类库里，由启动类加载器加载，但厂商的实现类在应用的 classpath 下。启动类加载器看不到，只能借助线程上下文类加载器去加载实现类。

### [f2] 自定义类加载器一般怎么写才合适？
只重写 `findClass()`，保留默认的双亲委派逻辑；只有确实要改变加载顺序时，才重写 `loadClass()`。
