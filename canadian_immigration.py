import csv
import time
# import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import datetime

def hard_refresh(driver):
    driver.execute_script("window.location.reload(true);")
    print('Page refreshed')

def js_click(driver, xpath):
    driver.execute_script("arguments[0].click();", driver.find_element(By.XPATH, xpath))

# Wait for the page to load completely
def initialize_driver():
    driver = webdriver.Chrome()
    driver.get("https://www.canada.ca/en/immigration-refugees-citizenship/services/application/check-processing-times.html")
    wait = WebDriverWait(driver, 10)
    time.sleep(10)
    return driver, wait

def restore_selections(driver, selections):
    print("Refreshing the page and restoring selections:", selections)
    hard_refresh(driver)
    time.sleep(10)
    for i, selection in enumerate(selections):
        try:
            if i == 0:
                select = Select(driver.find_element(By.ID, "wb-auto-24"))
            else:
                select = Select(driver.find_element(By.XPATH, f"(//div[@id='wb-auto-6']/select)[{i + 1}]"))
            select.select_by_visible_text(selection)
            print(f"Restored selection {i + 1}: {selection}")
            time.sleep(3)
        except NoSuchElementException:
            print(f"No dropdown found for selection {i + 1}")
            break
        except Exception as e:
            print(f"Error restoring selection {i + 1}: {e}")
            break

def scrape_processing_time(driver, wait, first_run, selections):
    try:
        if first_run:
            print("First run, clicking the submit button")
            js_click(driver, '(//button[@type="submit"])[2]')
            time.sleep(10)
            processing_time = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@class='glyphicon glyphicon-time']/following-sibling::span"))).text
            last_updated_date = driver.find_element(By.XPATH, '//span[contains(text(),"Last updated: ")]/span').text
            print("RAN FIRST")
            print(f"Scraped Processing Time: {processing_time}, Last Updated Date: {last_updated_date}")
            time.sleep(5)
            return processing_time, last_updated_date

        print("Clicking the submit button")
        html_before_click = driver.find_element(By.XPATH, "//div[@id='ajax']").get_attribute('outerHTML')
        js_click(driver, '(//button[@type="submit"])[2]')
        time.sleep(5)
        html_after_click = driver.find_element(By.XPATH, "//div[@id='ajax']").get_attribute('outerHTML')

        if html_before_click != html_after_click:
            print('Yes, the after and before are not the same')
            processing_time = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@class='glyphicon glyphicon-time']/following-sibling::span"))).text
            last_updated_date = driver.find_element(By.XPATH, '//span[contains(text(),"Last updated: ")]/span').text
            print(f"Scraped Processing Time: {processing_time}, Last Updated Date: {last_updated_date}")
            return processing_time, last_updated_date

        else:
            print("Into the for loop for clicking again for up to 5 times")
            for _ in range(5):
                js_click(driver, '(//button[@type="submit"])[2]')
                time.sleep(2)
                html_after_click = driver.find_element(By.XPATH, "//div[@id='ajax']").get_attribute('outerHTML')
                if html_before_click != html_after_click:
                    print("Yes, finally changes in HTML occurred after clicking and waiting for more")
                    processing_time = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@class='glyphicon glyphicon-time']/following-sibling::span"))).text
                    last_updated_date = driver.find_element(By.XPATH, '//span[contains(text(),"Last updated: ")]/span').text
                    print(f"Scraped Processing Time: {processing_time}, Last Updated Date: {last_updated_date}")
                    return processing_time, last_updated_date
                else:
                    print("Hell shit, nothing changed")
                    continue

            # Refresh and restore selections if needed
            try:
                restore_selections(driver, selections)
            except:
                return "N/A", "N/A"
            return scrape_processing_time(driver, wait, True, selections)

    except TimeoutException:
        print("Failed to scrape processing time")
        return "N/A", "N/A"
    except StaleElementReferenceException:
        print("StaleElementReferenceException occurred")
        return "N/A", "N/A"
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return "N/A", "N/A"

