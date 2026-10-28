### 一句话总结

采用 **WebGL 着色器管线（Shader Pipeline）或双缓冲 Canvas 渲染**。将 AI 生成的大分辨率图像上传为 GPU 纹理（Texture）；缩放、平移与色彩滤镜（如色温、降噪、增强）完全由 **GPU 片元着色器（Fragment Shader）并发计算**，避免 CPU 逐像素循环修改像素点造成的卡死，稳定保持 60fps。

---

### 详细回答

#### 1. 为什么不用普通 DOM 变换（`<img>` + CSS transform）？
- CSS transform 仅能支持基础平移缩放；
- 当需要对 AI 图像做局部修复擦除（Inpainting）、涂抹蒙版（Mask）、直方图调整或流式生成过程的扩散步数（Diffusion Steps）过渡动画时，DOM 无能为力。

#### 2. Canvas 2D 逐像素计算的死穴
- 使用 `ctx.getImageData()` 修改像素阵列，对 4K 图像需要操作数千万个数组元素，纯 CPU 运算单帧耗时几百毫秒。

#### 3. WebGL 架构解法
- **GPU 纹理绑定**：单次将图像像素上传到 GPU 显存；
- **片元着色器处理滤镜**：在 GPU 中并发运行 GLSL 代码；
- **矩阵变换（Matrix Transform）**：平移和缩放只计算 3x3 矩阵相乘，单帧仅需 1~2 毫秒。

---

### 核心代码片段（极简记法）

```javascript
// WebGL 片元着色器调整对比度与曝光（GPU 并行计算）
const fragmentShaderSource = `
  precision mediump float;
  uniform sampler2D u_image;
  uniform float u_brightness;
  varying vec2 v_texCoord;

  void main() {
    vec4 color = texture2D(u_image, v_texCoord);
    gl_FragColor = vec4(color.rgb * u_brightness, color.a);
  }
`;
```

---

### 面试加分项

- **OffscreenCanvas（离屏渲染与 Worker）**：将 Canvas 控制权通过 `canvas.transferControlToOffscreen()` 转移给 Web Worker，在独立线程中执行图像加载与渲染，彻底消除主线程阻塞。
