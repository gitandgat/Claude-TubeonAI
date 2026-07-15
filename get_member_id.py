#!/usr/bin/env python3
"""
Extract LinkedIn member ID using browser automation
"""

import sys
import json
import time
import re

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("❌ Selenium not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

print("\n" + "="*80)
print("🔍 LinkedIn Member ID Extractor")
print("="*80)

profile_url = "https://www.linkedin.com/in/sahawat-crosswalkwisdom/"

print(f"\n📱 Opening your profile: {profile_url}")
print("⏳ This will open a browser window...\n")

try:
    # Open browser
    driver = webdriver.Chrome()
    driver.get(profile_url)

    # Wait for page to load
    print("⏳ Waiting for page to load...")
    time.sleep(5)

    # Try to find member ID in page source
    page_source = driver.page_source

    # Search for member ID patterns
    patterns = [
        r'"trackingId":"([A-Za-z0-9_-]+)"',
        r'"memberId":"([0-9]+)"',
        r'"id":"([0-9]+)"',
        r'memberID=([0-9]+)',
    ]

    member_id = None
    for pattern in patterns:
        matches = re.findall(pattern, page_source)
        if matches:
            print(f"✅ Found potential ID: {matches[0]}")
            # Filter for numeric IDs
            for match in matches:
                if match.isdigit():
                    member_id = match
                    break
            if member_id:
                break

    # Try to get from meta tags
    if not member_id:
        try:
            meta_url = driver.find_element(By.CSS_SELECTOR, "meta[property='og:url']").get_attribute("content")
            print(f"   Profile meta URL: {meta_url}")
        except:
            pass

    driver.quit()

    if member_id:
        print(f"\n✅ Member ID: {member_id}")
        print(f"   Use this in the automation script")

        # Save to file
        with open("member_id.txt", "w") as f:
            f.write(member_id)
        print(f"✅ Saved to member_id.txt")
    else:
        print("\n⚠️  Could not extract member ID from page")
        print("\nAlternative: Check these browser DevTools steps:")
        print("1. Go to your profile: https://www.linkedin.com/in/sahawat-crosswalkwisdom/")
        print("2. Open DevTools (F12)")
        print("3. Go to Network tab")
        print("4. Reload the page")
        print("5. Look for API calls to 'api.linkedin.com' or 'linkedin.com/feed'")
        print("6. In the response, look for 'id' or 'trackingId' field")
        print("7. Paste the numeric ID here")

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nMake sure you have Chrome/Chromium installed")
    print("Or manually find your member ID in browser DevTools")
