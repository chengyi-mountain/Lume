#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lume 资源链接体检（白名单卡口）
------------------------------------------------
规则（见 tools/link-policy.json）：
 1. 每条资源若带 u（链接），其域名必须命中 whitelist；
 2. 命中 blacklist（电商/付费课/聚合搜索页）任何一段，一律判失败（黑名单优先）；
 3. 每个科目至少要有 1 条「可点击且合规」的直达链接，否则失败；
 4. --net 时额外做存活检测（HEAD，失败回退 GET），404/410 判死链。

用法：
    python tools/link-audit.py            # 只做静态规则校验
    python tools/link-audit.py --net      # 附带线上存活检测
退出码：0 全绿 / 1 有问题
"""
import io, json, os, re, sys, shutil, subprocess, socket, time, urllib.request, urllib.parse
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "index.html")
POLICY = os.path.join(ROOT, "tools", "link-policy.json")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"


def load_policy():
    p = json.load(io.open(POLICY, encoding="utf-8"))
    return p["whitelist"], p["blacklist"]


def parse_resources():
    h = io.open(SRC, encoding="utf-8").read()
    i = h.find("window.SUBJECTS")
    j = h.find("function renderGrid", i)
    block = h[i:j]
    rows = [(m.start(), m.group(1)) for m in re.finditer(r'id:"([a-z0-9\-]+)"', block)]
    subs = []
    for k, (pos, sid) in enumerate(rows):
        end = rows[k + 1][0] if k + 1 < len(rows) else len(block)
        seg = block[pos:end]
        m = re.search(r"(  resources:\[\n)(.+?)(\n  \])", seg, re.S)
        items = []
        if m:
            for line in m.group(2).splitlines():
                line = line.strip().rstrip(",")
                if not line.startswith("{"):
                    continue
                t = re.search(r't:"([^"]*)"', line)
                d = re.search(r'd:"([^"]*)"', line)
                u = re.search(r'u:"([^"]*)"', line)
                hh = re.search(r'h:"([^"]*)"', line)
                items.append({
                    "t": t.group(1) if t else "",
                    "d": d.group(1) if d else "",
                    "u": u.group(1) if u else None,
                    "h": hh.group(1) if hh else None,
                })
        subs.append({"id": sid, "res": items})
    return subs


def host_of(url):
    try:
        return urllib.parse.urlparse(url).hostname or ""
    except Exception:
        return ""


def check_rule(u, white, black):
    """返回 (ok, 原因)"""
    host = host_of(u).lower()
    if not host:
        return False, "URL 无法解析"
    for b in black:
        if b in u.lower() or b in host:
            return False, "命中黑名单 " + b
    for w in white:
        if w in host:
            return True, ""
    return False, "域名不在白名单 " + host


def _curl_code(url, timeout=25):
    exe = shutil.which("curl")
    if not exe:
        return None
    try:
        p = subprocess.run(
            [exe, "-sS", "-o", os.devnull, "-w", "%{http_code}", "-L",
             "--max-time", str(timeout), "-A", UA, url],
            capture_output=True, text=True, timeout=timeout + 5)
        code = (p.stdout or "").strip()[-3:]
        return int(code) if code.isdigit() else 0
    except Exception:
        return 0


def alive(url, timeout=25):
    """优先用系统 curl（证书与 HTTP/2 行为更接近浏览器），失败再退回 urllib。
    404/410 判死链；403/429、超时、连接重置一律算「本机不可达」，交人工复核。"""
    code = _curl_code(url, timeout)
    if code is None:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                code = r.status
        except urllib.error.HTTPError as e:
            code = e.code
        except Exception:
            code = 0
    if code and code not in (404, 410):
        return code, True
    return code or 0, False


def check_alive(url, tries=3):
    """网络抖动很常见（DNS 偶发解析失败、连接被重置），失败重试 2 次再定论。"""
    code, ok = 0, False
    for i in range(tries):
        code, ok = alive(url)
        if ok:
            return code, ok
        if code in (404, 410):
            return code, ok
        time.sleep(2)
    return code, ok


def main():
    net = "--net" in sys.argv
    white, black = load_policy()
    subs = parse_resources()
    total = sum(len(s["res"]) for s in subs)
    click = [r for s in subs for r in s["res"] if r["u"]]
    fails, warns = [], []

    for s in subs:
        ok_links = []
        for r in s["res"]:
            if not r["u"]:
                if not r["h"]:
                    warns.append("%s / %s：无链接但也没有提示文案" % (s["id"], r["t"]))
                continue
            ok, why = check_rule(r["u"], white, black)
            if ok:
                ok_links.append(r)
            else:
                fails.append("%s / %s → %s（%s）" % (s["id"], r["t"], r["u"], why))
        if not ok_links:
            fails.append("%s：该科目没有任何合规直达链接" % s["id"])

    print("科目 %d，资源 %d，可点击链接 %d，无链接 %d" % (
        len(subs), total, len(click), total - len(click)))

    if net and click:
        print("存活检测中（%d 条）…" % len(click))
        with ThreadPoolExecutor(max_workers=6) as ex:
            res = list(ex.map(lambda r: (r, check_alive(r["u"])), click))
        for r, (code, ok) in res:
            if ok:
                continue
            if code in (404, 410):
                fails.append("死链 %s（HTTP %s）" % (r["u"], code))
            else:
                warns.append("本机网络不可达（HTTP %s），需人工复核：%s / %s → %s" % (code, "?", r["t"], r["u"]))

    if fails:
        print("\n[FAIL] %d 项：" % len(fails))
        for f in fails:
            print("  -", f)
    if warns:
        print("\n[WARN] %d 项：" % len(warns))
        for w in warns:
            print("  -", w)
    if not fails:
        print("\n[PASS] 白名单卡口全部通过")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
