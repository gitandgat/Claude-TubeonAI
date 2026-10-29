#!/usr/bin/env python3
"""
LinkedIn Wrapper Service
Local service for posting to LinkedIn (browser automation approach)
Works like Zernio - accepts posts + images, handles the complexity
"""

import os
import json
import getpass
from pathlib import Path
from typing import List, Dict, Optional
import time

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.webdriver_chrome_service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("Installing Selenium...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC


class LinkedInWrapperService:
    """
    Local LinkedIn posting service - browser automation based
    Usage:
        service = LinkedInWrapperService(headless=False)
        service.login("your_email@gmail.com", "your_password")
        service.post_with_image("Post text here", "/path/to/image.png")
        service.close()
    """

    def __init__(self, headless: bool = False):
        """Initialize the LinkedIn wrapper service"""
        self.headless = headless
        self.driver = None
        self.logged_in = False

    def start_browser(self):
        """Start the Selenium browser"""
        print("🌐 Starting browser...")
        options = webdriver.ChromeOptions()

        if self.headless:
            options.add_argument("--headless")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"❌ Chrome setup failed: {e}")
            print("   Make sure Google Chrome is installed at /Applications/Google Chrome.app")
            return False

        return True

    def login(self, email: str, password: str) -> bool:
        """
        Login to LinkedIn

        Args:
            email: LinkedIn email
            password: LinkedIn password

        Returns:
            True if login successful
        """
        if not self.driver:
            if not self.start_browser():
                return False

        print(f"🔐 Logging in to LinkedIn as {email}...")

        try:
            self.driver.get("https://www.linkedin.com/login")

            # Wait for email field
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )

            # Enter credentials
            self.driver.find_element(By.ID, "username").send_keys(email)
            self.driver.find_element(By.ID, "password").send_keys(password)

            # Click login button
            self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='Sign in']").click()

            # Wait for successful login
            WebDriverWait(self.driver, 10).until(
                EC.url_contains("linkedin.com/feed")
            )

            self.logged_in = True
            print("✅ Logged in successfully")
            return True

        except Exception as e:
            print(f"❌ Login failed: {e}")
            return False

    def post_with_image(self, text: str, image_path: str) -> bool:
        """
        Create a post with image

        Args:
            text: Post text content
            image_path: Path to image file

        Returns:
            True if post successful
        """
        if not self.logged_in:
            print("❌ Not logged in. Call login() first")
            return False

        if not Path(image_path).exists():
            print(f"❌ Image not found: {image_path}")
            return False

        print(f"\n📝 Creating post...")

        try:
            # Go to feed
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(2)

            # Click "Start a post"
            start_post_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Start a post')]"))
            )
            start_post_btn.click()

            time.sleep(1)

            # Click text area
            text_area = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']"))
            )
            text_area.click()
            text_area.send_keys(text)

            print("   ✓ Text entered")

            # Upload image
            file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            file_input.send_keys(str(Path(image_path).absolute()))

            print("   ✓ Image uploaded")

            time.sleep(2)

            # Click Post button
            post_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Post')]"))
            )
            post_btn.click()

            print("   ✓ Post published")

            # Wait for confirmation
            time.sleep(3)

            print("✅ Post created successfully")
            return True

        except Exception as e:
            print(f"❌ Post failed: {e}")
            return False

    def post_batch(self, posts_with_images: List[Dict[str, str]]) -> Dict[str, any]:
        """
        Create multiple posts

        Args:
            posts_with_images: List of {"text": "...", "image": "path/to/image.png"}

        Returns:
            {"success": int, "failed": int, "results": [...]}
        """
        results = {
            "success": 0,
            "failed": 0,
            "posts": []
        }

        for idx, post_data in enumerate(posts_with_images, 1):
            print(f"\n[{idx}/{len(posts_with_images)}]", end=" ")

            text = post_data.get("text", "")
            image = post_data.get("image", "")

            if self.post_with_image(text, image):
                results["success"] += 1
                results["posts"].append({"index": idx, "status": "success"})
            else:
                results["failed"] += 1
                results["posts"].append({"index": idx, "status": "failed"})

            # Wait between posts
            if idx < len(posts_with_images):
                time.sleep(2)

        return results

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("\n🔐 Browser closed")


# Example usage
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🔗 LinkedIn Wrapper Service")
    print("="*80)

    # Initialize service
    service = LinkedInWrapperService(headless=False)

    # Login (you'll need to provide credentials)
    email = input("\n📧 Enter your LinkedIn email: ")
    password = getpass.getpass("🔐 Enter your LinkedIn password (hidden): ")

    if not service.login(email, password):
        print("❌ Could not log in")
        exit(1)

    # Create a test post
    test_post = {
        "text": "Testing LinkedIn wrapper service! 🚀",
        "image": str(Path.home() / "Downloads" / "Agency LinkedIn Post Pictures" / "01-linkedin-post-problem.png")
    }

    if Path(test_post["image"]).exists():
        service.post_with_image(test_post["text"], test_post["image"])
    else:
        print(f"⚠️  Test image not found: {test_post['image']}")

    # Close when done
    service.close()
