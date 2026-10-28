## 追问 1：如果变基过程中遇到冲突（Conflict），该如何解决？

**回答要点**：
手动打开冲突文件解决冲突并保存；执行 `git add <file>` 标记已解决；然后运行 `git rebase --continue` 继续变基流程；若想完全放弃此次变基恢复原样，运行 `git rebase --abort`。

---

## 追问 2：git reset --soft 和 git reset --mixed 以及 --hard 的核心区别是什么？

**回答要点**：
- `--soft`：仅移动 HEAD 指针，暂存区和工作区代码全保留；
- `--mixed`（默认）：移动 HEAD 指针并清空暂存区，工作区代码仍保留（变为未 add 状态）；
- `--hard`：彻底丢弃暂存区和工作区的所有改动，代码永久丢失，极度危险。
