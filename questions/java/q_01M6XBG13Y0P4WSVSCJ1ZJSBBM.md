---
id: q_01M6XBG13Y0P4WSVSCJ1ZJSBBM
title: throw 和 throws 分别怎么用？
type: concept
difficulty: easy
importance: 2
category: java
tags: [exception]
prerequisites: [q_01M6XBNWPCY2YAMPPACF1XC28Y]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
throw 是在方法体里抛出一个具体的异常对象；throws 写在方法签名上，声明这个方法可能抛出哪些异常，交给调用者处理。

## 要点
- [kp1|3] throw 是语句，在方法体里，后面跟一个异常对象
- [kp2|3] throws 是声明，写在方法签名后面，后面跟异常类型
- [kp3|2] throws 可以声明多个异常，用逗号分隔
- [kp4|2] 抛出受检异常，要么 try-catch，要么用 throws 声明
- [kp5] 运行时异常可以直接 throw，不必声明 throws

## 详解
### 先搞懂：发现问题与上报问题
做项目时，一个方法发现了问题（比如参数不合法），自己没法处理，只能“上报”给调用它的人，让上层来决定怎么办。就像仓库管理员发现货不对，不自己处理，而是把情况写成报告交给经理。

Java 里这件事涉及两个词：

- `throw`：真的“写一份报告并递上去”，是一个动作；
- `throws`：在方法门口挂个牌子：“本方法可能会上报这些类型的问题”，是一个声明。

后文用到的词：

- **异常对象**：用 new 创建出来的异常实例，里面有错误信息。
- **调用者**：调用这个方法的代码。

### throw：抛出一个异常对象
`throw` 是一条语句，出现在方法体里：

`throw new IllegalArgumentException("age 不能为负");`

执行到这一句，当前方法立即中断，异常沿调用链往上传，直到被某处 `catch` 接住。

### throws：声明可能抛出的异常
`throws` 写在方法的参数列表后面：

`void read() throws IOException, SQLException`

它告诉调用者：这个方法可能抛出这些异常，请你处理。多个异常用逗号分隔。

### 两者的关系
- 方法体里 `throw` 一个**受检异常**，又不想自己 `try-catch`，就必须在方法签名上用 `throws` 声明，否则编译不过；
- `throw` 一个**运行时异常**，不需要声明 `throws`；
- 方法声明了 `throws`，不代表一定会抛，只是“可能”；
- 调用有 `throws` 受检异常的方法时，调用者要 `try-catch`，或自己继续 `throws`。

## 示例
```java
void setAge(int age) {
    if (age < 0) {
        throw new IllegalArgumentException("age 不能为负"); // 运行时异常，不用声明
    }
}

void load(String path) throws java.io.IOException {  // 声明可能抛出
    if (path == null) {
        throw new java.io.IOException("path 为空");   // 抛出受检异常
    }
}
```

## 易错点
- 把 throw 和 throws 搞反；一个在方法体里抛，一个在签名上声明
- 抛出受检异常，既不捕获也不声明 throws，编译不通过
- 以为声明了 throws，调用者就不用处理；调用者仍需捕获或继续声明
- 在 throws 后面写异常对象而不是类型；throws 后面是类型，throw 后面是对象

## 追问
### [f1] 抛出异常后，后面的代码还会执行吗？
不会。throw 执行后当前方法立即中断，只有 finally 块里的代码仍会执行，其余不再运行，异常继续向上传。
