#!/usr/bin/env node
// 题目内容检查：补充 bank-spec validate 管不到的规则（见 prompts/answer.md）。
//
//   node scripts/check.mjs [--bank <dir>] [--no-run] [--repeat N] [file...]
//
// 不给文件时检查全部题目。Java 小实验会真的编译运行，并逐行比对类后面的 `//` 输出注释。
// 输出 `file:line: [warning|info] CODE 说明`：error 必须修，warning 也要处理，info 只是提示；有 error 时退出码 1。
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { listQuestionFiles, parseQuestion } from './lib.mjs';

const BANNED = ['面试加分项', '加分项', '一定要记住', '灾难性', '如下图', '如图所示', '见下图'];

const HEDGE_RE = /通常|仍可能|可能|一般来说|往往|不一定|未必|大多|某些情况|在一定程度上|但不代表|并不意味着|但不等于|不等于/g;
const LONG_SENTENCE = 70;

const norm = (s) => s.replace(/\s+/g, ' ').trim();

function runJava(code, repeat) {
  const cls = code.match(/public\s+(?:final\s+)?class\s+(\w+)/)?.[1];
  const lines = code.replace(/\s+$/, '').split('\n');
  const expected = [];
  while (lines.length && /^\s*\/\//.test(lines.at(-1))) {
    expected.unshift(norm(lines.pop().replace(/^\s*\/\/\s?/, '').replace(/\s*←.*$/, '')));
  }
  if (!expected.length) return { level: 'warning', code: 'EXPERIMENT_NO_OUTPUT', msg: `${cls} 末尾没有 // 输出注释` };
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'facee-check-'));
  try {
    fs.writeFileSync(path.join(dir, `${cls}.java`), code);
    let first = null;
    for (let i = 0; i < repeat; i++) {
      const r = spawnSync('java', ['-Dstdout.encoding=UTF-8', '-Dfile.encoding=UTF-8', `${cls}.java`], { cwd: dir, encoding: 'utf8', timeout: 60_000 });
      if (r.error?.code === 'ETIMEDOUT') return { level: 'error', code: 'EXPERIMENT_TIMEOUT', msg: `${cls} 运行超过 60 秒` };
      if (r.status !== 0) return { level: 'error', code: 'EXPERIMENT_FAILED', msg: `${cls} 编译或运行失败：${(r.stderr || '').trim().split('\n').slice(0, 3).join(' / ')}` };
      const actual = r.stdout.split('\n').map(norm).filter(Boolean);
      if (first && first.join('\n') !== actual.join('\n')) return { level: 'error', code: 'EXPERIMENT_FLAKY', msg: `${cls} 两次运行输出不同，结果不确定` };
      first = actual;
    }
    if (first.join('\n') !== expected.join('\n')) {
      return { level: 'error', code: 'EXPERIMENT_MISMATCH', msg: `${cls} 实际输出与注释不一致\n    注释：${JSON.stringify(expected)}\n    实际：${JSON.stringify(first)}` };
    }
    return null;
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

export function checkFile(file, { run = true, repeat = 2 } = {}) {
  const diags = [];
  const add = (line, level, code, msg) => diags.push({ file, line, level, code, msg });
  const { meta, sections, lines } = parseQuestion(fs.readFileSync(file, 'utf8'));

  // 要点：核心要点（权重 3）最多两条
  const kp = sections['要点'];
  if (kp) {
    const core = kp.lines.filter((l) => /^- \[(kp\d+)?\|3\]/.test(l.text));
    if (core.length > 2) add(core[2].no, 'error', 'TOO_MANY_CORE_POINTS', `|3 要点有 ${core.length} 条，最多 2 条`);
  }

  // 详解：第一节必须是「先搞懂」；对比表后要有结论
  const ex = sections['详解'];
  if (ex) {
    const subs = ex.lines.filter((l) => /^### /.test(l.text));
    if (!subs.length || !/^### 先搞懂/.test(subs[0].text)) add(subs[0]?.no ?? ex.start, 'error', 'MISSING_PRIMER', '详解的第一节应为「### 先搞懂：…」');
    // 只检查标题含「对比」的小节里的表；参数表、版本表不要求结论
    const ls = ex.lines;
    let heading = '';
    for (let i = 0; i < ls.length; i++) {
      if (/^### /.test(ls[i].text)) heading = ls[i].text;
      if (!heading.includes('对比') || !/^\|(\s*:?-{3,}:?\s*\|)+\s*$/.test(ls[i].text)) continue;
      let j = i + 1;
      while (j < ls.length && ls[j].text.startsWith('|')) j++;
      const after = ls.slice(j, j + 4).map((l) => l.text).filter((t) => t.trim());
      if (!after.some((t) => /^结论：/.test(t))) add(ls[i - 1]?.no ?? ls[i].no, 'warning', 'TABLE_WITHOUT_CONCLUSION', '对比表后没有以「结论：」开头的选型结论');
      i = j;
    }
  }

  // 可读性：主结论别堆限定语，详解别写超长句
  const hedges = (t) => (t.match(HEDGE_RE) || []).length;
  const summary = sections['一句话'];
  if (summary) {
    const text = summary.lines.map((l) => l.text).join('');
    if (hedges(text) >= 2) add(summary.start, 'warning', 'HEDGY_SUMMARY', `一句话里有 ${hedges(text)} 个限定语（${text.match(HEDGE_RE).join('、')}），主结论不直白`);
  }
  for (const l of kp?.lines || []) {
    if (hedges(l.text) >= 2) add(l.no, 'warning', 'HEDGY_POINT', '这条要点堆了多个限定语');
  }
  if (ex) {
    let inCode = false;
    const long = [];
    for (const l of ex.lines) {
      if (/^```/.test(l.text)) inCode = !inCode;
      if (inCode || /^(\||#|```)/.test(l.text) || !l.text.trim()) continue;
      const prose = l.text.replace(/`[^`]*`/g, 'x').replace(/\*\*/g, '');
      for (const s of prose.split(/[。！？；!?]/)) if (s.length > LONG_SENTENCE) long.push(l.no);
    }
    for (const no of [...new Set(long)].slice(0, 3)) add(no, 'warning', 'LONG_SENTENCE', `有超过 ${LONG_SENTENCE} 字的长句，拆成短句`);
  }

  // 口号与图片引用
  lines.forEach((t, i) => {
    for (const w of BANNED) if (t.includes(w)) add(i + 1, 'warning', 'BANNED_PHRASE', `出现「${w}」`);
  });

  // 面试题：要有来源，要关联基础题
  if (['medium', 'hard'].includes(meta.difficulty)) {
    if (!meta.references?.length) add(1, 'warning', 'NO_REFERENCES', 'medium / hard 题没有 references');
    if (!meta.prerequisites?.length) add(1, 'info', 'NO_PREREQUISITES', 'medium / hard 题没有关联前置题（prerequisites）');
  }

  // 小实验：Java 带 main 的类真的跑一遍
  const all = lines.join('\n');
  for (const m of all.matchAll(/^```java\n([\s\S]*?)^```/gm)) {
    const code = m[1];
    if (!/static\s+void\s+main\s*\(/.test(code)) continue;
    const line = all.slice(0, m.index).split('\n').length;
    if (!run) continue;
    const d = runJava(code, repeat);
    if (d) add(line, d.level, d.code, d.msg);
  }
  return diags;
}

export function format(d, base = process.cwd()) {
  const f = path.relative(base, d.file).replaceAll('\\', '/');
  return `${f}:${d.line}: ${d.level === 'error' ? '' : `${d.level} `}${d.code} ${d.msg}`;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const args = process.argv.slice(2);
  let bank = process.cwd();
  let run = true;
  let repeat = 2;
  const files = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--bank') bank = path.resolve(args[++i]);
    else if (args[i] === '--no-run') run = false;
    else if (args[i] === '--repeat') repeat = Number(args[++i]);
    else files.push(path.resolve(args[i]));
  }
  const targets = files.length ? files : listQuestionFiles(bank);
  const diags = targets.flatMap((f) => checkFile(f, { run, repeat }));
  for (const d of diags) console.log(format(d, bank));
  const n = (lv) => diags.filter((d) => d.level === lv).length;
  const errors = n('error');
  console.log(`检查 ${targets.length} 题：${errors} 个错误，${n('warning')} 个警告，${n('info')} 条提示`);
  process.exit(errors ? 1 : 0);
}
