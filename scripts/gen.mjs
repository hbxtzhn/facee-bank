#!/usr/bin/env node
// 批量生成答案：按题目清单逐题调用 pi，自动检查、自动修一轮、合并回题库。
//
//   node scripts/gen.mjs --plan plans/<name>.yaml [--model <provider/id>] [--concurrency 1]
//                        [--stagger 30] [--fix-rounds 1] [--only <key 或标题片段>] [--keys k1,k2] [--limit N] [--dry-run]
//
// 清单每项用稳定的 key 标识；生成并合并后，把题目 id 写回清单的 id 字段，之后按 id 判断是否已生成。
// 每题在系统临时目录的独立副本里生成，互不干扰；检查通过、元数据与清单一致才合并回仓库（不提交）。
// 生成期间分类和标签表冻结：不允许改 bank.yaml，题目只能用清单给定的标签。
// 日志、交付汇报和汇总写在 .gen/<runId>/ 下；summary.md 汇总缺少的前置题和难度调整。
import { spawn, spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { checkFile, format } from './check.mjs';
import { CLI, REPO, YAML, bankMeta, idIndex, parseQuestion, validate } from './lib.mjs';

// ---------- 参数 ----------
const argv = process.argv.slice(2);
const opt = { concurrency: 1, stagger: 30, fixRounds: 1, dryRun: false, only: null, keys: null, limit: 0, model: null, plan: null };
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === '--plan') opt.plan = argv[++i];
  else if (a === '--model') opt.model = argv[++i];
  else if (a === '--concurrency') opt.concurrency = Number(argv[++i]);
  else if (a === '--stagger') opt.stagger = Number(argv[++i]);
  else if (a === '--fix-rounds') opt.fixRounds = Number(argv[++i]);
  else if (a === '--only') opt.only = argv[++i];
  else if (a === '--limit') opt.limit = Number(argv[++i]);
  else if (a === '--keys') opt.keys = argv[++i].split(',').map((k) => k.trim()).filter(Boolean);
  else if (a === '--dry-run') opt.dryRun = true;
  else throw new Error(`未知参数：${a}`);
}
if (!opt.plan) {
  console.error('用法：node scripts/gen.mjs --plan plans/<name>.yaml [--model ...] [--concurrency 1] [--dry-run]');
  process.exit(2);
}

const planPath = path.resolve(opt.plan);
const plan = YAML.parse(fs.readFileSync(planPath, 'utf8'));
const model = opt.model || plan.model;
if (!model) throw new Error('清单里没有 model，也没有传 --model');
const AGENT = process.env.GEN_AGENT || 'pi';
const AGENT_TIMEOUT = 40 * 60_000;
// 限流后的等待（分钟），可用 GEN_RATE_LIMIT_WAITS="2,5,10,20" 覆盖
const RATE_LIMIT_WAITS = (process.env.GEN_RATE_LIMIT_WAITS || '2,5,10,20').split(',').map((m) => Number(m) * 60_000);

const runId = new Date().toISOString().replace(/[-:]/g, '').replace(/\..*/, '').replace('T', '-');
const logRoot = path.join(REPO, '.gen', runId);
const workRoot = path.join(os.tmpdir(), 'facee-gen', runId);

const META = bankMeta(REPO);
const DIFFS = ['easy', 'medium', 'hard'];
const existingIds = idIndex(REPO);
const isDone = (it) => it.id && existingIds.has(it.id);

const allItems = (plan.items || []).map((it, i) => ({ ...it, idx: i + 1 }));
const seenKeys = new Set();
for (const it of allItems) {
  const where = `第 ${it.idx} 项（${it.key || it.title}）`;
  if (!it.key || seenKeys.has(it.key)) throw new Error(`${where}缺少 key 或 key 重复`);
  seenKeys.add(it.key);
  if (!it.title || !META.categories.has(it.category)) throw new Error(`${where}缺 title，或分类未在 bank.yaml 声明`);
  if (!DIFFS.includes(it.difficulty)) throw new Error(`${where}difficulty 必须是 easy / medium / hard`);
  if (!Array.isArray(it.tags) || it.tags.length < 1 || it.tags.length > 3) throw new Error(`${where}tags 必须是 1–3 个`);
  if (it.importance !== undefined && ![1, 2, 3].includes(it.importance)) throw new Error(`${where}importance 必须是 1 / 2 / 3`);
  const unknown = it.tags.filter((t) => !META.tags.has(t));
  if (unknown.length) throw new Error(`${where}标签未在 bank.yaml 声明：${unknown.join(', ')}`);
}
let items = allItems.filter((it) => !opt.only || it.key === opt.only || it.title.includes(opt.only));
if (opt.keys) {
  const missing = opt.keys.filter((k) => !seenKeys.has(k));
  if (missing.length) throw new Error(`清单里没有这些 key：${missing.join(', ')}`);
  const want = new Set(opt.keys);
  items = items.filter((it) => want.has(it.key));
}
if (opt.limit) items = items.filter((it) => !isDone(it)).slice(0, opt.limit);

