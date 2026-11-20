# -*- coding: utf-8 -*-
"""
figstyle.py — 论文图表统一样式（橙蓝配色方案，来源：配色方案1.png）
=====================================================================
蓝系: NAVY #1F4E79（深）/ STEEL #376D9E（中）/ SKY #C2DAEF（浅）
橙系: ORANGE #ED7D31（亮，强调色）/ PEACH #F2A571（浅）/ CREAM #FDEADC（奶油底）
约定: 强调/处理组/关键发现用橙色，基准/对照组用蓝色。
"""
import matplotlib
matplotlib.use("Agg")

NAVY   = "#1F4E79"
STEEL  = "#376D9E"
SKY    = "#C2DAEF"
ORANGE = "#ED7D31"
PEACH  = "#F2A571"
CREAM  = "#FDEADC"
GREY   = "#9AA5AF"

SEQ_BLUE = [NAVY, STEEL, SKY]            # 蓝→浅蓝
SEQ_ORANGE = [ORANGE, PEACH, CREAM]      # 橙→奶油
DIVERGE = [NAVY, STEEL, "#E8EEF4", PEACH, ORANGE]  # 蓝-橙发散

def apply():
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.sans-serif": ["PingFang SC", "Hiragino Sans GB", "Arial Unicode MS", "Songti SC"],
        "axes.unicode_minus": False,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": "#4D4D4D",
        "axes.linewidth": 0.9,
        "axes.grid": True,
        "grid.color": "#E6E6E6",
        "grid.linewidth": 0.6,
        "grid.linestyle": "-",
        "axes.axisbelow": True,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.color": "#333333",
        "ytick.color": "#333333",
        "axes.labelsize": 12,
        "axes.labelweight": "bold",
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "legend.frameon": False,
        "legend.fontsize": 10.5,
        "font.size": 11,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
    })
    return plt
