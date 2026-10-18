## 追问 1：在实现 __getattribute__ 时，最容易出现的死循环是什么？如何正确解决？

在 __getattribute__ 内部如果直接写 self.name 或 self.__dict__['name']，这个访问本身又会触发对 __getattribute__ 的调用，导致无限递归暴栈。正确做法是必须通过父类调用：super().__getattribute__(name)。

## 追问 2：__getattr__ 适合用在哪些实际架构中？

非常适合用于动态 RPC 代理客户端（如 client.user.get_info() 动态抓取方法名发网络请求）、配置文件的链式读取（如 config.db.host），以及字典对象的属性化访问（attrdict）。
