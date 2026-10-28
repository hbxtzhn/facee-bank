### 一句话总结

前端国际化采用**“文案标识解耦（Key 映射） + 核心运行时（如 `react-i18next` / `vue-i18n`） + 语言包动态按需异步加载”**。界面严禁硬编码中文字符，统一使用 `t('login.submit')` 占位；通过 Webpack / Vite 将各语言包切分为独立 JSON 异步分包，切换语言时仅动态拉取对应语种资源，首屏零额外体积负担。

---

### 详细回答

#### 1. 核心架构设计三要素
- **语言检测中枢**：优先级判断：URL 参数（`?lang=en`） $	o$ 本地 LocalStorage 记忆 $	o$ 浏览器系统偏好（`navigator.language`）；
- **动态占位插值与复数处理**：支持变量插值（`t('welcome', { name: 'Jack' })`）以及英语等单复数转换规则；
- **按需加载（Code Splitting）**：用户在中国访问只下载中文包，点击切换“English”时才动态 fetch 英文语言包。

#### 2. 日常开发痛点：文案提取与维护
- 研发手动去文案表格复制 Key 极度低效痛苦；
- 引入自动化 CLI 工具（如 `i18n-ally` VS Code 插件）：在代码中直接写中文，构建时自动扫描提取并生成国际化 JSON 映射表。

---

### 核心代码片段（极简记法）

```javascript
import i18n from 'i18next';
import HttpBackend from 'i18next-http-backend';

i18n
  .use(HttpBackend) // 动态从 CDN 异步按需拉取目标语言包
  .init({
    lng: 'zh-CN',
    fallbackLng: 'en',
    backend: { loadPath: '/locales/{{lng}}/{{ns}}.json' }
  });

// 组件内消费
const { t } = useTranslation();
return <button>{t('common.confirm')}</button>;
```

---

### 面试加分项

- **样式与排版的国际化灾难（排版适配）**：不同语言文案长度差异巨大（德语、俄语文案通常比中文长 2~3 倍）。严禁在按钮上写死固定宽度（`width: 80px`），布局必须采用自适应宽度并留足安全间距；针对阿拉伯语等中东语言，还需在 `<html>` 标签动态切换 `dir="rtl"`（从右往左排版）。
