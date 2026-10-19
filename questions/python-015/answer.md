## 1. 先区分对象保留、分配器缓存与原生泄漏

常见原因包括无限增长的全局缓存、未移除的回调持有实例、未结束的任务持有大对象，以及 C 扩展未释放的原生内存。现代 CPython 的不可达引用环通常可以由 GC 处理，定义 `__del__` 并不必然造成永久泄漏；关闭 GC、对象复活或扩展类型未正确支持 GC 等需要另查。

RSS 还受内存池、碎片和原生库缓存影响。对象数量下降但 RSS 未下降，不能直接认定有强引用泄漏。

## 2. 用 tracemalloc 对比受追踪的分配

```python
import tracemalloc

tracemalloc.start(10)
before = tracemalloc.take_snapshot()

retained = [f"retained-{i}" for i in range(1000)]
after = tracemalloc.take_snapshot()
for stat in after.compare_to(before, "lineno")[:3]:
    print(stat)

tracemalloc.stop()
```

示例展示两次快照间、仍存活的受追踪分配增量，文件名、行号和字节数取决于运行环境，不预设固定结果。生产排查应在稳定工作负载下多次取样，结合对象引用链与 RSS 判断是否持续增长。

tracemalloc 不能自动覆盖所有 C 扩展的直接 `malloc` 或 GPU 内存；它也会增加时间与内存开销，保存更多栈帧会提高诊断成本。无法在快照中解释的 RSS 增长需结合原生分配分析工具。

参考：[tracemalloc](https://docs.python.org/3.14/library/tracemalloc.html)、[gc](https://docs.python.org/3.14/library/gc.html)。