# Function to write results to CSV
def write_to_csv(data):
    try:
        current_time = datetime.datetime.now().strftime("%H%M")
        with open(f'visa_processing_times_{current_time}.csv', 'a', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(data)
    except Exception as e:
        print(f"Error writing to CSV: {e}")

# Function to iterate through dropdowns
def iterate_dropdowns(selection):
    driver, wait = initialize_driver()
    first_run = True
    selections = [selection]
    first_dropdown = Select(driver.find_element(By.ID, "wb-auto-24"))
    first_dropdown.select_by_visible_text(selection)
    print(f"Selected first option: {selection}")
    time.sleep(3)

    try:
        second_dropdown = Select(driver.find_element(By.XPATH, "(//div[@id='wb-auto-6']/select)[2]"))
        for option2 in second_dropdown.options:
            if option2.text == "Make your selection...":
                continue
            second_dropdown.select_by_visible_text(option2.text)
            selections.append(option2.text)
            print(f"Selected second option: {option2.text}")
            time.sleep(3)

            try:
                third_element = driver.find_element(By.XPATH, "(//div[@id='wb-auto-6']/select)[3]")
                third_dropdown = Select(third_element)
                for option3 in third_dropdown.options:
                    if option3.text == "Make your selection...":
                        continue
                    third_dropdown.select_by_visible_text(option3.text)
                    selections.append(option3.text)
                    print(f"Selected third option: {option3.text}")
                    time.sleep(3)

                    try:
                        fourth_element = driver.find_element(By.XPATH, "(//div[@id='wb-auto-6']/select)[4]")
                        fourth_dropdown = Select(fourth_element)
                        for option4 in fourth_dropdown.options:
                            if option4.text == "Make your selection...":
                                continue
                            fourth_dropdown.select_by_visible_text(option4.text)
                            selections.append(option4.text)
                            print(f"Selected fourth option: {option4.text}")
                            time.sleep(3)

                            try:
                                fifth_element = driver.find_element(By.XPATH, "(//div[@id='wb-auto-6']/select)[5]")
                                fifth_dropdown = Select(fifth_element)
                                for option5 in fifth_dropdown.options:
                                    if option5.text == "Make your selection...":
                                        continue
                                    fifth_dropdown.select_by_visible_text(option5.text)
                                    selections.append(option5.text)
                                    print(f"Selected fifth option: {option5.text}")
                                    time.sleep(3)

                                    processing_time, last_updated_date = scrape_processing_time(driver, wait, first_run, selections)
                                    first_run = False  # Set first_run to False after the first successful scrape
                                    data = [selection, option2.text, option3.text, option4.text, option5.text, processing_time, last_updated_date]
                                    write_to_csv(data)
                                    selections.pop()  # Remove last selection after processing
                            except NoSuchElementException:
                                print("No fifth dropdown found")
                                processing_time, last_updated_date = scrape_processing_time(driver, wait, first_run, selections)
                                first_run = False  # Set first_run to False after the first successful scrape
                                data = [selection, option2.text, option3.text, option4.text, "N/A", processing_time, last_updated_date]
                                write_to_csv(data)
                            finally:
                                selections.pop()  # Remove fourth selection after processing
                    except NoSuchElementException:
                        print("No fourth dropdown found")
                        processing_time, last_updated_date = scrape_processing_time(driver, wait, first_run, selections)
                        first_run = False  # Set first_run to False after the first successful scrape
                        data = [selection, option2.text, option3.text, "N/A", "N/A", processing_time, last_updated_date]
                        write_to_csv(data)
                        selections.pop()  # Remove third selection after processing
            except NoSuchElementException:
                print("No third dropdown found")
                processing_time, last_updated_date = scrape_processing_time(driver, wait, first_run, selections)
                first_run = False  # Set first_run to False after the first successful scrape
                data = [selection, option2.text, "N/A", "N/A", "N/A", processing_time, last_updated_date]
                write_to_csv(data)
                selections.pop()  # Remove second selection after processing
    except NoSuchElementException:
        print("No second dropdown found")
        processing_time, last_updated_date = scrape_processing_time(driver, wait, first_run, selections)
        first_run = False  # Set first_run to False after the first successful scrape
        data = [selection, "N/A", "N/A", "N/A", "N/A", processing_time, last_updated_date]
        write_to_csv(data)

    driver.quit()

# Main function
def main():
    selections_to_scrape = [
        "Temporary residence (visiting, studying, working)",
        "Economic immigration",
        "Family sponsorship",
        "Refugees",
        "Humanitarian and Compassionate cases",
        "Citizenship",
        "Passport",
        "Permanent resident cards",
        "Replacing or amending documents, verifying status"
    ]

    for selection in selections_to_scrape:
        iterate_dropdowns(selection)

if __name__ == "__main__":
    main()
