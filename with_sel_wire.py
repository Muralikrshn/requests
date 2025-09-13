import json
import time
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options

# URL     = "https://www.dtc-lease.nl/voorraad?lease_type=financial&entity=business"
URL     = "https://www.realestate.com.au/buy/in-inner+east+melbourne,+vic/list-1"
OUTPUT  = "onedoc_network_log.json"

chrome_opts = Options()
chrome_opts.add_argument("--disable-gpu")
chrome_opts.add_experimental_option(
    "prefs", {"profile.managed_default_content_settings.images": 2}
)

driver = webdriver.Chrome(options=chrome_opts)

try:
    driver.get(URL)
    time.sleep(15)

    harvested = []
    for req in driver.requests:
        if not req.response:
            continue #skips over no response

        ct = req.response.headers.get("Content-Type", "")
        entry = {
            "method":       req.method,
            "url":          req.url,
            "status_code":  req.response.status_code,
            "content_type": ct,
        }

        if "application/json" in ct and req.response.body:
            try:
                entry["json"] = req.response.json
            except Exception:
                entry["text_snippet"] = req.response.body[:200].decode(errors="ignore")

        harvested.append(entry)

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(harvested, f, indent=2, ensure_ascii=False)

    print(f"✅  Saved {len(harvested)} requests to {OUTPUT}")

finally:
    driver.quit()
