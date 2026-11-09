---
id: q_01M6WWFMXS0BXCPFS7A2NS8XDV
title: Java 中 JDK、JRE 和 JVM 分别是什么？
type: concept
difficulty: easy
importance: 3
category: java
tags: [bytecode-execution]
prerequisites: [q_01M6XBFXC3474DTDBN4086JVDN]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
JVM 是执行字节码的虚拟机，JRE 是 JVM 加核心类库，是运行 Java 程序的环境，JDK 是 JRE 再加上 javac 等开发工具，是开发用的工具包。

## 要点
- [kp1|3] 包含关系：JDK 包含 JRE，JRE 包含 JVM 和核心类库
- [kp2|3] JVM 负责加载、验证并执行字节码
- [kp3|2] JDK 额外带了 javac 编译器、javadoc 文档工具等开发工具
- [kp4] 只运行程序需要 JRE，开发程序需要 JDK

## 详解
### 先搞懂：用「开餐厅」类比
把 Java 程序想成一道菜：

- **JVM** 是灶台，负责把菜（字节码）真正做出来；
- **JRE** 是灶台加上调料和锅碗瓢盆（核心类库），有了它就能把现成的菜谱做出来；
- **JDK** 是整个后厨，除了 JRE，还有切菜、写菜谱的工具（编译器等），能自己研发新菜。

后文要用的词：
- **字节码**：.class 文件里的指令，由 javac 编译 .java 得到。
- **核心类库**：Java 自带的一大堆现成类，如 `String`、集合、IO。

### 三者各是什么
- **JVM**：Java 虚拟机，加载 .class 文件、检查它是否合规，然后执行。它是实现跨平台的关键，不同系统装不同版本。
- **JRE**：Java 运行时环境，包含 JVM 和程序运行必需的核心类库。只想运行别人写好的 Java 程序，有它就够了。
- **JDK**：Java 开发工具包，包含 JRE，还有 `javac`（编译器）、`javadoc`（文档生成）、`jar`（打包）等工具。写代码、编译、打包都需要它。

### 开发和运行各要哪个
自己写代码、编译、打包：装 JDK。只在服务器上运行打好的 jar：理论上有运行环境就行。不过现在不少新版本的 JDK 发行版已经不再单独提供 JRE，实际部署时通常直接装 JDK。

## 示例
```bash
javac Hello.java   # 属于 JDK 的工具：编译
java Hello         # 运行：由 JVM 执行字节码
```

## 易错点
- 把 JVM 当成 JDK 的别名；JVM 只是虚拟机，JDK 还包含编译器等工具
- 以为 JVM 自带编译 .java 的能力；把源码变成字节码的是 javac，属于 JDK
- 说「JVM 是跨平台的」；字节码跨平台，JVM 每个平台各有一份

## 追问
### [f1] 为什么说 JVM 是跨平台的关键？
字节码与平台无关，各平台的 JVM 把同一份字节码转成本机指令执行，平台差异都由 JVM 吸收。

### [f2] 服务器上只想跑程序，需要装 JDK 吗？
只运行的话不一定需要编译器，但现在很多发行版不再单独提供 JRE，通常直接装 JDK，方便排查问题，比如使用 jstack 等诊断工具。
