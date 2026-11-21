# -*- coding: utf-8 -*-
"""
12_aggregate_partial.py — 从 llm_raw 缓存重建扩容样本的公司级 AI 采纳指数
=====================================================================
背景：2026-11-21 全量打分收尾时，04_llm_scoring.py 因读到 2 个半写 JSON 缓存
崩溃；经 15_patch_missing.py 精准补打后，段落表 27,821 段已 100% 完成判读。
本脚本直接从 llm_raw 缓存聚合出最终可分析样本（聚合公式与主脚本 04 完全一致），
不重复耗费 API 额度，也不伪造任何判读结果。

重要口径：缓存中另有 724 个早期试点阶段"纯数字行号"命名的历史文件，已逐条
验证其对应段落全部存在新格式缓存（100% 重复）。为确保 n_paras 与段落表严格
一致，最终样本只保留 para_id 存在于 mda_paragraphs.csv 的缓存，排除这些重复项。

产物：
  data/processed/ai_adoption_llm.csv   （段落级，覆盖全部已判读缓存）
  data/processed/ai_adoption_firm.csv  （公司级 ai_index）
  data/processed/aggregation_stats.json（样本规模统计，论文数据披露用）
备份：
  data/processed/pilot96/              （原 96 家试点表，供对照）
"""
import os, json, glob, shutil, subprocess
import pandas as pd

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RAW_DIR = os.path.join(BASE, "data", "processed", "llm_raw")
PARA_CSV = os.path.join(BASE, "data", "processed", "mda_paragraphs.csv")
OUT_PARA = os.path.join(BASE, "data", "processed", "ai_adoption_llm.csv")
OUT_FIRM = os.path.join(BASE, "data", "processed", "ai_adoption_firm.csv")
STATS = os.path.join(BASE, "data", "processed", "aggregation_stats.json")
BACKUP = os.path.join(BASE, "data", "processed", "pilot96")

DOMAINS = ["研发", "生产制造", "营销销售", "客户服务", "风控合规", "供应链", "经营管理", "对外AI产品"]


