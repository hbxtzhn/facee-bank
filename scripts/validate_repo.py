import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(BASE_DIR, 'catalog.json')
QUESTIONS_DIR = os.path.join(BASE_DIR, 'questions')

with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
    catalog = json.load(f)

errors = []
warnings = []

# 1. 验证 catalog 结构
catalog_q_ids = set()
for q in catalog['questions']:
    qid = q['id']
    if qid in catalog_q_ids:
        errors.append(f"Duplicate question id in catalog.json: {qid}")
    catalog_q_ids.add(qid)
    
    # 检查对应目录是否存在
    qdir = os.path.join(QUESTIONS_DIR, qid)
    if not os.path.isdir(qdir):
        errors.append(f"Directory missing for question: {qid}")
    else:
        # 新增题目强制三件套齐全；老题目只要 question.md 和 answer.md
        required_files = ['question.md', 'answer.md']
        if qid.startswith('fe-ai-') or qid.startswith('fe-scenario-'):
            required_files.append('followups.md')
            
        for fname in required_files:
            fpath = os.path.join(qdir, fname)
            if not os.path.exists(fpath):
                errors.append(f"File missing: {qid}/{fname}")
            else:
                size = os.path.getsize(fpath)
                if size == 0:
                    errors.append(f"Empty file: {qid}/{fname}")

# 2. 检查 questions 目录下是否有多余未入库目录
fs_dirs = set(os.listdir(QUESTIONS_DIR))
orphan_dirs = fs_dirs - catalog_q_ids
if orphan_dirs:
    # 忽略非题目目录（如果有）
    real_orphans = [d for d in orphan_dirs if os.path.isdir(os.path.join(QUESTIONS_DIR, d))]
    if real_orphans:
        warnings.append(f"Orphan question directories on disk not in catalog: {real_orphans}")

print("=== Validation Report ===")
print(f"Total categories: {len(catalog['categories'])}")
print(f"Total registered questions: {len(catalog['questions'])}")
if errors:
    print(f"❌ Found {len(errors)} errors:")
    for err in errors[:20]:
        print(f"  - {err}")
else:
    print("✅ All questions and files verified successfully with ZERO errors!")

if warnings:
    print(f"⚠️ Warnings: {warnings}")
