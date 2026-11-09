---
id: q_01M6XBFZ29QQ8BNA8XKNS3FKDF
title: 如何实现深拷贝？
type: coding
difficulty: medium
importance: 2
category: java
tags: [object-methods, serialization]
prerequisites: [q_01M6XBFYHZ765RFXYWFKENG92J, q_01M6XBFYT5YCECW2685R8WYMPM]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 4
---

## 一句话
实现深拷贝就是把引用成员也逐层复制：可以重写 clone() 递归复制每个引用成员，也可以把对象序列化再反序列化，一次得到完整的新对象。

## 要点
- [kp1|3] 重写 clone()：先 super.clone()，再对每个引用成员单独复制
- [kp2|3] 序列化法：写入字节流再读回，得到整张对象图的副本，要求类可序列化
- [kp3|2] 拷贝构造器：手写 new，逐层复制，最直观
- [kp4|2] transient 字段不会被序列化复制，副本里是默认值
- [kp5] 对象间有循环引用时，手工递归要小心死循环

## 详解
### 先搞懂：复印订单，还要跟着复印所有附件
还是订单里挂着地址的场景。浅拷贝只复印订单，地址依然共用；深拷贝要把订单、地址，以及地址里面再挂着的东西，一层层都复印一遍。

怎么保证一层不漏？有两种思路：

- 手工办法：对每个引用成员，自己写一行“再复制一次”的代码；
- 自动办法：把整个对象“打包”成一串字节，再“拆包”还原，拆出来的就是全新的一套。

后文用到的词：

- **序列化**：把对象转换成字节序列，可以存文件或在网络上传输。
- **反序列化**：把字节序列还原成对象。
- **对象图**：一个对象以及它直接、间接引用的所有对象。

### 方式一：重写 clone() 逐层复制
1. 类实现 `Cloneable`，重写 `clone()`；
2. 先 `super.clone()` 得到浅拷贝副本；
3. 对每个可变的引用成员，也调用它自己的复制方法，把结果赋给副本。

引用成员的类也要支持复制。层数越多，要写的地方越多，漏一处就是一处共用。

### 方式二：序列化再反序列化
把对象通过对象输出流写进内存字节数组，再用对象输入流读回来。读出来的对象图是全新的，里面所有层级的对象都不与原对象共用。

条件和注意：

- 对象图里所有类都要实现 `Serializable`，否则会抛异常；
- 被 `transient` 修饰的字段不参与序列化，副本里它是默认值（引用是 null、数字是 0）；
- 对象之间有循环引用也能正确处理，因为序列化会记住已经处理过的对象。

### 方案对比：三种做法
| 方案 | 怎么做 | 优点 | 缺点 | 适合 |
|---|---|---|---|---|
| 重写 clone() | super.clone() 加手动补引用成员 | 不用额外依赖，调用方便 | 容易漏层，依赖 Cloneable | 结构简单、层数少 |
| 拷贝构造器 | new 时逐字段复制 | 最直观，没有隐含规则 | 字段多时代码多 | 大多数手写场景 |
| 序列化 | 写入字节流再读回 | 一次复制整张对象图，不会漏 | 要求可序列化，较慢，transient 丢失 | 层次深、结构复杂 |

结论：结构简单时用拷贝构造器或重写 clone()，更直观；对象图很深或结构常变，并且类本来就可序列化时，用序列化省事。

## 示例
```java
@SuppressWarnings("unchecked")
static <T extends java.io.Serializable> T deepCopy(T obj) throws Exception {
    var bos = new java.io.ByteArrayOutputStream();
    try (var out = new java.io.ObjectOutputStream(bos)) {
        out.writeObject(obj);
    }
    try (var in = new java.io.ObjectInputStream(
            new java.io.ByteArrayInputStream(bos.toByteArray()))) {
        return (T) in.readObject();
    }
}
```

## 易错点
- 重写 clone() 时只复制了第一层引用成员，更深一层仍然共用
- 用序列化复制，却忘了让内部类也实现 Serializable，运行时才抛 NotSerializableException
- 集合里的元素是可变对象时，只复制集合本身，元素仍然是同一批
- 以为 transient 字段也会被复制；它在副本里是默认值

## 追问
### [f1] 序列化方式有什么缺点？
要求所有相关类可序列化，比手工复制慢，transient 字段会丢失，而且序列化本身也有安全方面的顾虑，不应该反序列化来路不明的数据。对自己内存里的对象做复制时，安全问题不大。

### [f2] 为什么说深拷贝要“逐层”复制？
因为引用成员指向的对象里可能还有引用成员。只复制一层，更深那层仍和原对象共用，改了就会互相影响。