if (opt.dryRun) {
  for (const it of items) console.log(`${it.key}  ${isDone(it) ? '已生成，跳过' : '待生成'}  [${it.category}/${it.difficulty}] [${it.tags.join(', ')}] ${it.title}`);
  process.exit(0);
}

fs.mkdirSync(logRoot, { recursive: true });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const log = (it, msg) => console.log(`[${new Date().toTimeString().slice(0, 8)}] ${it.key} ${msg}`);

// ---------- 工作副本 ----------
const COPY = ['AGENTS.md', 'bank.yaml', 'prompts', 'questions', 'scripts'];

function snapshot(dir) {
  const files = new Map();
  const walk = (rel) => {
    const abs = path.join(dir, rel);
    if (!fs.existsSync(abs)) return;
    if (fs.statSync(abs).isDirectory()) {
      for (const e of fs.readdirSync(abs)) walk(path.join(rel, e));
    } else {
      // 只读文本；资源文件（图片等）暂不支持，记成占位串，交给变更检查报错
      const r = rel.replaceAll('\\', '/');
      files.set(r, /\.(md|ya?ml)$/.test(r) ? fs.readFileSync(abs, 'utf8') : `<binary ${fs.statSync(abs).size}>`);
    }
  };
  for (const c of ['bank.yaml', 'questions']) walk(c);
  return files;
}

function prepareWorkdir(it) {
  const wd = path.join(workRoot, it.key);
  fs.rmSync(wd, { recursive: true, force: true });
  fs.mkdirSync(path.join(wd, '.gen'), { recursive: true });
  for (const c of COPY) {
    const src = path.join(REPO, c);
    if (fs.existsSync(src)) fs.cpSync(src, path.join(wd, c), { recursive: true });
  }
  return { wd, base: snapshot(wd) };
}

// ---------- 调用 agent ----------
function promptFor(it) {
  const tagText = it.tags.map((t) => `${t}（${META.tags.get(t).name}）`).join('、');
  return [
    '为下面这道题生成答案文件，按 AGENTS.md 和 prompts/answer.md 执行。',
    '',
    `title: ${it.title}`,
    `category: ${it.category}`,
    `tags: [${it.tags.join(', ')}]   # ${tagText}；第一个是主要考点，必须原样使用`,
    `difficulty: ${it.difficulty}   # 初值，按内容判断不合适可以改，在汇报里说明`,
    it.importance ? `importance: ${it.importance}   # 清单统一评定，原样使用` : null,
    it.type ? `type: ${it.type}` : null,
    it.note ? `note: ${it.note}` : null,
    '',
    '环境：',
    `- bank-spec CLI 在本机的路径是 ${CLI.replaceAll('\\', '/')}（AGENTS.md 里的相对路径在这里不适用）。`,
    `- 小实验如需 Docker，容器名加后缀 -${it.key}，用完删除。`,
    '- 只新增本题一个文件；可以改已有题目的 related / prerequisites 两行（建立关联）。不要改 bank.yaml，不要改其他内容。',
  ].filter((l) => l !== null).join('\n');
}

function killTree(child) {
  if (process.platform === 'win32') spawnSync('taskkill', ['/pid', String(child.pid), '/T', '/F']);
  else child.kill('SIGKILL');
}

let callNo = 0;
function callAgent(it, wd, message, cont) {
  const n = ++callNo;
  const msgFile = `.gen/msg-${n}.md`;
  fs.writeFileSync(path.join(wd, msgFile), message);
  const out = fs.openSync(path.join(wd, '.gen', 'run.jsonl'), 'a');
  const err = fs.openSync(path.join(wd, '.gen', 'run.err'), 'a');
  const args = ['-p', '--mode', 'json', '--session-dir', '.gen/session', '--model', model, ...(cont ? ['-c'] : []), `@${msgFile}`];
  return new Promise((resolve) => {
    const child = spawn(AGENT, args, { cwd: wd, shell: process.platform === 'win32', stdio: ['ignore', out, err], env: { ...process.env, BANK_SPEC_CLI: CLI } });
    const timer = setTimeout(() => { killTree(child); }, AGENT_TIMEOUT);
    child.on('close', (code) => {
      clearTimeout(timer);
      fs.closeSync(out);
      fs.closeSync(err);
      resolve(code);
    });
  });
}

