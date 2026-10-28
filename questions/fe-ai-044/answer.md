### 一句话总结

多租户前端架构采用**“域名解析租户标识（Tenant Resolver） + CSS 变量运行时主题换肤 + 特征开关（Feature Flags）动态能力树”**。首屏通过二级域名或 CNAME 识别当前租户并预先获取租户配置；将主题颜色下发注入 `:root` CSS 变量；界面菜单与模型列表根据租户购买套餐的功能开关（Feature Flag）动态裁减，实现千企千面的白牌（White-label）定制。

---

### 详细回答

#### 1. 自定义域名与租户识别
- **域名解析流程**：
  - 访问 `tenantA.ai.com` 或 CNAME `ai.companyB.com`；
  - 前端路由拦截或 Next.js Edge Middleware 提取 `host` 请求头；
  - 携带域名向配置网关请求该租户元数据（Logo、品牌名称、色系、已购模型列表）。

#### 2. CSS 变量动态一键换肤
- 杜绝针对每个租户单独打包一套 CSS；
- 全局使用 CSS 自定义属性（CSS Variables）：
  ```css
  :root {
    --primary-color: #1677ff;
    --chat-bubble-radius: 8px;
  }
  ```
- 接口返回配置后，一行 JS 动态注入：
  `document.documentElement.style.setProperty('--primary-color', tenant.themeColor);`

#### 3. 特征开关（Feature Flags）与模型权限控制
- 租户配置返回模块权限树：`{ enableCodeInterpreter: false, allowedModels: ['gpt-4o-mini'] }`；
- 前端通过 `<FeatureGate flag="enableCodeInterpreter">` 条件包裹，未购买高级特性的租户直接隐藏该入口。

---

### 核心代码片段（极简记法）

```javascript
// 1. 动态挂载租户品牌主题
function applyTenantTheme(theme) {
  const root = document.documentElement;
  root.style.setProperty('--primary-color', theme.brandColor);
  root.style.setProperty('--navbar-bg', theme.navBackground);
  document.title = theme.brandTitle;
}

// 2. 特征开关组件保护高阶功能
function FeatureGate({ flag, children }) {
  const tenantFlags = useTenantStore(s => s.features);
  return tenantFlags[flag] ? children : null;
}
```

---

### 面试加分项

- **防白屏防闪烁（FOUC 优化）**：租户配置拉取完成前界面容易闪烁。在 HTML `<head>` 中嵌入一小段内联 JS，在页面 DOM 解析前即刻根据本地缓存的租户主题设好 CSS 变量，消除色彩突变。
