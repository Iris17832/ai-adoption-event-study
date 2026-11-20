# -*- coding: utf-8 -*-
"""
04_dict_baseline.py —— 词典法 AI 采纳指数（baseline）
=====================================================
方法：对每家公司 MD&A 全文统计 AI 关键词出现次数，除以 MD&A 千字数，
      得到"词典法 AI 采纳指数"（每千字 AI 词频）。

词表来源说明（引用核验表 #1 对应）：
  - 主体采用 Wu et al. (2026) 73 词 AI 词典的中文对应词（待孔佳怡核验原文词表后逐一对齐替换）；
  - 补充采用吴非等(2021,管理世界)数字化转型词典中的 AI 子词表（学界通行做法）。
  - ⚠ 词表为 v1 草案，论文附录必须列全词表；终稿前需人工核验对齐。

输出：
  data/processed/ai_adoption_dict.csv —— code,name,year,mda_len,ai_hit,dict_index
  results/dict_vs_llm_correlation.txt —— 词典法与LLM法指数的对比（ spearman 相关 + 分组交叉表）
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
TXT = os.path.join(BASE, "data", "processed", "mda_text")
FIRM_LLM = os.path.join(BASE, "data", "processed", "ai_adoption_firm.csv")
OUT = os.path.join(BASE, "data", "processed", "ai_adoption_dict.csv")
RES = os.path.join(BASE, "results", "dict_vs_llm_correlation.txt")
os.makedirs(os.path.dirname(RES), exist_ok=True)

# ---------- AI 词典 v1 ----------
AI_DICT = [
    # 核心概念
    "人工智能", "AI", "机器学习", "深度学习", "神经网络", "大模型", "大语言模型",
    "生成式人工智能", "AIGC", "预训练", "多模态",
    # 技术与应用载体
    "自然语言处理", "计算机视觉", "知识图谱", "智能语音", "语音识别", "图像识别",
    "人脸识别", "ocr", "自动驾驶", "无人驾驶", "智能驾驶", "机器人", "智能机器人",
    "智能算法", "算法模型", "智能推荐", "智能客服", "智能风控", "智能投顾",
    "智能质检", "智能巡检", "智能制造", "智能仓储", "智能营销",
    # 平台与基础设施
    "ai大模型", "ai平台", "ai中台", "算力", "gpu", "推理引擎", "训练模型",
    "模型训练", "数字化平台", "智慧化",
]
_PAT = re.compile("|".join(re.escape(w) for w in AI_DICT), re.IGNORECASE)


def dict_index(text: str) -> dict:
    n = len(text)
    hits = len(_PAT.findall(text))
    per_k = hits / max(n, 1) * 1000  # 每千字词频
    return {"mda_len": n, "ai_hit": hits, "dict_index": round(per_k, 4)}


def main():
    rows = []
    for fn in sorted(os.listdir(TXT)):
        if not fn.endswith(".txt"):
            continue
        code, year = fn.replace(".txt", "").split("_")
        name = ""
        text = open(os.path.join(TXT, fn), encoding="utf-8").read()
        r = dict_index(text)
        rows.append({"code": code, "name": name, "year": int(year), **r})
    df = pd.DataFrame(rows)
    # 补充公司名
    mda = pd.read_csv(os.path.join(BASE, "data", "processed", "mda_paragraphs.csv"), dtype={"code": str})
    names = mda.drop_duplicates("code").set_index("code")["name"].to_dict()
    df["name"] = df["code"].map(names)
    df.to_csv(OUT, index=False)
    print(f"词典法指数计算完成: {len(df)} 家 -> {OUT}")

    # ---------- 对比 LLM 法 ----------
    lines = []
    lines.append(f"词典法 vs LLM法 AI采纳指数对比（N={len(df)} 家）\n")
    if os.path.exists(FIRM_LLM):
        llm = pd.read_csv(FIRM_LLM, dtype={"code": str})
        m = df.merge(llm[["code", "ai_index"]], on="code", suffixes=("_dict", "_llm"))
        if len(m) >= 10:
            from scipy.stats import spearmanr, pearsonr
            rs, ps = spearmanr(m["dict_index"], m["ai_index"])
            rp, pp = pearsonr(m["dict_index"], m["ai_index"])
            lines.append(f"合并样本: {len(m)} 家")
            lines.append(f"Spearman 相关: rho={rs:.3f} (p={ps:.4f})")
            lines.append(f"Pearson 相关: r={rp:.3f} (p={pp:.4f})")
            # 高估检验：词典法将strategy/none段落也计入 → 词典法>0的公司数应远多于LLM法>0
            n_dict_pos = (df["dict_index"] > 0).sum()
            n_llm_pos = (llm["ai_index"] > 0).sum() if "ai_index" in llm else None
            lines.append(f"词典法识别为采纳(dict_index>0): {n_dict_pos}/{len(df)} 家")
            if n_llm_pos is not None:
                lines.append(f"LLM法识别为采纳(ai_index>0): {n_llm_pos}/{len(llm)} 家")
                # 同一公司集合上的口径对比
                merged_codes = set(m["code"])
                d_pos_llm0 = m[(m["dict_index"] > 0) & (m["ai_index"] == 0)]
                lines.append(f"词典法>0 但 LLM法=0（词典法高估）: {len(d_pos_llm0)} 家 "
                             f"({len(d_pos_llm0)/max(len(m),1)*100:.1f}% of 合并样本)")
            m.to_csv(os.path.join(BASE, "data", "processed", "dict_vs_llm_merged.csv"), index=False)
    txt = "\n".join(lines)
    print(txt)
    open(RES, "w", encoding="utf-8").write(txt)


if __name__ == "__main__":
    main()
