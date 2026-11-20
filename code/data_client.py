# -*- coding: utf-8 -*-
"""
data_client.py — 公开数据薄客户端（东财行情 + 巨潮公告）
替代 akshare（本机安装受限），直接调用公开接口，保证可复现性。
"""
import requests, time, datetime, json, os

# 共享 Session：绕过本地代理直连（本地代理在长时间任务中会断流；
# 直连通道经 2026-11-20 验证稳定），trust_env=False 忽略环境代理变量。
SESSION = requests.Session()
SESSION.trust_env = False
NOPROXY = {"http": None, "https": None}

PYOK_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "http://www.cninfo.com.cn/new/commonUrl?url=disclosure/list/notice",
}

# ---------- 东方财富：A股全部股票列表 ----------
def fetch_all_a_shards():
    """返回 DataFrame[code, name, market]；沪深A股（含主板/创业板/科创板，北交所由下游剔除）"""
    import pandas as pd
    url = "https://push2.eastmoney.com/api/qt/clist/get"
    # 深主板A(t:6) + 创业板(t:80) + 沪主板A(t:2) + 科创板(t:23) + 北交所(t:81 s:2048)
    FS = "m:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23,m:0 t:81 s:2048"
    rows, page, pages = [], 1, None
    while pages is None or page <= pages:
        params = {
            "pn": str(page), "pz": "100", "po": "1", "np": "1",
            "fltt": "2", "invt": "2", "fid": "f12", "fs": FS, "fields": "f12,f14",
        }
        r = requests.get(url, params=params, timeout=25, headers={"User-Agent": PYOK_HEADERS["User-Agent"]})
        d = r.json()["data"]
        if d is None:
            break
        pages = (d["total"] + 99) // 100
        for it in d.get("diff", []):
            code = str(it["f12"]).zfill(6)
            mkt = 1 if code.startswith(("6", "9")) else 0
            rows.append({"code": code, "name": it["f14"], "market": mkt})
        page += 1
        time.sleep(0.25)
    df = pd.DataFrame(rows).drop_duplicates("code")
    return df

# ---------- 行情主通道：腾讯 ifzq（2026-11-20 验证可用）----------
# 东财 push2his 对本机 IP 限流后，行情改用腾讯接口；东财保留为兜底。
_TX_LAST = 0.0

def _pace_tx():
    global _TX_LAST
    wait = 0.15 - (time.time() - _TX_LAST)
    if wait > 0:
        time.sleep(wait)
    _TX_LAST = time.time()

def _tx_symbol(code):
    """A股代码 → 腾讯/新浪通用符号（sh/sz 前缀）"""
    code = str(code).zfill(6)
    if code.startswith(("6", "9", "5")):
        return "sh" + code
    if code.startswith(("0", "2", "3")):
        return "sz" + code
    return "sz" + code

def _fetch_kline_sina(symbol, beg, end, datalen=1500):
    """新浪日K兜底（scale=240）。注意：新浪返回不复权价格；指数无需复权，
    个股仅在腾讯通道失败时使用（跨除权日会有微小跳变，论文中如实说明）。"""
    import pandas as pd, re, json
    url = ("https://quotes.sina.cn/cn/api/jsonp_v2.php/var%5F=/CN_MarketDataService.getKLineData"
           f"?symbol={symbol}&scale=240&ma=no&datalen={datalen}")
    _pace_tx()
    r = SESSION.get(url, timeout=20, headers={"User-Agent": PYOK_HEADERS["User-Agent"]}, proxies=NOPROXY)
    m = re.search(r"\[.*\]", r.text, re.S)
    arr = json.loads(m.group(0)) if m else []
    b, e = f"{beg[:4]}-{beg[4:6]}-{beg[6:]}", f"{end[:4]}-{end[4:6]}-{end[6:]}"
    rows, prev = [], None
    for it in arr:
        if not (b <= it["day"] <= e):
            continue
        o, c, h, l = (float(it["open"]), float(it["close"]),
                      float(it["high"]), float(it["low"]))
        rows.append({"date": it["day"], "open": o, "close": c, "high": h, "low": l,
                     "volume": float(it.get("volume") or "nan"), "amount": float("nan"),
                     "pct_chg": (c / prev - 1) * 100 if prev else float("nan")})
        prev = c
    return pd.DataFrame(rows)

