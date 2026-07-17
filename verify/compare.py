#!/usr/bin/env python3
"""Compare live globepasshub.com vs local mirror page by page."""
import json, sys, time, difflib, os
from playwright.sync_api import sync_playwright

LIVE = "https://globepasshub.com"
LOCAL = "http://127.0.0.1:8321"
OUT = "/mnt/agents/output/verify"
os.makedirs(OUT + "/shots", exist_ok=True)

ROUTES = ["/", "/faqs", "/about-us", "/contact-us", "/privacy-policy",
          "/terms-and-conditions-of-service", "/refund-policy",
          "/solicitud-eta-canada", "/canada-eta-application", "/canada-eta",
          "/canada-study-permit", "/canada-visitor-visa",
          "/usa-esta-application", "/canada-eta/apply", "/application/eta",
          "/login-gest"]

def name(route):
    return "index" if route == "/" else route.strip("/").replace("/", "_")

def grab(page, url, shot_path, collect_console=False):
    console_msgs = []
    if collect_console:
        page.on("console", lambda m: console_msgs.append((m.type, m.text[:300])) if m.type in ("error",) else None)
        page.on("pageerror", lambda e: console_msgs.append(("pageerror", str(e)[:300])))
    try:
        page.goto(url, wait_until="load", timeout=60000)
    except Exception as e:
        return {"error": f"goto failed: {e}", "console": console_msgs}
    page.wait_for_timeout(2000)
    # scroll through page to trigger lazy loading, then back to top
    try:
        page.evaluate("""async () => {
            await new Promise(res => {
                let y = 0;
                const step = () => {
                    y += 600; window.scrollTo(0, y);
                    if (y < document.body.scrollHeight) setTimeout(step, 60);
                    else { window.scrollTo(0,0); setTimeout(res, 400); }
                }; step();
            });
        }""")
    except Exception:
        pass
    page.wait_for_timeout(800)
    try:
        text = page.evaluate("() => { const el = document.querySelector('#app'); return el ? el.innerText : document.body.innerText; }")
    except Exception as e:
        text = ""
    try:
        broken = page.evaluate("""() => {
            const out = [];
            document.querySelectorAll('img').forEach(im => {
                if (im.complete && im.naturalWidth === 0) out.push(im.currentSrc || im.src || '(no src)');
            });
            return out;
        }""")
    except Exception:
        broken = ["<eval failed>"]
    try:
        height = page.evaluate("() => document.body ? document.body.scrollHeight : 0")
    except Exception:
        height = 0
    try:
        title = page.title()
    except Exception:
        title = ""
    try:
        page.screenshot(path=shot_path, full_page=True, timeout=60000)
    except Exception as e:
        # retry viewport-only screenshot
        try:
            page.screenshot(path=shot_path, full_page=False)
        except Exception as e2:
            return {"error": f"screenshot failed: {e} / {e2}", "text": text, "broken": broken, "console": console_msgs, "height": height, "title": title}
    return {"text": text, "broken": broken, "console": console_msgs, "height": height, "title": title}

def main():
    routes = ROUTES
    if len(sys.argv) > 1:
        routes = [r for r in ROUTES if r in sys.argv[1:]]
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/chromium",
                                    args=["--no-sandbox", "--disable-dev-shm-usage"])
        ctx = browser.new_context(viewport={"width": 1440, "height": 900},
                                  user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36")
        page = ctx.new_page()
        for r in routes:
            n = name(r)
            print(f"=== {r} ===", flush=True)
            live = grab(page, LIVE + r + ("/" if r != "/" else ""), f"{OUT}/shots/{n}_live.png")
            print(f"  live: text={len(live.get('text',''))} h={live.get('height')} broken={len(live.get('broken',[]))} err={live.get('error','-')}", flush=True)
            local = grab(page, LOCAL + r + ("/" if r != "/" else ""), f"{OUT}/shots/{n}_local.png", collect_console=True)
            print(f"  local: text={len(local.get('text',''))} h={local.get('height')} broken={len(local.get('broken',[]))} console_err={len(local.get('console',[]))} err={local.get('error','-')}", flush=True)
            lt, ll = live.get("text", "") or "", local.get("text", "") or ""
            ratio = difflib.SequenceMatcher(None, lt, ll).ratio()
            results[r] = {"live": {k: v for k, v in live.items() if k != "text"},
                          "local": {k: v for k, v in local.items() if k != "text"},
                          "live_text_len": len(lt), "local_text_len": len(ll),
                          "text_ratio": ratio}
            with open(f"{OUT}/texts/{n}_live.txt", "w") as f: f.write(lt)
            with open(f"{OUT}/texts/{n}_local.txt", "w") as f: f.write(ll)
            print(f"  text_ratio={ratio:.4f}", flush=True)
            with open(f"{OUT}/results.json", "w") as f:
                json.dump(results, f, indent=1)
        browser.close()
    print("DONE")

if __name__ == "__main__":
    main()
