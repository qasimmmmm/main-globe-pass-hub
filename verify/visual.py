#!/usr/bin/env python3
"""Visual comparison of full-page screenshots: RMSE + mean abs diff on top 2000px."""
import os, json
from PIL import Image, ImageChops
import math

OUT = "/mnt/agents/output/verify"
ROUTES = ["/", "/faqs", "/about-us", "/contact-us", "/privacy-policy",
          "/terms-and-conditions-of-service", "/refund-policy",
          "/solicitud-eta-canada", "/canada-eta-application", "/canada-eta",
          "/canada-study-permit", "/canada-visitor-visa",
          "/usa-esta-application", "/canada-eta/apply", "/application/eta",
          "/login-gest"]

def name(route):
    return "index" if route == "/" else route.strip("/").replace("/", "_")

def compare(r):
    n = name(r)
    lp = f"{OUT}/shots/{n}_live.png"
    op = f"{OUT}/shots/{n}_local.png"
    if not (os.path.exists(lp) and os.path.exists(op)):
        return {"error": "missing screenshot"}
    a = Image.open(lp).convert("RGB")
    b = Image.open(op).convert("RGB")
    # resize both to width 720 for speed
    w = 720
    ah = int(a.height * w / a.width)
    bh = int(b.height * w / b.width)
    a = a.resize((w, ah), Image.LANCZOS)
    b = b.resize((w, bh), Image.LANCZOS)
    top = min(2000, ah, bh)
    a_top = a.crop((0, 0, w, top))
    b_top = b.crop((0, 0, w, top))
    diff = ImageChops.difference(a_top, b_top)
    h = diff.histogram()
    # RMS across channels
    sq = sum(value * ((idx % 256) ** 2) for idx, value in enumerate(h))
    n_px = w * top * 3
    rmse = math.sqrt(sq / n_px)
    # mean abs diff
    tot = sum(value * (idx % 256) for idx, value in enumerate(h))
    mad = tot / n_px
    # pct of pixels that differ noticeably (>24 on any channel)
    stat = diff.convert("L").point(lambda x: 255 if x > 24 else 0)
    frac_changed = sum(1 for px in stat.getdata() if px > 0) / (w * top)
    # full height comparison where heights equal
    full = None
    if ah == bh:
        d2 = ImageChops.difference(a, b)
        h2 = d2.histogram()
        sq2 = sum(value * ((idx % 256) ** 2) for idx, value in enumerate(h2))
        full = math.sqrt(sq2 / (w * ah * 3))
    # save diff image for inspection
    diff.save(f"{OUT}/shots/{n}_diff.png")
    return {"live_h_orig": Image.open(lp).height, "local_h_orig": Image.open(op).height,
            "cmp_width": w, "cmp_top_px": top, "rmse_top": round(rmse, 2),
            "mad_top": round(mad, 3), "frac_px_changed_gt24": round(frac_changed, 4),
            "rmse_full_if_same_h": (round(full, 2) if full is not None else None)}

results = {}
for r in ROUTES:
    res = compare(r)
    results[r] = res
    print(f"{r:40s} rmse_top={res.get('rmse_top')} mad={res.get('mad_top')} changed={res.get('frac_px_changed_gt24')} liveH={res.get('live_h_orig')} localH={res.get('local_h_orig')}")

with open(f"{OUT}/visual.json", "w") as f:
    json.dump(results, f, indent=1)
