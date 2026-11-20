# -*- coding: utf-8 -*-
"""
07_cross_section.py — 横截面回归：什么公司对 DeepSeek 冲击反应更强？
====================================================================
模型: CAR_w = b0 + b1*ai_index + b2*ln(事件前成交额) + b3*事件前波动率 + e
特征（均来自价格数据，避免额外接口依赖）:
    size_proxy  = ln(事件窗前[-250,-21]日均成交额, 千元)
    vol_pre     = 事件前估计窗日收益标准差
    beta        = 06 步骤估出的市场模型 beta
    ai_index    = LLM 度量 AI 采纳强度（0~1）
产物:
    results/table4_cross_section.csv  每个CAR窗口的横截面回归表
"""
import sys, os
import numpy as np
import pandas as pd
import statsmodels.api as sm

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
R_DIR = os.path.join(BASE, "results")
P_DIR = os.path.join(BASE, "data", "prices")
os.makedirs(R_DIR, exist_ok=True)

EVENT_DATE = "2025-01-20"

def build_features(code):
    pth = os.path.join(P_DIR, "deepseek", f"{code}.csv")
    if not os.path.exists(pth):
        return None
    df = pd.read_csv(pth, dtype={"date": str}).sort_values("date").reset_index(drop=True)
    dates = df["date"].tolist()
    if EVENT_DATE not in dates:
        after = [d for d in dates if d >= EVENT_DATE]
        if not after:
            return None
        t0 = dates.index(after[0])
    else:
        t0 = dates.index(EVENT_DATE)
    pre = df.iloc[max(t0 - 250, 0):t0 - 20]
    if len(pre) < 60:
        return None
    ret = pre["close"].pct_change().dropna()
    # 腾讯行情无成交额字段：用 成交量(手)×100股×收盘价 合成成交额代理（元）
    amt = (pre["volume"].fillna(0) * 100.0 * pre["close"]).mean()
    return {
        "size_proxy": np.log(amt / 1000.0 + 1),   # 千元
        "vol_pre": ret.std(),
        "mom_pre": (pre["close"].iloc[-1] / pre["close"].iloc[0] - 1) if len(pre) > 1 else np.nan,
    }

def main():
    panel = pd.read_csv(os.path.join(R_DIR, "car_panel_deepseek.csv"), dtype={"code": str})
    print(f"面板样本: {len(panel)}")
    feats = []
    for code in panel["code"]:
        f = build_features(code) or {}
        feats.append({"code": code, **f})
    df = panel.merge(pd.DataFrame(feats), on="code", how="left").dropna(
        subset=["size_proxy", "vol_pre"])

    windows = [c for c in df.columns if c.startswith("CAR[")]
    rows = []
    for w in windows:
        sub = df.dropna(subset=[w])
        X = sub[["ai_index", "size_proxy", "vol_pre", "mom_pre"]].copy()
        X = sm.add_constant(X)
        y = sub[w]
        m = sm.OLS(y, X).fit()
        for var in ["ai_index", "size_proxy", "vol_pre", "mom_pre"]:
            rows.append({"CAR_window": w, "variable": var, "coef": m.params[var],
                         "se": m.bse[var], "t": m.tvalues[var], "p": m.pvalues[var],
                         "r2": m.rsquared, "n": int(m.nobs)})
        print(f"\n--- {w}: ai_index coef={m.params['ai_index']:.4f} "
              f"(t={m.tvalues['ai_index']:.2f}, p={m.pvalues['ai_index']:.4f}), R2={m.rsquared:.3f}, N={int(m.nobs)}")
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(R_DIR, "table4_cross_section.csv"), index=False)
    print("\n已写入 results/table4_cross_section.csv")
    print(out[out.variable == "ai_index"][["CAR_window", "coef", "t", "p"]].round(4).to_string(index=False))

if __name__ == "__main__":
    main()
