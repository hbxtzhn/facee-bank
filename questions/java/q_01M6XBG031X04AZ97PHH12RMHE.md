---
id: q_01M6XBG031X04AZ97PHH12RMHE
title: 为什么重写 equals 时必须重写 hashCode？
type: concept
difficulty: medium
importance: 3
category: java
tags: [object-methods, hash-table]
prerequisites: [q_01M6XBFZADH0AVDGPZ3532ZNPE, q_01M6XBFZJMZD7VG6THZ137E4WW, q_01M6XBFZTSPMHVQE5AN77AZK14]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
哈希集合先用 hashCode 找桶、再用 equals 比对；只重写 equals 不重写 hashCode，两个相等的对象就会落进不同的桶，导致查找不到或重复存入。

## 要点
- [kp1|3] 哈希集合先用 hashCode 定位桶，再在桶里用 equals 比对
- [kp2|3] equals 相等的两个对象，hashCode 必须相同，这是约定
- [kp3|2] 只重写 equals，相等的对象可能落在不同桶，HashSet 里会出现重复
- [kp4|2] 同样的原因，HashMap 用另一个相等的 key 去 get，会取到 null
- [kp5] 重写时用同一批字段计算 hashCode，比如 Objects.hash

## 详解
### 先搞懂：先找分区，再核对身份
还是用图书馆的比方：找书先看分区号，再到区里按书名核对。假设有两本一模一样的书（内容相同，算“相等”），但管理员给它们编了不同的分区号，一本放 A 区，一本放 B 区。你去 A 区找，找不到放在 B 区的那一本，即使它和你要的是同一本书。

HashSet、HashMap 也是这样：分区号就是 `hashCode`，核对书名就是 `equals`。

后文用到的词：

- **桶**：哈希集合中的一个存放位置，由哈希码决定。
- **重复元素**：在 Set 中本来应该只留一个的“相等”对象，却出现了两个。

### 哈希集合怎么判断两个对象是同一个
放入或查找时，分两步：

1. 先用 `hashCode` 算出桶；
2. 只在这个桶里，用 `equals` 一个个比对。

所以，“相等”要成立，前提是 hashCode 先落到同一个桶。如果两个 equals 相等的对象 hashCode 不同，第 1 步就把它们分开了，第 2 步根本没机会比较。

### 只重写 equals 会出什么事
`Object` 默认的 `hashCode` 通常和对象身份有关，不同对象一般算出不同的值。如果你只重写了 `equals`，按 id 判断相等，但 `hashCode` 仍用默认的：

- 把 `new User(1)` 两次放进 `HashSet`：虽然 equals 相等，但哈希码不同，通常落在不同的桶，Set 里就有两个，去重失效；
- 用 `new User(1)` 作为 key 放入 `HashMap`，再用另一个 `new User(1)` 去 `get`，通常得到 null。

注意：有时两个哈希码碰巧落在同一个桶，问题就不出现。这种“有时好有时坏”更难排查。

### 正确做法
重写 equals 时，同时重写 hashCode，并且用 equals 里比较的那些字段来算哈希码。这样 equals 相等的对象，一定得到同样的哈希码。反过来，hashCode 相同的对象不一定 equals 相等，那没有问题，桶里还会再用 equals 比一次。

## 示例
```java
class User {
    long id;
    User(long id) { this.id = id; }

    @Override
    public boolean equals(Object o) {
        return o instanceof User u && id == u.id;
    }
    // 去掉下面这个方法，HashSet 去重通常就会失效
    @Override
    public int hashCode() {
        return Long.hashCode(id);
    }
}
// Set<User> set = new HashSet<>();
// set.add(new User(1)); set.add(new User(1)); // set.size() == 1
```

## 易错点
- 以为 equals 相等就够了；哈希集合还要求 hashCode 一致
- 用会变化的字段算 hashCode，对象放入集合后字段一改，就找不到它了
- hashCode 用的字段比 equals 多，导致 equals 相等的对象 hashCode 却不同
- 以为 hashCode 相同就是 equals 相等；还需要 equals 比对

## 追问
### [f1] 只重写 hashCode 不重写 equals 会怎样？
哈希码相同会落在同一个桶，但桶里用默认 equals 比较，也就是比地址，不同对象仍然不相等，去重依然失败。所以两个方法要一起重写。

### [f2] 为什么不干脆让所有对象的 hashCode 都返回同一个值？
这样虽然符合约定，但所有对象都落进同一个桶，查找退化成逐个比较，哈希集合的速度优势就没有了。
