## 追问 1：为什么自定义对象作为字典的 key 时，必须同时实现 __hash__ 和 __eq__？

字典查找 key 时先调用 hash(key) 得到哈希值，算出在 indices 数组中的槽位；若遇到哈希冲突（不同对象的 hash 相同或落在同个槽位），必须调用 __eq__ 判断两者是否真正相等。如果只实现 hash 不实现 eq，遇到冲突时就无法准确定位目标。

## 追问 2：在遍历字典的过程中直接修改或删除 key 为什么会抛出 RuntimeError: dictionary changed size during iteration？

因为字典的扩容、缩容或插入新元素会改变底层 entries 数组的长度和连续内存布局，使得当前正在遍历的迭代器索引指针失效。若需安全修改，必须先用 list(d.keys()) 或 list(d.items()) 创建一份浅拷贝再做遍历。
