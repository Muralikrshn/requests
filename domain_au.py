import requests
import json
import pandas as pd

BASE_URL = "https://www.domain.com.au"
SEARCH_URL = "https://www.domain.com.au/sale/?ptype=house&bedrooms=3-any&price=300000-500000&excludeunderoffer=1&landsize=400-any&state=nsw"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.domain.com.au/",
    "Origin": "https://www.domain.com.au",
    "Accept-Encoding": "gzip, deflate, br, zstd"
}

all_data = []

print("Starting the scraper...\n")

for page in range(1, 11):
    url = f"{SEARCH_URL}&page={page}"
    print(f"Fetching page {page}...")

    resp = requests.get(url, headers=HEADERS, timeout=20)
    # with open(f'raw_{page}.html', 'w', encoding='utf-8') as f:
    #     f.write(resp.text)
    json_data = json.loads(resp.text)
    listings = json_data["props"]["listingsMap"]
    print(f"Found {len(listings)} listings on page {page}")

    for listing in listings.values():
        model = listing.get("listingModel", {})
        features = model.get("features", {})
        address = model.get("address", {})
        images = model.get("images", [])
        
        item = {
            "Title": model.get("promoType", ""),
            "URL": BASE_URL + model.get("url", ""),
            "Price": model.get("price", ""),  # top-level price key in model
            "Beds": features.get("beds"),
            "Baths": features.get("baths"),
            "Parking": features.get("parking"),
            "Land Size": f"{features.get('landSize')} {features.get('landUnit')}" if features.get("landSize") else "",
            "Property Type": features.get("propertyTypeFormatted"),  # better label for display
            "Street": address.get("street"),
            "Suburb": address.get("suburb"),
            "State": address.get("state"),
            "Postcode": address.get("postcode"),
            "Image URL": images[0] if images else ""  # get first image if available
        }

        all_data.append(item)

    
print("\nSaving scraped data to CSV...")
df = pd.DataFrame(all_data)
df.to_csv("domain_nsw_scraped.csv", index=False)
print(f"Done! {len(all_data)} listings saved to 'domain_nsw_scraped.csv'")
