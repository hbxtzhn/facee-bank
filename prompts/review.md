# 审校规范（轻量）

八股题的结论大多早已稳定，审校只抓容易写错的具体细节，不做逐句考证。

## 要核对什么

只核对正文里的**具体数字、默认值、版本行为**（如「默认 10 秒」「JDK 15 起默认关闭」「Redis 7.0 起多文件 AOF」）。通用概念、原理讲解、选型建议不用查。

## 怎么核对

- **只看官方文档页面**（Oracle / OpenJDK 文档与 JEP、MySQL 手册、Redis 文档、Spring / MyBatis 文档、RFC 等），**不翻源码**。
- **每题最多打开 2 个页面**。查不到就保留原文，不要为了找依据继续深挖。
- 确认写错了 → 只改那一句，保持原来的语气。
- 文档里打开过、能支持正文的页面，可以顺手写进 front matter 的 `references`（`- { title: "…", url: "…" }`）；没有就不加，不强求。

## 不要动的

`id`、`title`、`category`、`tags`、`difficulty`、`importance`、`prerequisites`、`related`、`source`、要点和追问的编号；不增删章节；不加 `reviewedAt`。

## 校验

改过的题运行 `node scripts/check.mjs <题目文件>`（在仓库根目录 `E:/orca/workspace/facee-bank` 下），零错误零警告。

## 汇报

每题一行：「核对无误」或「改正：原 → 新（依据 URL）」。
