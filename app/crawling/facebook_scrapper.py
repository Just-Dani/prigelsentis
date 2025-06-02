from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random
import pymongo
import json
import schedule

email = "johnwick67319@gmail.com"
password = "herofavorit123"
driver = None
target = "https://www.facebook.com/unnesshitpost"

def initialize_driver():
    options = webdriver.EdgeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Edge(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def simulate_human_typing(element, text):
    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.1, 0.5))
        if random.random() < 0.2:
            time.sleep(random.uniform(0.3, 0.7))

def login(driver, email, password):
    driver.get("https://www.facebook.com/login")

    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email"))
    )
    simulate_human_typing(email_input, email)

    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "pass"))
    )
    simulate_human_typing(password_input, password)

    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    ActionChains(driver)\
        .move_to_element(login_button)\
        .pause(random.uniform(0.2, 0.4))\
        .click()\
        .perform()

    time.sleep(30)

def slow_scroll(driver, scroll_container=None, step=300):
    """
    Scrolls slowly within the specified scrollable container or the entire page.
    """
    if scroll_container:
        # Scroll within the container
        driver.execute_script("arguments[0].scrollBy(0, arguments[1]);", scroll_container, step)
    else:
        # Scroll the entire page
        driver.execute_script(f"window.scrollBy(0, {step});")
    
    time.sleep(random.uniform(1, 3))

def navigate_to_profile(driver, target):
    driver.get(target)
    time.sleep(4)

def extract_posts_with_bs(driver):
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    links_data = []
    seen_links = set()

    links = soup.find_all("div", {"class": "x1n2onr6 x1ja2u2z"})

    for link in links:
        try:
            link_post = link.select_one("div.xu06os2.x1ok221b > span > div > span > span > span > a")
            href = link_post.get('href') if link_post else None

            # Filter: only include links that contain '/posts/' and not '/videos/'
            if href and "/posts/" in href and "/videos/" not in href and href not in seen_links:
                links_data.append(href)
                seen_links.add(href)
                
        except Exception as e:
            print("Error extracting link data:", e)

    return links_data

def take_link(driver, max_links):
    all_links = []

    while len(all_links) < max_links:
        links = extract_posts_with_bs(driver)
        new_links = [link for link in links if link not in all_links]
        all_links.extend(new_links)
        print(f"Extracted {len(all_links)} unique posts so far.")
        slow_scroll(driver, step=500)

        if len(all_links) >= max_links:
            break

    return all_links[:max_links]

def click_all_see_more(driver, timeout=5):
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            see_more_buttons = driver.find_elements(By.XPATH, "//div[@role='button' and contains(text(), 'See more')]")
            if not see_more_buttons:
                break

            for btn in see_more_buttons:
                try:
                    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                    time.sleep(0.5)
                    btn.click()
                    time.sleep(1)
                except Exception as click_error:
                    continue  # Some buttons may disappear; skip errors
        except Exception as e:
            break
        
        time.sleep(2)  # Pause before re-checking

def extract_comments_from_post(driver, post_url, max_comments):
    driver.get(post_url)
    time.sleep(5)

    comments = []
    same_count = 0
    last_comment_len = 0
    scroll_container = driver.find_element(By.CSS_SELECTOR, "div.xb57i2i.x1q594ok.x5lxg6s.x78zum5.xdt5ytf.x6ikm8r.x1ja2u2z.x1pq812k.x1rohswg.xfk6m8.x1yqm8si.xjx87ck.xx8ngbg.xwo3gff.x1n2onr6.x1oyok0e.x1odjw0f.x1iyjqo2.xy5w88m")

    button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and .//span[text()='Most relevant']]"))
        )
    button.click()

    time.sleep(3)

    all_comments_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@role='menuitem']//span[text()='All comments']"))
    )
    all_comments_btn.click()

    while len(comments) < max_comments:
        click_all_see_more(driver)
        slow_scroll(driver, scroll_container=scroll_container, step=500)
        print("[[Comments Len:", len(comments))

        time.sleep(random.uniform(1, 3))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        comment_elements = soup.find_all("div", {"class": "x16hk5td x12rz0ws"})

        for comment in comment_elements:
            try:
                username = comment.find("span", {"class": "x3nfvp2"}).text.strip()
                text = comment.find("span", {"class": "xudqn12"}).text.strip()

                if {"username": username, "comment": text} not in comments:
                    comments.append({"username": username, "comment": text})
            except Exception as e:
                print("Error extracting comment:", e)

        if len(comments) == last_comment_len:
            same_count += 1
            print(f"No new comments. same_count = {same_count}")
        else:
            same_count = 0
            last_comment_len = len(comments)

        # Break if no new comments were found 3 times in a row
        if same_count >= 3:
            print("No new comments found in 3 consecutive tries. Stopping.")
            break

        if len(comments) >= max_comments:
            print(f"Collected {max_comments} comments. Stopping.")
            break

    return comments[:max_comments]

def visit_links(driver, post_links):
    all_comments = []

    for post_link in post_links:
        print(f"Scraping comments from post: {post_link}")
        comments = extract_comments_from_post(driver, post_link, 30)
        
        # Print the post link and its comments
        print(f"\nPost Link: {post_link}")
        if comments:
            for idx, comment in enumerate(comments, start=1):
                print(f"{idx}. Username: {comment['username']}, Comment: {comment['comment']}")
                all_comments.append({
                    "URL": post_link,
                    "Username": comment["username"],
                    "Comment": comment["comment"]
                })
        else:
            print("No comments found for this post.")
        
        print("-" * 80)  # Separator for readability

    return all_comments

def save_mongo(data):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client["db_analisis_sentimen"]
    collection = db["facebook"]

    inserted_count = 0
    for item in data:
        existing = collection.find_one({
            "URL": item["URL"],
            "Username": item["Username"],
            "Comment": item["Comment"]
        })

        if not existing:
            collection.insert_one(item)
            inserted_count += 1

    print(f"Saved {inserted_count} new comments to MongoDB.")

if __name__ == "__main__":
    driver = initialize_driver()

    login(driver, email, password)

    navigate_to_profile(driver, target)

    post_links = take_link(driver, max_links=5)

    all_comments = visit_links(driver, post_links)

    if all_comments:
        save_mongo(all_comments)
    else:
        print("No comments were scraped?")

    time.sleep(2)