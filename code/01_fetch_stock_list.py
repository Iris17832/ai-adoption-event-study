# -*- coding: utf-8 -*-
"""
01_fetch_stock_list.py — 获取A股股票列表并落盘
产物: data/processed/stock_list.csv
"""
import sys, os, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from data_client import fetch_all_a_shards

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(BASE, "data", "processed", "stock_list.csv")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

force = "--force" in sys.argv
if os.path.exists(OUT) and not force:
    print(f"已存在 {OUT}，跳过（--force 强制刷新）")
    df = pd.read_csv(OUT, dtype={"code": str})
else:
    df = fetch_all_a_shards()
    df.to_csv(OUT, index=False)
print(f"A股股票列表: {len(df)} 只")
print(df.head())
