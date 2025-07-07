import os
import csv
import time
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException
import schedule
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains

def openselenium():
    driver = Options()
    driver.add_argument("--ignore-certificate-errors")
    driver.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")
    driver.add_experimental_option("detach", True)
    driver.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=driver)
    driver.get("https://www.instagram.com/")
    return driver

def login(driver, username_str, password_str):
    username = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "username")))
    password = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.NAME, "password")))

    username.clear()
    password.clear()
    username.send_keys(username_str)
    password.send_keys(password_str)

    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    time.sleep(3)

    input("Complete CAPTCHA if required, then press Enter to continue...")

def search(driver, keyword):
    search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[text()='Search']")))
    ActionChains(driver).move_to_element(search_box).click().perform()
    time.sleep(1)
    searchbox = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Search']")))
    searchbox.clear()
    searchbox.send_keys(keyword)
    
    retry_attempts = 2
    for attempt in range(retry_attempts):
        try:
            result = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f"//span[contains(text(), '{keyword}')]")))
            result.click()
            break
        except StaleElementReferenceException:
            print(f"StaleElementReferenceException on attempt {attempt + 1}")
            time.sleep(1)
    time.sleep(2)

def get_link(driver):
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
    time.sleep(3)
    anchors = driver.find_elements(By.TAG_NAME, 'a')    
    print(f"Found {len(anchors)} anchor elements.")  # Debug print
    
    hrefs = []
    seen_links = set()  # Gunakan set untuk menghindari duplikasi

    for a in anchors:
        if len(hrefs) >= 5:  # Ambil hanya 5 link teratas
            break
        try:
            href = a.get_attribute('href')
            if href and '/p/' in href and href not in seen_links:  
                hrefs.append(href)
                seen_links.add(href)  # Tambahkan ke set untuk menghindari duplikasi
                print(f"Found link: {href}")  # Debug print
        except StaleElementReferenceException:
            continue  # Lewati elemen yang tidak stabil

    return hrefs
    
def visit_links(driver, links):
    if not os.path.exists('insta-data'):
        os.makedirs('insta-data')

    filepath = os.path.join('insta-data', 'comments_usernames.csv')
    
    with open(filepath, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'URL', 'Username', 'Comment'])

        for link in links:
            driver.get(link)
            print(f"Visiting {link}")
            time.sleep(5)
            try:
                # Ambil tanggal postingan
                date_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'time'))
                )
                post_date = date_element.get_attribute('datetime')

                # Konversi format tanggal
                post_date_obj = datetime.fromisoformat(post_date.replace('Z', ''))
                formatted_date = post_date_obj.strftime('%m/%d/%Y')

                # Ambil komentar dan username
                comments = driver.find_elements(By.XPATH, "//span[contains(@class, '_ap3a')]")
                usernames = driver.find_elements(By.XPATH, "//a[contains(@class, 'x1i10hfl')]")


                for username, comment in zip(usernames, comments):
                    username_text = username.text
                    comment_text = comment.text
                    print(f"Username: @{username_text}, Comment: {comment_text}")

                    writer.writerow([formatted_date, link, f"@{username_text}", comment_text])
                    print(f"Wrote to CSV: {formatted_date}, {link}, @{username_text}, {comment_text}")

            except Exception as e:
                print("Error:", e)
                print("Could not retrieve data for:", link)

               
def save_mongo(filename):
    client = MongoClient('mongodb://localhost:27017/')
    db = client.db_analisis_sentimen
    insta_collection = db.instagram
    
    data_dir = 'insta-data'
    filepath = os.path.join(data_dir, filename)
    
    if not os.path.isfile(filepath):
        print(f"File {filepath} does not exist.")
        return
    
    with open(filepath, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for comment in reader:
            if comment.get("URL") and comment["URL"] != "URL":
                existing_comment = insta_collection.find_one({"URL": comment["URL"], "Username": comment["Username"], "Comment": comment["Comment"]})

                if not existing_comment:
                    comment_to_save = {
                        "Date": comment.get("Date"),
                        "URL": comment.get("URL"),
                        "Username": comment.get("Username"),
                        "Comment": comment.get("Comment"),
                    }
                    insta_collection.insert_one(comment_to_save)
        
def main():
    driver = openselenium()
    login(driver, "sentis2872", "SENTISprigel")
    search(driver, "pesanunnes")
    links = get_link(driver)
    print(links)
    visit_links(driver, links)
    save_mongo('comments_usernames.csv')
    
def schedule_crawling():
    main()
    # schedule.every().day.at("13:25").do(main)  # Atur waktu sesuai kebutuhan Anda
    
    # while True:
    #     schedule.run_pending()
    #     time.sleep(10)

if __name__ == "__main__":
    # main()
    schedule_crawling()
    