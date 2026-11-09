---
id: q_01M6ZYJHFSEVJTTTXTPFBZCR1V
title: 二级缓存的 flushInterval、size、readOnly、eviction 分别是什么意思？
type: concept
difficulty: easy
importance: 1
category: spring
tags: [mybatis-cache, replacement-policy]
prerequisites: [q_01M6XCBSNWRWKD6XSZ1X4ZS2CS]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 2
references:
  - { title: "MyBatis 3 文档：Mapper XML 文件（cache 元素的 eviction、flushInterval、size、readOnly）", url: "https://mybatis.org/mybatis-3/sqlmap-xml.html" }
---

## 一句话
flushInterval 是定时清空的间隔，size 是缓存对象数量上限。readOnly 决定返回拷贝还是原对象，eviction 是容量满时淘汰谁的策略。

## 要点
- [kp1|3] `eviction` 是回收策略，默认 LRU，淘汰最久没用的
- [kp2|3] `size` 是最多缓存多少个对象，默认 1024
- [kp3|2] `flushInterval` 是自动清空间隔，毫秒，默认不按时间清
- [kp4|2] `readOnly` 为 false（默认）时返回拷贝，true 时直接返回同一对象

## 详解
### 先搞懂：给公告栏定规矩
二级缓存像一块公告栏，需要定几条规矩。栏能贴多少张（size）。满了撕哪张（eviction）。多久整体清一次（flushInterval）。别人能不能在上面乱涂乱画（readOnly）。

### 四个属性分别是什么
- **eviction**：缓存满了要腾位置时，淘汰哪个。常见取值有 `LRU`（最近最少使用）、`FIFO`（先进先出）、`SOFT`（软引用）、`WEAK`（弱引用）。默认是 `LRU`。
- **size**：能缓存的对象数量上限，默认 1024。
- **flushInterval**：每隔多少毫秒清空整个缓存。不设置就不按时间清，只在增删改时清。
- **readOnly**：默认 false。

### readOnly 容易搞混
- `readOnly="false"`：每次从缓存取，得到的是一份拷贝（靠序列化实现），你改它不会影响缓存。因为要拷贝，所以实体类要实现 `Serializable`，速度稍慢，但更安全。
- `readOnly="true"`：每次直接返回缓存里的同一个对象，没有拷贝，速度更快。但是如果有人改了这个对象，后来读到它的人都会看到被改的值。所以只适合你保证不会修改的场景。

### 怎么写
```xml
<cache eviction="LRU" flushInterval="60000" size="512" readOnly="true"/>
```
意思是：满了淘汰最近最少使用的，每 60 秒清空一次，最多 512 个对象，返回只读对象。

## 易错点
- 把 `readOnly` 理解成「数据库只读」；它说的是缓存返回的对象能不能被修改，不涉及数据库
- 设 `readOnly="true"` 后又修改查出来的对象；会污染缓存里的数据
- 以为 `flushInterval` 单位是秒；它是毫秒

## 追问
### [f1] LRU 是什么意思？
Least Recently Used，最近最少使用。缓存满了的时候，把最长时间没被访问过的那个对象淘汰掉，留下最近常用的。
