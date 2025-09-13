from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

def main():
    # Set up Chrome options
    options = Options()
    
    # Path to your Chrome User Data folder
    options.add_argument("user-data-dir=C:/Users/murha/AppData/Local/Google/Chrome/User Data/Default")
    
    # Specify the profile to use
    options.add_argument("--profile-directory=Default")
    
    # Optional: start maximized
    options.add_argument("--start-maximized")
    
    # Point to the correct Chrome binary (only needed if Chrome isn't in default location)
    # options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    
    # Launch browser with your profile
    driver = webdriver.Chrome(options=options)
    
    # Open Facebook (you’ll already be logged in if profile has session cookies)
    driver.get("https://www.facebook.com")
    
    time.sleep(30)  # So you can see it working before closing
    
    driver.quit()

if __name__ == "__main__":
    main()
