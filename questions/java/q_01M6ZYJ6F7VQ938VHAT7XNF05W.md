---
id: q_01M6ZYJ6F7VQ938VHAT7XNF05W
title: 什么是自动装箱和拆箱？
type: concept
difficulty: easy
importance: 2
category: java
tags: [type-system]
prerequisites: [q_01M6WWFN6JAGSWQB6CWANG7GRF, q_01M6XBG6NSJS9AHNQQT7WZVYMD]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
自动装箱是编译器自动把基本类型转成包装类（如 int 到 Integer），自动拆箱是反过来转回基本类型，不用手写转换代码。

## 要点
- [kp1|3] 装箱：基本类型转成包装类，如 int 到 Integer
- [kp2|3] 拆箱：包装类转成基本类型，如 Integer 到 int
- [kp3|2] 由编译器自动完成，装箱实际调用 valueOf，拆箱调用 xxxValue
- [kp4|2] 拆箱时如果包装类是 null，会抛 NullPointerException
- [kp5] 循环里频繁装箱会创建大量对象，影响性能

## 详解
### 先搞懂：自动套壳和脱壳
把零件装进外壳是装箱，把外壳拿掉取出零件是拆箱。以前这两步要自己手写，从 Java 5 开始，编译器替你做了。

后文术语：
- **装箱**：基本类型变成包装类对象。
- **拆箱**：包装类对象变回基本类型。

### 什么时候发生
```java
Integer a = 10;       // 装箱：int 变 Integer
int b = a;            // 拆箱：Integer 变 int
list.add(5);          // 往 List<Integer> 里放 int，也是装箱
int c = list.get(0);  // 取出来赋给 int，是拆箱
```
写起来像是直接转换，其实编译器偷偷加了转换代码：装箱调用 `Integer.valueOf(10)`，拆箱调用 `a.intValue()`。

### 坑一：null 拆箱
```java
Integer x = null;
int y = x; // 抛出 NullPointerException
```
Map 的 `get` 找不到键返回 null，直接赋给 int 就会出这个错，很常见。

### 坑二：性能
```java
Long sum = 0L;
for (long i = 0; i < 100000; i++) {
    sum += i; // 每次都要拆箱再装箱
}
```
`sum` 声明成了 Long，每次加法都要拆箱、计算、再装箱，产生大量临时对象。把 sum 声明成 long 就没有这个问题。

### 坑三：用 == 比较
两个包装类对象用 `==` 比较的是引用。Integer 对小范围的数值会缓存复用，所以有时看起来相等，有时不等，不要依赖，比较值请用 equals。

## 易错点
- 把 Map.get 的结果直接赋给基本类型；键不存在时返回 null，拆箱会抛空指针
- 用 == 比较包装类的值；结果可能因缓存而不稳定
- 累加变量声明成包装类；每次循环都在装箱拆箱

## 追问
### [f1] 自动装箱底层是怎么实现的？
编译器在编译时插入方法调用：装箱调用包装类的 valueOf，拆箱调用 intValue 等方法，运行时并没有什么特殊机制。