/** 读最后一次调用的结果：最终回复文本、是否以错误结束、是否限流。 */
function lastOutcome(wd) {
  const file = path.join(wd, '.gen', 'run.jsonl');
  let text = '';
  let error = null;
  if (!fs.existsSync(file)) return { text, error: 'no output' };
  const lines = fs.readFileSync(file, 'utf8').split('\n');
  for (const l of lines) {
    let e;
    try { e = JSON.parse(l); } catch { continue; }
    if (e.type === 'session') { text = ''; error = null; }
    if (e.type !== 'message_end' || e.message?.role !== 'assistant') continue;
    const m = e.message;
    if (m.stopReason === 'error') error = m.errorMessage || 'unknown error';
    else {
      error = null;
      const t = (m.content || []).filter((c) => c.type === 'text').map((c) => c.text).join('');
      if (t.trim()) text = t;
    }
  }
  return { text, error, rateLimited: !!error && /429|rate.?limit/i.test(error) };
}

async function runAgent(it, wd, message, cont) {
  let waits = 0;
  let otherErrors = 0;
  let first = true;
  for (;;) {
    await callAgent(it, wd, first ? message : '上一次调用因接口错误中断了。请检查工作区当前状态，继续完成原任务。', cont || !first);
    first = false;
    const r = lastOutcome(wd);
    if (!r.error) return r;
    if (r.rateLimited && waits < RATE_LIMIT_WAITS.length) {
      log(it, `限流，${RATE_LIMIT_WAITS[waits] / 60_000} 分钟后继续`);
      await sleep(RATE_LIMIT_WAITS[waits++]);
    } else if (!r.rateLimited && otherErrors < 1) {
      otherErrors++;
      log(it, `接口错误，重试一次：${r.error.slice(0, 120)}`);
      await sleep(RATE_LIMIT_WAITS[0] / 4);
    } else {
      return r;
    }
  }
}

// ---------- 变更检查 ----------
function diffWorkdir(wd, base) {
  const now = snapshot(wd);
  const added = [];
  const modified = [];
  const problems = [];
  for (const [rel, content] of now) {
    if (!base.has(rel)) {
      if (!rel.startsWith('questions/')) problems.push(`新增了题目目录以外的文件：${rel}`);
      else if (!rel.endsWith('.md')) problems.push(`新增了非 Markdown 文件（资源文件暂不支持）：${rel}`);
      else added.push(rel);
    } else if (base.get(rel) !== content) {
      modified.push(rel);
      if (rel === 'bank.yaml') problems.push('改动了 bank.yaml（生成期间分类和标签表冻结，缺标签请在汇报里提出）');
      if (rel.startsWith('questions/')) {
        const strip = (s) => s.replace(/\r\n/g, '\n').replace(/^(related|prerequisites):.*\n/gm, '');
        if (strip(base.get(rel)) !== strip(content)) problems.push(`改动了已有题目 related / prerequisites 以外的内容：${rel}`);
      }
    }
  }
  for (const rel of base.keys()) if (!now.has(rel)) problems.push(`删除了文件：${rel}`);
  return { added, modified, problems, now };
}

