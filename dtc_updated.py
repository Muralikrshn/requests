# DTC-Lease – Easy JSON API Scraper (50 brand limit)

import requests
import csv
import re
from lxml import html


# https://www.dtc-lease.nl/_next/data/LRVRBtkyERflPlgnpBJoi/voorraad/793020.json

BASE_URL = "https://www.dtc-lease.nl"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

CSV_FIELDS = ["url", "title", "price", "brand", "model", "fuel_type", "mileage", "location"]

# 1. Discover buildId (needed for API call)
def discover_build_id():
    homepage = BASE_URL
    r = requests.get(homepage, headers=HEADERS)
    match = re.search(r'"buildId":"([^"]+)"', r.text)
    if match:
        return match.group(1)
    return None

# 2. Get the first 50 brand URLs from /merken page
def get_brand_urls():
    merken_page = BASE_URL + "/merken"
    r = requests.get(merken_page, headers=HEADERS)
    tree = html.fromstring(r.text)
    links = tree.xpath('//main[@id="main-content"]//ul/li/a/@href')
    full_links = []
    count = 0
    for link in links:
        full_url = BASE_URL + link
        full_links.append(full_url)
        count += 1
        if count == 50:
            break
    return full_links

# 3. Get car listing URLs from a brand page
def get_car_listings(brand_url):
    r = requests.get(brand_url, headers=HEADERS)
    tree = html.fromstring(r.text)
    raw_links = tree.xpath('//a[starts-with(@data-testid, "product-result-")]/@href')
    full_links = []
    for l in raw_links:
        full_links.append(BASE_URL + l)
    return full_links

# 4. Get just the car ID from the URL
def extract_car_id(url):
    return url.strip("/").split("/")[-1]

# 5. Build the API URL for a specific car using the buildId and ID
def build_api_url(build_id, car_id):
    return f"{BASE_URL}/_next/data/{build_id}/voorraad/{car_id}.json?id={car_id}"

# 6. Parse the JSON response
def parse_api_json(detail_url, data):
    try:
        product = data["pageProps"]["pageProps"]["product"]
        info = product.get("product_data", {})
        return {
            "url": detail_url,
            "title": info.get("merk", {}).get("name", "") + " " + info.get("model", {}).get("name", ""),
            "price": info.get("prijs", {}).get("value", ""),
            "brand": info.get("merk", {}).get("name", ""),
            "model": info.get("model", {}).get("name", ""),
            "fuel_type": info.get("brandstof", {}).get("name", ""),
            "mileage": info.get("km_stand", {}).get("value", ""),
            "location": product.get("dealer", {}).get("Plaats_dealer", "")
        }
    except:
        return None

# 7. Main scraping logic
def main():
    print("🔍 Step 1: Getting buildId...")
    build_id = discover_build_id()
    if not build_id:
        print("❌ Failed to get buildId")
        return
    print("✅ buildId found:", build_id)

    print("\n📦 Step 2: Getting brand URLs...")
    brands = get_brand_urls()
    print("✅ Found", len(brands), "brands")

    all_rows = []

    print("\n🚗 Step 3: Scraping listings...")
    for brand_url in brands:
        listings = get_car_listings(brand_url)
        for listing_url in listings:
            car_id = extract_car_id(listing_url)
            api_url = build_api_url(build_id, car_id)
            try:
                r = requests.get(api_url, headers=HEADERS)
                if r.status_code != 200:
                    continue
                json_data = r.json()
                row = parse_api_json(listing_url, json_data)
                if row:
                    all_rows.append(row)
            except Exception as e:
                print("[error]", e)
                continue

    print("\n💾 Step 4: Saving to CSV...")
    with open("dtc_easy_api_scraper.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)

    print("✅ Scraping complete!")

# 8. Entry point
main()
