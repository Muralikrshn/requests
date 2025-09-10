import requests
from lxml import html
import csv

Base_url= 'https://www.dtc-lease.nl'

LIST_URL_TEMPLATE = ('https://www.dtc-lease.nl/voorraad?lease_type=financial&entity=business&page={page_num}')

car_listing_urls = []

# step 1: Gather all the car listing urls
for page_num in range(1,6):
    url = LIST_URL_TEMPLATE.format(page_num=page_num)
    # print(page_num)
    r = requests.get(url)
    tree = html.fromstring(r.text)

    links = tree.xpath('//a[contains(@data-testid,"product-result")]/@href')
    for link in links:
        full_url = Base_url+link
        print(full_url)
        car_listing_urls.append(full_url)


# Step 2: Define the fields to extract
XPATHS = {
    "title": '//h1/text()',
    "subtitle": '//p[contains(@class,"type-auto")]/text()',
    "financial_lease_price": '//div[@data-testid="price-block"]//h2/text()',
    "financial_lease_term": '//div[@data-testid="price-block"]//p[contains(text(),"mnd")]/text()',
    "advertentienummer": '//div[contains(text(),"Advertentienummer")]/text()',
    "merk": '//div[text()="Merk"]/following-sibling::div/text()',
    "model": '//div[text()="Model"]/following-sibling::div/text()',
    "bouwjaar": '//div[text()="Bouwjaar"]/following-sibling::div/text()',
    "km_stand": '//div[text()="Km stand"]/following-sibling::div/text()',
    "transmissie": '//div[text()="Transmissie"]/following-sibling::div/text()',
    "prijs": '//div[text()="Prijs"]/following-sibling::div/text()',
    "brandstof": '//div[text()="Brandstof"]/following-sibling::div/text()',
    "btw_marge": '//div[text()="Btw/marge"]/following-sibling::div/text()',
    "opties_accessoires": '//h2[contains(.,"Opties & Accessoires")]/following-sibling::ul/li/text()',
    "address": '//div[@class="flex justify-between"]//p/text()',
    "images": '//ul[contains(@class,"swiper-wrapper")]//img/@src',
}

# step 3: extract and write to csv
with open('dtc-lease.csv', 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['url']+list(XPATHS.keys())
    writer = csv.DictWriter(f,fieldnames=fieldnames)
    writer.writeheader()

    for detail_url in car_listing_urls:
        # print(detail_url)
        r = requests.get(detail_url)
        tree = html.fromstring(r.text)

        row = {"url":detail_url}

        for key, xpath in XPATHS.items():
            result = tree.xpath(xpath)

            if result:
                row[key] = result[0].strip()
            else:
                row[key] = ""
                
            # print(row)

        writer.writerow(row)

    print(f"Finished extracting Page {page_num}") 




    
























