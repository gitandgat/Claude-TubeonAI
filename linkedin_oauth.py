#!/usr/bin/env python3
"""
LinkedIn OAuth 2.0 Authentication
Get access token for LinkedIn API
"""

import webbrowser
import json
import os
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, parse_qs
import requests
from dotenv import load_dotenv

# Load from .env file
load_dotenv()

# LinkedIn OAuth credentials (you need to set these up)
CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/auth/callback"
SCOPE = "openid profile email w_member_social"

# LinkedIn OAuth endpoints
AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

# Global variable to store auth code
auth_code = None
auth_error = None


class LinkedInCallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback from LinkedIn"""

    def do_GET(self):
        global auth_code, auth_error

        if self.path.startswith("/auth/callback"):
            # Parse the authorization code from query string
            params = parse_qs(self.path.split("?")[1])

            if "code" in params:
                auth_code = params["code"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write("""
                    <html>
                    <head><title>LinkedIn Auth Success</title></head>
                    <body>
                        <h1>Authentication Successful!</h1>
                        <p>You can close this window and return to the terminal.</p>
                    </body>
                    </html>
                """.encode())
            elif "error" in params:
                auth_error = params["error"][0]
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(f"""
                    <html>
                    <head><title>LinkedIn Auth Error</title></head>
                    <body>
                        <h1>Authentication Failed</h1>
                        <p>Error: {auth_error}</p>
                    </body>
                    </html>
                """.encode())

    def log_message(self, format, *args):
        """Suppress request logging"""
        pass


def setup_linkedin_app():
    """Guide user through LinkedIn app setup"""
    print("\n" + "="*80)
    print("📋 LinkedIn App Setup Required")
    print("="*80)
    print("""
You need to create a LinkedIn Developer app first:

1. Go to: https://www.linkedin.com/developers/apps
2. Click "Create app"
3. Fill in:
   - App name: "LinkedIn Image Uploader"
   - LinkedIn Page: (select or create one)
   - App logo: (upload a logo)
   - Accept terms and create

4. Once created, go to "Auth" tab and:
   - Add Redirect URL: http://localhost:8000/callback
   - Copy your Client ID and Client Secret

5. Set environment variables:
   export LINKEDIN_CLIENT_ID="your-client-id"
   export LINKEDIN_CLIENT_SECRET="your-client-secret"

6. Run this script again.
""")
    print("="*80)


def get_access_token() -> str:
    """
    Perform LinkedIn OAuth 2.0 flow and return access token

    Returns:
        Access token string
    """
    global auth_code, auth_error

    # Check for credentials
    if not CLIENT_ID or not CLIENT_SECRET:
        setup_linkedin_app()
        return None

    print("\n" + "="*80)
    print("🔐 LinkedIn OAuth Authentication")
    print("="*80)

    # Step 1: Generate authorization URL
    auth_params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "state": "random-state-string"
    }

    auth_request_url = f"{AUTH_URL}?{urlencode(auth_params)}"

    print("\n🌐 Opening LinkedIn authorization page...")
    print("(A browser window will open. Please authorize the app.)\n")

    # Step 2: Open authorization page in browser
    webbrowser.open(auth_request_url)

    # Step 3: Start local server to receive callback
    server = HTTPServer(("localhost", 8000), LinkedInCallbackHandler)
    print("⏳ Waiting for authorization callback...")
    print("(If browser doesn't open, visit this URL manually:)")
    print(f"   {auth_request_url}\n")

    # Handle one request (the callback)
    server.handle_request()
    server.server_close()

    if auth_error:
        print(f"\n❌ Authorization failed: {auth_error}")
        return None

    if not auth_code:
        print("\n❌ No authorization code received")
        return None

    print("✅ Authorization received!")

    # Step 4: Exchange code for access token
    print("🔄 Exchanging authorization code for access token...")

    token_data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    try:
        response = requests.post(TOKEN_URL, data=token_data)
        response.raise_for_status()
        token_response = response.json()

        access_token = token_response.get("access_token")
        if not access_token:
            print("❌ No access token in response")
            return None

        print("✅ Access token received!")

        # Step 5: Save token
        save_token(access_token)

        return access_token

    except Exception as e:
        print(f"❌ Error exchanging token: {e}")
        return None


def save_token(access_token: str):
    """Save access token to local config file and .env"""
    config_dir = Path.home() / ".linkedin"
    config_dir.mkdir(exist_ok=True)

    config_file = config_dir / "config.json"

    config = {
        "access_token": access_token,
        "note": "This file contains your LinkedIn API access token. Keep it secret!"
    }

    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)

    config_file.chmod(0o600)  # Read/write for owner only

    print(f"\n✅ Token saved to: {config_file}")
    print("   (This file is private and should not be shared)")

    # Also update LINKEDIN_ACCESS_TOKEN in .env so automation scripts use the new token
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        lines = env_file.read_text().splitlines()
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("LINKEDIN_ACCESS_TOKEN="):
                lines[i] = f"LINKEDIN_ACCESS_TOKEN={access_token}"
                updated = True
                break
        if not updated:
            lines.append(f"LINKEDIN_ACCESS_TOKEN={access_token}")
        env_file.write_text("\n".join(lines) + "\n")
        print(f"✅ Updated LINKEDIN_ACCESS_TOKEN in .env")
    else:
        env_file.write_text(f"LINKEDIN_ACCESS_TOKEN={access_token}\n")
        print(f"✅ Created .env with LINKEDIN_ACCESS_TOKEN")


def main():
    """Main entry point"""
    access_token = get_access_token()

    if access_token:
        print("\n" + "="*80)
        print("🎉 Authentication Complete!")
        print("="*80)
        print("\nYou can now run the image uploader:")
        print("  python linkedin_image_uploader.py\n")
        print("The script will use your saved access token automatically.")
        return True
    else:
        print("\n❌ Authentication failed. Please try again.")
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
