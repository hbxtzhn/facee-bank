## 1. 传统字典的痛点（Python 3.6 之前）

早期的 Python 字典本质是一个巨大的稀疏哈希表（Sparse Hash Table）：
每个槽位都是一个 24 字节的大结构体：
```c
struct {
    Py_hash_t me_hash;
    PyObject *me_key;
    PyObject *me_value;
}
```
- 为了减少哈希冲突，哈希表的负载因子维持在 2/3 左右，意味着至少有 **1/3 的空间是空的（None）**；
- 每一个空的槽位都在白白浪费 24 字节内存，而且遍历时无法保证插入顺序。

---

## 2. 现代紧凑字典（Compact Dict，Python 3.6+ / PyPy 方案）

Python 3.6 开始采用两层数组解耦的精妙设计：

```text
原始数据：d = {'timmy': 'red', 'barry': 'green', 'guido': 'blue'}

① 稀疏哈希索引表（indices）:
[-1,  0, -1, -1,  1, -1, -1,  2]   <-- 仅存 entries 数组的小整数索引（1字节 int8）

② 紧凑数据表（entries，致密连续数组）:
[
  [hash('timmy'), 'timmy', 'red'],     # 索引 0
  [hash('barry'), 'barry', 'green'],   # 索引 1
  [hash('guido'), 'guido', 'blue']     # 索引 2
]
```

### 带来的两大巨大收益：
1. **极大节省内存**：空的槽位只占 1 个字节（`int8`），真正存储键值对的 `entries` 数组永远是**紧凑连续存储**的，整体节省 25%~40% 内存。
2. **天然保持插入顺序**：新插入的键值对永远追加在 `entries` 的末尾，遍历字典时直接顺序扫描 `entries` 数组，因此字典自 3.6 起天然保序（3.7 正式写入语言规范）。

---

## 3. 哈希冲突与扩容

- **寻址方式**：采用**开放寻址法（Open Addressing）中的伪随机探测**：
  $$	ext{next\_idx} = (5 	imes 	ext{idx} + 1 + 	ext{perturb}) \pmod{	ext{size}}$$
  通过扰动值（perturb）让冲突后的跳跃步长散列得更均匀。
- **扩容阈值**：当字典元素达到总容量的 **2/3** 时触发扩容。
  - 小型字典（<= 50000 元素）：按 $4 	imes 	ext{当前大小}$ 翻倍扩容；
  - 大型字典：按 $2 	imes 	ext{当前大小}$ 扩容；
- **元素删除**：删除时不直接缩短数组，而是将对应的 entries 槽位标记为 `dummy` 墓碑，只有当再次扩容/重构哈希表时才真正丢弃无用槽位。
