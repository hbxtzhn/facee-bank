---
id: q_01M6ZYJ70SP4RG2TAB4V2E0MZM
title: 双亲委派模型的加载流程是怎样的？
type: concept
difficulty: medium
importance: 3
category: jvm
tags: [class-loading]
prerequisites: [q_01M6XBGETV46EJNC6JY9R5X884, q_01M6XBGFKRNVJX1180XX4DZNDH]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
双亲委派是指类加载器收到加载请求时，不自己先加载，而是先交给父加载器，一路向上；父加载器都加载不了，子加载器才自己尝试。

## 要点
- [kp1|3] 加载类时，先把请求交给父加载器，层层向上，直到启动类加载器
- [kp2|3] 父加载器加载不了（不在它的搜索范围），才由子加载器自己加载
- [kp3|2] `loadClass()` 先查缓存，再委派父加载器，最后调用 `findClass()`
- [kp4] 这里的"父子"是组合关系，不是继承

## 详解
### 先搞懂：先问上级，上级不行再自己来
你想办一件事，先问部门经理能不能办，经理再问总监，总监也办不了才退回来，由你自己想办法。类加载也是这样：先问上级，上级都办不了，才自己办。

后文用到的术语：
- **父加载器**：上一级类加载器。
- **委派**：自己不动手，把任务交给上级。
- **全限定名**：带包名的完整类名，如 `java.lang.String`。

### 加载流程：一路向上，再一路向下
1. 应用类加载器收到请求，先检查这个类是否已加载过，加载过直接返回；
2. 没加载过，不自己动手，交给父加载器（扩展/平台类加载器）；
3. 它同样先交给自己的父加载器，一直到启动类加载器；
4. 启动类加载器在自己的范围里找：找到就加载并返回；找不到，告诉子加载器"我加载不了"；
5. 子加载器收到失败后，在自己的范围里找；找不到再往下传，最终都找不到就抛出 `ClassNotFoundException`。

### 在源码里是什么样
`ClassLoader.loadClass()` 的核心步骤是：先检查是否已加载；没有就调用父加载器的 `loadClass`；父加载器失败后，再调用自己的 `findClass()` 去查找。所以自定义类加载器通常只需要重写 `findClass()`。

### 举个例子
你的代码里使用 `String`：应用类加载器会先问到启动类加载器，启动类加载器发现它是核心类库里的，直接加载。你自己写的 `com.demo.User`：启动类加载器和平台类加载器都找不到，最后由应用类加载器加载。

## 示例
```java
protected Class<?> loadClass(String name, boolean resolve) throws ClassNotFoundException {
    Class<?> c = findLoadedClass(name);   // 1. 先查是否已加载
    if (c == null) {
        try {
            if (parent != null) c = parent.loadClass(name, false);  // 2. 委派给父加载器
        } catch (ClassNotFoundException e) {
            // 父加载器加载不了
        }
        if (c == null) c = findClass(name);                          // 3. 自己加载
    }
    return c;
}
```

## 易错点
- 以为子加载器优先加载；实际是父加载器优先
- 以为"双亲"是两个父加载器；每个类加载器只有一个父加载器
- 以为父子是继承关系；它们是通过字段引用组合在一起的

## 追问
### [f1] 为什么要有双亲委派？
保证核心类库由启动类加载器统一加载，防止被篡改或重复加载，详见"为什么需要双亲委派模型"。

### [f2] 父加载器加载失败后会发生什么？
抛出的 `ClassNotFoundException` 被子加载器捕获，子加载器接着调用自己的 `findClass()`；都找不到才会向外抛出异常。
