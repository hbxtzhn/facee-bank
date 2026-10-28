import os
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATALOG_PATH = os.path.join(BASE_DIR, 'catalog.json')
QUESTIONS_DIR = os.path.join(BASE_DIR, 'questions')

with open(CATALOG_PATH, 'r', encoding='utf-8') as f:
    catalog = json.load(f)

# 过滤掉已有的 fe-ai 和 fe-scenario，重新全量按目录同步
catalog['questions'] = [q for q in catalog['questions'] if not (q['id'].startswith('fe-ai-') or q['id'].startswith('fe-scenario-'))]

# 扫描 questions 目录下所有的 fe-ai-* 和 fe-scenario-*
all_q_dirs = sorted([d for d in os.listdir(QUESTIONS_DIR) if d.startswith('fe-ai-') or d.startswith('fe-scenario-')])

new_questions = []

def extract_title(q_path):
    if not os.path.exists(q_path):
        return ""
    with open(q_path, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
        if first_line.startswith('# '):
            return first_line[2:].strip()
    return ""

def count_followups(f_path):
    if not os.path.exists(f_path):
        return 0
    with open(f_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return len(re.findall(r'^##\s+追问', content, re.MULTILINE))

def determine_difficulty(qid, title):
    # 场景题或架构设计默认为 medium，深入协议或大模型底层为 hard，基础语法为 easy
    hard_keywords = ['沙箱', '底层原理', '深度剖析', '安全', '并发', 'Fiber', 'Proxy', 'AST', '架构', '监控', '隔离']
    easy_keywords = ['区别', '代表什么', '如何判空', 'px如何转为rem', '受控组件']
    for kw in hard_keywords:
        if kw in title:
            return 'hard'
    for kw in easy_keywords:
        if kw in title:
            return 'easy'
    return 'medium'

def determine_tags(qid, title):
    tags = []
    if qid.startswith('fe-ai-'):
        tags.append('frontend-ai')
        if any(k in title for k in ['TypeScript', 'TS', '类型', '泛型']):
            tags.extend(['typescript', 'type-system'])
        elif any(k in title for k in ['SSE', '流式', 'WebSocket', 'Fetch', '打字机']):
            tags.extend(['streaming', 'sse', 'network'])
        elif any(k in title for k in ['Function Calling', 'Tools', '结构化', 'JSON', 'Zod']):
            tags.extend(['function-calling', 'tools', 'schema'])
        elif any(k in title for k in ['分块', 'Chunk', '向量', 'Embedding', 'RAG', '知识库']):
            tags.extend(['rag', 'vector', 'knowledge-base'])
        elif any(k in title for k in ['Agent', '工作流', 'ReAct', 'Human-in-the-loop', '状态机']):
            tags.extend(['agent', 'workflow'])
        elif any(k in title for k in ['Vercel AI SDK', 'LobeChat', '开源']):
            tags.extend(['vercel-ai-sdk', 'open-source'])
        elif any(k in title for k in ['Prompt', '注入', '安全', '降级', '重试', '压测', '并发', 'Token', '缓存']):
            tags.extend(['prompt', 'security', 'performance'])
        elif any(k in title for k in ['虚拟列表', 'Markdown', '代码高亮', 'KaTeX', 'DOM']):
            tags.extend(['ui-rendering', 'markdown', 'performance'])
        else:
            tags.append('llm')
    else:
        tags.append('scenario')
        if 'React' in title or 'Fiber' in title or 'Hooks' in title or 'Context' in title:
            tags.extend(['react', 'frontend-framework'])
        elif 'Vue' in title or 'Pinia' in title:
            tags.extend(['vue', 'frontend-framework'])
        elif '微前端' in title or 'Qiankun' in title or '沙箱' in title:
            tags.extend(['micro-frontend', 'architecture'])
        elif any(k in title for k in ['性能优化', '首屏', '加载']):
            tags.extend(['performance', 'optimization'])
        elif any(k in title for k in ['XSS', 'CSRF', 'HTTP', 'HTTPS', '同源', 'Cookie']):
            tags.extend(['network', 'security'])
        elif any(k in title for k in ['Webpack', 'Vite', 'Babel', '重构', '清理']):
            tags.extend(['engineering', 'build-tools'])
        elif any(k in title for k in ['CSS', 'flex', '翻牌', 'rem']):
            tags.extend(['css', 'layout'])
        elif any(k in title for k in ['DOM', '划词', '富文本', 'PDF']):
            tags.extend(['dom', 'rich-text'])
        else:
            tags.append('practical')
    return list(dict.fromkeys(tags))

ai_order = 10
scenario_order = 10

for qid in all_q_dirs:
    qdir = os.path.join(QUESTIONS_DIR, qid)
    title = extract_title(os.path.join(qdir, 'question.md'))
    has_answer = os.path.exists(os.path.join(qdir, 'answer.md'))
    followup_count = count_followups(os.path.join(qdir, 'followups.md'))
    
    if qid.startswith('fe-ai-'):
        cat_id = 'frontend-ai'
        order = ai_order
        ai_order += 10
    else:
        cat_id = 'frontend-scenario'
        order = scenario_order
        scenario_order += 10
        
    diff = determine_difficulty(qid, title)
    tags = determine_tags(qid, title)
    
    new_questions.append({
        "id": qid,
        "title": title,
        "difficulty": diff,
        "categoryId": cat_id,
        "tags": tags,
        "order": order,
        "hasAnswer": has_answer,
        "followupCount": followup_count
    })

catalog['questions'].extend(new_questions)

# 确保 categories 列表中存在 frontend-ai 和 frontend-scenario
cat_map = {c['id']: c for c in catalog['categories']}
if 'frontend-ai' not in cat_map:
    catalog['categories'].append({
        "id": "frontend-ai",
        "name": "前端 AI 工程化",
        "description": "涵盖前端+AI时代核心考点：TypeScript强类型约束、流式渲染(SSE/Fetch/Worker)、Function Calling/Tools、端侧RAG/向量检索、前端Agent工作流、Vercel AI SDK架构与性能安全治理",
        "order": 160
    })
if 'frontend-scenario' not in cat_map:
    catalog['categories'].append({
        "id": "frontend-scenario",
        "name": "前端场景与高频实战",
        "description": "涵盖高频实操与场景设计：微前端沙箱隔离、富文本与划词选区、大文件/PDF预览、高并发竞态取消、工程化重构与灰度发布、React/Vue深度原理及全链路性能安全",
        "order": 170
    })

# 更新所有 category 的 questionCount
counts = {}
for q in catalog['questions']:
    cid = q['categoryId']
    counts[cid] = counts.get(cid, 0) + 1

for c in catalog['categories']:
    c['questionCount'] = counts.get(c['id'], 0)

with open(CATALOG_PATH, 'w', encoding='utf-8') as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)

print(f"Catalog updated successfully!")
print(f"Total questions in catalog: {len(catalog['questions'])}")
print(f"frontend-ai: {counts.get('frontend-ai', 0)} questions")
print(f"frontend-scenario: {counts.get('frontend-scenario', 0)} questions")
