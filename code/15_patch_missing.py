# -*- coding: utf-8 -*-
"""
15_patch_missing.py — 精准补打"缺失 / 损坏"缓存段落
=====================================================================
背景：2026-11-21 04_llm_scoring.py 因读到 2 个半写 JSON 缓存（非原子写 +
进程中断所致）抛出 JSONDecodeError 而崩溃。事后全量校验发现：27,821 段中
仅 11 段没有有效缓存（2 个损坏 + 9 个从未写成功）。

本脚本：
  1) 对照 mda_paragraphs.csv 的 para_id，用单进程 awk 批量校验 llm_raw 缓存，
     找出"无有效判读"的段落（容错半写/空文件/FAILED）；
  2) 删除对应的损坏缓存，复用 04_llm_scoring.score_paragraph（同一 prompt v1、
     同一 GLM-4-Flash、temperature=0）逐个补打；
  3) 复核覆盖率并如实打印结果。

只处理缺失段落，不重复消耗已打分的 27,810 段额度。
用法： python3 15_patch_missing.py
"""
import os, json, subprocess, importlib.util
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd

CODE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(CODE, "..")
RAW_DIR = os.path.join(BASE, "data", "processed", "llm_raw")
PARA_CSV = os.path.join(BASE, "data", "processed", "mda_paragraphs.csv")
VALID_LABELS = ("application", "strategy", "none")


def valid_cache_ids():
    """返回 llm_raw 中所有『有效判读』缓存的 para_id 集合（单进程 awk 批量读）。"""
    names = sorted(f for f in os.listdir(RAW_DIR) if f.endswith(".json"))
    valid = set()
    BATCH = 3000
    for start in range(0, len(names), BATCH):
        batch = names[start:start + BATCH]
        paths = [os.path.join(RAW_DIR, f) for f in batch]
        txt = subprocess.run(
            ["awk", 'FNR==1 {print "###FILE###" FILENAME} {print}'] + paths,
            capture_output=True, text=True, timeout=180).stdout
        cur, buf = None, []

        def flush(cur, buf):
            if cur is None or not buf:
                return None
            try:
                rec = json.loads("".join(buf))
            except Exception:
                return None
            if rec.get("label") in VALID_LABELS:
                return os.path.basename(cur)[:-5]
            return None

        for line in txt.splitlines():
            if line.startswith("###FILE###"):
                v = flush(cur, buf)
                if v:
                    valid.add(v)
                cur, buf = line[len("###FILE###"):], []
            else:
                buf.append(line + "\n")
        v = flush(cur, buf)
        if v:
            valid.add(v)
    return valid


def main():
    # 复用 04 的配置与打分函数（顶层只加载 key / prompt，不执行 main）
    spec = importlib.util.spec_from_file_location(
        "scoring04", os.path.join(CODE, "04_llm_scoring.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    para = pd.read_csv(PARA_CSV, dtype={"code": str})
    all_ids = set(para["para_id"].astype(str))
    valid = valid_cache_ids()
    missing = sorted(all_ids - valid)
    print(f"段落表: {len(all_ids)} 段 | 有效缓存覆盖: {len(all_ids & valid)} | 待补: {len(missing)}")
    print("待补 para_id:", missing)
    if not missing:
        print("✅ 无缺失段落，无需补打")
        return

    # 删除损坏/失败缓存，触发重新打分（04 已改为原子写，不会再次留下半写文件）
    for pid in missing:
        p = os.path.join(RAW_DIR, pid + ".json")
        if os.path.exists(p):
            os.remove(p)
            print(f"  已删除损坏缓存: {pid}.json")

    row_by_id = {str(r.para_id): r for r in para.itertuples()}
    # 串行：补打量极小（个位数），并发反而易触发 GLM 免费额度瞬时限流
    # （2026-11-21 实测 4 并发下 9/11 段重试耗尽返回 FAILED，单段直调 200 OK）
    results = []
    with ThreadPoolExecutor(max_workers=1) as ex:
        futs = {
            ex.submit(mod.score_paragraph, pid,
                      row_by_id[pid].code, row_by_id[pid].name,
                      row_by_id[pid].paragraph): pid
            for pid in missing
        }
        for f in as_completed(futs):
            rec = f.result()
            results.append(rec)
            print(f"  {futs[f]} -> {rec.get('label')}")
    print("补打结果分布:", dict(Counter(r.get("label") for r in results)))

    # 复核
    valid2 = valid_cache_ids()
    print(f"复核: 覆盖率 {len(all_ids & valid2)}/{len(all_ids)} "
          f"({len(all_ids & valid2) / len(all_ids) * 100:.2f}%) | 仍缺 {len(all_ids - valid2)}")
    if all_ids - valid2:
        print("仍缺 para_id:", sorted(all_ids - valid2)[:20])


if __name__ == "__main__":
    main()
