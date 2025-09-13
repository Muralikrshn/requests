


import requests
from lxml import html





base_url = "https://www.dtc-lease.nl"
page_url = "https://www.dtc-lease.nl/voorraad?lease_type=operational&entity=business&page=1"
car_urls = [] # {} Both can be used
r= requests.get(url=page_url)
tree = html.fromstring(r.text)

for i in range(1,6):
    page_url = f"https://www.dtc-lease.nl/voorraad?lease_type=operational&entity=business&page={i}"
    r= requests.get(url=page_url)
    tree = html.fromstring(r.text)
    links = tree.xpath("//a[contains(@data-testid, 'product-result')]/@href")
    
    print(f"====Extracting Links from Page {i}====")
    if not links:
        break
    
    for href in links:
        print(base_url + href)
    
    car_urls.extend(links)