def _fetch_daily_kline_tx(code, beg, end):
    """腾讯日K（前复权）。beg/end 为 YYYYMMDD。返回与东财版同构的 DataFrame。"""
    import pandas as pd
    sym = _tx_symbol(code)
    b = f"{beg[:4]}-{beg[4:6]}-{beg[6:]}"
    e = f"{end[:4]}-{end[4:6]}-{end[6:]}"
    url = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
    params = {"param": f"{sym},day,{b},{e},800,qfq"}
    _pace_tx()
    r = SESSION.get(url, params=params, timeout=20,
                    headers={"User-Agent": PYOK_HEADERS["User-Agent"]}, proxies=NOPROXY)
    d = r.json()
    if d.get("code") != 0:
        raise RuntimeError(f"tx kline error {sym}: {d.get('msg')}")
    data = (d.get("data") or {}).get(sym) or {}
    kl = data.get("qfqday") or data.get("day") or []
    rows, prev = [], None
    for p in kl:
        o, c, h, l = float(p[1]), float(p[2]), float(p[3]), float(p[4])
        vol = float(p[5]) if len(p) > 5 else float("nan")
        rows.append({"date": p[0], "open": o, "close": c, "high": h, "low": l,
                     "volume": vol, "amount": float("nan"),
                     "pct_chg": (c / prev - 1) * 100 if prev else float("nan")})
        prev = c
    return pd.DataFrame(rows)

# ---------- 东方财富：日K线（兜底通道） ----------
def fetch_daily_kline(code, beg="20241101", end="20250331", market=None, fqt=1):
    """返回 DataFrame[date, open, close, high, low, volume, amount, pct_chg]（前复权）。
    主用腾讯接口；失败时回退东财。"""
    import pandas as pd
    try:
        return _fetch_daily_kline_tx(code, beg, end)
    except Exception:
        pass
    try:
        return _fetch_kline_sina(_tx_symbol(code), beg, end)
    except Exception:
        pass
    if market is None:
        market = 1 if code.startswith(("6", "9", "5")) else 0
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "secid": f"{market}.{code}",
        "fields1": "f1,f2,f3,f4,f5,f6",
        "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
        "klt": "101", "fqt": str(fqt), "beg": beg, "end": end,
    }
    r = _get_with_backoff(url, params=params, timeout=25, kind="list")
    d = r.json().get("data") or {}
    kl = d.get("klines") or []
    rows = []
    for line in kl:
        p = line.split(",")
        rows.append({"date": p[0], "open": float(p[1]), "close": float(p[2]),
                     "high": float(p[3]), "low": float(p[4]),
                     "volume": float(p[5]), "amount": float(p[6]), "pct_chg": float(p[8])})
    return pd.DataFrame(rows)

# ---------- 指数日K线（市场基准）：腾讯主通道 + 东财兜底 ----------
def fetch_index_kline(index_code, beg="20241101", end="20250331"):
    """index_code: '000300'=沪深300, '000001'=上证指数, '399001'=深成指, '000905'=中证500
    注意：指数代码不能套用股票的交易所前缀规则（000300 是沪市指数而非深市股票）"""
    import pandas as pd
    IDX_SYMBOL = {"000300": "sh000300", "000001": "sh000001", "000905": "sh000905",
                  "399001": "sz399001", "399006": "sz399006", "399300": "sz399300"}
    sym = IDX_SYMBOL.get(index_code, _tx_symbol(index_code))
    b = f"{beg[:4]}-{beg[4:6]}-{beg[6:]}"
    e = f"{end[:4]}-{end[4:6]}-{end[6:]}"
    try:
        url = "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get"
        params = {"param": f"{sym},day,{b},{e},800"}
        _pace_tx()
        r = SESSION.get(url, params=params, timeout=20,
                        headers={"User-Agent": PYOK_HEADERS["User-Agent"]}, proxies=NOPROXY)
        d = r.json()
        if d.get("code") == 0:
            kl = ((d.get("data") or {}).get(sym) or {}).get("day") or []
            rows = [{"date": p[0], "open": float(p[1]), "close": float(p[2]),
                     "high": float(p[3]), "low": float(p[4])} for p in kl]
            if rows:
                return pd.DataFrame(rows)
    except Exception:
        pass
    # 新浪兜底（2026-11-20 验证：datalen=1500 覆盖 2020-09 起全部两个事件窗口）
    try:
        df = _fetch_kline_sina(sym, beg, end)
        if len(df) > 30:
            return df[["date", "open", "close", "high", "low"]]
    except Exception:
        pass
    # 东财兜底
    secid = {"000001": "1.000001", "399001": "0.399001", "399006": "0.399006",
             "000300": "1.000300", "000905": "1.000905"}.get(index_code)
    url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    params = {
        "secid": secid, "fields1": "f1,f2,f3", "fields2": "f51,f52,f53,f54,f55",
        "klt": "101", "fqt": "1", "beg": beg, "end": end,
    }
    r = requests.get(url, params=params, timeout=25, headers={"User-Agent": PYOK_HEADERS["User-Agent"]})
    d = r.json().get("data") or {}
    rows = []
    for line in (d.get("klines") or []):
        p = line.split(",")
        rows.append({"date": p[0], "open": float(p[1]), "close": float(p[2]),
                     "high": float(p[3]), "low": float(p[4])})
    return pd.DataFrame(rows)

