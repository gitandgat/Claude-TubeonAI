#!/usr/bin/env python3
"""
Selenium Chrome Setup Fixer
Diagnoses and fixes chromedriver issues on Mac
"""

import subprocess
import os
import json
from pathlib import Path
import urllib.request
import zipfile

def get_chrome_version():
    """Get installed Chrome version"""
    try:
        result = subprocess.run(
            ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"],
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"❌ Chrome not found: {e}")
        return None

def download_chromedriver(version):
    """Download matching chromedriver"""
    print(f"\n📥 Downloading chromedriver for Chrome {version}...")

    # Extract major version
    major_version = version.split()[2].split('.')[0]

    # Try to get download URL from chromedriver JSON endpoint
    try:
        url = f"https://googlechromelabs.github.io/chrome-for-testing/json/api_v1/channels/Stable"
        # Simplified approach - use webdriver-manager instead
        print("   Installing webdriver-manager to auto-download correct chromedriver...")
        subprocess.check_call(["pip", "install", "webdriver-manager"])
        return True
    except Exception as e:
        print(f"❌ Failed to download: {e}")
        return False

def main():
    """Main diagnostic flow"""
    print("\n" + "="*80)
    print("🔧 Selenium Chrome Setup Fixer")
    print("="*80)

    # Check Chrome
    print("\n📍 Checking Chrome installation...")
    chrome_version = get_chrome_version()

    if not chrome_version:
        print("❌ Google Chrome is not installed at /Applications/Google Chrome.app")
        print("   Install Chrome from: https://www.google.com/chrome/")
        return False

    print(f"✅ Found: {chrome_version}")

    # Fix: Use webdriver-manager
    print("\n📥 Setting up webdriver-manager (auto-downloads correct chromedriver)...")
    try:
        subprocess.check_call(["pip", "install", "webdriver-manager", "-q"])
        print("✅ webdriver-manager installed")
    except Exception as e:
        print(f"❌ Failed to install webdriver-manager: {e}")
        return False

    # Update the wrapper script to use webdriver-manager
    print("\n✏️  Updating linkedin_wrapper_service.py...")

    wrapper_path = Path("linkedin_wrapper_service.py")
    if wrapper_path.exists():
        content = wrapper_path.read_text()

        # Replace the Chrome initialization
        old_chrome = """try:
            self.driver = webdriver.Chrome(options=options)
        except Exception as e:
            print(f"❌ Chrome not found: {e}")
            print("   Install Chrome/Chromium or Selenium WebDriver")
            return False"""

        new_chrome = """try:
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service

            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"❌ Chrome setup failed: {e}")
            print("   Make sure Google Chrome is installed at /Applications/Google Chrome.app")
            return False"""

        if old_chrome in content:
            content = content.replace(old_chrome, new_chrome)
            wrapper_path.write_text(content)
            print("✅ Updated wrapper script to use webdriver-manager")
        else:
            print("⚠️  Could not find Chrome initialization code to update")

    print("\n" + "="*80)
    print("✅ Setup complete! Try running:")
    print("   python linkedin_auto_post.py")
    print("="*80 + "\n")

    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
