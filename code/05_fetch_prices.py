# -*- coding: utf-8 -*-
"""
05_fetch_prices.py — 事件窗口行情获取（个股 + 沪深300基准）
设计（对标事件研究惯例）:
  主事件: DeepSeek-R1 发布 2025-01-20
    估计窗: 事件前 [-250, -21] 个交易日（市场模型参数估计）
    事件窗: [-10, +15] 个交易日
  安慰剂: ChatGPT 发布 2022-11-30（同一公司、同一窗口结构）
用法:
    python 05_fetch_prices.py --codes-from firm   # 用已打分公司清单
    python 05_fetch_prices.py --codes-from sample # 用全部已下载年报的公司
    python 05_fetch_prices.py --limit 20          # 试点
产物:
    data/prices/index_000300.csv                  沪深300日K
    data/prices/deepseek/{code}.csv               主事件窗口行情
    data/prices/placebo/{code}.csv                ChatGPT安慰剂窗口行情
"""
import sys, os, argparse, time
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from data_client import fetch_daily_kline, fetch_index_kline

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
P_DIR = os.path.join(BASE, "data", "prices")

WINDOWS = {
    "deepseek": {"beg": "20240601", "end": "20250331"},   # 估计窗+事件窗
    "placebo":  {"beg": "20220601", "end": "20230331"},
}

def codes_from(source, limit):
    if source == "firm":
        df = pd.read_csv(os.path.join(BASE, "data", "processed", "ai_adoption_firm.csv"), dtype={"code": str})
        codes = df["code"].tolist()
    else:
        idx = pd.read_csv(os.path.join(BASE, "data", "processed", "report_index.csv"), dtype={"code": str})
        codes = idx[idx["status"] == "downloaded"]["code"].tolist()
    return codes[:limit] if limit else codes

def fetch_one(code):
    """拉取单只个股两个窗口行情；已有文件直接跳过（断点续跑）。返回是否全部成功。"""
    all_ok = True
    for wname, w in WINDOWS.items():
        out = os.path.join(P_DIR, wname, f"{code}.csv")
        if os.path.exists(out):
            continue
        try:
            df = fetch_daily_kline(code, w["beg"], w["end"])
            if len(df) > 30:
                df.to_csv(out, index=False)
            else:
                all_ok = False  # 数据过短（如事件期停牌/新股）
        except Exception:
            all_ok = False
        time.sleep(0.5)
    return all_ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--codes-from", default="sample", choices=["firm", "sample"])
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=6,
                    help="并发数（腾讯行情接口保守限速；2026-11-21 实测 6 并发无限流）")
    args = ap.parse_args()

    codes = codes_from(args.codes_from, args.limit)
    print(f"目标 {len(codes)} 只 | 并发 {args.workers}")

    os.makedirs(os.path.join(P_DIR, "deepseek"), exist_ok=True)
    os.makedirs(os.path.join(P_DIR, "placebo"), exist_ok=True)

    # 基准指数（沪深300）两个窗口
    idx_path = os.path.join(P_DIR, "index_000300.csv")
    if not os.path.exists(idx_path):
        idx_df = pd.concat([fetch_index_kline("000300", w["beg"], w["end"]).assign(window=k)
                            for k, w in WINDOWS.items()])
        idx_df.to_csv(idx_path, index=False)
        print("沪深300基准获取完成:", len(idx_df), "行")

    # 并发拉取：串行版实测约 40 家/分钟（每家两窗口 + 0.5s 限速），
    # 3,460 家需 40+ 分钟；并发后已有文件仍直接跳过，仅对缺口发请求。
    ok = err = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(fetch_one, c) for c in codes]
        for i, fut in enumerate(as_completed(futs), 1):
            all_ok = fut.result()
            ok += all_ok
            err += (not all_ok)
            if i % 100 == 0:
                print(f"[{i}/{len(codes)}] 成功{ok} 异常{err}", flush=True)
    print(f"\n完成: 成功 {ok}, 异常 {err}（异常多为新股/长期停牌，论文中说明剔除规则）")
    print("行情目录:", P_DIR)

if __name__ == "__main__":
    main()
