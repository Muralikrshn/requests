# amazon_pg_scraper.py
import csv
import requests
# import psycopg2
from lxml import html
from concurrent.futures import ThreadPoolExecutor, as_completed

# -------------------- PROXY CONFIG --------------------
PROXY_USERNAME = "9e2fc7fa1cca2ea89973"
PROXY_PASSWORD = "91e704fc92d8f184"
PROXY_HOST     = "gw.dataimpulse.com"
PROXY_PORT     = "823"
PROXY_URL      = f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}"

proxies = {
    'http': PROXY_URL,
    'https': PROXY_URL
}

# -------------------- HEADERS --------------------
HEADERS = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Origin": "https://images-na.ssl-images-amazon.com",
        "Referer": "https://images-na.ssl-images-amazon.com/",
        "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"macOS"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site"
}

# -------------------- POSTGRES CONNECTION --------------------
def connect_to_db():
    return psycopg2.connect(
        dbname="demo_amz_scraping",
        password="",      # <<< add your password
        host="localhost",
        port="5432"
    )

# -------------------- CSV READER --------------------
def load_links():
    print("📂 Loading product links from links.csv ...")
    with open("links.csv", newline='', encoding='utf-8') as file:
        return [row[0] for row in csv.reader(file) if row and "http" in row[0]]

# -------------------- SCRAPER FUNCTION --------------------
def fetch_data(url):
    print(f"🌐 Scraping: {url}")
    try:
        session = requests.Session()
        session.headers.update(HEADERS)
        resp = session.get(url, proxies=proxies, timeout=15)

        # if there is any captcha blocking
        if "captcha" in resp.text.lower():
            print("🚫 CAPTCHA triggered.")
            return [url, "BLOCKED", "BLOCKED", "0", 0.0]

        tree = html.fromstring(resp.content)

        title = tree.xpath('normalize-space(//span[@id="productTitle"]/text())') or "N/A"
        price = tree.xpath('normalize-space(//span[@class="a-price-whole"]/text())') or "0"
        sales_raw = tree.xpath('//span[contains(text()," in past month")]/preceding-sibling::span/text()')
        sales = "0"
        if sales_raw:
            raw = sales_raw[0].lower().replace("bought", "").replace("in past month", "").strip()
            raw = raw.replace("+", "").replace("k", "000").replace(",", "")
            try:
                sales = str(int(raw))
            except:
                sales = "0"

        # Safe conversion
        try:
            price_float = float(price.replace(",", ""))
            sales_int = int(sales.replace(",", ""))
            revenue = round(price_float * sales_int, 2)
        except:
            revenue = 0.0

        return [url, title, price, sales, revenue]

    except Exception as e:
        print(f"❌ Error: {e}")
        return [url, "ERROR", "ERROR", "0", 0.0]

# -------------------- DB INSERT --------------------
def insert_into_db(conn, row):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO amazon_products (url, title, price, sales, revenue)
            VALUES (%s, %s, %s, %s, %s)
        """, row)
        conn.commit()
        print(f"✅ Inserted → {row[1][:50]}...")

# -------------------- MAIN FUNCTION --------------------
def main():
    conn = connect_to_db()
    links = load_links()

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_data, url) for url in links]
        for future in as_completed(futures):
            result = future.result()
            if result:
                insert_into_db(conn, result)

    conn.close()
    print("\n🎉 Done! All data saved to PostgreSQL.")

if __name__ == "__main__":
    main()
