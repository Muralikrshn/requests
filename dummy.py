

import requests
from lxml import html
import csv

HEADERS = {
  "user-agent": "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 CrKey/1.54.250320",
  "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
  "accept-encoding": "gzip, deflate, br",
  "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
  "referer": "https://themes.woocommerce.com/"
}


XPATHS = {
  'electronics_list': "//ul[@class='products columns-4']/li[contains(@class, 'purchasable')]",
  "image": ".//a[@class='woocommerce-LoopProduct-link woocommerce-loop-product__link']/img/@src",
  "name": ".//a[@class='woocommerce-LoopProduct-link woocommerce-loop-product__link']/h2/text()",
  "price": ".//span[@class='woocommerce-Price-amount amount']/bdi/text()",
  "next_page": "(//a[@class='next page-numbers'])[1]/@href"
}




with open('dummy_products.csv', mode='w', newline='', encoding='utf-8') as file:
  writer = csv.writer(file)
  writer.writerow(['Name', 'Price', 'Image'])

def get_page(url, headers) -> tuple[str, html.HtmlElement]:
  r = requests.get(url, headers=headers)
  print(r.content[:3000])
  tree = html.fromstring(r.text)
  return url, tree

def get_product_list(tree) -> list:
  return tree.xpath(XPATHS['electronics_list'])

def get_product_data(product) -> tuple[str, str, str]:
  name = product.xpath(XPATHS['name'])[0]
  price = product.xpath(XPATHS['price'])[0]
  image = product.xpath(XPATHS['image'])[0]
  return name, price, image

def go_to_next_page(next_page_xpath, tree) -> tuple[bool, str]:
  if tree.xpath(next_page_xpath):
    return True, tree.xpath(next_page_xpath)[0]
  return False, "No More Pages"

def scrape_page(url, headers, writer) -> None:
    print(f"\n====== Scraping URL: {url} ======\n")

    url, tree = get_page(url, headers=headers)
    product_list = get_product_list(tree)
    for product in product_list:
        name, price, image = get_product_data(product)
        print(name, price, image)
        writer.writerow([name, price, image])

    isNext, next_page_url = go_to_next_page(XPATHS['next_page'], tree)
    if isNext:
        scrape_page(next_page_url, headers, writer)


def main():
    with open('dummy_products.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Name', 'Price', 'Image'])  # header row
        scrape_page("http://themes.woocommerce.com/storefront/product-category/electronics/", HEADERS, writer)


if __name__ == "__main__":
    main()

