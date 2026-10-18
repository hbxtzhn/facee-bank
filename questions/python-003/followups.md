## 追问 1：yield 和 yield from 有什么区别？

yield 每次产出一个单独的值；而 yield from iterable 会把右侧的可迭代对象展开并逐个产出。更重要的是，yield from 会在调用方和子生成器之间建立一条双向的数据与异常传递通道（透明委托），是 Python 3 早期实现协程调度的重要基础。
