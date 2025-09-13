"""
Educational demo – USA Health “find-a-doctor” API
-------------------------------------------------
• Python 3.9+ (no extra packages – just requests & csv)
• Meant for classroom use only. Respect the site’s ToS /
  rate limits if you try it live.
"""

import csv
import json
import time
import requests

BASE_URL = "https://host-2wrod6.api.swiftype.com/api/as/v1/engines/usa-health-system/search.json"
AUTH_TOKEN = "search-6yovot2cpxdbxgxbjgnn5dtg"          # public client token
PAGE_SIZE  = 10                                          # rows per call
OUTFILE    = "usa_health_doctors.csv"                    # quick dump

# ---------------------------------------------
# Session & headers
# ---------------------------------------------
sess = requests.Session()
sess.headers.update({
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "*/*",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137 Safari/537.36"
    ),
    "Origin": "https://www.usahealthsystem.com",
    "Referer": "https://www.usahealthsystem.com/find-a-doctor",
    "X-Swiftype-Client": "swiftype-app-search-javascript",
    "X-Swiftype-Client-Version": "2.1.0"
})

def make_payload(page_number: int) -> dict:
    """Return the JSON body for a given page."""
    return {
        "query": "",                     # blank = “match all”
        "search_fields": {"title": {}},  # default search rules (same as UI)
        "filters": {
            "all": [
                {"type": "personnel"},
                {"researcher_at_mci": "false"}
            ],
            "any": []
        },
        "page": {"size": PAGE_SIZE, "current": page_number},
        "sort": {"last_name": "asc"}
    }

# ---------------------------------------------
# Main loop: page -> JSON -> rows
# ---------------------------------------------
all_rows = []
page = 1

while True:
    payload = make_payload(page)
    resp = sess.post(BASE_URL, data=json.dumps(payload), timeout=20)
    resp.raise_for_status()                  # die loudly if the call fails

    data = resp.json()
    meta   = data["meta"]["page"]
    docs   = data["results"]

    # Pick the fields we want to show in class
    for doc in docs:
        # ---- inside the for doc in docs: loop ----
        row = {
            "name"       : doc["title"]["raw"],
            "last_name"  : doc["last_name"]["raw"],
            "phone"      : doc.get("phone_number", {}).get("raw", ""),
            "location"   : doc.get("primary_location", {}).get("raw", ""),
            "specialties": ", ".join(doc.get("specialties", {}).get("raw", [])),
            "url"        : "https://www.usahealthsystem.com/" + doc["url"]["raw"],
        }
        all_rows.append(row)


    print(f"✅ Page {page}/{meta['total_pages']} done…")

    # stop when we hit the last page
    if meta["current"] >= meta["total_pages"]:
        break

    page += 1
    time.sleep(0.8)   # polite pause – real prod code should obey robots / back-off

# ---------------------------------------------
# Dump to CSV so the students can open it
# ---------------------------------------------
with open(OUTFILE, "w", newline="", encoding="utf-8") as f:
    fieldnames = ["name", "last_name", "phone", "location", "specialties", "url"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_rows)

print(f"\n🎉 Finished! {len(all_rows):,} records written to {OUTFILE}")
