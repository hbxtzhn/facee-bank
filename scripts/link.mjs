#!/usr/bin/env node
// 把清单里的前置关系（按 key 写）落到题目文件的 prerequisites（按题目 id 写）。
//
//   node scripts/link.mjs --plan plans/<name>.yaml [--write]
//
// 清单项的 prerequisites 是 key 列表；只有双方都已生成（有 id 且文件存在）的关系才会写入。
// 不加 --write 只统计。写入只改题目 front matter 的 prerequisites 一行，其余内容不动。
import fs from 'node:fs';
import path from 'node:path';
import { REPO, YAML, idIndex } from './lib.mjs';

const argv = process.argv.slice(2);
const planArg = argv[argv.indexOf('--plan') + 1];
const write = argv.includes('--write');
if (!argv.includes('--plan') || !planArg) {
  console.error('用法：node scripts/link.mjs --plan plans/<name>.yaml [--write]');
  process.exit(2);
}

const plan = YAML.parse(fs.readFileSync(planArg, 'utf8'));
const ids = idIndex(REPO);
const idOf = new Map(plan.items.filter((it) => it.id && ids.has(it.id)).map((it) => [it.key, it.id]));
let changed = 0, links = 0, pending = 0;
for (const it of plan.items) {
  const id = idOf.get(it.key);
  if (!id) continue;
  const want = (it.prerequisites || []).map((k) => idOf.get(k)).filter(Boolean);
  pending += (it.prerequisites || []).length - want.length;
  links += want.length;
  const file = path.join(REPO, ids.get(id));
  const src = fs.readFileSync(file, 'utf8');
  const line = want.length ? `prerequisites: [${want.join(', ')}]` : null;
  let out;
  if (/^prerequisites:.*$/m.test(src)) out = line ? src.replace(/^prerequisites:.*$/m, line) : src.replace(/^prerequisites:.*\r?\n/m, '');
  else out = line ? src.replace(/^(tags:.*)$/m, `$1\n${line}`) : src;
  if (out !== src) {
    changed++;
    if (write) fs.writeFileSync(file, out);
  }
}
console.log(`前置关系 ${links} 条（另有 ${pending} 条因对方未生成暂不写入）；${write ? '已改' : '需改'} ${changed} 个题目文件`);
