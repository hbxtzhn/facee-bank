## 追问 1：数字、日期、货币的国际化（如人民币 vs 美元格式）怎么处理？

**回答要点**：
无需引入庞大的第三方库，优先使用现代浏览器原生内置的 **`Intl` 对象**！
- 货币与数字：`new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(1234.5)`；
- 日期时间：`new Intl.DateTimeFormat('zh-CN').format(new Date())`。

---

## 追问 2：多语言页面如何做好 SEO 搜索引擎优化？

**回答要点**：
在 HTML `<head>` 中添加包含语言指示的 `<link rel="alternate" hreflang="en" href="https://example.com/en/" />` 标签，并在服务端根据路由直接输出对应语种的纯净 HTML，禁止由纯前端客户端异步渲染导致爬虫抓到空白 Key。
