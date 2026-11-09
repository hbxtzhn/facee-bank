# FaceE 题库

本仓库是 FaceE 的面试题库（规范 v2），每道题是 `questions/<category>/q_<ULID>.md`。

## 写题 / 生成答案

任何新增或改写题目的任务，先完整读 `prompts/answer.md`，按其中的流程、分段规则和自检清单执行，完成后按「交付汇报」格式回复。

## 工具

题库 CLI 在同级的 App 仓库里（依赖 App 根目录的 `node_modules`）：

```bash
node ../facee/packages/bank-spec/cli.mjs new      --bank . --category <id> --tags <a,b> --title <标题>
node ../facee/packages/bank-spec/cli.mjs fix-ids  --bank .
node ../facee/packages/bank-spec/cli.mjs validate --bank .
node ../facee/packages/bank-spec/cli.mjs stats    --bank . [--json]          # 分类 / 标签 / 难度 / 重要度分布、专题覆盖、过期复核
node ../facee/packages/bank-spec/cli.mjs merge-question  --bank . --from A --into B [--dry-run]   # 合并重复题，改写所有引用
node ../facee/packages/bank-spec/cli.mjs remove-question --bank . --id A [--dry-run]              # 删除题目，记入 lifecycle
```

删除或合并题目必须用上面两个命令（或照它们的步骤手工做），不能直接删文件。

题库维护脚本：

```bash
node scripts/tags.mjs   [--write] [--with-meta]          # plans/tags.yaml → bank.yaml 的 tags，并检查别名冲突与层级
node scripts/routes.mjs --plan plans/<name>.yaml [--write] # 清单里的学习路线 → bank.yaml 的 collections，并检查前置顺序
```

内容检查（validate 管不到的规则，并实际运行 Java 小实验）：

```bash
node scripts/check.mjs [题目文件...]
```

批量生成（维护者使用；按 `plans/*.yaml` 清单逐题调用 pi，检查通过才合并回仓库，不提交）：

```bash
node scripts/gen.mjs --plan plans/<name>.yaml [--model <provider/id>] [--concurrency 1] [--dry-run]
```

- 分类和标签以 `bank.yaml` 为准；新标签先加到 `bank.yaml`。
- 小实验需要 JDK 21、Docker；临时容器用完删除。
- 不改与任务无关的题目文件。
