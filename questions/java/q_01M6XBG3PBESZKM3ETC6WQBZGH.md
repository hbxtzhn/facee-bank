---
id: q_01M6XBG3PBESZKM3ETC6WQBZGH
title: Java 原生序列化怎么用？
type: coding
difficulty: easy
importance: 1
category: java
tags: [serialization, io-stream]
prerequisites: [q_01M6XBNXGSEB1GY352GJHDQCVF]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
让类实现 Serializable 接口，用 ObjectOutputStream.writeObject 写出，再用 ObjectInputStream.readObject 读回，就完成了 Java 原生的序列化和反序列化。

## 要点
- [kp1|3] 类要实现 Serializable 接口，这是个没有方法的标记接口
- [kp2|3] 写出用 ObjectOutputStream.writeObject，读回用 ObjectInputStream.readObject
- [kp3|2] 被 transient 修饰的字段不会被序列化，读回后是默认值
- [kp4|2] 建议显式声明 serialVersionUID，避免类改动后读回失败
- [kp5] 对象里引用的其他对象也必须可序列化，否则抛 NotSerializableException

## 详解
### 先搞懂：给对象贴“可打包”的标签
Java 默认不允许随便把对象打包存盘，就像快递不收没有贴标签的货。给类实现 `Serializable`，就是贴上“允许打包”的标签。这个接口里没有任何方法，只是个标记。

后文术语：
- **ObjectOutputStream**：对象输出流，把对象写成字节。
- **ObjectInputStream**：对象输入流，把字节读回对象。
- **serialVersionUID**：类的版本号，读回时用来核对类是否对得上。

### 基本用法
1. 类实现 `Serializable`；
2. 创建一个文件输出流，外面包一层 ObjectOutputStream，调用 `writeObject(对象)`；
3. 读取时反过来，用 ObjectInputStream 的 `readObject()`，返回的是 Object，要强转成原类型。

流用完要关闭，示例里用 try-with-resources 自动关闭。

### transient：不想存的字段
密码、临时缓存之类不想写出去的字段，用 `transient` 修饰。反序列化后它会是类型的默认值（对象是 null，数字是 0）。`static` 字段属于类而不是对象，也不会被序列化。

### serialVersionUID：版本号
序列化时会带上类的版本号，读回时和当前类对比，不一致就抛 InvalidClassException。不显式声明时，版本号由编译器根据类结构计算，类稍微改动版本号就变。所以建议自己固定写一个。

## 示例
```java
class User implements Serializable {
    private static final long serialVersionUID = 1L;
    String name;
    transient String password; // 不会被序列化
}

try (ObjectOutputStream out = new ObjectOutputStream(new FileOutputStream("user.bin"))) {
    out.writeObject(user);
}
try (ObjectInputStream in = new ObjectInputStream(new FileInputStream("user.bin"))) {
    User u = (User) in.readObject();
}
```

## 易错点
- 忘记实现 Serializable 就写出对象；会抛 NotSerializableException
- 以为 transient 字段读回来还有值；它是默认值
- 不写 serialVersionUID，之后给类加个字段，旧数据读回时报错
- 读取来自不可信来源的数据；反序列化不可信数据有安全风险，不要直接使用

## 追问
### [f1] 父类没实现 Serializable，子类实现了会怎样？
父类的字段不会被序列化，反序列化时会调用父类的无参构造器来初始化，父类字段得到的是构造器给的值。
