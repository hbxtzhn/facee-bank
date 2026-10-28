## 追问 1：lint-staged 能直接跑 tsc --noEmit 吗？会有什么坑？

**回答要点**：
有坑！
`tsc` 不支持只编译部分单文件，它必须读取全量项目工程文件。若将 `tsc` 挂在 `lint-staged` 的单文件匹配列表里会导致每个暂存文件全量跑一次 `tsc`（卡死电脑）。
正确做法是：在 `lint-staged` 运行完之后，单独在 `pre-commit` 脚本末尾追加一行单次的 `pnpm type-check`。

---

## 追问 2：新手觉得 git cz 命令太麻烦，只想用 VS Code Git 界面点击提交，Commitizen 会失效吗？

**回答要点**：
会失效。但因为配置了 Husky 的 `commit-msg` 强制校验，哪怕在 VS Code 界面点击提交，如果手写的日志不合规也会被直接打回并弹出报错，依然能够强力守护规范底线。