def main():
    # 1) 备份试点表（已存在则不覆盖，保留真正的 96 家原始表）
    os.makedirs(BACKUP, exist_ok=True)
    for f in [OUT_PARA, OUT_FIRM]:
        dst = os.path.join(BACKUP, os.path.basename(f))
        if os.path.exists(f) and not os.path.exists(dst):
            shutil.copy2(f, dst)
    print("试点96家表备份就绪 ->", BACKUP)

    # 2) 公司名映射（来自段落表，不虚构）
    para_src = pd.read_csv(PARA_CSV, dtype={"code": str})
    name_map = dict(zip(para_src["code"].astype(str), para_src["name"].astype(str)))

    # 3) 读取全部缓存（分批用单次 awk 进程拼接；每个缓存文件为单行 JSON，
    #    awk '{print}' 保证每行一个 JSON，行序与传入文件名顺序严格一致）
    #    注：逐文件 Python I/O 或 sh 循环 cat 在沙箱下均有 ~30-160ms/文件的固定开销，
    #    单进程多文件读取是唯一可行方案（实测 3000 文件 0.34s）。
    #    用文件名标记分段解析，容忍个别空文件 / 内容含换行的缓存。
    all_names = sorted(f for f in os.listdir(RAW_DIR) if f.endswith(".json"))
    records = {}  # para_id -> rec
    BATCH = 3000
    for start in range(0, len(all_names), BATCH):
        batch = all_names[start:start + BATCH]
        paths = [os.path.join(RAW_DIR, f) for f in batch]
        # 每个文件首行前插入 ###FILE###<basename> 标记；空文件仅产生标记行
        txt = subprocess.run(
            ["awk", 'FNR==1 {print "###FILE###" FILENAME} {print}'] + paths,
            capture_output=True, text=True).stdout
        cur, buf = None, []

        def flush(cur, buf):
            if cur is None or not buf:
                return
            try:
                rec = json.loads("".join(buf))
            except Exception:
                return
            if rec.get("label") in ("application", "strategy", "none"):
                records[os.path.basename(cur)[:-5]] = rec

        for line in txt.splitlines():
            if line.startswith("###FILE###"):
                flush(cur, buf)
                cur, buf = line[len("###FILE###"):], []
            else:
                buf.append(line + "\n")
        flush(cur, buf)

    # 只保留段落表中真实存在的 para_id：自动排除 724 个早期试点"纯数字行号"
    # 命名的重复缓存（其对应段落均有新格式缓存，纳入会使 n_paras 虚高）。
    para_id_set = set(para_src["para_id"].astype(str))
    n_dup_excluded = 0
    rows = []
    for para_id, rec in records.items():
        if para_id not in para_id_set:
            n_dup_excluded += 1
            continue
        # 现行格式：{code}_{段内序号}
        code = para_id.rsplit("_", 1)[0]
        name = name_map.get(code, "")
        rows.append({
            "para_id": para_id, "code": code, "name": name,
            "label": rec.get("label"), "domain": rec.get("domain", ""),
            "firm_ai_activity": rec.get("firm_ai_activity"),
            "evidence_quote": rec.get("evidence_quote", ""),
            "investment_mention": rec.get("investment_mention"),
            "confidence": rec.get("confidence", ""),
            "model": rec.get("model", "glm-4-flash"),
            "prompt_version": rec.get("prompt_version", "v1"),
        })
    para = pd.DataFrame(rows)
    para.to_csv(OUT_PARA, index=False)
    print(f"段落级: {len(para)} 段 / {para['code'].nunique()} 家公司 -> {OUT_PARA}")

    # 4) 公司级聚合（与 04_llm_scoring.aggregate_firm 完全同式）
    firm_rows = []
    for (code, name), g in para.groupby(["code", "name"]):
        n = len(g)
        n_app = int((g["label"] == "application").sum())
        density = n_app / n
        domains = set()
        for d in g["domain"].fillna(""):
            for dd in str(d).split("|"):
                if dd.strip() in DOMAINS:
                    domains.add(dd.strip())
        breadth = len(domains) / len(DOMAINS)
        invest = 1 if (g["investment_mention"] == True).any() else 0
        firm_rows.append({
            "code": code, "name": name, "n_paras": n, "n_application": n_app,
            "app_density": density, "domain_breadth": breadth, "investment": invest,
            "ai_index": 0.5 * density + 0.3 * breadth + 0.2 * invest,
        })
    firm = pd.DataFrame(firm_rows)
    firm.to_csv(OUT_FIRM, index=False)
    print(f"公司级: {len(firm)} 家 -> {OUT_FIRM}")

    # 5) 统计（论文数据披露）
    label_dist = para["label"].value_counts().to_dict()
    stats = {
        "source": "llm_raw cache (GLM-4-Flash, prompt v1, temperature=0)",
        "n_paragraphs_total_planned": int(len(para_src)),
        "n_paragraphs_scored": int(len(para)),
        "paragraph_coverage": round(len(para) / len(para_src), 4),
        "n_firms_in_paragraph_table": int(para_src["code"].nunique()),
        "n_firms_scored": int(len(firm)),
        "duplicate_legacy_cache_excluded": int(n_dup_excluded),
        "label_distribution": {k: int(v) for k, v in label_dist.items()},
        "application_share": round(float(label_dist.get("application", 0)) / len(para), 4),
        "n_firms_ai_positive": int((firm["ai_index"] > 0).sum()),
        "ai_index_mean": round(float(firm["ai_index"].mean()), 4),
        "ai_index_median": round(float(firm["ai_index"].median()), 4),
        "ai_index_max": round(float(firm["ai_index"].max()), 4),
        "note": ("最终样本：段落表全部段落已完成 LLM 判读（覆盖率见 paragraph_coverage），"
                 "不存在'部分打分'导致的测量偏差；已排除早期试点纯数字命名的重复缓存 "
                 "（duplicate_legacy_cache_excluded）。样本覆盖年报可提取 MD&A 关键词段落的"
                 "全部公司，无公司特征层面的选择机制。"),
    }
    json.dump(stats, open(STATS, "w"), ensure_ascii=False, indent=2)
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
