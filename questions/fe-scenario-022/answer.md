### 一句话总结

还原用户流程采用**“轻量行为轨迹探针（Breadcrumbs 面包屑链） + 基于 DOM 快照的录屏回放（如 rrweb）”**。全局拦截点击、路由跳转、网络请求并存入环形缓冲区；更极致的方案是利用 **rrweb 监听 DOM 树的 MutationObserver 增量突变**，将页面交互序列化为时间轴事件流，在后台像播放视频一样 1:1 动态还原用户点击与报错现场。

---

### 详细回答

#### 1. 方案一：行为轨迹日志（Breadcrumbs，开销极低）
- 拦截用户所有交互行为并在本地内存维护一个固定容量（如 50 条）的队列：
  - 点击事件：记录点击的元素标签、类名、按钮文案；
  - 路由跳转：记录从 `/list` 跳转到 `/detail/10`；
  - 接口调用：记录发送的请求与返回的状态码；
- 当报错触发时，将这 50 条足迹随错误报告一并上报，排查人员按步骤点击复现。

#### 2. 方案二：真实 DOM 录屏回放（rrweb，极致排查）
- **绝不是用 Canvas 或截图转视频**（那样做体积几十兆、卡死浏览器且暴露隐私）；
- **rrweb 核心原理**：
  1. 首屏全量 DOM 序列化为轻量 JSON 树快照；
  2. 使用 `MutationObserver` 监听后续每一个微小的 DOM 增删改差量事件；
  3. 捕获鼠标移动、滚动、点击坐标轨迹；
  4. 压缩后体积每分钟仅几十 KB，后台通过 `rrweb-player` 完美重放真实 DOM 渲染！

---

### 核心代码片段（极简记法）

```javascript
import { record } from 'rrweb';

let events = [];

// 监听并录制所有 DOM 变化与用户鼠标轨迹
record({
  emit(event) {
    events.push(event);
    if (events.length > 200) events.shift(); // 仅保留最近轨迹
  },
  maskAllInputs: true // 自动遮罩所有输入框密码与手机号
});

// 报错时上报录像
window.onerror = () => {
  sendBeacon('/api/replay', JSON.stringify({ events }));
};
```

---

### 面试加分项

- **严苛的隐私数据脱敏（Data Masking）**：生产落地录屏必须通过合规审计。在录制配置中开启 `maskAllInputs: true`，将所有输入框文字全部替换为 `***`；对敏感区域添加特定类名 `.rr-mask`，rrweb 在录制阶段直接将其置灰遮罩，坚决杜绝密码与个人隐私泄漏。