function checkWorkdir(it, wd, base) {
  const d = diffWorkdir(wd, base);
  const msgs = [...d.problems];
  if (d.added.length !== 1) msgs.push(`应新增恰好 1 个题目文件，实际 ${d.added.length} 个`);
  const v = validate(wd);
  if (!v.ok) msgs.push(`bank-spec validate 未通过：\n${v.out}`);
  const diags = d.added.flatMap((rel) => checkFile(path.join(wd, rel)));
  for (const x of diags.filter((x) => x.level !== 'info')) msgs.push(format(x, wd));
  const notes = diags.filter((x) => x.level === 'info').map((x) => format(x, wd));
  // 元数据必须和清单一致；难度允许调整、标题改动都记录下来供复核
  let meta = null;
  if (d.added.length === 1) {
    meta = parseQuestion(d.now.get(d.added[0])).meta;
    if (meta.category !== it.category) msgs.push(`分类应为 ${it.category}，实际 ${meta.category}`);
    const got = meta.tags || [];
    if (got.join(',') !== it.tags.join(',')) msgs.push(`标签应为 [${it.tags.join(', ')}]（顺序也要一致），实际 [${got.join(', ')}]`);
    if (it.importance && meta.importance !== it.importance) msgs.push(`importance 应为 ${it.importance}（清单统一评定），实际 ${meta.importance}`);
    if (meta.difficulty !== it.difficulty) notes.push(`难度调整：${it.difficulty} → ${meta.difficulty}`);
    if (meta.title !== it.title) notes.push(`标题改动：${it.title} → ${meta.title}`);
  }
  return { ...d, msgs, notes, meta };
}

// 合并成功后把题目 id 写回清单（在合并锁内串行执行，保留清单原有格式和注释）
function recordId(it, id) {
  const doc = YAML.parseDocument(fs.readFileSync(planPath, 'utf8'));
  const node = doc.get('items').items.find((n) => n.get('key') === it.key);
  if (!node) throw new Error(`清单里找不到 ${it.key}`);
  node.set('id', id);
  fs.writeFileSync(planPath, doc.toString({ lineWidth: 0 }));
  existingIds.set(id, true);
}

// ---------- 合并回仓库（串行） ----------
let mergeLock = Promise.resolve();
function mergeBack(it, wd, base, diff) {
  const job = mergeLock.then(() => {
    const written = new Map(); // rel -> 合并前内容（null 表示原来不存在）
    const restore = () => {
      for (const [rel, old] of written) {
        const p = path.join(REPO, rel);
        if (old === null) fs.rmSync(p, { force: true });
        else fs.writeFileSync(p, old);
      }
    };
    try {
      for (const rel of diff.added) {
        const p = path.join(REPO, rel);
        if (fs.existsSync(p)) throw new Error(`仓库里已有同名文件：${rel}`);
        fs.mkdirSync(path.dirname(p), { recursive: true });
        written.set(rel, null);
        fs.writeFileSync(p, diff.now.get(rel));
      }
      for (const rel of diff.modified) {
        const p = path.join(REPO, rel);
        const ours = fs.readFileSync(p, 'utf8');
        written.set(rel, ours);
        if (ours === base.get(rel)) {
          fs.writeFileSync(p, diff.now.get(rel));
          continue;
        }
        // 别的题已经改过这个文件：三方合并
        const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'facee-merge-'));
        const [fb, ft] = [path.join(tmp, 'base'), path.join(tmp, 'theirs')];
        fs.writeFileSync(fb, base.get(rel));
        fs.writeFileSync(ft, diff.now.get(rel));
        const r = spawnSync('git', ['merge-file', '-p', p, fb, ft], { encoding: 'utf8' });
        fs.rmSync(tmp, { recursive: true, force: true });
        if (r.status !== 0) throw new Error(`合并冲突：${rel}`);
        fs.writeFileSync(p, r.stdout);
      }
      const v = validate(REPO);
      if (!v.ok) throw new Error(`合并后仓库校验未通过：\n${v.out}`);
      recordId(it, diff.meta.id);
      return { ok: true };
    } catch (e) {
      restore();
      return { ok: false, error: e.message };
    }
  });
  mergeLock = job.then(() => {}, () => {});
  return job;
}

