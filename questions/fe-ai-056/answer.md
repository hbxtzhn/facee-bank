### 一句话总结

前端本地合规过滤采用**“Aho-Corasick 多模式匹配算法（AC 自动机）或前缀树（Trie Tree）结合拼音/变体归一化”**。在请求发出前对 Prompt 执行毫秒级本地扫描；提前拦截明显的涉政、暴恐、个人敏感隐私（手机号、身份证、API Key）数据，实现零网络开销、即时拦截提示并保护企业隐私不外泄。

---

### 详细回答

#### 1. 为什么用 AC 自动机而不是写 10,000 个正则表达式？
- 若用数组 `words.some(w => text.includes(w))`，时间复杂度是 $O(M 	imes N)$，词库过万时页面直接卡死；
- **AC 自动机（Aho-Corasick）**：预先根据敏感词构建字典树并设置失败指针（Fail Pointer），只需对目标文本**单次线性扫描**（时间复杂度 $O(N)$），扫描万字长文仅需几毫秒。

#### 2. 对抗文本变体与混淆（Text Normalization）
- 用户经常通过拼音、繁体字、空格插入、特殊符号分隔绕过检测（如 `敏 感 词`、`mǐngǎn`）；
- 前端在匹配前执行标准化流水线：
  1. 繁体转简体；
  2. 剔除标点与空格缩进；
  3. 全角字符转半角。

#### 3. 隐私数据脱敏（PII Sanitization）
- 正则匹配手机号、中国大陆身份证号、银行卡号、JWT 凭证；
- 提示用户：“检测到您的输入包含手机号，已自动替换为 `[PHONE]` 脱敏发送”。

---

### 核心代码片段（极简记法）

```javascript
// 基于 Trie 树的前缀快速匹配骨架
class SensitiveWordFilter {
  constructor(wordList) {
    this.root = {};
    for (const word of wordList) {
      let node = this.root;
      for (const char of word) {
        node[char] = node[char] || {};
        node = node[char];
      }
      node.isEnd = true;
    }
  }

  hasSensitive(text) {
    for (let i = 0; i < text.length; i++) {
      let node = this.root;
      for (let j = i; j < text.length; j++) {
        if (!node[text[j]]) break;
        node = node[text[j]];
        if (node.isEnd) return true; // 命中敏感词！
      }
    }
    return false;
  }
}
```

---

### 面试加分项

- **安全防御纵深认知（Defense in Depth）**：必须清醒认识到**前端的本地过滤永远只能用于“提升体验与粗筛”**，绝不能作为唯一安全防线。黑客可轻松通过控制台绕过前端 JS，因此后端和模型网关必须保留最终严格的安全过滤关卡。
