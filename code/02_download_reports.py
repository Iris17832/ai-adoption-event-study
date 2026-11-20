# -*- coding: utf-8 -*-
"""
02_download_reports.py — 下载年报PDF（双通道：cninfo / eastmoney）
用法:
    python 02_download_reports.py --sample 100                # 随机抽100家试点（默认cninfo）
    python 02_download_reports.py --sample all                # 全量（约5000家，断点续跑）
    python 02_download_reports.py --sample all --channel em   # 东财通道
产物: data/raw/annual_reports/{code}_{year}.pdf
      data/processed/report_index.csv（下载清单+公告URL+下载日志）
注: 下载日志即过程证据，也是数据许可说明"获取方式"列的依据。
"""
import sys, os, argparse, time, random, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from data_client import (find_annual_report_em, em_announcement_pdf_url, download_pdf,
                         query_annual_report, download_cninfo_pdf)

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RAW = os.path.join(BASE, "data", "raw", "annual_reports")
IDX = os.path.join(BASE, "data", "processed", "report_index.csv")
ORG = os.path.join(BASE, "data", "processed", "cninfo_orgid.json")
YEAR = 2023
random.seed(42)
os.makedirs(RAW, exist_ok=True)
os.makedirs(os.path.dirname(IDX), exist_ok=True)

def load_targets(sample):
    df = pd.read_csv(os.path.join(BASE, "data", "processed", "stock_list.csv"), dtype={"code": str})
    df = df[~df["code"].str.startswith(("4", "8", "92"))]  # 剔除北交所/新三板（主板+双创口径，论文中说明）
    df = df.reset_index(drop=True)
    if sample and sample != "all":
        df = df.sample(min(int(sample), len(df)), random_state=42)
    return df

def try_cninfo(code, year, out_pdf):
    """巨潮通道。返回 (status, title, url, date)"""
    org = json.load(open(ORG)) if os.path.exists(ORG) else {}
    org_id = (org.get(code) or {}).get("orgId")
    if not org_id:
        return "no_orgid", "", "", ""
    target = f"{year}年年度报告"
    BAD = ("摘要", "英文", "更正", "问询", "补充", "撤销", "停牌")
    try:
        anns = query_annual_report(code, org_id, year=year)
    except Exception as e:
        return f"error:{str(e)[:50]}", "", "", ""
    best, best_rank = None, -1
    for a in anns:
        t = a["title"]
        if target not in t or any(b in t for b in BAD):
            continue
        rank = 3 if t == target else (2 if ("更新" in t or "修订" in t) else 1)
        if rank > best_rank:
            best, best_rank = a, rank
    if not best:
        return "not_found", "", "", ""
    ok = download_cninfo_pdf(best["adjunctUrl"], out_pdf)
    return ("downloaded" if ok else "download_failed"), best["title"], best["adjunctUrl"], best["time"]

def try_eastmoney(code, year, out_pdf):
    """东财通道。返回 (status, title, url, date)"""
    try:
        rep = find_annual_report_em(code, year=year)
    except Exception as e:
        return f"error:{str(e)[:50]}", "", "", ""
    if not rep:
        return "not_found", "", "", ""
    pdf_url = em_announcement_pdf_url(rep["art_code"])
    if not pdf_url:
        return "no_pdf_url", rep["title"], "", rep["notice_date"]
    ok = download_pdf(pdf_url, out_pdf)
    return ("downloaded" if ok else "download_failed"), rep["title"], pdf_url, rep["notice_date"]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", default="100")
    ap.add_argument("--year", type=int, default=YEAR)
    ap.add_argument("--channel", default="cninfo", choices=["cninfo", "em"])
    args = ap.parse_args()

    targets = load_targets(args.sample)
    print(f"目标 {len(targets)} 家（{args.year} 年报，通道 {args.channel}）")

    records = []
    if os.path.exists(IDX):
        old = pd.read_csv(IDX, dtype={"code": str}).to_dict("records")
        # 载入历史，但失败/未完成记录不保留（避免重复）
        records = [r for r in old if r.get("status") == "downloaded"]
    done = {r["code"] for r in records}

    for i, row in targets.iterrows():
        code, name = row["code"], row["name"]
        if code in done:
            continue
        out_pdf = os.path.join(RAW, f"{code}_{args.year}.pdf")
        rec = {"code": code, "name": name, "year": args.year, "status": "start",
               "title": "", "art_code": "", "announce_date": "", "pdf_path": "", "pdf_url": ""}
        try:
            if args.channel == "cninfo":
                status, title, url, date = try_cninfo(code, args.year, out_pdf)
            else:
                status, title, url, date = try_eastmoney(code, args.year, out_pdf)
            rec.update({"status": status, "title": title, "pdf_url": url,
                        "announce_date": date, "pdf_path": out_pdf if status == "downloaded" else ""})
        except Exception as e:
            rec["status"] = f"error:{str(e)[:60]}"
        records.append(rec)
        if (len(records) % 20) == 0:
            pd.DataFrame(records).to_csv(IDX, index=False)
            ok = sum(1 for r in records if r["status"] == "downloaded")
            print(f"[{len(records)}] 累计成功 {ok} | 最近: {code} {name} -> {rec['status']}", flush=True)
        time.sleep(1.5 + random.uniform(0, 1.0))  # 限速（巨潮也做IP频控）
    pd.DataFrame(records).to_csv(IDX, index=False)
    stat = pd.DataFrame(records)["status"].value_counts().to_dict()
    print("完成。状态统计:", stat)
    print("索引:", IDX)

if __name__ == "__main__":
    main()