# ---------- 东方财富：公告检索（替代巨潮，后者有IP频控） ----------
EM_HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

# ---- 限速器：防止触发东财IP风控（2026-11-20晚 burst 下载曾被限流）----
import random as _random
_MIN_INTERVAL = {"list": 1.2, "content": 1.5, "cdn": 1.0}
_LAST_TS = {"list": 0.0, "content": 0.0, "cdn": 0.0}

def _pace(kind):
    wait = _MIN_INTERVAL[kind] - (time.time() - _LAST_TS[kind]) + _random.uniform(0.2, 0.8)
    if wait > 0:
        time.sleep(wait)
    _LAST_TS[kind] = time.time()

def _get_with_backoff(url, headers=None, params=None, timeout=25, kind="list", max_retry=4):
    """带指数退避的 GET：连接错误时 5s→15s→45s 退避，全失败抛异常。"""
    delays = [5, 15, 45, 90]
    for i in range(max_retry + 1):
        _pace(kind)
        try:
            r = SESSION.get(url, params=params, timeout=timeout, headers=headers, proxies=NOPROXY)
            if r.status_code in (403, 429):        # 明确限流：长冷却
                time.sleep(delays[-1])
                continue
            return r
        except requests.exceptions.ConnectionError:
            if i == max_retry:
                raise
            time.sleep(delays[min(i, len(delays) - 1)])
    raise requests.exceptions.ConnectionError("rate-limit cooldown exhausted")

def find_annual_report_em(code, year=2023, max_pages=6, page_size=100):
    """在东财公告列表（财报类 f_node=1）中翻页定位 {year}年年度报告。
    标题格式多样（"公司:2023年年度报告"/"公司:某某有限公司2023年年度报告"），
    用子串匹配 target 并排除摘要/英文/更正类。返回 dict 或 None。"""
    url = "https://np-anotice-stock.eastmoney.com/api/security/ann"
    target = f"{year}年年度报告"
    BAD = ("摘要", "英文", "更正", "问询", "摘要(", "补充")
    best, best_rank = None, -1
    for page in range(1, max_pages + 1):
        params = {"page_size": str(page_size), "page_index": str(page), "ann_type": "A",
                  "client_source": "web", "stock_list": code, "f_node": 1, "s_node": 0}
        try:
            r = _get_with_backoff(url, headers=EM_HEADERS, params=params, kind="list")
            lst = (r.json().get("data") or {}).get("list") or []
        except Exception:
            time.sleep(2); continue
        if not lst:
            break
        for it in lst:
            t = (it.get("title") or "")
            name_part = t.split(":", 1)[-1].split("：", 1)[-1]  # 兼容中英文冒号
            if target not in name_part or any(b in name_part for b in BAD):
                continue
            # 排序优先级：完全一致 > 更新版 > 其他
            if name_part == target:
                rank = 3
            elif "更新" in name_part or "修订" in name_part:
                rank = 2
            else:
                rank = 1
            if rank > best_rank:
                best, best_rank = it, rank
        dates = [(it.get("notice_date") or "")[:10] for it in lst]
        if dates and dates[-1] < f"{year+1}-01-01":
            break
    if best:
        return {"art_code": best["art_code"], "title": best["title"],
                "notice_date": (best.get("notice_date") or "")[:10]}
    return None

