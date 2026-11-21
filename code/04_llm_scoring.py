# -*- coding: utf-8 -*-
"""
04_llm_scoring.py — LLM 逐段判读 MD&A 中的企业 AI 采纳（GLM-4-Flash，永久免费额度）
用法:
    python 04_llm_scoring.py --limit 200      # 试点：前200段
    python 04_llm_scoring.py                  # 全量（支持断点续跑）
产物:
    data/processed/llm_raw/{para_id}.json     原始响应（审计证据，REPRODUCE.md 引用）
    data/processed/ai_adoption_llm.csv        段落级打分结果
    data/processed/ai_adoption_firm.csv       公司级聚合指数（论文核心变量）
提示词版本: prompts/llm_scoring_prompt_v1.md（三分类 + 证据摘录）
"""
import sys, os, re, json, time, argparse, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
import requests

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RAW_DIR = os.path.join(BASE, "data", "processed", "llm_raw")
OUT_PARA = os.path.join(BASE, "data", "processed", "ai_adoption_llm.csv")
OUT_FIRM = os.path.join(BASE, "data", "processed", "ai_adoption_firm.csv")
ENV_PATH = os.path.join(BASE, ".env")
os.makedirs(RAW_DIR, exist_ok=True)

API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
MODEL = "glm-4-flash"

SYSTEM_PROMPT = """你是一名公司披露文本分析专家。你的任务是判读下面这段来自中国上市公司年报"管理层讨论与分析"（MD&A）的文本段落，判断该公司是否存在真实的人工智能（AI）采纳，并区分"真实应用"与"战略口号"。

判读标准（三分类）：
1. application（真实应用）：文本描述了已经部署、正在建设或已投入资源的人工智能应用，且有具体场景或载体。特征包括：
   - 提及具体业务场景（如智能风控、智能客服、智能质检、机器视觉检测、智能投研、智能营销等）
   - 提及具体技术载体（如机器学习模型、大模型、知识图谱、OCR、智能算法平台等）
   - 提及落地证据（如"已上线""投入使用""应用于XX环节""覆盖XX业务""效率提升XX%"）
   - 提及专门投入（研发投入金额、AI 项目、数字化团队建设针对 AI）
2. strategy（战略口号）：仅将人工智能作为宏观方向、行业趋势或愿景表述，无具体场景、载体或投入。特征包括：
   - 仅说"把握人工智能机遇""顺应AI发展趋势""探索人工智能应用"等
   - AI 与大数据/云计算/数字化转型并列罗列，无任何一项展开
3. none（无关）：该段落中"智能"等词与人工智能技术无关（如"智能化园区"仅指楼宇自控、"智能制造"仅为行业通用词且无公司自身实践）。

判读原则：
- 宁缺毋滥：只有出现公司自身（而非行业/客户/宏观经济）的具体应用证据才判 application。
- 公司为客户"提供AI解决方案/产品"属于公司的真实AI业务，判 application（需在 domain 中标注为"对外AI产品"）。
- 引用宏观政策或描述行业AI趋势而不涉及公司行动的，判 strategy 或 none。

输出严格 JSON：
{"label": "application|strategy|none", "firm_ai_activity": true/false, "domain": "研发|生产制造|营销销售|客户服务|风控合规|供应链|经营管理|对外AI产品|其他|无", "evidence_quote": "从原文中逐字摘录一句最能支撑判断的话（不超过80字；label=none 时填空字符串）", "investment_mention": true/false, "confidence": "high|medium|low"}
只输出 JSON，不要输出任何其他文字。

示例（务必严格对齐这些判例的尺度）：
示例1【application】输入：报告期内，公司智能风控平台已上线运行，覆盖信贷审批全流程，运用机器学习模型实现自动评分，审批效率提升约50%。输出：{"label": "application", "firm_ai_activity": true, "domain": "风控合规", "evidence_quote": "智能风控平台已上线运行，覆盖信贷审批全流程", "investment_mention": false, "confidence": "high"}
示例2【strategy】输入：公司持续推进数字化转型，把握人工智能发展机遇，未来将积极探索AI技术在生产经营中的应用。输出：{"label": "strategy", "firm_ai_activity": false, "domain": "无", "evidence_quote": "把握人工智能发展机遇，未来将积极探索AI技术", "investment_mention": false, "confidence": "high"}
示例3【none】输入：行业智能化升级趋势明显，下游客户对智能制造装备的需求持续增长，公司主营业务为特种胶粘材料的研发与销售。输出：{"label": "none", "firm_ai_activity": false, "domain": "无", "evidence_quote": "", "investment_mention": false, "confidence": "high"}
示例4【application】输入：公司为金融客户提供智能客服解决方案，基于自然语言处理与知识图谱技术，已在多家银行投入使用。输出：{"label": "application", "firm_ai_activity": true, "domain": "对外AI产品", "evidence_quote": "智能客服解决方案...已在多家银行投入使用", "investment_mention": false, "confidence": "high"}"""


