from playwright.sync_api import sync_playwright

def hero_src(page, url):
    page.goto(url, wait_until="load", timeout=60000)
    page.wait_for_timeout(2500)
    return page.evaluate("""() => {
        const out = [];
        document.querySelectorAll('img').forEach(im => {
            const r = im.getBoundingClientRect();
            if (r.top < 700 && r.bottom > 0 && im.naturalWidth > 0) out.push(im.currentSrc);
        });
        document.querySelectorAll('div,section,header').forEach(el => {
            const r = el.getBoundingClientRect();
            if (r.top < 600 && r.height > 200) {
                const bg = getComputedStyle(el).backgroundImage;
                if (bg && bg !== 'none') out.push('BG:' + bg.slice(0, 200));
            }
        });
        return out;
    }""")

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/chromium", args=["--no-sandbox", "--disable-dev-shm-usage"])
    ctx = b.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()
    for i in range(3):
        print(f"LIVE run {i+1}:", hero_src(page, "https://globepasshub.com/canada-study-permit"), flush=True)
    for i in range(3):
        print(f"LOCAL run {i+1}:", hero_src(page, "http://127.0.0.1:8321/canada-study-permit"), flush=True)
    b.close()
