# -*- coding: utf-8 -*-
"""
09_make_figures.py — 论文全部图表（橙蓝配色统一方案）
======================================================
fig1  LLM 打分标签构成柱状图（application 用橙色强调）
fig2  词典法 vs LLM 法散点（词典法高估点橙色高亮）——核心论点可视化
fig3  公司级 ai_index 分布直方图（中位数橙色虚线）
fig4  事件窗 CAAR：高采纳组(橙) vs 低采纳组(蓝)，DeepSeek vs ChatGPT 安慰剂
产物: results/figures/fig*.png (300dpi)
样式: figstyle.py（配色方案1.png 提取的橙蓝方案）
"""
import sys, os
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figstyle import apply, NAVY, STEEL, SKY, ORANGE, PEACH, CREAM, GREY
plt = apply()

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
D = os.path.join(BASE, "data", "processed")
R = os.path.join(BASE, "results")
FIG = os.path.join(R, "figures")
os.makedirs(FIG, exist_ok=True)

def fig1_label_dist():
    df = pd.read_csv(os.path.join(D, "ai_adoption_llm.csv"))
    order = ["application", "strategy", "none"]
    names = {"application": "真实AI应用", "strategy": "战略口号", "none": "无关提及"}
    colors = {"application": ORANGE, "strategy": STEEL, "none": SKY}  # 关键类目橙色强调
    cnt = df["label"].value_counts().reindex(order)
    pct = cnt / cnt.sum() * 100
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    bars = ax.bar([names[o] for o in order], cnt.values,
                  color=[colors[o] for o in order], edgecolor="#4D4D4D", linewidth=0.6, width=0.62)
    for b, c, p in zip(bars, cnt.values, pct.values):
        ax.text(b.get_x() + b.get_width() / 2, c + cnt.max() * 0.02, f"{c}\n({p:.0f}%)",
                ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.set_ylabel("段落条数")
    ax.set_xlabel("")
    ax.set_ylim(0, cnt.max() * 1.18)
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig1_label_dist.png"))
    plt.close(fig)

def fig2_dict_vs_llm():
    m = pd.read_csv(os.path.join(D, "dict_vs_llm_merged.csv"), dtype={"code": str})
    over = (m["dict_index"] > 0) & (m["ai_index"] == 0)   # 词典法高估
    fig, ax = plt.subplots(figsize=(6.8, 5.4))
    lo, lim = 0.05, m["dict_index"].max() * 1.15   # 对数轴下限（dict_index=0 截断绘制）
    xd = m["dict_index"].clip(lower=lo)
    ax.scatter(xd[~over], m["ai_index"][~over], s=36, alpha=0.75,
               color=STEEL, edgecolor="white", linewidth=0.5, label="两法判定一致")
    ax.scatter(xd[over], m["ai_index"][over], s=42, alpha=0.9,
               color=ORANGE, edgecolor="white", linewidth=0.5, label=f"词典法高估（{over.sum()}家）")
    ax.axhline(0.005, color=GREY, lw=0.9)  # ai_index=0 基线
    ax.set_xscale("log")
    ax.set_xlim(lo * 0.8, lim)
    ax.set_ylim(-0.02, m["ai_index"].max() * 1.15)
    ax.set_xticks([0.05, 0.1, 0.3, 1, 3, 10])
    ax.set_xticklabels(["0", "0.1", "0.3", "1", "3", "10"])
    ax.set_xlabel("词典法 AI 采纳指数（每千字词频，对数轴）")
    ax.set_ylabel("LLM 法 AI 采纳指数（0–1）")
    ax.legend(loc="upper right")
    ax.grid(axis="both", which="major")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig2_dict_vs_llm.png"))
    plt.close(fig)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig2_dict_vs_llm.png"))
    plt.close(fig)

def fig3_ai_index_hist():
    f = pd.read_csv(os.path.join(D, "ai_adoption_firm.csv"), dtype={"code": str})
    med = f["ai_index"].median()
    fig, ax = plt.subplots(figsize=(6.6, 4.4))
    n, bins, patches = ax.hist(f["ai_index"], bins=24, edgecolor="white", linewidth=0.7)
    for p, b0 in zip(patches, bins[:-1]):   # 中位数右侧柱用橙色，左侧蓝色
        p.set_facecolor(ORANGE if b0 >= med else STEEL)
    ax.axvline(med, color=NAVY, ls="--", lw=1.4, label=f"中位数 {med:.2f}")
    ax.set_xlabel("公司 AI 采纳强度 ai_index")
    ax.set_ylabel("公司数")
    ax.legend(loc="upper right")
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig3_ai_index_hist.png"))
    plt.close(fig)

def fig4_car_event(event="deepseek"):
    """事件窗逐日累计平均AR：高采纳组(橙) vs 低采纳组(蓝)"""
    pth = os.path.join(BASE, "data", "prices", event)
    if not os.path.isdir(pth):
        print(f"fig4[{event}] 跳过：行情数据未就绪")
        return
    firm = pd.read_csv(os.path.join(D, "ai_adoption_firm.csv"), dtype={"code": str})
    med = firm["ai_index"].median()
    hi_codes = set(firm[firm["ai_index"] >= med]["code"])
    ar_hi, ar_lo = [], []
    import statsmodels.api as sm
    idx_df = pd.read_csv(os.path.join(BASE, "data", "prices", "index_000300.csv"))
    idx_df = idx_df[idx_df["window"] == event]
    for fn in os.listdir(pth):
        code = fn.replace(".csv", "")
        s = pd.read_csv(os.path.join(pth, fn), dtype={"date": str})
        mrg = s[["date", "close"]].rename(columns={"close": "cs"}).merge(
            idx_df[["date", "close"]].rename(columns={"close": "cm"}), on="date").sort_values("date").reset_index(drop=True)
        mrg["rs"], mrg["rm"] = mrg["cs"].pct_change(), mrg["cm"].pct_change()
        dates = mrg["date"].tolist()
        ev_date = "2025-01-20" if event == "deepseek" else "2022-11-30"
        if ev_date not in dates:
            after = [d for d in dates if d >= ev_date]
            if not after:
                continue
            t0 = dates.index(after[0])
        else:
            t0 = dates.index(ev_date)
        est = mrg.iloc[max(t0 - 250, 1):t0 - 20].dropna(subset=["rs", "rm"])
        if len(est) < 60:
            continue
        X = sm.add_constant(est["rm"]); model = sm.OLS(est["rs"], X).fit()
        lo_i, hi_i = max(t0 - 10, 1), min(t0 + 15, len(mrg) - 1)
        ev = mrg.iloc[lo_i:hi_i + 1].copy()
        ev["ar"] = ev["rs"] - (model.params["const"] + model.params["rm"] * ev["rm"])
        ev["t_rel"] = np.arange(lo_i, hi_i + 1) - t0
        (ar_hi if code in hi_codes else ar_lo).append(ev.set_index("t_rel")["ar"])
    if not ar_hi:
        print(f"fig4[{event}] 跳过：样本不足")
        return
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    hi_caar = pd.concat(ar_hi, axis=1).mean(axis=1).cumsum() * 100
    ax.plot(hi_caar.index, hi_caar.values, color=ORANGE, lw=2.4,
            label=f"高 AI 采纳组 (N={len(ar_hi)})", solid_capstyle="round")
    if ar_lo:
        lo_caar = pd.concat(ar_lo, axis=1).mean(axis=1).cumsum() * 100
        ax.plot(lo_caar.index, lo_caar.values, color=STEEL, lw=2.4,
                label=f"低 AI 采纳组 (N={len(ar_lo)})", solid_capstyle="round")
        ax.fill_between(lo_caar.index, lo_caar.values, hi_caar.reindex(lo_caar.index).values,
                        where=(hi_caar.reindex(lo_caar.index) >= lo_caar), color=ORANGE, alpha=0.08)
    ax.axhline(0, color=GREY, lw=0.9)
    ax.axvline(0, color="#4D4D4D", lw=1.1, ls=":")
    ev_label = "DeepSeek-R1 发布\n(2025-01-20)" if event == "deepseek" else "ChatGPT 发布\n(2022-11-30, 安慰剂)"
    ax.annotate(ev_label, xy=(0, ax.get_ylim()[1] * 0.85), ha="center", fontsize=10)
    ax.set_xlabel("相对事件日交易日 t")
    ax.set_ylabel("累计平均异常收益 CAAR (%)")
    ax.legend(loc="upper left")
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, f"fig4_car_{event}.png"))
    plt.close(fig)

if __name__ == "__main__":
    fig1_label_dist(); print("fig1 ok")
    fig2_dict_vs_llm(); print("fig2 ok")
    fig3_ai_index_hist(); print("fig3 ok")
    fig4_car_event("deepseek"); print("fig4(deepseek) ok")
    fig4_car_event("placebo"); print("fig4(placebo) ok")
    print("全部图表 ->", FIG)