def load_key():
    with open(ENV_PATH) as f:
        for line in f:
            if line.startswith("GLM_API_KEY="):
                return line.split("=", 1)[1].strip()
    raise RuntimeError("GLM_API_KEY 未找到，请检查 .env")

_KEY = load_key()
_print_lock = threading.Lock()

def _parse_model_output(content):
    """解析 GLM 返回的 JSON，容忍 evidence_quote 摘录原文时带入的非法转义。

    2026-11-21 发现 9 个段落反复 FAILED：GLM 把原文的中文引号/反斜杠原样
    写进 JSON 字符串（如 \\“ 或 \\下），json.loads 抛 Invalid \\escape，而
    label 本身是正确输出的。处理顺序：
      1) 标准解析；
      2) 去掉「反斜杠 + 非标准 JSON 转义字符」中的反斜杠后重试；
      3) 仍失败则正则只抽取核心结构化字段（label/domain/investment_mention/
         confidence），evidence_quote 置空——该字段仅用于审计展示，不参与
         ai_index 计算，故不影响核心变量，也不伪造摘录。
    返回 (dict, note)，note 写入缓存供审计（standard / unescape / regex_fallback）。
    """
    c = content.strip()
    if c.startswith("```"):
        c = c.strip("`").lstrip("json").strip()
    for cand, note in ((c, "standard"),
                       (re.sub(r'\\(?!["\\/bfnrtu])', "", c), "unescape")):
        try:
            obj = json.loads(cand)
            if isinstance(obj, dict) and obj.get("label") in ("application", "strategy", "none"):
                return obj, note
        except (json.JSONDecodeError, TypeError):
            continue
    obj = {}
    m = re.search(r'"label"\s*:\s*"(application|strategy|none)"', c)
    obj["label"] = m.group(1) if m else None
    if obj["label"] is None:
        raise json.JSONDecodeError("label not found", c, 0)  # 触发上层重试
    m = re.search(r'"domain"\s*:\s*"([^"]*)"', c)
    obj["domain"] = m.group(1) if m else "无"
    m = re.search(r'"investment_mention"\s*:\s*(true|false)', c)
    obj["investment_mention"] = (m.group(1) == "true") if m else False
    m = re.search(r'"confidence"\s*:\s*"(high|medium|low)"', c)
    obj["confidence"] = m.group(1) if m else ""
    m = re.search(r'"firm_ai_activity"\s*:\s*(true|false)', c)
    obj["firm_ai_activity"] = (m.group(1) == "true") if m else None
    obj["evidence_quote"] = ""   # 审计摘录不可靠时置空，不伪造
    return obj, "regex_fallback"


