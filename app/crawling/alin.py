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
target = "https://www.facebook.com/cnn"


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
        time.sleep(random.uniform(0.1, 0.3))
        if random.random() < 0.1:
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

    time.sleep(15)

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
            link = link_post.get('href') if link_post else None

            if link and link not in seen_links:
                links_data.append(link)
                seen_links.add(link)
                
        except Exception as e:
            print("Error extracting link data:", e)

    return links_data

def slow_scroll(driver, scroll_container_selector=None, step=300):
    """
    Scrolls slowly within the specified scrollable container or the entire page.
    """
    if scroll_container_selector:
        # Locate the scrollable container
        scroll_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, scroll_container_selector))
        )
        # Scroll within the container
        driver.execute_script("arguments[0].scrollBy(0, arguments[1]);", scroll_container, step)
    else:
        # Scroll the entire page
        driver.execute_script(f"window.scrollBy(0, {step});")
    
    time.sleep(random.uniform(1, 3))  # Simulate human-like delay


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

def click_all_see_more_buttons(driver):
    while True:
        try:
            # Locate all "See more..." buttons using the provided HTML structure
            see_more_buttons = driver.find_elements(
                By.CSS_SELECTOR,
                "div.x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n.x9f619.x1ypdohk.xt0psk2.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x16tdsg8.x1hl2dhg.xggy1nq.x1a2a7pz.xkrqix3.x1sur9pj.xzsf02u.x1s688f[role='button']"
            )

            if not see_more_buttons:
                print("No more 'See more...' buttons found.")
                break

            # Click each "See more..." button
            for button in see_more_buttons:
                try:
                    # Scroll into view to make the button clickable
                    driver.execute_script("arguments[0].scrollIntoView(true);", button)
                    time.sleep(random.uniform(0.5, 1.5))  # Simulate human delay
                    
                    # Click the button
                    ActionChains(driver).move_to_element(button).click().perform()
                    print("Clicked a 'See more...' button.")
                    
                    # Wait for content to load dynamically
                    time.sleep(random.uniform(2, 4))
                except Exception as e:
                    print(f"Failed to click a 'See more...' button: {e}")

        except Exception as e:
            print(f"Error while finding 'See more...' buttons: {e}")
            break

def extract_comments_from_post(driver, post_url, max_comments=10):
    driver.get(post_url)
    time.sleep(5)

    #click_all_see_more_buttons(driver)

    comments = []
    previous_comments_count = 0
    #scroll_container_selector = "div.x14nfmen.x1s85apg.x5yr21d.xds687c.xg01cxk.x10l6tqk.x13vifvy.x1wsgiic.x19991ni.xwji4o3.x1kky2od.x1sd63oq"

    while len(comments) < max_comments:
        # Scroll slowly to load more comments
        #slow_scroll(driver, scroll_container_selector=scroll_container_selector, step=300)
        time.sleep(random.uniform(2, 4))

        # Extract visible comments
        soup = BeautifulSoup(driver.page_source, "html.parser")
        comment_elements = soup.find_all("div", {"class": "x16hk5td x12rz0ws"})  # Adjust class based on FB structure

        for comment in comment_elements:
            try:
                username = comment.find("span", {"class": "x3nfvp2"}).text.strip()
                text = comment.find("span", {"class": "xudqn12"}).text.strip()

                # Avoid duplicates by checking if the comment is already added
                if {"username": username, "comment": text} not in comments:
                    comments.append({"username": username, "comment": text})
            except Exception as e:
                print("Error extracting comment:", e)

        # Break if no new comments are loaded after scrolling
        if len(comments) == previous_comments_count:
            print("No new comments loaded. Stopping.")
            break

        previous_comments_count = len(comments)

        # If we've reached the desired number of comments, stop
        if len(comments) >= max_comments:
            print(f"Collected {max_comments} comments. Stopping.")
            break

    return comments[:max_comments]  # Return only the first `max_comments`

def visit_links(driver, post_links):
    all_comments = []

    for post_link in post_links:
        print(f"Scraping comments from post: {post_link}")
        comments = extract_comments_from_post(driver, post_link, max_comments=10)
        
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

def close(driver):
    if driver:
        driver.quit()

def main():
    driver = initialize_driver()
    
    login(driver, email, password)

    navigate_to_profile(driver, target)

    posts_links = take_link(driver, max_links=10)

    for link in posts_links:
        print(link)

    all_comments = visit_links(driver, posts_links)
    
    if all_comments:
        save_mongo(all_comments)
    else:
        print("No comments were scraped?")
    
    time.sleep(2)

def schedule_crawling():
    main()
    # schedule.every().day.at("13:25").do(main)  # Atur waktu sesuai kebutuhan Anda
    
    # while True:
    #     schedule.run_pending()
    #     time.sleep(10)

if __name__ == "__main__":
    schedule_crawling()