---
id: q_01M6WWFN6JAGSWQB6CWANG7GRF
title: Java 有哪些基本数据类型？
type: concept
difficulty: easy
importance: 2
category: java
tags: [type-system]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
---

## 一句话
Java 有 8 种基本数据类型：整数 byte、short、int、long，小数 float、double，字符 char，布尔 boolean；它们直接存值，其余类型都是引用类型。

## 要点
- [kp1|3] 8 种基本类型：byte、short、int、long、float、double、char、boolean
- [kp2|3] 整数类型 byte、short、int、long 位数依次是 8、16、32、64，int 最常用
- [kp3|2] 小数用 float（32 位）和 double（64 位），默认的小数字面量是 double
- [kp4] char 是 16 位，保存一个字符；boolean 只有 true 和 false

## 详解
### 先搞懂：基本类型就是「直接放值的小盒子」
做项目时你一定写过 `int age = 18;`、`boolean paid = true;`。这些变量里放的就是值本身，不是指向别处的地址。

类比一下：基本类型像口袋里的现金，拿出来就能用；引用类型像一张取件码，要凭它去别处取东西。

后文要用的词：
- **位（bit）**：存储的最小单位，位数越多，能表示的范围越大。
- **字面量**：直接写在代码里的值，如 `18`、`3.14`、`'a'`。

### 整数：byte、short、int、long
- `byte`：8 位，范围 -128 到 127。
- `short`：16 位。
- `int`：32 位，日常最常用，整数字面量默认就是 int。
- `long`：64 位，数值大时用，字面量后面加 `L`，如 `100L`。

比如订单金额用「分」存，数值可能很大，就要考虑 long。

### 小数：float、double
- `float`：32 位，字面量后面加 `f`。
- `double`：64 位，精度更高，小数字面量默认是 double。

二者都是近似存储，不适合精确计算金额，金额一般用 `BigDecimal`。

### 字符和布尔
- `char`：16 位，保存一个字符，如 `'A'`、`'中'`。
- `boolean`：只有 `true` 和 `false` 两个值，用于条件判断。

### 基本类型和引用类型
除了这 8 种，类、接口、数组等都是引用类型，变量里保存的是对象的引用。

## 示例
```java
byte b = 10;
int count = 100;
long big = 10_000_000_000L;
double price = 9.9;
float rate = 0.5f;
char c = '中';
boolean paid = true;
```

## 易错点
- 把 String 当成基本类型；String 是类，属于引用类型
- 写 `long x = 10000000000;` 不加 L，编译报错，因为整数字面量默认是 int
- 用 double 算金额，会出现精度误差；金额计算用 BigDecimal 或者用整数的「分」

## 追问
### [f1] 基本类型和它的包装类有什么区别？
基本类型直接存值，不能为 null；包装类（如 Integer）是对象，可以为 null，还能用于泛型和集合。

### [f2] float 和 double 怎么选？
一般用 double，精度更高，也是小数字面量的默认类型；对内存特别敏感的大数组才考虑 float。
