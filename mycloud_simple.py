#!/usr/bin/env python3
"""
Simplified Swisscom MyCloud Authentication
With automatic ChromeDriver management

Usage:
    1. pip install -r requirements.txt
    2. Create .env with MYCLOUD_USERNAME and MYCLOUD_PASSWORD
    3. Run: python mycloud_simple.py
"""

import os
import time
import traceback
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# from seleniumwire import webdriver as wire_webdriver
from selenium import webdriver
import requests
import csv, time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

# Load environment variables from .env
load_dotenv()

def extract_video_details(driver, fig, wait=15):
    details = {}

    # Scroll into view and click thumbnail
    driver.execute_script("arguments[0].scrollIntoView(true);", fig)
    time.sleep(0.5)
    img = fig.find_element(By.CSS_SELECTOR, "img")
    driver.execute_script("arguments[0].click();", img)

    # Wait for preview container and get video URL (poster or <video> src)
    preview_div = WebDriverWait(driver, wait).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.mono-preview-content-image-preview-container"))
    )
    try:
        video_el = preview_div.find_element(By.CSS_SELECTOR, "video")
        details["url"] = video_el.get_attribute("src")
    except:
        try:
            poster_el = preview_div.find_element(By.CSS_SELECTOR, "img")
            details["url"] = poster_el.get_attribute("src")
        except:
            details["url"] = None

    # Click info icon if present
    try:
        info_icon = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".pi-preview-icon-information"))
        )
        driver.execute_script("arguments[0].click();", info_icon)
        time.sleep(0.5)
    except:
        pass

    # Metadata fields (gracefully handle missing ones)
    try:
        details["date"] = driver.find_element(
            By.CSS_SELECTOR, "div.pi-information-row span.max-width"
        ).text
    except:
        details["date"] = None
    try:
        details["time"] = driver.find_element(
            By.CSS_SELECTOR, "div.pi-information-row .edit-subtitle span"
        ).text
    except:
        details["time"] = None
    try:
        details["location"] = driver.find_element(
            By.CSS_SELECTOR, "div.pi-information-row[title]"
        ).get_attribute("title")
    except:
        details["location"] = None
    try:
        details["filename"] = driver.find_element(
            By.CSS_SELECTOR, "div.pi-information-row[title] span.max-width"
        ).text
    except:
        details["filename"] = None
    try:
        # Video-specific metadata: resolution, format, duration
        subtitle = driver.find_element(
            By.CSS_SELECTOR, "div.pi-information-row .edit-subtitle span"
        ).text
        details["metadata"] = subtitle
    except:
        details["metadata"] = None

    # Click Back to return to grid
    try:
        back_btn = WebDriverWait(driver, wait).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".pi-preview-back-text"))
        )
        driver.execute_script("arguments[0].click();", back_btn)
        time.sleep(0.5)
    except:
        pass

    return details

def extract_photo_details(driver, fig, wait=15):
    details = {}

    # Scroll into view and click thumbnail
    driver.execute_script("arguments[0].scrollIntoView(true);", fig)
    time.sleep(0.5)
    img = fig.find_element(By.CSS_SELECTOR, "img")
    driver.execute_script("arguments[0].click();", img)

    # Wait for preview container and get full image URL
    preview_div = WebDriverWait(driver, wait).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div.mono-preview-photo-container"))
    )
    bg_url = preview_div.value_of_css_property("background-image")
    bg_url = bg_url.replace('url("', '').replace('")', '')
    details["url"] = bg_url

    # Click info icon if present
    try:
        info_icon = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".pi-preview-icon-information"))
        )
        driver.execute_script("arguments[0].click();", info_icon)
        time.sleep(0.5)
    except:
        pass

    # Metadata fields (gracefully handle missing ones)
    try:
        details["date"] = driver.find_element(By.CSS_SELECTOR, "div.pi-information-row span.max-width").text
    except:
        details["date"] = None
    try:
        details["time"] = driver.find_element(By.CSS_SELECTOR, "div.pi-information-row .edit-subtitle span").text
    except:
        details["time"] = None
    try:
        details["location"] = driver.find_element(
            By.CSS_SELECTOR, "div.pi-information-row[title]"
        ).get_attribute("title")
    except:
        details["location"] = None
    try:
        details["filename"] = driver.find_element(
            By.CSS_SELECTOR, "div.pi-information-row[title] span.max-width"
        ).text
    except:
        details["filename"] = None
    try:
        details["camera"] = driver.find_element(
            By.CSS_SELECTOR, "div.pi-information-row span[data-bind*='valueCamera']"
        ).text
    except:
        details["camera"] = None

    # Click Back to return to grid
    try:
        back_btn = WebDriverWait(driver, wait).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".pi-preview-back-text"))
        )
        driver.execute_script("arguments[0].click();", back_btn)
        time.sleep(0.5)
    except:
        pass

    return details

