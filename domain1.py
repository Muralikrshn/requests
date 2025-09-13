import requests
from lxml import html


HEADERS = {
  "User-Agent": "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 CrKey/1.54.250320",
  "accept": "application/xml",
  "accept-encoding": "gzip, deflate, br, zstd",
  "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
  "referer": "https://www.domain.com.au/",
  "Origin": "https://www.domain.com.au"
}

print("requests going....")
r = requests.get("https://www.domain.com.au/sale/indi-nsw-2642/?excludeunderoffer=1&page=1", headers=HEADERS)
with open(f'raw.html', 'w', encoding='utf-8') as f:
  f.write(r.text)