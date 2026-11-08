// 生成脚本与检查脚本共用的工具函数。
import { spawnSync } from 'node:child_process';
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

// bank-spec CLI 在同级的 App 仓库；可用环境变量 BANK_SPEC_CLI 覆盖。
export const CLI = path.resolve(process.env.BANK_SPEC_CLI || path.join(REPO, '..', 'facee', 'packages', 'bank-spec', 'cli.mjs'));

// yaml 包跟随 CLI，从 App 仓库的 node_modules 解析，题库本身不装依赖。
export const YAML = createRequire(CLI)('yaml');

export function runCli(args, cwd) {
  const r = spawnSync(process.execPath, [CLI, ...args], { cwd, encoding: 'utf8' });
  return { code: r.status, out: `${r.stdout || ''}${r.stderr || ''}`.trim() };
}

export function validate(bankDir) {
  const r = runCli(['validate', '--bank', '.'], bankDir);
  const lines = r.out.split('\n').filter(Boolean);
  const warnings = lines.filter((l) => / warning /.test(l));
  return { ok: r.code === 0 && warnings.length === 0, code: r.code, out: r.out, summary: lines.at(-1) || '' };
}

/** 拆出 front matter 和各 `## ` 段落；行号从 1 开始。 */
export function parseQuestion(text) {
  const norm = text.replace(/\r\n/g, '\n');
  const m = norm.match(/^---\n([\s\S]*?)\n---\n/);
  const meta = m ? YAML.parse(m[1]) || {} : {};
  const lines = norm.split('\n');
  const sections = {};
  let cur = null;
  lines.forEach((line, i) => {
    const h = line.match(/^## (\S.*)$/);
    if (h && (!m || i >= m[0].split('\n').length - 1)) {
      cur = { name: h[1].trim(), start: i + 1, lines: [] };
      sections[cur.name] = cur;
    } else if (cur) {
      cur.lines.push({ no: i + 1, text: line });
    }
  });
  return { meta, sections, lines };
}

export function listQuestionFiles(bankDir) {
  const root = path.join(bankDir, 'questions');
  const out = [];
  const walk = (d) => {
    if (!fs.existsSync(d)) return;
    for (const e of fs.readdirSync(d, { withFileTypes: true })) {
      const p = path.join(d, e.name);
      if (e.isDirectory()) walk(p);
      else if (e.name.endsWith('.md')) out.push(p);
    }
  };
  walk(root);
  return out;
}

export function titleIndex(bankDir) {
  const map = new Map();
  for (const f of listQuestionFiles(bankDir)) {
    const t = fs.readFileSync(f, 'utf8').match(/^title:\s*"?(.*?)"?\s*$/m);
    if (t) map.set(t[1].trim(), path.relative(bankDir, f).replaceAll('\\', '/'));
  }
  return map;
}

/** 题目 id → 相对路径。 */
export function idIndex(bankDir) {
  const map = new Map();
  for (const f of listQuestionFiles(bankDir)) {
    const m = fs.readFileSync(f, 'utf8').match(/^id:\s*(q_[0-9A-Z]+)\s*$/m);
    if (m) map.set(m[1], path.relative(bankDir, f).replaceAll('\\', '/'));
  }
  return map;
}

/** bank.yaml 里声明的分类和标签。 */
export function bankMeta(bankDir) {
  const b = YAML.parse(fs.readFileSync(path.join(bankDir, 'bank.yaml'), 'utf8'));
  return {
    categories: new Set((b.categories || []).map((c) => c.id)),
    tags: new Map((b.tags || []).map((t) => [t.id, t])),
  };
}