// ---------- 单题流程 ----------
async function processItem(it) {
  const dir = path.join(logRoot, it.key);
  fs.mkdirSync(dir, { recursive: true });
  const result = { idx: it.idx, key: it.key, title: it.title, status: 'failed', files: [], notes: [], report: '' };
  if (isDone(it)) {
    log(it, `已生成（${existingIds.get(it.id)}），跳过`);
    return { ...result, status: 'skipped' };
  }
  const { wd, base } = prepareWorkdir(it);
  const started = Date.now();
  log(it, `开始：${it.title}`);
  try {
    let r = await runAgent(it, wd, promptFor(it), false);
    let chk = checkWorkdir(it, wd, base);
    for (let round = 0; chk.msgs.length && !r.error && round < opt.fixRounds; round++) {
      log(it, `自动检查发现 ${chk.msgs.length} 个问题，进入修复第 ${round + 1} 轮`);
      const fix = ['自动检查发现以下问题，请修复，重新跑 validate 和 scripts/check.mjs，然后重新给出完整的交付汇报：', '', ...chk.msgs.map((m) => `- ${m}`)].join('\n');
      r = await runAgent(it, wd, fix, true);
      chk = checkWorkdir(it, wd, base);
    }
    result.report = r.text;
    result.notes = chk.notes;
    fs.writeFileSync(path.join(dir, 'report.md'), r.text || '');
    fs.writeFileSync(path.join(dir, 'check.txt'), [...chk.msgs, ...chk.notes].join('\n'));
    if (r.error) {
      result.error = `接口错误：${r.error}`;
    } else if (chk.msgs.length) {
      result.error = `检查未通过：\n${chk.msgs.join('\n')}`;
    } else {
      const m = await mergeBack(it, wd, base, chk);
      if (m.ok) {
        result.status = 'merged';
        result.files = [...chk.added, ...chk.modified];
      } else {
        result.error = m.error;
      }
    }
  } catch (e) {
    result.error = String(e?.stack || e);
  } finally {
    for (const f of ['run.jsonl', 'run.err']) {
      const src = path.join(wd, '.gen', f);
      if (fs.existsSync(src)) fs.copyFileSync(src, path.join(dir, f));
    }
    result.minutes = ((Date.now() - started) / 60_000).toFixed(1);
  }
  if (result.status === 'merged') fs.rmSync(wd, { recursive: true, force: true });
  else result.workdir = wd;
  log(it, result.status === 'merged' ? `完成，用时 ${result.minutes} 分钟` : `失败：${result.error.replace(/\n+/g, ' / ').slice(0, 200)}（工作副本保留在 ${wd}）`);
  return result;
}

// ---------- 汇总 ----------
function missingFoundations(report) {
  const m = report.match(/缺少的前置题[：:]?([\s\S]*?)(?=\n\s*\n?(?:难度调整|事实清单|实验|校验)|$)/);
  const body = (m?.[1] || '').trim();
  return !body || /^无[。.]?$/.test(body) ? '' : body;
}

function writeSummary(results) {
  const rows = results.map((r) => `| ${r.key} | ${r.title} | ${r.status} | ${r.minutes ?? ''} | ${(r.files || []).join('<br>')} |`);
  const gaps = results.map((r) => [r, missingFoundations(r.report || '')]).filter(([, g]) => g);
  const adjust = results.flatMap((r) => (r.notes || []).filter((n) => /^(难度调整|标题改动)/.test(n)).map((n) => `- ${r.key} ${r.title}：${n}`));
  const failed = results.filter((r) => r.status === 'failed');
  const md = [
    `# 生成汇总 ${runId}`,
    '',
    `模型：${model}`,
    '',
    '| key | 题目 | 结果 | 分钟 | 文件 |',
    '|---|---|---|---|---|',
    ...rows,
    '',
    '## 缺少的前置题',
    '',
    ...(gaps.length ? gaps.flatMap(([r, g]) => [`### ${r.key} ${r.title}`, g, '']) : ['无', '']),
    '## 难度调整与标题改动（请复核）',
    '',
    ...(adjust.length ? [...adjust, ''] : ['无', '']),
    '## 失败项',
    '',
    ...(failed.length ? failed.flatMap((r) => [`### ${r.key} ${r.title}`, '```text', r.error || '', '```', `工作副本：${r.workdir || ''}`, '']) : ['无', '']),
  ].join('\n');
  fs.writeFileSync(path.join(logRoot, 'summary.md'), md);
}

// ---------- 主流程 ----------
const results = [];
const queue = [...items];
let started = 0;
async function worker() {
  while (queue.length) {
    const it = queue.shift();
    if (opt.concurrency > 1 && started++ > 0 && opt.stagger) await sleep(opt.stagger * 1000);
    results.push(await processItem(it));
    writeSummary(results.sort((a, b) => a.idx - b.idx));
  }
}
console.log(`run ${runId}：${items.length} 题，模型 ${model}，并发 ${opt.concurrency}`);
await Promise.all(Array.from({ length: Math.max(1, opt.concurrency) }, worker));
writeSummary(results.sort((a, b) => a.idx - b.idx));
const count = (s) => results.filter((r) => r.status === s).length;
console.log(`完成：合并 ${count('merged')}，跳过 ${count('skipped')}，失败 ${count('failed')}。汇总：${path.relative(REPO, path.join(logRoot, 'summary.md'))}`);
process.exit(count('failed') ? 1 : 0);
