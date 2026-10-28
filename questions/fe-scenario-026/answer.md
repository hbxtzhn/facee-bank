### 一句话总结

`@babel/plugin-transform-runtime` 配合 `@babel/runtime` 核心解决两大痛点：**“公共辅助函数抽离复用以缩小体积”**与**“无全局变量污染的沙箱 Polyfill”**。它将每个文件里重复生成的 `_extend`、`_classCallCheck` 等内联助手函数提取为模块导入，并使用局部重命名的别名引入 Promise/Symbol，避免污染全局命名空间，是开发通用 NPM 库的行业标配。

---

### 详细回答

#### 1. 痛点一：辅助函数重复注入（包体积膨胀）
- 默认情况下，Babel 在转译 ES6 `class` 时，会在每个打包文件中都硬编码一份几十行的辅助代码 `function _classCallCheck(...)`；
- 如果项目有 200 个文件，就会被重复拷贝 200 次；
- **解决**：transform-runtime 将其替换为统一从 `@babel/runtime/helpers/classCallCheck` 导入，全包只保留一份单例。

#### 2. 痛点二：全局 Polyfill 污染（库开发的大忌）
- `@babel/polyfill`（已废弃）采用的是在全局 `window` 上直接无脑挂载 `window.Promise = ...`；
- 如果你在开发一个工具库（SDK）给别人用，你的 SDK 偷偷篡改了用户的全局 Promise，极易导致宿主应用出现不可预知的冲突 Bug；
- **解决**：runtime 插件采用沙箱化局部替换：`import _Promise from '@babel/runtime-corejs3/core-js-stable/promise'`，在局部作用域内安全运行，完全不碰全局变量。

---

### 核心代码片段（极简记法）

```json
// .babelrc 配置生产级 transform-runtime
{
  "plugins": [
    [
      "@babel/plugin-transform-runtime",
      {
        "corejs": 3,       // 提供不污染全局的 API Polyfill
        "helpers": true,     // 抽离重复的 helper 辅助函数
        "regenerator": true // 抽离 async/await 运行时生成器
      }
    ]
  ]
}
```

---

### 面试加分项

- **应用开发 vs 库开发的 Polyfill 选型**：指出在业务应用（Application）开发中，通常推荐 `@babel/preset-env` 搭配 `useBuiltIns: 'usage'`，直接按需按浏览器目标兼容性全局填充；而在基础库/组件库（Library）开发中，坚决强制使用 `transform-runtime` 保持纯洁无污染。
