

# import requests

# URL = "https://www.imdb.com/chart/top/"

# def demo_no_headers():
#     resp = requests.get(URL)
#     print(resp.status_code)  # Usually 403

# demo_no_headers()




# import requests 

# URL = "https://www.imdb.com/chart/top/"

# HEADERS = {
#     "User-Agent":      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
#                        "AppleWebKit/537.36 (KHTML, like Gecko) "
#                        "Chrome/137.0.0.0 Safari/537.36",
#     "Accept":          "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
#     "Accept-Encoding": "gzip, deflate, br, zstd",
#     "Accept-Language": "en-US,en;q=0.9",
#     "Referer":         "https://www.imdb.com/",
# }

# def demo_with_headers():
#     resp = requests.get(URL, headers=HEADERS)
#     print(resp.status_code)


# demo_with_headers()

 

import requests
from lxml import html


URL = "https://www.imdb.com/chart/top/"

HEADERS = {
    "User-Agent":      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/137.0.0.0 Safari/537.36",
    "Accept":          "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer":         "https://www.imdb.com/",
}


TITLE_XP = (
    '//div[@class="sc-15ac7568-0 jQHOho cli-children"]'
    '/div/a/h3/text()'
)

def demo_with_xpath():
    resp = requests.get(URL, headers=HEADERS)
    tree  = html.fromstring(resp.content)
    titles = tree.xpath(TITLE_XP)
    print("Block C  status:", resp.status_code)
    print("First 10 titles:")
    for t in titles[:10]:
        print("  ", t.strip())

demo_with_xpath()
