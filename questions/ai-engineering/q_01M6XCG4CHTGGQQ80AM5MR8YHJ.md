---
id: q_01M6XCG4CHTGGQQ80AM5MR8YHJ
title: JSON Mode 和 JSON Schema 的约束有什么区别？
type: concept
difficulty: medium
importance: 2
category: ai-engineering
tags: [prompt-engineering]
prerequisites: [q_01M6XCG3YB7F89YDSZ47CVV5R4]
source: { name: FaceE, license: CC-BY-4.0 }
estimatedMinutes: 3
---

## 一句话
JSON Mode 只保证输出是合法的 JSON，不保证里面有哪些字段；JSON Schema 还会约束字段名、类型和必填项，契约更严格。

## 要点
- [kp1|3] JSON Mode 只保证语法合法，能被 JSON 解析器解析
- [kp2|3] JSON Schema 额外规定字段名、类型和必填项
- [kp3|2] 仅用 JSON Mode，字段可能缺失、名字不对或类型错
- [kp4] 各家接口的支持程度不同，是否强制遵守 schema 以文档为准

## 详解
### 先搞懂：能打开的文件和内容对的文件
你让同事发来一份表格。他发来的文件能正常打开，这是“格式合法”；但里面的列是不是你要的、有没有缺列，是另一回事。

JSON Mode 保证的是前者：输出一定是能解析的 JSON。JSON Schema 管的是后者：内容是否符合你定的结构。

后文用到的词：
- **JSON Mode**：让模型只输出合法 JSON 的模式。
- **JSON Schema**：用来描述 JSON 应有结构的规范，写明字段、类型、必填。
- **必填项**：Schema 里要求必须出现的字段。

### JSON Mode：保证语法
它保证输出是语法正确的 JSON，比如括号、引号都配对。但它不知道你想要哪些字段。

你要 `name` 和 `age`，它可能返回 `{"username": "Tom"}`。这是合法 JSON，却不是你要的。

### JSON Schema：定好契约
你用 Schema 事先写明：必须有 `name`（字符串）和 `age`（整数）。这就是程序和模型之间的契约。

```json
{
  "type": "object",
  "properties": {
    "name": {"type": "string"},
    "age": {"type": "integer"}
  },
  "required": ["name", "age"]
}
```

输出按这个契约去对照，字段名、类型、必填项都能检查。

### 方案对比：JSON Mode 与 JSON Schema
| 方式 | 保证什么 | 不保证什么 | 适合 |
|---|---|---|---|
| 提示里要求 JSON | 无保证 | 格式、字段 | 快速试验 |
| JSON Mode | 语法合法 | 字段、类型 | 只要能解析 |
| JSON Schema | 字段、类型、必填 | 取值的语义是否正确 | 程序严格依赖结构 |

结论：程序依赖固定字段时用 JSON Schema；只想要合法 JSON 时才用 JSON Mode。无论哪种，字段的取值是否合理，仍需程序校验。

### 进阶：不同接口的差异（基础薄弱可先跳过）
有的接口只是把 Schema 当提示，有的会在生成阶段强制遵守。后者可靠得多，选用前要看清文档说明。

## 易错点
- 以为 JSON Mode 会保证字段正确；它只保证语法
- 以为符合 Schema 就代表内容正确；字段值仍可能是错的
- 不看接口文档，默认 Schema 一定被强制执行

## 追问
### [f1] 用了 JSON Schema 还要校验吗？
建议仍然校验。Schema 管结构，不管值是否合理，还要处理接口不强制遵守的情况。

### [f2] JSON Mode 有什么用？
它保证输出能被解析，适合只需要合法 JSON、对字段要求不高的场景。
