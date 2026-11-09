---
id: q_01M6XBFY0RAR93FD8W7WEH9RQC
title: 方法重载和方法重写有什么区别？
type: concept
difficulty: medium
importance: 3
category: java
tags: [oop, bytecode-execution]
prerequisites: [q_01M6WWFR19J8V8HXD8C4DPNED4, q_01M6WWFRKE43EXW2YKWNAZ4598]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
references:
  - { title: "Java 语言规范 SE 21：8.4.9 Overloading", url: "https://docs.oracle.com/javase/specs/jls/se21/html/jls-8.html#jls-8.4.9" }
  - { title: "Java 语言规范 SE 21：8.4.8.3 Requirements in Overriding and Hiding", url: "https://docs.oracle.com/javase/specs/jls/se21/html/jls-8.html#jls-8.4.8.3" }
---

## 一句话
重载是同一个类里方法名相同、参数不同，调用哪个在编译期按参数类型定；重写是子类改写父类方法，签名相同，调用哪个在运行期按对象真实类型定。

## 要点
- [kp1|3] 重载在同一个类，方法名相同、参数列表不同，返回值不参与区分
- [kp2|3] 重写在父子类之间，方法名和参数相同，子类提供新实现
- [kp3|2] 重载由编译器按引用的声明类型选择，重写在运行时按对象真实类型选择
- [kp4|2] 重写是多态的基础，重载不是
- [kp5] 重写要求访问权限不能更小，返回类型相同或是其子类型

## 详解
### 先搞懂：「加菜单」和「换做法」
做项目时，你写工具类：`log(String)`、`log(String, int)`，一个名字多种参数，这是**重载**，相当于菜单上多了几种点法，由你点菜时说的内容决定上哪个。

另一种情况：父类定了「支付」，子类微信支付自己重写了「支付」的做法，这是**重写**。相当于同一道菜，后厨换了做法。具体用谁家的做法，要看实际上桌的是哪家厨师。

后文要用的术语：
- **方法签名**：方法名加参数列表。
- **编译期**：javac 编译代码的阶段。
- **运行期**：程序真正运行的阶段。
- **动态绑定**：运行时才决定调用哪个方法。

### 对比：位置、规则和绑定时机
| 维度 | 重载 Overload | 重写 Override |
|---|---|---|
| 发生位置 | 同一个类（含继承来的方法） | 父类和子类之间 |
| 方法名 | 相同 | 相同 |
| 参数列表 | 必须不同 | 必须相同 |
| 返回类型 | 可以不同，但不能只靠它区分 | 相同，或是父类返回类型的子类型 |
| 访问权限 | 无要求 | 不能比父类更小 |
| 何时确定调用哪个 | 编译期，按参数的声明类型 | 运行期，按对象真实类型 |
| 与多态的关系 | 不属于通常说的多态 | 多态的基础 |

结论：区分两者先看位置和参数：同类、参数不同是重载；父子类、签名相同是重写。

### 编译期和运行期的差别，用代码看
重载时，编译器只看**变量声明的类型**。重写时，JVM 看的是**对象真实类型**。下面的例子里，调用 `show(a)` 选的是 `show(Animal)`，因为变量 `a` 的声明类型是 `Animal`；而 `a.speak()` 执行的是 `Dog` 重写的版本。

### 为什么要这样设计
重载只是为了让同类功能共用一个名字，省得记很多名字，编译器根据参数就能选好。重写则是为了让子类在不改接口的前提下换行为，必须到运行时才知道真实对象是谁。

### 进阶：字节码层面的差别（基础薄弱可先跳过）
重载的选择在编译期完成，编译后字节码里已经写明了具体的方法描述符。重写则对应虚方法调用，JVM 运行时根据对象的真实类型去查找该调用的实现。

## 示例
```java
class Animal { void speak() { System.out.println("动物叫"); } }
class Dog extends Animal {
    @Override void speak() { System.out.println("汪汪"); }
}

class Demo {
    static void show(Animal a) { System.out.println("show Animal"); }
    static void show(Dog d)    { System.out.println("show Dog"); }

    public static void main(String[] args) {
        Animal a = new Dog();
        a.speak();   // 汪汪（重写：运行期按真实类型）
        show(a);     // show Animal（重载：编译期按声明类型）
    }
}
```

## 易错点
- 以为只改返回类型就是重载；编译报错，返回值不参与区分
- 误以为 `show(a)` 会根据真实对象选 `show(Dog)`；重载看声明类型
- 子类写了同名但参数不同的方法，以为是重写；其实是重载
- 把 static 方法的同名定义当成重写；它只是隐藏

## 追问
### [f1] 构造方法能重载、能重写吗？
能重载，不能重写。构造方法不会被继承。

### [f2] 为什么重写时不能缩小访问权限？
因为用父类引用调用时，调用方按父类的权限来使用。如果子类缩小权限，同一个调用会出现「父类能访问、实际对象不让访问」的矛盾。
