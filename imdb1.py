# import requests
# from lxml import html


# HEADERS = {
#   "user-agent": "Mozilla/5.0 (X11; Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36 CrKey/1.54.250320",
#   "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
#   "accept-encoding": "gzip, deflate, br",
#   "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
#   "referer": "https://www.imdb.com/"
# }

# XPATH = (
#   '//div[@class="sc-15ac7568-0 jQHOho cli-children"]'
#   '/div/a/h3/text()'
# )

# r = requests.get("https://www.imdb.com/chart/top/", headers=HEADERS)
# tree = html.fromstring(r.text)
# values = tree.xpath(XPATH)
# movies = {"movie_names": values}
# print(movies)


print(len(['449.95', '58.00', '149.95', '329.95', '599.95', '1,494.95', '499.95', '449.95', '529.95', '394.95', '744.95', '125.95', '69.99', '99.99', '79.99', '99.99', '20.00', '9.00', '18.00']))