def em_announcement_pdf_url(art_code):
    """东财公告详情接口 → PDF 附件地址"""
    url = "https://np-cnotice-stock.eastmoney.com/api/content/ann"
    r = _get_with_backoff(url, params={"art_code": art_code, "client_source": "web", "page_index": 1},
                          timeout=25, kind="content")
    d = (r.json().get("data") or {})
    for a in (d.get("attach_list") or []):
        u = a.get("attach_url")
        if u and u.lower().endswith(".pdf"):
            return u
        if u and ".pdf" in u:
            return u
    return d.get("attach_url_guba") or None

def download_pdf(url, out_path, retries=3):
    for i in range(retries):
        try:
            _pace("cdn")
            r = SESSION.get(url, timeout=180, headers=EM_HEADERS, proxies=NOPROXY)
            if r.status_code == 200 and len(r.content) > 10000:
                with open(out_path, "wb") as f:
                    f.write(r.content)
                return True
        except Exception:
            pass
        time.sleep(3)
    return False

# ---------- 巨潮资讯（备用通道，注意IP频控） ----------
# 巨潮限速器（2026-11-20晚验证恢复可用；东财被限流期间主用巨潮通道）
_LAST_CN = {"query": 0.0, "cdn": 0.0}
def _pace_cn(kind):
    wait = (1.5 if kind == "query" else 1.0) - (time.time() - _LAST_CN[kind]) + _random.uniform(0.3, 1.0)
    if wait > 0:
        time.sleep(wait)
    _LAST_CN[kind] = time.time()

def query_annual_report(code, org_id, year=2023, page_size=30):
    """返回 [ {title, adjunctUrl, time} ]；adjunctUrl 拼在 static.cninfo.com.cn/ 后即PDF地址"""
    url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
    data = {
        "pageNum": "1", "pageSize": str(page_size),
        "column": "szse", "tabName": "fulltext", "plate": "",
        "stock": f"{code},{org_id}", "searchkey": "", "secid": "",
        "category": "category_ndbg_szsh", "trade": "",
        "seDate": f"{year+1}-01-01~{year+1}-06-30",
        "sortName": "", "sortType": "", "isHLtitle": "true",
    }
    _pace_cn("query")
    r = SESSION.post(url, data=data, timeout=25, headers=PYOK_HEADERS, proxies=NOPROXY)
    d = r.json()
    out = []
    for a in (d.get("announcements") or []):
        title = (a.get("announcementTitle") or "").replace("<em>", "").replace("</em>", "")
        out.append({
            "title": title,
            "adjunctUrl": a.get("adjunctUrl"),
            "time": datetime.datetime.fromtimestamp(a["announcementTime"] / 1000).strftime("%Y-%m-%d"),
        })
    return out

# ---------- 巨潮资讯：code -> orgId ----------
def cninfo_orgid(code):
    url = "http://www.cninfo.com.cn/new/information/topSearch/detailOfQuery"
    data = {"keyWord": code, "maxSecNum": 10, "maxListNum": 5}
    try:
        r = requests.post(url, data=data, timeout=20, headers=PYOK_HEADERS)
        for it in (r.json() or []):
            if it.get("code") == code:
                return it.get("orgId")
    except Exception:
        return None
    return None

def download_cninfo_pdf(adjunct_url, out_path, retries=3):
    for i in range(retries):
        try:
            _pace_cn("cdn")
            r = SESSION.get("https://static.cninfo.com.cn/" + adjunct_url, timeout=120,
                            headers={"User-Agent": PYOK_HEADERS["User-Agent"]}, proxies=NOPROXY)
            if r.status_code == 200 and len(r.content) > 10000:
                with open(out_path, "wb") as f:
                    f.write(r.content)
                return True
            if r.status_code in (403, 429):
                time.sleep(60)   # 巨潮限流长冷却
        except Exception:
            time.sleep(5)
    return False
