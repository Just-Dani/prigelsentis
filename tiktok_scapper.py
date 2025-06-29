# TikTok Scraper dengan Login Manual & Scraping Komentar + Balasan (reply) + Parent ID + View More + Export Cookies ke TXT
# Menyimpan sesi login ke cookie, men-scrape komentar utama dan balasan jika ada, serta mengaitkan balasan dengan komentar induk

import asyncio
from playwright.async_api import async_playwright
import csv
import json
import os
import uuid
from datetime import datetime

COOKIE_FILE = f"tiktok_cookies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
COOKIE_TXT = f"tiktok_cookies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

async def save_cookies(context):
    cookies = await context.storage_state()
    with open(COOKIE_FILE, 'w') as f:
        json.dump(cookies, f)

async def export_cookies_txt(context, output_file=COOKIE_TXT):
    cookies = await context.cookies()
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Netscape HTTP Cookie File\n")
        for cookie in cookies:
            domain = cookie['domain']
            include_subdomain = "TRUE" if domain.startswith('.') else "FALSE"
            path = cookie.get('path', '/')
            secure = "TRUE" if cookie.get('secure') else "FALSE"
            expires = cookie.get('expires', 2147483647)
            name = cookie['name']
            value = cookie['value']
            f.write(f"{domain}\t{include_subdomain}\t{path}\t{secure}\t{int(expires)}\t{name}\t{value}\n")

async def load_cookies(context):
    file_path = os.path.join("zzdree_", "tiktok_cookies1.json")
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            state = json.load(f)
        if isinstance(state, list):
            return state  # Sudah list cookie
        elif 'cookies' in state:
            return state['cookies']  # Ambil dari storage_state
        else:
            return None
    return None

async def login_once():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://www.tiktok.com/login", timeout=60000)
        print("🔐 Silakan login secara manual, lalu tekan ENTER di terminal jika sudah selesai...")
        input()
        await save_cookies(context)
        await export_cookies_txt(context)
        await browser.close()

async def click_all_view_more(page):
    print("🔄 Menekan semua tombol 'View replies' dan 'View more' jika ada...")
    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            spans = await page.query_selector_all("span")
            clicked = False
            for span in spans:
                try:
                    text = (await span.inner_text()).strip().lower()
                    if text.startswith("view") and ("repl" in text or "more" in text):
                        parent = await span.evaluate_handle('node => node.closest("div[role=button], div[class*=ViewReplies], div.css-1idgi02-DivViewRepliesContainer") || node.parentElement')
                        if parent:
                            await parent.click()
                            await page.wait_for_timeout(1500)
                            clicked = True
                except Exception:
                    continue
            if not clicked:
                break
            await page.wait_for_timeout(2000)
        except Exception as e:
            print("Error saat mencoba klik View replies/more:", e)

async def scrape_comments_with_login(video_url, output_file='tiktok_comments.csv'):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        cookies = await load_cookies(None)
        context = await browser.new_context()

        if cookies:
            valid_cookies = []
            for cookie in cookies:
                if 'sameSite' in cookie:
                    if cookie['sameSite'] not in ['Strict', 'Lax', 'None']:
                        cookie['sameSite'] = 'Lax'
                else:
                    cookie['sameSite'] = 'Lax'
                valid_cookies.append(cookie)
            await context.add_cookies(valid_cookies)

        page = await context.new_page()
        print("Menguji validitas sesi login...")
        await page.goto("https://www.tiktok.com", timeout=60000)
        await page.wait_for_timeout(3000)
        logged_in = await page.evaluate("() => !!document.querySelector('[data-e2e=profile-icon]')")

        if not logged_in:
            print("❌ Cookie kadaluarsa atau tidak valid. Login ulang diperlukan.")
            await browser.close()
            await login_once()
            await scrape_comments_with_login(video_url, output_file)
            return

        print("Membuka halaman video TikTok...")
        await page.goto(video_url, timeout=60000)
        await page.wait_for_timeout(6000)

        print("Scroll untuk memuat komentar dan balasan...")
        for _ in range(20):
            await page.mouse.wheel(0, 3000)
            await page.wait_for_timeout(2000)

        await click_all_view_more(page)

        print("Mengambil komentar dan balasan...")
        comment_wrappers = await page.query_selector_all("div.css-1gstnae-DivCommentItemWrapper")

        comments_data = []
        parent_id = None

        for wrapper in comment_wrappers:
            try:
                username_el = await wrapper.query_selector("div[data-e2e^='comment-username-'] p")
                comment_text_el = await wrapper.query_selector("span[data-e2e^='comment-level-'] p")
                time_el = await wrapper.query_selector("div.css-1lglotn-DivCommentSubContentWrapper span")

                username = await username_el.inner_text() if username_el else 'N/A'
                comment_text = await comment_text_el.inner_text() if comment_text_el else 'N/A'
                comment_time = await time_el.inner_text() if time_el else 'N/A'

                is_reply = await wrapper.evaluate("el => el.innerText.includes('@')")
                unique_id = str(uuid.uuid4())

                if not is_reply:
                    parent_id = unique_id

                comments_data.append([
                    comment_time, video_url, username, comment_text,
                    "Balasan" if is_reply else "Komentar", parent_id if is_reply else unique_id
                ])
            except Exception as e:
                print("Lewat komentar karena error:", e)
                continue

        await browser.close()

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Tanggal', 'Link Komentar', 'Nama Akun', 'Isi Komentar', 'Tipe', 'Parent_ID'])
        writer.writerows(comments_data)

    print(f"✅ {len(comments_data)} entri (termasuk balasan) disimpan ke '{output_file}'")

if __name__ == '__main__':
    url = input("Masukkan URL video TikTok: ")
    asyncio.run(scrape_comments_with_login(url))
