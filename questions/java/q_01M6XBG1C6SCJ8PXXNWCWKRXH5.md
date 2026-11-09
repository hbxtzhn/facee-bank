---
id: q_01M6XBG1C6SCJ8PXXNWCWKRXH5
title: 怎么用 try-catch 捕获异常？
type: concept
difficulty: easy
importance: 1
category: java
tags: [exception]
prerequisites: [q_01M6XBNWPCY2YAMPPACF1XC28Y, q_01M6ZYJ3C3Y1WZXJ6BB8CNC0TE]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
try 包住可能出错的代码，catch 按异常类型接住并处理，finally 放无论是否出错都要执行的收尾代码，比如关闭资源。

## 要点
- [kp1|3] try 里放可能抛异常的代码，出错后其余部分被跳过
- [kp2|3] catch 按异常类型匹配，匹配到才执行对应的处理
- [kp3|2] finally 无论是否异常都会执行，常用来释放资源
- [kp4|2] 多个 catch 时，子类异常要写在父类异常前面
- [kp5] 推荐用 try-with-resources 自动关闭资源

## 详解
### 先搞懂：出错了别让整个程序崩掉
做项目时，读一个配置文件、调一个外部接口，都可能失败。如果不处理，异常一路往上抛，最后整个请求或程序崩溃。`try-catch` 让你在出错的地方先“接住”，做点补救，程序继续往下走。

打个比方：走钢丝时下面铺了一张安全网。`try` 是走钢丝的动作，`catch` 是安全网，`finally` 是不管摔没摔、表演结束后都要做的收尾工作，比如收拾道具。

后文用到的词：

- **异常类型**：如 IOException，`catch` 靠它判断“接不接”。
- **资源**：文件、数据库连接、网络连接这类用完要关闭的东西。

### 三个部分各管什么
- **try**：包住可能出错的代码。一旦其中某行抛出异常，这一行后面的代码不再执行，直接跳到匹配的 `catch`；
- **catch**：声明接哪一种异常，并写出处理方法，如打日志、返回默认值；
- **finally**：不管有没有异常、有没有被 catch 接住，都会执行。

### 执行流程
1. 没出异常：执行完 try，跳过 catch，执行 finally；
2. 出了异常且有匹配的 catch：执行对应 catch，然后执行 finally；
3. 出了异常但没有匹配的 catch：先执行 finally，异常继续向上抛。

### 多个 catch 的顺序
可以写多个 `catch`，从上往下依次匹配，第一个匹配的执行。因此范围小的子类异常要放前面，范围大的父类异常放后面，否则子类的 catch 永远不会被执行，编译器会直接报错。Java 7 起也可以用 `|` 把几个异常合并在一个 catch 里。

### 用 try-with-resources 管理资源
对实现了 `AutoCloseable` 的资源，在 `try` 后面的括号里声明，代码块结束时会自动关闭，不需要手写 finally 来 close，也不容易漏。

## 示例
```java
try (var in = new java.io.FileInputStream("a.txt")) { // 自动关闭
    int b = in.read();
    System.out.println(b);
} catch (java.io.FileNotFoundException e) {
    System.out.println("文件不存在");
} catch (java.io.IOException e) {
    System.out.println("读取失败：" + e.getMessage());
} finally {
    System.out.println("无论如何都会执行");
}
```

## 易错点
- catch 里什么都不写，把异常吞掉，出问题后没有任何线索
- 把父类异常的 catch 写在子类前面，编译不通过
- 在 finally 里写 return，会覆盖 try 里的返回值或异常，容易掩盖问题
- 忘了关闭资源；应使用 try-with-resources

## 追问
### [f1] try 里有 return，finally 还会执行吗？
会。先计算好要返回的值，执行 finally，再返回。如果 finally 里自己也 return，就会覆盖前面的返回值，所以不要在 finally 里 return。

### [f2] 什么时候 finally 不会执行？
调用 System.exit 让虚拟机退出、虚拟机崩溃或线程被强行终止时，finally 可能不会执行。正常的 return 和异常不影响它执行。
