#!/usr/bin/env node
// 快速模式：每道题只调用一次模型写正文，元数据由清单决定，脚本负责组装、补 id、校验和写回。
//
//   node scripts/fast.mjs --plan plans/<name>.yaml [--materials <素材.json>] [--model <provider/id>]
//                         [--thinking medium] [--concurrency 6] [--keys k1,k2 | --limit N] [--dry-run]
//
// 与 gen.mjs（agent 模式，逐题查证、可写实验）的区别：模型不开任何工具，不改任何文件；
// 分类、标签、难度、重要度全部取自清单；前置 / 相关题在全部生成后统一补。
// 每题流程：组装提示词 → 调用一次模型 → 拼成题目文件 → 补要点 / 追问 id → 单题隔离校验（bank-spec + check.mjs）
//          → 不通过则带着错误再调用一次 → 通过后写入 questions/ 并把 id 写回清单。
// 汇总写在 .gen/<runId>/summary.md：失败项、需要核对事实的题（factcheck: yes）。
//
// 外部写作模式（模型不能由脚本直接调用时，如 Claude 子代理）：
//   --prepare <目录> [--batch 40]   把待写的题打包成 batch-XX.md，写作者把回答写到 <目录>/out/<key>.md
//   --ingest  <目录>                读取 out/ 下的回答，组装、校验、写入题库；不通过的生成 fix-XX.md 供下一轮修正
//                                   第二次仍只剩警告的放行，记进 <目录>/ingest-summary.md
import { spawn, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
import { checkFile, format } from './check.mjs';
import { CLI, REPO, YAML, bankMeta, idIndex } from './lib.mjs';

const { newQuestionId } = await import(pathToFileURL(path.join(path.dirname(CLI), 'lib', 'ulid.mjs')).href);
const { fixIdsInSource } = await import(pathToFileURL(path.join(path.dirname(CLI), 'lib', 'ids.mjs')).href);

// ---------- 参数 ----------
const argv = process.argv.slice(2);
const opt = { plan: null, materials: null, model: null, thinking: 'medium', concurrency: 6, keys: null, limit: 0, dryRun: false, prepare: null, ingest: null, batch: 40 };
for (let i = 0; i < argv.length; i++) {
  const a = argv[i];
  if (a === '--plan') opt.plan = argv[++i];
  else if (a === '--materials') opt.materials = argv[++i];
  else if (a === '--model') opt.model = argv[++i];
  else if (a === '--thinking') opt.thinking = argv[++i];
  else if (a === '--concurrency') opt.concurrency = Number(argv[++i]);
  else if (a === '--keys') opt.keys = argv[++i].split(',').map((k) => k.trim()).filter(Boolean);
  else if (a === '--limit') opt.limit = Number(argv[++i]);
  else if (a === '--dry-run') opt.dryRun = true;
  else if (a === '--prepare') opt.prepare = path.resolve(argv[++i]);
  else if (a === '--ingest') opt.ingest = path.resolve(argv[++i]);
  else if (a === '--batch') opt.batch = Number(argv[++i]);
  else throw new Error(`未知参数：${a}`);
}
if (!opt.plan) {
  console.error('用法：node scripts/fast.mjs --plan plans/<name>.yaml [--materials m.json] [--keys ...|--limit N] [--concurrency 6]');
  process.exit(2);
}

const planPath = path.resolve(opt.plan);
const plan = YAML.parse(fs.readFileSync(planPath, 'utf8'));
const model = opt.model || plan.model;
const materials = opt.materials ? JSON.parse(fs.readFileSync(opt.materials, 'utf8')) : {};
const META = bankMeta(REPO);
const existingIds = idIndex(REPO);
const isDone = (it) => it.id && existingIds.has(it.id);
const AGENT = process.env.GEN_AGENT || 'pi';
const CALL_TIMEOUT = 10 * 60_000;
const RATE_LIMIT_WAITS = (process.env.GEN_RATE_LIMIT_WAITS || '2,5,10,20').split(',').map((m) => Number(m) * 60_000);

for (const it of plan.items) {
  if (!it.key || !META.categories.has(it.category) || !['easy', 'medium', 'hard'].includes(it.difficulty)) throw new Error(`清单项不完整：${it.key || it.title}`);
  if (!Array.isArray(it.tags) || !it.tags.length || it.tags.some((t) => !META.tags.has(t))) throw new Error(`${it.key} 的标签缺失或未声明`);
}
let items = plan.items.filter((it) => !isDone(it));
if (opt.keys) {
  const want = new Set(opt.keys);
  items = items.filter((it) => want.has(it.key));
}
if (opt.limit) items = items.slice(0, opt.limit);

if (opt.dryRun) {
  for (const it of items) console.log(`${it.key} [${it.category}/${it.difficulty}/${it.importance ?? '-'}] [${it.tags.join(', ')}] ${materials[it.key] ? '有素材' : '无素材'}  ${it.title}`);
  console.log(`共 ${items.length} 题待生成`);
  process.exit(0);
}

const runId = new Date().toISOString().replace(/[-:]/g, '').replace(/\..*/, '').replace('T', '-');
const logRoot = path.join(REPO, '.gen', `fast-${runId}`);
const tmpRoot = path.join(os.tmpdir(), 'facee-fast', runId);
fs.mkdirSync(logRoot, { recursive: true });
fs.mkdirSync(tmpRoot, { recursive: true });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const log = (it, msg) => console.log(`[${new Date().toTimeString().slice(0, 8)}] ${it.key} ${msg}`);

// ---------- 提示词 ----------
const GUIDE = fs.readFileSync(path.join(REPO, 'prompts', 'write.md'), 'utf8');
const sampleBody = (file) => fs.readFileSync(path.join(REPO, 'prompts', 'examples', file), 'utf8').replace(/^---\n[\s\S]*?\n---\n\s*/, '');
const SAMPLES = {
  easy: sampleBody('basic-why-thread-pool.md'),
  medium: sampleBody('interview-thread-pool-create.md'),
};

function questionBlock(it) {
  const tagText = it.tags.map((t) => META.tags.get(t).name).join('、');
  return [
    `- 标题：${it.title}`,
    `- 领域：${it.category}`,
    `- 知识点：${tagText}（第一个是主要考点）`,
    `- 难度：${it.difficulty}`,
    it.note ? `- 范围说明：${it.note}` : null,
    '',
    materials[it.key] ? `### 导图素材（二手资料，仅供对齐考点）\n\n${materials[it.key]}\n` : null,
  ].filter((l) => l !== null).join('\n');
}

function promptFor(it) {
  return [
    GUIDE,
    '',
    '---',
    '',
    '## 样题（只参考格式、语气和详略，不要照搬内容）',
    '',
    SAMPLES[it.difficulty === 'easy' ? 'easy' : 'medium'],
    '---',
    '',
    '## 现在要写的题',
    '',
    questionBlock(it),
    '按「输出格式」直接输出：四行元数据、空一行、然后从 `## 一句话` 开始的正文。',
  ].join('\n');
}

function fixPrompt(it, prev, errors) {
  return [
    promptFor(it),
    '',
    '---',
    '',
    '## 你上一次的输出没有通过检查',
    '',
    '错误：',
    ...errors.map((e) => `- ${e}`),
    '',
    '上一次的输出：',
    '',
    prev,
    '',
    '请修正上述错误，按同样的格式重新输出完整内容（四行元数据 + 正文）。',
  ].join('\n');
}

// ---------- 调用模型 ----------
function killTree(child) {
  if (process.platform === 'win32') spawnSync('taskkill', ['/pid', String(child.pid), '/T', '/F']);
  else child.kill('SIGKILL');
}

function callOnce(it, text, tag) {
  const file = path.join(tmpRoot, `${it.key}-${tag}.md`);
  fs.writeFileSync(file, text);
  const args = ['-p', '--no-session', '--no-tools', '--no-extensions', '--no-skills', '--no-context-files',
    '--model', model, '--thinking', opt.thinking, `@${path.basename(file)}`];
  return new Promise((resolve) => {
    let out = '';
    // stdin 必须关闭：pi 在非交互模式下会读取管道里的 stdin，不关就一直等
    const child = spawn(AGENT, args, { cwd: tmpRoot, shell: process.platform === 'win32', stdio: ['ignore', 'pipe', 'pipe'] });
    child.stdout.on('data', (d) => { out += d; });
    child.stderr.on('data', (d) => { out += d; });
    const timer = setTimeout(() => killTree(child), CALL_TIMEOUT);
    child.on('close', (code) => { clearTimeout(timer); resolve({ code, out: out.trim() }); });
  });
}

async function call(it, text, tag) {
  for (let w = 0; ; w++) {
    const r = await callOnce(it, text, tag);
    if (r.out.includes('## 一句话')) return r.out;
    const limited = /429|rate.?limit/i.test(r.out);
    if (w >= RATE_LIMIT_WAITS.length || (!limited && w >= 1)) throw new Error(`模型调用失败：${r.out.slice(0, 300) || `exit ${r.code}`}`);
    log(it, limited ? `限流，${RATE_LIMIT_WAITS[w] / 60_000} 分钟后重试` : '输出异常，重试一次');
    await sleep(limited ? RATE_LIMIT_WAITS[w] : 15_000);
  }
}

// ---------- 组装与校验 ----------
const scalar = (s) => YAML.stringify(String(s)).trim();

function assemble(it, id, raw) {
  const text = raw.replace(/^```[a-z]*\n|\n```\s*$/g, '').replace(/\r\n/g, '\n');
  const i = text.indexOf('## 一句话');
  const head = text.slice(0, i);
  const body = text.slice(i).trim();
  const pick = (k) => head.match(new RegExp(`^${k}:\\s*(.+)$`, 'm'))?.[1].trim();
  const TYPES = ['concept', 'scenario', 'coding', 'design', 'behavioral', 'choice'];
  let type = TYPES.includes(pick('type')) ? pick('type') : it.type || 'concept';
  if (type === 'choice' && !/^## 选项/m.test(body)) type = 'concept'; // choice 专指带选项的选择题
  const minutes = Math.max(1, Math.min(15, parseInt(pick('estimatedMinutes'), 10) || 3));
  let appliesTo = [];
  try { appliesTo = YAML.parse(pick('appliesTo') || '[]') || []; } catch { appliesTo = []; }
  if (!Array.isArray(appliesTo)) appliesTo = [];
  appliesTo = appliesTo.map(String).filter(Boolean);
  const factcheck = /^y/i.test(pick('factcheck') || '');
  const fm = [
    '---',
    `id: ${id}`,
    `title: ${scalar(it.title)}`,
    `type: ${type}`,
    `difficulty: ${it.difficulty}`,
    ...(it.importance ? [`importance: ${it.importance}`] : []),
    `category: ${it.category}`,
    `tags: [${it.tags.join(', ')}]`,
    ...(appliesTo.length ? [`appliesTo: [${appliesTo.map((a) => JSON.stringify(a)).join(', ')}]`] : []),
    'source: { name: FaceE, license: CC-BY-4.0 }',
    `estimatedMinutes: ${minutes}`,
    '---',
    '',
  ].join('\n');
  const fixed = fixIdsInSource(`${fm}\n${body}\n`, { newId: () => id });
  return { source: fixed.text, factcheck };
}

function validateOne(it, id, source) {
  const dir = path.join(tmpRoot, `bank-${it.key}`);
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(path.join(dir, 'questions', it.category), { recursive: true });
  fs.copyFileSync(path.join(REPO, 'bank.yaml'), path.join(dir, 'bank.yaml'));
  const file = path.join(dir, 'questions', it.category, `${id}.md`);
  fs.writeFileSync(file, source);
  const r = spawnSync(process.execPath, [CLI, 'validate', '--bank', '.'], { cwd: dir, encoding: 'utf8' });
  const lines = `${r.stdout}${r.stderr}`.trim().split('\n').filter(Boolean);
  // 行号对写作者没用（他们看不到 front matter），改成附上那一行的原文片段
  const srcLines = source.split(/\r?\n/);
  const tidy = (l) => {
    const m = l.match(/^questions\/[^:]+:(\d+):\s*(.*)$/);
    if (!m) return l;
    const text = (srcLines[Number(m[1]) - 1] || '').trim().slice(0, 40);
    return text ? `${m[2]}（位置：「${text}…」）` : m[2];
  };
  const errors = [];
  const warnings = [];
  for (const l of lines.filter((x) => /^questions\//.test(x))) (/ warning /.test(l) ? warnings : errors).push(tidy(l));
  if (r.status !== 0 && !errors.length) errors.push(lines.at(-1) || 'bank-spec validate 失败');
  for (const d of checkFile(file)) {
    if (d.level === 'error') errors.push(tidy(format(d, dir)));
    else if (d.level === 'warning') warnings.push(tidy(format(d, dir)));
  }
  fs.rmSync(dir, { recursive: true, force: true });
  return { errors, warnings };
}

// 写回清单：单进程、同步写，不会与其他任务交错
function recordId(it, id) {
  const doc = YAML.parseDocument(fs.readFileSync(planPath, 'utf8'));
  const node = doc.get('items').items.find((n) => n.get('key') === it.key);
  node.set('id', id);
  fs.writeFileSync(planPath, doc.toString({ lineWidth: 0 }));
  existingIds.set(id, path.join('questions', it.category, `${id}.md`));
}

// ---------- 单题 ----------
async function processItem(it) {
  const started = Date.now();
  const result = { key: it.key, title: it.title, status: 'failed' };
  const id = newQuestionId();
  try {
    let raw = await call(it, promptFor(it), 'a');
    let built = assemble(it, id, raw);
    // 第一次：错误和警告都要修；修正后只剩警告的放行，并记进汇总
    let v = validateOne(it, id, built.source);
    if (v.errors.length || v.warnings.length) {
      const all = [...v.errors, ...v.warnings];
      log(it, `检查发现 ${all.length} 个问题，修正一次`);
      raw = await call(it, fixPrompt(it, raw, all), 'b');
      built = assemble(it, id, raw);
      v = validateOne(it, id, built.source);
    }
    fs.writeFileSync(path.join(logRoot, `${it.key}.raw.md`), raw);
    result.warnings = v.warnings;
    if (v.errors.length) {
      result.error = v.errors.join('\n');
    } else {
      const dest = path.join(REPO, 'questions', it.category, `${id}.md`);
      fs.mkdirSync(path.dirname(dest), { recursive: true });
      fs.writeFileSync(dest, built.source);
      recordId(it, id);
      result.status = 'ok';
      result.factcheck = built.factcheck;
      result.file = path.relative(REPO, dest).replaceAll('\\', '/');
    }
  } catch (e) {
    result.error = String(e.message || e);
  }
  result.seconds = Math.round((Date.now() - started) / 1000);
  log(it, result.status === 'ok' ? `完成 ${result.seconds}s${result.factcheck ? '（含数字 / 版本，待核对）' : ''}` : `失败：${result.error.split('\n')[0].slice(0, 160)}`);
  return result;
}

function writeSummary(results) {
  const ok = results.filter((r) => r.status === 'ok');
  const failed = results.filter((r) => r.status !== 'ok');
  const fc = ok.filter((r) => r.factcheck);
  const warned = ok.filter((r) => r.warnings?.length);
  const avg = ok.length ? Math.round(ok.reduce((s, r) => s + r.seconds, 0) / ok.length) : 0;
  fs.writeFileSync(path.join(logRoot, 'summary.md'), [
    `# 快速模式汇总 ${runId}`, '', `模型：${model}（thinking ${opt.thinking}），并发 ${opt.concurrency}`, '',
    `完成 ${ok.length}，失败 ${failed.length}，平均每题 ${avg} 秒。`, '',
    `## 含具体数字 / 默认值 / 版本行为、待核对（${fc.length}）`, '', ...(fc.length ? fc.map((r) => `- ${r.key} ${r.title}（${r.file}）`) : ['无']), '',
    `## 带警告通过（${warned.length}）`, '', ...(warned.length ? warned.flatMap((r) => [`- ${r.key} ${r.title}`, ...r.warnings.map((w) => `  - ${w}`)]) : ['无']), '',
    `## 失败（${failed.length}）`, '', ...(failed.length ? failed.flatMap((r) => [`### ${r.key} ${r.title}`, '```text', r.error || '', '```', '']) : ['无']),
  ].join('\n'));
}

// ---------- 外部写作模式 ----------
const ATTEMPTS_FILE = (dir) => path.join(dir, 'attempts.json');
const writerHeader = (title, task) => [
  `# ${title}`,
  '',
  `先完整读写作规范 ${path.join(REPO, 'prompts', 'write.md').replaceAll('\\', '/')}，再读两道样题（只参考格式、语气和详略，不要照搬内容；样题开头的 front matter 不用管）：`,
  `- easy：${path.join(REPO, 'prompts', 'examples', 'basic-why-thread-pool.md').replaceAll('\\', '/')}`,
  `- medium / hard：${path.join(REPO, 'prompts', 'examples', 'interview-thread-pool-create.md').replaceAll('\\', '/')}`,
  '',
  task,
  '',
  '规则：不要读其他文件、不要上网、不要运行命令；每题写完就保存，写完全部后回复「已写完 N 题」。',
  '',
].join('\n');

if (opt.prepare) {
  const dir = opt.prepare;
  fs.mkdirSync(path.join(dir, 'out'), { recursive: true });
  const out = path.join(dir, 'out').replaceAll('\\', '/');
  const batches = [];
  for (let i = 0; i < items.length; i += opt.batch) batches.push(items.slice(i, i + opt.batch));
  batches.forEach((b, n) => {
    const name = `batch-${String(n + 1).padStart(2, '0')}.md`;
    const body = [
      writerHeader(`写作批次 ${n + 1}（${b.length} 题）`, `然后逐题写作：每题严格按规范的「输出格式」输出（四行元数据、空一行、从 \`## 一句话\` 开始的正文），保存到 \`${out}/<key>.md\`，文件里只放回答本身。`),
      ...b.map((it) => `## ${it.key}\n\n${questionBlock(it)}\n`),
    ].join('\n');
    fs.writeFileSync(path.join(dir, name), body);
  });
  fs.writeFileSync(ATTEMPTS_FILE(dir), '{}');
  console.log(`已打包 ${items.length} 题为 ${batches.length} 个批次：${dir}`);
  process.exit(0);
}

if (opt.ingest) {
  const dir = opt.ingest;
  const attempts = fs.existsSync(ATTEMPTS_FILE(dir)) ? JSON.parse(fs.readFileSync(ATTEMPTS_FILE(dir), 'utf8')) : {};
  const byKey = new Map(plan.items.map((it) => [it.key, it]));
  const files = fs.existsSync(path.join(dir, 'out')) ? fs.readdirSync(path.join(dir, 'out')).filter((f) => f.endsWith('.md')) : [];
  const done = [], warned = [], fix = [], failed = [], factcheck = [];
  for (const f of files) {
    const key = f.replace(/\.md$/, '');
    const it = byKey.get(key);
    if (!it || isDone(it)) continue;
    const raw = fs.readFileSync(path.join(dir, 'out', f), 'utf8');
    if (!raw.includes('## 一句话')) { fix.push({ it, raw, errors: ['输出里没有 `## 一句话`，格式不对'] }); continue; }
    const id = newQuestionId();
    const built = assemble(it, id, raw);
    const v = validateOne(it, id, built.source);
    // 只有回答内容变了才算新的一次尝试（重复收稿不累加）
    const hash = createHash('sha1').update(raw).digest('hex');
    const prev = typeof attempts[key] === 'object' ? attempts[key] : { n: 0, hash: null };
    const n = prev.hash === hash ? Math.max(prev.n, 1) : prev.n + 1;
    attempts[key] = { n, hash };
    if (!v.errors.length && (!v.warnings.length || n >= 2)) {
      const dest = path.join(REPO, 'questions', it.category, `${id}.md`);
      fs.mkdirSync(path.dirname(dest), { recursive: true });
      fs.writeFileSync(dest, built.source);
      recordId(it, id);
      done.push(it);
      if (v.warnings.length) warned.push({ it, warnings: v.warnings });
      if (built.factcheck) factcheck.push(it);
    } else if (n >= 3) {
      failed.push({ it, errors: [...v.errors, ...v.warnings] });
    } else {
      fix.push({ it, raw, errors: [...v.errors, ...v.warnings] });
    }
  }
  fs.writeFileSync(ATTEMPTS_FILE(dir), JSON.stringify(attempts, null, 1));
  // 修正批次：带着错误和上一版回答，覆盖写回 out/<key>.md
  const old = fs.readdirSync(dir).filter((f) => /^fix-\d+\.md$/.test(f));
  for (const f of old) fs.rmSync(path.join(dir, f));
  const out = path.join(dir, 'out').replaceAll('\\', '/');
  for (let i = 0, n = 1; i < fix.length; i += opt.batch, n++) {
    const b = fix.slice(i, i + opt.batch);
    fs.writeFileSync(path.join(dir, `fix-${String(n).padStart(2, '0')}.md`), [
      writerHeader(`修正批次 ${n}（${b.length} 题）`, `下面每题的上一版回答没通过检查。逐题修正列出的问题，按同样格式重新输出完整回答，覆盖保存到 \`${out}/<key>.md\`。`),
      ...b.map(({ it, raw, errors }) => `## ${it.key}\n\n${questionBlock(it)}\n### 没通过的检查\n\n${errors.map((e) => `- ${e}`).join('\n')}\n\n### 上一版回答\n\n${raw}\n`),
    ].join('\n'));
  }
  const total = existingIds.size;
  fs.appendFileSync(path.join(dir, 'ingest-summary.md'), [
    `## ${new Date().toISOString()}`, '',
    `本次写入 ${done.length}，带警告放行 ${warned.length}，需修正 ${fix.length}（已生成 fix-*.md），放弃 ${failed.length}；题库累计 ${total} / ${plan.items.length}。`, '',
    ...(warned.length ? ['带警告放行：', ...warned.map(({ it, warnings }) => `- ${it.key} ${it.title}：${warnings.join('；')}`), ''] : []),
    ...(factcheck.length ? ['含数字 / 版本、待核对：', ...factcheck.map((it) => `- ${it.key} ${it.title}`), ''] : []),
    ...(failed.length ? ['放弃（三次未通过）：', ...failed.map(({ it, errors }) => `- ${it.key} ${it.title}：${errors.join('；')}`), ''] : []),
  ].join('\n'));
  console.log(`写入 ${done.length}，带警告放行 ${warned.length}，需修正 ${fix.length}，放弃 ${failed.length}；题库累计 ${total} / ${plan.items.length}`);
  process.exit(0);
}

// ---------- 主流程 ----------
console.log(`fast ${runId}：${items.length} 题，模型 ${model}（thinking ${opt.thinking}），并发 ${opt.concurrency}`);
const results = [];
const queue = [...items];
async function worker(n) {
  await sleep(n * 3000); // 错开启动，避免同时打满接口
  while (queue.length) {
    results.push(await processItem(queue.shift()));
    writeSummary(results);
  }
}
await Promise.all(Array.from({ length: Math.max(1, opt.concurrency) }, (_, n) => worker(n)));
writeSummary(results);
const okN = results.filter((r) => r.status === 'ok').length;
console.log(`完成：成功 ${okN}，失败 ${results.length - okN}。汇总：${path.relative(REPO, path.join(logRoot, 'summary.md'))}`);
process.exit(results.length - okN ? 1 : 0);
