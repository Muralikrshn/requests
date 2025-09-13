import csv
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import re
import time
import json
    
def append_dict_to_csv(data, filename):
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=data.keys())
        if csvfile.tell() == 0:
            writer.writeheader()
        writer.writerow(data)

def configure_browser():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")
    # options.add_argument("--headless")  # Optional: enable for headless

    driver = webdriver.Chrome(options=options)
    return driver

driver = configure_browser()

# ✅ MUST go to Facebook first before setting cookies!
driver.get("https://www.facebook.com")
time.sleep(5)

with open('cookies.json', 'r') as cookies_file:
    cookies = json.load(cookies_file)
    for cookie in cookies:
        if 'expiry' in cookie:
            del cookie['expiry']  
        if 'sameSite' not in cookie or cookie['sameSite'] not in ["Strict", "Lax", "None"]:
            cookie['sameSite'] = "None" 
        driver.add_cookie(cookie)


with open('members1.csv', mode='r', encoding='utf-8') as csvfile:
    csv_reader = csv.DictReader(csvfile)
    for row in csv_reader:
        try:
            Name = row['name']
            profile_link = row["profile_link"]
            driver.get(profile_link)
            time.sleep(3)  
            emails = re.findall(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,6}\b", driver.page_source, re.IGNORECASE)
            phones = re.findall(r"[\d]{3}[-]?[\d]{3}-[\d]{4}", driver.page_source) + re.findall(r"[(][\d]{3}[)][ ]?[\d]{3}-[\d]{4}", driver.page_source)

            if emails:
                row['Email'] = emails[0]
                print(f"email found: { emails[0]}")
            else:
                row['Email'] = ''

            print(row)
            
            data = {
                'profile_link': profile_link,
                'Name': Name,
                'Email': row['Email'],
            }

            append_dict_to_csv(data,'memb61.csv')
         
        except Exception as e:
            print(f"Error processing profile {profile_link}: {e}")
            row['Email'] = ''
            data = {
                'profile_link': profile_link,
                'Name': Name,
                'Email': row['Email'],
            }
            append_dict_to_csv(data,'memb61.csv')
            
            continue  

# Close the WebDriver
driver.quit()
