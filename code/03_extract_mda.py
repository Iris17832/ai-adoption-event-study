# -*- coding: utf-8 -*-
"""
03_extract_mda.py — 从年报PDF提取"管理层讨论与分析"章节
产物:
  data/processed/mda_text/{code}_{year}.txt        每家MD&A全文
  data/processed/mda_paragraphs.csv                含AI关键词的段落表（LLM打分输入）
策略: MD&A 章节从目录定位起点；终点为下一个主章节标题。
"""
import sys, os, re, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from pypdf import PdfReader

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RAW = os.path.join(BASE, "data", "raw", "annual_reports")
TXT = os.path.join(BASE, "data", "processed", "mda_text")
PARA_CSV = os.path.join(BASE, "data", "processed", "mda_paragraphs.csv")
os.makedirs(TXT, exist_ok=True)

NEXT_SECTIONS = ["第{N}节", "重要事项", "公司治理", "环境和社会责任", "股份变动及股东情况",
                 "优先股", "公司债券", "财务报告", "备查文件"]
AI_KEYWORDS = ["人工智能", "智能", "大模型", "大语言模型", "机器学习", "深度学习", "神经网络",
               "算法", "数字化", "数智", "智能风控", "智能制造", "智慧", "AIGC", "AI"]

def extract_mda_text(pdf_path, max_pages=320):
    try:
        rd = PdfReader(pdf_path)
    except Exception:
        return None, None
    texts = []
    for p in rd.pages[:max_pages]:
        try:
            texts.append(p.extract_text() or "")
        except Exception:
            texts.append("")
    full = "\n".join(texts)
    # 起点：目录后正文中的章节标题（第二处出现）
    hits = [m.start() for m in re.finditer(r"管理层讨论与分析", full)]
    if not hits:
        return None, "no_mda_title"
    start = hits[-1] if len(hits) == 1 else hits[1]
    start = full.find("\n", start) + 1
    # 终点：下一个主章节
    end = len(full)
    for pat in [r"第[一二三四五六七八九十]+节\s*重要事项", r"重要事项", r"第[一二三四五六七八九十]+节\s*公司治理"]:
        m = re.search(pat, full[start + 500:])
        if m:
            cand = start + 500 + m.start()
            if cand < end:
                end = cand
    return full[start:end], None

def split_paragraphs(text, min_len=40):
    text = re.sub(r"\s+", "", text)
    # 无空格中文文本按句号/分号/换行切成段
    parts = re.split(r"[。；！？]", text)
    # 合并成段落：约每6-10句一段
    paras, buf, cnt = [], [], 0
    for s in parts:
        buf.append(s); cnt += 1
        if cnt >= 8:
            paras.append("。".join(buf) + "。"); buf, cnt = [], 0
    if buf:
        paras.append("。".join(buf) + "。")
    return [p for p in paras if len(p) >= min_len]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="只处理前N家（0=全部）")
    args = ap.parse_args()
    idx = pd.read_csv(os.path.join(BASE, "data", "processed", "report_index.csv"), dtype={"code": str})
    idx = idx[idx["status"] == "downloaded"]
    if args.limit:
        idx = idx.head(args.limit)
    rows = []
    for _, r in idx.iterrows():
        pdf = r["pdf_path"] if isinstance(r.get("pdf_path"), str) else os.path.join(RAW, f"{r['code']}_{r['year']}.pdf")
        if not os.path.exists(pdf):
            continue
        mda, err = extract_mda_text(pdf)
        if mda is None:
            print(f"  {r['code']} 提取失败: {err}")
            continue
        with open(os.path.join(TXT, f"{r['code']}_{r['year']}.txt"), "w") as f:
            f.write(mda)
        kps = [p for p in split_paragraphs(mda) if any(k in p for k in AI_KEYWORDS)]
        for j, para in enumerate(kps):  # 稳定 para_id：公司内序号，增量运行不漂移
            rows.append({"para_id": f"{r['code']}_{j}", "code": r["code"], "name": r["name"],
                         "year": r["year"], "paragraph": para, "para_len": len(para)})
        print(f"  {r['code']} {r['name']}: MD&A {len(mda)}字, 关键词段落 {len(kps)}", flush=True)
    pd.DataFrame(rows).to_csv(PARA_CSV, index=False)
    print(f"\n关键词段落总数: {len(rows)} -> {PARA_CSV}")

if __name__ == "__main__":
    main()
