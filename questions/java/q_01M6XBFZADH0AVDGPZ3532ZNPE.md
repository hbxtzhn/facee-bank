---
id: q_01M6XBFZADH0AVDGPZ3532ZNPE
title: equals 方法是做什么的？
type: concept
difficulty: easy
importance: 2
category: java
tags: [object-methods]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
equals 用来判断两个对象是否“相等”；Object 默认比较的是地址，也就是是不是同一个对象，类可以重写它来按内容比较。

## 要点
- [kp1|3] equals 判断两个对象是否相等，返回 boolean
- [kp2|3] Object 默认的 equals 比较地址，等价于 ==
- [kp3|2] String、包装类等已重写 equals，比较的是内容
- [kp4|2] 自定义类按业务字段比较时，要自己重写 equals
- [kp5] 重写 equals 时通常也要重写 hashCode

## 详解
### 先搞懂：两个用户是不是同一个人
做项目时，常要判断“两个用户对象是不是同一个用户”。有两种“相同”：

- 是不是同一个对象：就像同一张身份证；
- 内容是不是一样：就像两张不同的复印件，上面的身份证号一样。

`==` 对引用类型比较的是前者：两个变量是不是指向同一个对象。`equals` 用来表达后者：按业务上的意义判断是否相等。

后文用到的词：

- **引用**：变量里存的对象地址。
- **重写**：子类重新定义父类已有的方法。

### Object 的默认实现：比较地址
所有类都继承 `Object`，`Object.equals` 默认的写法等价于 `this == obj`，只有是同一个对象才返回 true。

所以如果你自己的 `User` 类没有重写 `equals`，`new User(1)` 和另一个 `new User(1)` 用 `equals` 比较，结果是 false。

### 重写 equals：按内容比较
`String`、`Integer`、`LocalDate` 等常用类已经重写了 `equals`，比较的是内容。自己的类想按业务字段判断，就要重写。

写法的一般步骤：

1. 是同一个对象，直接返回 true；
2. 对方为 null 或类型不同，返回 false；
3. 逐个比较关键字段，字段都一致才返回 true。

重写后，`equals` 应当满足：自己和自己相等；A 等于 B 则 B 也等于 A；A 等于 B、B 等于 C，则 A 等于 C；同样的输入多次比较结果一致；任何对象与 null 比较都返回 false。

### 为什么常提到 hashCode
HashMap、HashSet 这类集合会同时用到 `hashCode` 和 `equals`。所以只重写 `equals` 而不重写 `hashCode`，放进这些集合时会出问题，这部分在另一道题详细讲。

## 示例
```java
class User {
    long id;
    String name;

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        User u = (User) o;
        return id == u.id && java.util.Objects.equals(name, u.name);
    }

    @Override
    public int hashCode() {
        return java.util.Objects.hash(id, name);
    }
}
```

## 易错点
- 用 `==` 比较两个字符串内容；`==` 比较地址，要比内容应该用 equals
- 重写 equals 时方法参数写成了具体类型而不是 Object，结果是重载，不是重写
- 在 equals 里忘了判空，对方为 null 时抛空指针
- 调用 `a.equals(b)` 时 a 可能为 null，会抛空指针；可以用 `Objects.equals(a, b)`

## 追问
### [f1] equals 和 == 有什么区别？
对基本类型，== 比较值。对引用类型，== 比较是不是同一个对象，equals 默认也是这样，但可以被重写成按内容比较。