def scroll_until_no_new(driver, pause=2):
    """Scroll down until no new figures load."""
    last_count = 0
    while True:
        figures = driver.find_elements(By.CSS_SELECTOR, "figure.pi-figure")
        if len(figures) > last_count:
            last_count = len(figures)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause)
        else:
            break

def get_images(driver, out_csv="photos.csv", outvid_csv="videos.csv", pause=1.5, max_scrolls=5000):
    """
    Crawl the Swisscom gallery, extract photo metadata, and export to CSV.
    - Handles infinite/virtualized scrolling
    - Skips videos
    - Deduplicates by thumbnail URL
    - Never reuses stale WebElement references
    """

    # Wait until at least one photo is visible
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "figure.pi-figure img"))
    )

    photos, seen, videos = [], set(), []
    scrolls_without_new, scroll_count = 0, 0

    # Identify the scrollable container (adjust selector if needed)
    try:
        gallery = driver.find_element(By.CSS_SELECTOR, "div.pi-matrix-container")
    except:
        gallery = driver.find_element(By.TAG_NAME, "body")

    while scrolls_without_new < 30 and scroll_count < max_scrolls:
        # Always re‑query fresh thumbnails
        thumbs = driver.find_elements(By.CSS_SELECTOR, "figure.pi-figure img")
        new_found = 0
        newvideo_found = 0

        try:
            for img in thumbs:
                try:
                    thumb_url = img.get_attribute("data-src") or img.get_attribute("src")
                except StaleElementReferenceException:
                    continue

                if not thumb_url or thumb_url in seen:
                    continue
            
                # ⬇️ NEW: check if this <img> belongs to a video figure
                fig = img.find_element(By.XPATH, "./ancestor::figure")
                if fig.find_elements(By.CSS_SELECTOR, ".video"):
                    print("Found video thumbnail")
                    try:
                        details = extract_video_details(driver, fig)
                        if details:
                            videos.append(details)
                            newvideo_found += 1
                            print(f"✓ Collected {len(videos)} videos")
                    except Exception as e:
                        print(f"Error extracting details: {e}")
                        traceback.print_exc()                    
                    continue

                seen.add(thumb_url)

                # Re‑locate the figure fresh by this URL
                try:
                    fresh_img = driver.find_element(By.CSS_SELECTOR, f'img[src="{thumb_url}"]')
                except:
                    # Sometimes it's in data-src instead of src
                    fresh_img = driver.find_element(By.CSS_SELECTOR, f'img[data-src="{thumb_url}"]')

                fig = fresh_img.find_element(By.XPATH, "./ancestor::figure")

                try:
                    details = extract_photo_details(driver, fig)
                    if details:
                        photos.append(details)
                        new_found += 1
                        print(f"✓ Collected {len(photos)} photos")
                except Exception as e:
                    print(f"Error extracting details: {e}")
                    traceback.print_exc()

            if new_found == 0:
                scrolls_without_new += 1
            else:
                scrolls_without_new = 0

            # Scroll the gallery container
            driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollTop + arguments[0].offsetHeight;",
                gallery
            )
            scroll_count += 1
            pos = driver.execute_script("return arguments[0].scrollTop;", gallery)
            print(f"Scroll {scroll_count}: scrollTop={pos}, total={len(seen)}")
            time.sleep(pause)
        except Exception as e:
            print(f"Scrolling error: {e}")
            traceback.print_exc()
            break
    # Export to CSV
    if photos:
        keys = sorted({k for d in photos for k in d.keys()})
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(photos)
        print(f"Exported {len(photos)} photos to {out_csv}")

    if videos:
        keys = sorted({k for d in videos for k in d.keys()})
        with open(outvid_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(videos)
        print(f"Exported {len(videos)} videos to {outvid_csv}")

    return photos

def get_mycloud_data(username=None, password=None, headless=False):
    """
    Simplified function to get bearer token
    
    Args:
        username: MyCloud username (or reads from MYCLOUD_USERNAME env)
        password: MyCloud password (or reads from MYCLOUD_PASSWORD env)
        headless: Run browser without GUI
        
    Returns:
        str: Bearer token or None
    """
    username = username or os.getenv('MYCLOUD_USERNAME')
    password = password or os.getenv('MYCLOUD_PASSWORD')
    
    if not username or not password:
        print("ERROR: Username and password required!")
        print("Set MYCLOUD_USERNAME and MYCLOUD_PASSWORD in .env file")
        return None
    
    print(f"Logging in as: {username}")
    
    # Setup Chrome with automatic driver management
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')
    # chrome_options.add_argument('--headless=new') --- it does not logn into it
    
    # Selenium-wire options for intercepting network traffic
    seleniumwire_options = {
        'disable_encoding': True  # Don't decode responses
    }
    
    # Create driver with automatic ChromeDriver installation
    """ driver = wire_webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options,
        seleniumwire_options=seleniumwire_options
    ) """
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    bearer_token = None
    
    try:
        print("Opening MyCloud...")
        driver.get('https://www.mycloud.swisscom.ch/?cid=myCloud_subscription#photos')
        time.sleep(3)
        
        print("Looking for login form...")
        
        # Try to find and fill username
        # <input type="text" id="username" name="identifier" spellcheck="false" minlength="3" maxlength="100" placeholder="Enter username" value="" aria-errormessage="identifierError" autocomplete="username" aria-invalid="false" required="required" autofocus="autofocus">
        try:
            username_field = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.ID, "username"))
                #EC.presence_of_element_located((By.ID, "username"))
            )
            print(f'username_field={username_field}')
        except:
            # Alternative selectors
            selectors = [
                (By.NAME, "username"),
                (By.CSS_SELECTOR, "input[type='email']"),
                (By.CSS_SELECTOR, "input[name='email']"),
            ]
            for selector_type, selector in selectors:
                try:
                    username_field = driver.find_element(selector_type, selector)
                    break
                except:
                    continue
        
        print("Entering username...")
        username_field.clear()
        username_field.send_keys(username)
        time.sleep(1)

        # Wait for and click the Continue button
        # <button class="clickable button-reset primary light" href="" type="button" aria-labelledby="label srhint"><span id="label" class="label">Continue</span></button>
        print("Waiting for the Continue button...")
        print("Waiting for Continue button inside shadow DOM...")

        # Wait for the shadow host to appear
        shadow_host = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "continueButton"))
        )

        # Get the shadow root
        shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)

        # Find the real <button> inside the shadow root
        continue_btn = shadow_root.find_element(By.CSS_SELECTOR, "button")

        # Click it via JS (safer than .click() for shadow DOM)
        driver.execute_script("arguments[0].click();", continue_btn)

        print("Clicked Continue...")

        """ continue_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Continue']]"))
        ) 
        continue_btn = WebDriverWait(driver, 15).until(
               EC.element_to_be_clickable((By.XPATH, "//button//span[contains(., 'Continue')]"))
        )
        continue_btn.click()
        print("Clicked Continue...")"""
        time.sleep(3)

        # Find password field
        #<input type="password" id="password" name="password" spellcheck="false" autocomplete="current-password" maxlength="100" aria-errormessage="pwdError" aria-invalid="false" required="required" autofocus="autofocus">
        try:
            # password_field = driver.find_element(By.ID, "password")
            password_field = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, "password"))
            )
            print(f'password_field={password_field}')
        except:
            selectors = [
                (By.NAME, "password"),
                (By.CSS_SELECTOR, "input[type='password']"),
            ]
            for selector_type, selector in selectors:
                try:
                    password_field = driver.find_element(selector_type, selector)
                    break
                except:
                    continue
        
        print("Entering password...")
        password_field.clear()
        password_field.send_keys(password)
        time.sleep(1)
        
        # Find and click login button
        print("Clicking login...")
        try:
            login_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        except:
            selectors = [
                (By.ID, "login-button"),
                (By.ID, "submitButton"),
                (By.XPATH, "//button[contains(text(), 'Login')]"),
                (By.XPATH, "//button[contains(text(), 'Anmelden')]"),
            ]
            for selector_type, selector in selectors:
                try:
                    login_button = driver.find_element(selector_type, selector)
                    break
                except:
                    continue
        
        login_button.click()
        
        print("Waiting for login to complete...")
        time.sleep(5)
        
        # Navigate to photos to trigger API calls
        print("Loading photos page...")
        driver.get('https://www.mycloud.swisscom.ch/#photos')
        time.sleep(4)
        
        try:
            get_images(driver)
            if(True):
                exit(0)
        except Exception as e:
            print(f"Error getting images: {e}")
            traceback.print_exc()

        # Extract bearer token from network requests
        print("Extracting bearer token...")
        print("Checking localStorage for token...")
        storage = driver.execute_script("return window.localStorage;")
        for key in storage:
            value = storage[key]
            if value and "Bearer" in value:
                bearer_token = value
                break
            if "token" in key.lower() and value and len(value) > 20:
                bearer_token = f"Bearer {value}" if not value.startswith("Bearer") else value
                break

        if not bearer_token:
            print("Checking sessionStorage...")
            storage = driver.execute_script("return window.sessionStorage;")
            for key in storage:
                value = storage[key]
                if value and "Bearer" in value:
                    bearer_token = value
                    break
        
        if bearer_token:
            print(f"\n✓ SUCCESS! Bearer token obtained")
            print(f"Token: {bearer_token[:50]}...")
            
            # Save to file
            with open('./claude/mycloud_token.txt', 'w') as f:
                f.write(bearer_token)
            print("Token saved to: ./claude/mycloud_token.txt")
        else:
            print("\n✗ Failed to extract bearer token")
            driver.save_screenshot('./claude/login_error.png')
            print("Screenshot saved for debugging: ./claude/login_error.png")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        traceback.print_exc()
        try:
            driver.save_screenshot('./claude/login_error.png')
            print("Screenshot saved: ./claude/login_error.png")
        except:
            pass
    finally:
        driver.quit()
    
    return bearer_token


def main():
    print("="*80)
    print("Swisscom MyCloud - Simple Authentication")
    print("="*80)
    
    # Check for .env
    if not os.path.exists('.env'):
        print("\n⚠ .env file not found!")
        print("\nCreate a .env file with:")
        print("MYCLOUD_USERNAME=your_email@example.com")
        print("MYCLOUD_PASSWORD=your_password")
        print("\nOr copy .env.example to .env and edit it")
        return
    
    # Get MyCloud data
    print("\nStarting automated login...")
    print("(Set headless=True in code to hide browser)")
    
    get_mycloud_data(headless=False)

if __name__ == "__main__":
    main()
    