def score_paragraph(para_id, code, name, paragraph, retries=4):
    raw_path = os.path.join(RAW_DIR, f"{para_id}.json")
    if os.path.exists(raw_path):  # 断点续跑（容错：半写/损坏缓存视为未打分）
        try:
            with open(raw_path) as f:
                cached = json.load(f)
            if cached.get("label") in ("application", "strategy", "none"):
                return {**cached, "para_id": para_id, "code": code, "name": name}
        except (json.JSONDecodeError, OSError, ValueError, TypeError):
            pass
        # 损坏缓存（进程中断留下的半写 JSON）→ 删除并重新打分
        try:
            os.remove(raw_path)
        except OSError:
            pass
    user_msg = f"【公司代码】{code}\n【公司简称】{name}\n【MD&A 段落】\n{paragraph}"
    for attempt in range(retries):
        try:
            r = requests.post(API_URL,
                headers={"Authorization": f"Bearer {_KEY}", "Content-Type": "application/json"},
                json={"model": MODEL, "temperature": 0,
                      "messages": [{"role": "system", "content": SYSTEM_PROMPT},
                                   {"role": "user", "content": user_msg}]},
                timeout=60)
            if r.status_code == 200:
                content = r.json()["choices"][0]["message"]["content"].strip()
                parsed, parse_note = _parse_model_output(content)
                rec = {"label": parsed.get("label"), "domain": parsed.get("domain"),
                       "firm_ai_activity": parsed.get("firm_ai_activity"),
                       "evidence_quote": (parsed.get("evidence_quote") or "")[:100],
                       "investment_mention": parsed.get("investment_mention"),
                       "confidence": parsed.get("confidence"), "model": MODEL,
                       "prompt_version": "v1", "parse_note": parse_note}
                # 原子写：先写 .tmp 再 rename，避免进程中断产生半写 JSON
                # （2026-11-21 曾因此产生 2 个损坏缓存，导致断点续跑崩溃）
                tmp_path = raw_path + ".tmp"
                with open(tmp_path, "w") as f:
                    json.dump({**rec, "paragraph_head": paragraph[:80]}, f, ensure_ascii=False)
                os.replace(tmp_path, raw_path)
                with _print_lock:
                    print(f"  {para_id} {code} -> {rec['label']} ({rec['confidence']})", flush=True)
                return {**rec, "para_id": para_id, "code": code, "name": name}
            elif r.status_code == 429:
                time.sleep(2 ** attempt)
            else:
                with _print_lock:
                    print(f"  {para_id} HTTP {r.status_code}: {r.text[:80]}", flush=True)
                time.sleep(2)
        except (json.JSONDecodeError, KeyError):
            time.sleep(1)  # JSON解析失败重试
        except requests.RequestException:
            time.sleep(2 ** attempt)
    return {"label": "FAILED", "para_id": para_id, "code": code, "name": name,
            "domain": "", "firm_ai_activity": None, "evidence_quote": "",
            "investment_mention": None, "confidence": "", "model": MODEL, "prompt_version": "v1"}

def aggregate_firm(para_df):
    """公司层聚合（提示词v1规则）：0.5×应用密度 + 0.3×场景广度 + 0.2×投入"""
    DOMAINS = ["研发", "生产制造", "营销销售", "客户服务", "风控合规", "供应链", "经营管理", "对外AI产品"]
    rows = []
    for (code, name), g in para_df.groupby(["code", "name"]):
        g = g[g["label"] != "FAILED"]
        n = len(g)
        if n == 0:
            continue
        n_app = int((g["label"] == "application").sum())
        density = n_app / n
        domains = set()
        for d in g["domain"].fillna(""):
            for dd in str(d).split("|"):
                dd = dd.strip()
                if dd in DOMAINS:
                    domains.add(dd)
        breadth = len(domains) / len(DOMAINS)
        invest = 1 if (g["investment_mention"] == True).any() else 0
        rows.append({"code": code, "name": name, "n_paras": n, "n_application": n_app,
                     "app_density": density, "domain_breadth": breadth,
                     "investment": invest, "ai_index": 0.5 * density + 0.3 * breadth + 0.2 * invest})
    return pd.DataFrame(rows)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    df = pd.read_csv(os.path.join(BASE, "data", "processed", "mda_paragraphs.csv"))
    if "para_id" not in df.columns:  # 兼容旧版段落表
        df["para_id"] = df["code"].astype(str) + "_" + df.groupby("code").cumcount().astype(str)
    if args.limit:
        df = df.head(args.limit)
    print(f"待打分段落: {len(df)}（模型 {MODEL}，并发 {args.workers}）")

    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(score_paragraph, r.para_id, r.code, r.name, r.paragraph)
                for r in df.itertuples()]
        for f in as_completed(futs):
            results.append(f.result())
    para_out = pd.DataFrame(results)[["para_id","code","name","label","domain","firm_ai_activity",
                                      "evidence_quote","investment_mention","confidence","model","prompt_version"]]
    para_out.to_csv(OUT_PARA, index=False)
    failed = int((para_out["label"] == "FAILED").sum())
    print(f"\n段落级完成: {len(para_out)-failed}/{len(para_out)}（失败{failed}）-> {OUT_PARA}")

    firm_out = aggregate_firm(para_out)
    firm_out.to_csv(OUT_FIRM, index=False)
    print(f"公司级聚合: {len(firm_out)} 家 -> {OUT_FIRM}")
    if len(firm_out):
        print(firm_out[["name","n_paras","n_application","ai_index"]].sort_values("ai_index", ascending=False).head(10))

if __name__ == "__main__":
    main()
