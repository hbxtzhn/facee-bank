#!/usr/bin/env node
// 把 plans/tags.yaml（标签定义的源头）同步到 bank.yaml 的 tags。
//
//   node scripts/tags.mjs [--write] [--with-meta]
//
// 默认只检查：别名冲突（全库唯一、忽略大小写；不得与任何标签的 id / name 相同）、父标签存在、层级不超过两层。
// --write 写入 bank.yaml；--with-meta 同时写 description 和 aliases（需要支持这两个字段的 bank-spec）。
import fs from 'node:fs';
import path from 'node:path';
import { REPO, YAML } from './lib.mjs';

const write = process.argv.includes('--write');
const withMeta = process.argv.includes('--with-meta');
const tags = YAML.parse(fs.readFileSync(path.join(REPO, 'plans', 'tags.yaml'), 'utf8'));

const errors = [];
const ids = new Map(tags.map((t) => [t.id, t]));
const norm = (s) => String(s).trim().toLowerCase();
const names = new Set(tags.flatMap((t) => [norm(t.id), norm(t.name)]));
const seen = new Map();
for (const t of tags) {
  if (!/^[a-z0-9][a-z0-9-]{0,63}$/.test(t.id)) errors.push(`${t.id}: id 不符合规范`);
  if (t.parent && !ids.has(t.parent)) errors.push(`${t.id}: 父标签 ${t.parent} 不存在`);
  if (t.parent && ids.get(t.parent)?.parent) errors.push(`${t.id}: 超过两层`);
  for (const a of t.aliases || []) {
    const n = norm(a);
    if (names.has(n)) errors.push(`${t.id}: 别名「${a}」与某个标签的 id / 名称相同`);
    else if (seen.has(n)) errors.push(`${t.id}: 别名「${a}」已是 ${seen.get(n)} 的别名`);
    else seen.set(n, t.id);
  }
}
for (const e of errors) console.log(`error ${e}`);
console.log(`标签 ${tags.length} 个（根 ${tags.filter((t) => !t.parent).length}），${errors.length} 个错误`);
if (errors.length) process.exit(1);

if (write) {
  const file = path.join(REPO, 'bank.yaml');
  const doc = YAML.parseDocument(fs.readFileSync(file, 'utf8'));
  const out = tags.map((t) => {
    const o = { id: t.id, name: t.name, parent: t.parent ?? null };
    if (withMeta) {
      if (t.description) o.description = t.description;
      if (t.aliases?.length) o.aliases = t.aliases.map(String);
    }
    return o;
  });
  doc.set('tags', doc.createNode(out));
  // 每个标签写成一行，便于阅读和比对
  for (const item of doc.get('tags').items) item.flow = !withMeta;
  fs.writeFileSync(file, doc.toString({ lineWidth: 0 }));
  console.log(`已写入 bank.yaml：${out.length} 个标签${withMeta ? '（含 description / aliases）' : ''}`);
}
