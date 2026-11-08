#!/usr/bin/env node
// 把清单里的学习路线写进 bank.yaml 的 collections，并检查路线顺序与前置关系是否一致。
//
//   node scripts/routes.mjs --plan plans/<name>.yaml [--write]
//
// 路线在清单里按 key 列出题目；只有已生成（清单项有 id 且题目存在）的题会写进专题。
// 不加 --write 只做检查和统计。检查项：
//   - error：路线里 A 以 B 为前置，B 却排在 A 后面
//   - info ：A 的前置题不在同一条路线里（读者要跳出路线去学）；路线里还有未生成的题
import fs from 'node:fs';
import path from 'node:path';
import { REPO, YAML, idIndex, parseQuestion } from './lib.mjs';

const argv = process.argv.slice(2);
const planArg = argv[argv.indexOf('--plan') + 1];
const write = argv.includes('--write');
if (!argv.includes('--plan') || !planArg) {
  console.error('用法：node scripts/routes.mjs --plan plans/<name>.yaml [--write]');
  process.exit(2);
}

const plan = YAML.parse(fs.readFileSync(planArg, 'utf8'));
const ids = idIndex(REPO);
const byKey = new Map((plan.items || []).map((it) => [it.key, it]));
const prereqOf = new Map();
const titleOf = new Map();
for (const [id, rel] of ids) {
  const { meta } = parseQuestion(fs.readFileSync(path.join(REPO, rel), 'utf8'));
  prereqOf.set(id, meta.prerequisites || []);
  titleOf.set(id, meta.title);
}

const collections = [];
let errors = 0;
for (const r of plan.routes || []) {
  const members = [];
  let pending = 0;
  for (const key of r.questions) {
    const it = byKey.get(key);
    if (!it) { console.log(`${r.id}: error 路线引用了清单里不存在的 key ${key}`); errors++; continue; }
    if (it.id && ids.has(it.id)) members.push(it.id);
    else pending++;
  }
  const pos = new Map(members.map((id, i) => [id, i]));
  const outside = new Set();
  for (const id of members) {
    for (const p of prereqOf.get(id) || []) {
      if (!pos.has(p)) { outside.add(p); continue; }
      if (pos.get(p) > pos.get(id)) {
        console.log(`${r.id}: error 「${titleOf.get(id)}」以「${titleOf.get(p)}」为前置，但前置题排在后面`);
        errors++;
      }
    }
  }
  if (outside.size) console.log(`${r.id}: info 有 ${outside.size} 道前置题不在本路线：${[...outside].map((p) => titleOf.get(p) || p).slice(0, 5).join('、')}${outside.size > 5 ? '…' : ''}`);
  if (pending) console.log(`${r.id}: info 还有 ${pending} 道题未生成，暂不写入`);
  console.log(`${r.id}: ${members.length} 道已生成`);
  if (members.length) {
    collections.push({ id: r.id, name: r.name, description: r.description || `按思维导图顺序，完整过一遍${r.name.replace(/路线$/, '')}`, questions: members });
  }
}

if (write) {
  const file = path.join(REPO, 'bank.yaml');
  const doc = YAML.parseDocument(fs.readFileSync(file, 'utf8'));
  const routeIds = new Set((plan.routes || []).map((r) => r.id));
  const others = (doc.toJS().collections || []).filter((c) => !routeIds.has(c.id)); // 保留手工维护的专题
  doc.set('collections', doc.createNode([...others, ...collections]));
  fs.writeFileSync(file, doc.toString({ lineWidth: 0 }));
  console.log(`已写入 bank.yaml：${collections.length} 条路线专题（另保留 ${others.length} 个手工专题）`);
}
process.exit(errors ? 1 : 0);
