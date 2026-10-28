### 一句话总结

最常用的方案是 **`git rebase -i HEAD~N`（交互式变基，将后续提交标记为 `squash` 或 `s`）**；或使用 **`git reset --soft <base-commit>` 一键将所有改动撤回暂存区后统一 `git commit`**；在向主干合并 PR 时，也可直接通过 GitHub/GitLab 网页端勾选 **Squash and merge** 实现一键压缩。

---

### 详细回答

#### 1. 方案一：交互式变基（git rebase -i，最经典可控）
- 执行命令查看最近 3 次提交：`git rebase -i HEAD~3`；
- 在弹出的 Vim 编辑器中，保留第一个提交为 `pick`，将其余后续提交的指令改为 `squash`（或简写为 `s`）：
  ```text
  pick a1b2c3d feat: 完成用户登录组件骨架
  squash e4f5g6h fix: 修复输入框样式
  squash i7j8k9l style: 调整按钮边距
  ```
- 保存退出后，编辑最终合并后的单一 Commit Message 并保存。

#### 2. 方案二：git reset --soft（极速无脑方案）
- 将 HEAD 指针重置回最初的分支基线，但**完全保留工作区与暂存区的所有代码变更**：
  ```bash
  git reset --soft origin/main
  git commit -m "feat: 完成用户登录全套功能与样式规范"
  ```

#### 3. 方案三：git merge --squash（合并时压缩）
- 在 master 分支执行：`git merge --squash feature-branch`，将特性分支的所有提交打平为一个未提交的改动，手动 commit 即可。

---

### 核心代码片段（极简记法）

```bash
# 极速压缩最近 3 次 commit
git reset --soft HEAD~3
git commit -m "feat: 规范合并后的完整提交说明"
```

---

### 面试加分项

- **黄金安全法则（Public Branch Rule）**：压缩提交本质是在**改写 Git 提交历史**。绝对不要在已经推送到公共主干分支（如 `main` / `master`）的代码上执行 `rebase` 或 `reset` 并强推（`--force`），这会导致协同其他开发者的本地历史全部错乱！只允许在个人的私有特性分支（Feature Branch）上使用。
