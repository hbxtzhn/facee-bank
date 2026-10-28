### 一句话总结

最优雅的核心思路是**“在全局请求拦截器中就地 `new Error().stack` 提取调用栈并正则解析行号”**，结合 **构建工具插件（Babel / Vite Plugin）在编译期 AST 自动注入文件名**。在发起 Fetch / Axios 时实例化 Error 对象读取堆栈，向上回溯跳过 Axios 内部封装层，精准定位到业务组件的调用行，结合 SourceMap 在后台还原出原始 TS 源码位置。

---

### 详细回答

#### 1. 运行时方案：利用 Error 调用栈追溯（零构建侵入）
- 当你在 JS 中执行 `new Error().stack` 时，V8 引擎会瞬间捕获当前函数执行的调用栈帧；
- 打印出的堆栈长这样：
  ```text
  Error
      at Object.get (/utils/request.js:12:15)
      at fetchUserProfile (/services/user.ts:45:10)  <-- 真实的业务发起点！
      at UserProfile.vue:88:5
  ```
- 编写简单的正则表达式，跳过通用的封装拦截文件，直接提取第一行属于业务目录的文件路径与行列号。

#### 2. 编译期方案：Babel / Vite 编译宏注入（零运行时性能损耗）
- 编写 Vite 插件，在 AST 语法树遍历时识别所有 `api.call(...)` 函数；
- 自动向函数隐式追加调用元数据参数：
  `api.get('/users', { __caller: 'src/pages/User.tsx:42' })`。

---

### 核心代码片段（极简记法）

```javascript
// 在 Axios 拦截器中动态提取发起代码位置
axios.interceptors.request.use((config) => {
  const stack = new Error().stack || '';
  const lines = stack.split('
');
  // 跳过前几层 axios 内部堆栈，找到业务层调用行
  const callerLine = lines.find(line => !line.includes('axios') && !line.includes('request.js')) || '';
  
  config.headers['X-Request-Source'] = callerLine.trim(); // 注入请求头或监控字段
  return config;
});
```

---

### 面试加分项

- **生产环境代码混淆与 SourceMap 还原**：生产代码经过打包后全是 `bundle.min.js:1:3485`。必须结合后端的 **SourceMap Consumer 还原服务**：上报行列号后，在监控后台根据发版时的隐藏 SourceMap 文件，将其还原为如 `src/components/PayButton.tsx:28` 的真实人类可读行号。
