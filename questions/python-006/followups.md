## 追问 1：super() 到底是在调用谁？是父类吗？

不是直接调用父类，而是调用当前类在 MRO（方法解析顺序）链表中的下一个类。在单继承下它恰好是父类；但在多继承（如菱形继承）下，super() 可能会横向调用兄弟类，以保证每个公共基类的方法只被调用一次。

## 追问 2：什么情况下会导致 Python 抛出 TypeError: Cannot create a consistent method resolution order？

当类的继承关系违背了局部优先级（单调性）产生死循环冲突时。例如定义 class A(B, C): pass，同时另一个类 class D(C, B): pass，如果再试图定义 class E(A, D): pass，C3 算法检测到无法在保持 B 在 C 前的同时又让 C 在 B 前，就会在类定义加载阶段直接阻断报错。
