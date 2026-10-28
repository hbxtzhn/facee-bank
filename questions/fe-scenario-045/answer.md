### 一句话总结

前端灰度发布核心有两大路径：**“网关/CDN 路由级灰度（分流静态资源入口 `index.html`）”**与**“代码层特征开关灰度（Feature Flag 动态控制功能组件）”**。网关根据用户 ID、IP 或 Cookie 计算一致性哈希，将 10% 的流量导流至加载了 `index_v2.html` 的灰度版本，一旦发现监控报错激增，秒级调整分流比例归零实现一键无感回滚。

---

### 详细回答

#### 1. 方案一：Nginx / 网关层分流（最彻底的整站灰度）
- 构建时打包出两份产物：`dist_v1`（稳定版）与 `dist_v2`（灰度版）；
- 在 Nginx 或边缘网关（OpenResty / Cloudflare Workers）提取用户 Cookie `uid`：
  - 对 `uid` 做 MurmurHash 取模 100；
  - 若数值小于设定阈值（如 10），Nginx 内部代理转发到 `dist_v2/index.html`；
  - 其余 90% 流量依然加载 `dist_v1/index.html`。

#### 2. 方案二：特征开关（Feature Flags / 业务组件级灰度）
- 代码正常全量发版；
- 页面加载时向配置中心拉取当前用户的 Flag 清单；
- 代码中包裹判断：`if (flags.enableNewCheckout) { ... }`；
- 优势：无需多版本打包部署，颗粒度细化到单个按钮与组件。

---

### 核心代码片段（极简记法）

```nginx
# Nginx 基于 Cookie 的 uid 做 10% 权重灰度路由
split_clients "${cookie_uid}" $app_version {
  10%     "/dist_v2/"; # 灰度版
  *       "/dist_v1/"; # 稳定版
}

location / {
  root /var/www$app_version;
  try_files $uri $uri/ /index.html;
}
```

---

### 面试加分项

- **静态资源版本容错（Version Cascade）**：灰度发布期间，CDN 上**必须同时完整保留 v1 和 v2 的所有带 hash 的 JS/CSS 文件**！若直接覆盖或清理了旧版资源，会导致尚未刷新页面的 90% 旧版用户在懒加载新页面路由时触发致命的 404 ChunkLoadError。
