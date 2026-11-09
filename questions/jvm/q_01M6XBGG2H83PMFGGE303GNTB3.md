---
id: q_01M6XBGG2H83PMFGGE303GNTB3
title: 为什么需要双亲委派模型？
type: concept
difficulty: medium
importance: 3
category: jvm
tags: [class-loading]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
references:
  - { title: "Java SE 21 API：java.lang.ClassLoader", url: "https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/lang/ClassLoader.html" }
  - { title: "JVMS 21 第 5 章：Loading, Linking, and Initializing", url: "https://docs.oracle.com/javase/specs/jvms/se21/html/jvms-5.html" }
---

## 一句话
双亲委派让 JDK 核心类始终由启动类加载器统一加载，防止有人写一个同名的类替换掉核心类，同时避免同一个类被重复加载。

## 要点
- [kp1|3] 核心类库由启动类加载器统一加载，保证全程序用的是同一份
- [kp2|3] 防止自定义的同名类（如 `java.lang.Object`）冒充和替换核心类，保证安全
- [kp3|2] 避免同一个类被不同加载器重复加载，节省内存、避免冲突
- [kp4] JVM 里判断两个类是否相同，要看类名和加载它的类加载器都相同

## 详解
### 先搞懂：别人想偷换你的"身份证"
假如任何人都可以自己写一个 `java.lang.String`，并让 JVM 优先用它，那么整个程序里最基础的字符串类就可能被换成恶意版本，后果很严重。

双亲委派就是一个"先问上级"的机制：凡是 JDK 核心类，一定先让最上面的启动类加载器加载，轮不到别人。

后文用到的术语：
- **核心类库**：JDK 自带的基础类，如 `String`、`Object`。
- **类的唯一性**：JVM 里一个类由"类加载器 + 全限定名"共同确定。
- **全限定名**：带包名的完整类名。

### 好处一：保证核心类安全
假如你自己写了一个 `java.lang.Object` 并放到 classpath 里。按照双亲委派，请求会先到启动类加载器，它从 JDK 里找到真正的 `Object` 并加载，你写的那个永远不会被用到。

即使绕开委派，JVM 也不允许自定义加载器去定义以 `java.` 开头的类，会抛出 `SecurityException`。

### 好处二：避免重复加载
一个类被父加载器加载过后，子加载器直接复用，不会再加载一遍。这样同一个类在内存里只有一份，省空间，也避免了因为版本混乱引起的类型转换问题。

### 为什么"同名不同加载器"是个问题
JVM 判断两个类是否相同，不只看类名，还要看加载它的类加载器。同一个类名被两个不同的加载器各加载一次，就是两个不同的类，互相赋值时会报 `ClassCastException`。双亲委派尽量让同一个类只由一个加载器加载，减少这种混乱。

## 易错点
- 以为双亲委派是为了提高加载速度；主要目的是安全和一致性
- 以为双亲委派能防止所有重复加载；不同的自定义加载器各加载一次，仍然是不同的类
- 以为不委派就能自己定义 `java.lang.Object`；JVM 会拒绝定义 `java.` 开头的类

## 追问
### [f1] 如果自己写一个 `java.lang.String` 会怎样？
应用类加载器会把请求委派给启动类加载器，启动类加载器加载 JDK 里真正的 String，你自己写的不会被使用。

### [f2] 双亲委派有什么缺点？
它规定了子加载器一定先问上级，所以上层加载器无法反过来加载下层的类，像 JDBC 这类需要加载厂商实现的场景，就必须靠破坏模型来解决。
