import csv
import json
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import random
import re

def configure_browser():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_argument("--headless")  # Optional: enable for headless

    driver = webdriver.Chrome(options=options)
    return driver
def load_cookies(driver):
    # Navigate to Facebook first to match the cookie domain
    driver.get('https://www.facebook.com')
    time.sleep(5)  # Allow some time for the page to load fully

    with open('cookies.json', 'r') as cookies_file:
        cookies = json.load(cookies_file)
        for cookie in cookies:
            if 'expiry' in cookie:
                del cookie['expiry']
            if 'sameSite' not in cookie or cookie['sameSite'] not in ["Strict", "Lax", "None"]:
                cookie['sameSite'] = "None"
            driver.add_cookie(cookie)

def scrape_facebook_group_members(driver, url):
    driver.get(url)
    scraped_members = set()
    try:
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(3.5, 4.5))
            members = driver.find_elements(By.XPATH, '(//div[@role="list"]//span[@class="xt0psk2"]//a)[position() mod 2 = 0]')
            new_data_found = False
            for member in members:
                name = member.text
                profile_link_raw = member.get_attribute('href')
                profile_link_converted = re.sub(r'groups/\d+/user/', '', profile_link_raw)
                if profile_link_converted not in scraped_members:
                    print(f"Scraping: {name} - {profile_link_converted}")
                    with open('members1.csv', mode='a', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow([name, profile_link_converted])
                    scraped_members.add(profile_link_converted)
                    new_data_found = True
            if not new_data_found:
                print("No new members found in this iteration.")
                break
    except Exception as e:
        print(len(scraped_members))
        print("Error occurred:", e)

def main():
    driver = configure_browser()
    load_cookies(driver)
    with open('member_links.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            group_url = row[0]
            print(f"Starting scrape for group: {group_url}")
            scrape_facebook_group_members(driver, group_url)
    driver.quit()

if __name__ == '__main__':
    main()
