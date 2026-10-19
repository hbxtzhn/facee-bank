## 1. 为什么需要 MRO 与 C3 算法？

在支持多重继承的面向对象语言中，最棘手的问题是**菱形继承（Diamond Problem）**：
```text
    A
   / \
  B   C
   \ /
    D
```
- **Python 2 的经典类使用深度优先、从左到右搜索**；在菱形结构中可能先找到较远基类的方法，从而绕过另一分支的重写。Python 3 已不存在经典类与新式类之分。
- **广度优先搜索（BFS）**：遍历顺序为 `D -> B -> C -> A`，但如果遇到不对称继承结构，会违背“局部优先（声明顺序在前先调用）”原则。

为了彻底解决此问题，Python 2.3+ 的新式类全面引入了 **C3 线性化算法（C3 Linearization Algorithm）**。

---

## 2. C3 算法的三大保证

1. **子类优先于父类**：派生类总是在其基类之前被访问。
2. **保持局部声明顺序**：若声明 `class D(B, C)`，则 `B` 的优先级一定高于 `C`。
3. **单调性（Monotonicity）**：在整个继承树中，若某个类 `X` 在 `Y` 前面，则在所有派生类的 MRO 中，`X` 必须始终保持在 `Y` 前面。

---

## 3. C3 归并计算过程极简推导

一个类 $C(B_1, B_2, \dots, B_n)$ 的 MRO 定义为：
L(C) = [C] + merge(L(B1), L(B2), ..., L(Bn), [B1, B2, ..., Bn])

**Merge 规则**：
- 依次检查各个列表的表头（Head）。
- 如果这个表头不在任何其他列表的表尾（Tail，即除表头外的其余元素）中，就将其提取出来放入最终 MRO，并从所有列表中移除该元素；
- 否则跳过，检查下一个列表的表头；
- 直到所有列表为空即成功；若所有候选表头都在其他列表的表尾中，说明继承顺序冲突，抛出异常。

---

## 4. 实战与 super() 的真相

```python
class A:
    def greet(self):
        print("A")

class B(A):
    def greet(self):
        super().greet()
        print("B")

class C(A):
    def greet(self):
        super().greet()
        print("C")

class D(B, C):
    def greet(self):
        super().greet()
        print("D")

# 查看 MRO
print([cls.__name__ for cls in D.mro()])
# 输出顺序：['D', 'B', 'C', 'A', 'object']

d = D()
d.greet()
# 输出：
# A
# C
# B
# D
```

**核心结论**：`super()` 不是调用父类，而是**沿着实例所属类的 MRO 链表查找下一个节点**。在 `B` 中调用 `super().greet()` 时，按照 `D.mro()` 找到的下一个是 `C`，而不是 `A`，保证了菱形顶端的 `A` 最终只被执行一次。
