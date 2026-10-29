import requests
import os
import json
from datetime import datetime, timedelta

# LinkedIn API endpoints
LINKEDIN_AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
LINKEDIN_TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
LINKEDIN_API_BASE = "https://api.linkedin.com/v2"

class LinkedInAPIClient:
    """
    LinkedIn Marketing Developer Platform API client.
    Handles OAuth 2.0 flow and direct LinkedIn post creation.
    """

    def __init__(self, client_id: str = None, client_secret: str = None, access_token: str = None):
        self.client_id = client_id or os.getenv("LINKEDIN_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("LINKEDIN_CLIENT_SECRET")
        self.access_token = access_token or os.getenv("LINKEDIN_ACCESS_TOKEN")
        self.redirect_uri = os.getenv("LINKEDIN_REDIRECT_URI", "http://localhost:8000/auth/callback")

        # LinkedIn user URN (format: urn:li:person:{id})
        self.user_urn = os.getenv("LINKEDIN_USER_URN")

        if not self.client_id or not self.client_secret:
            raise ValueError("LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET required")

        self.session = requests.Session()
        self.token_file = ".linkedin_token"

    def get_auth_url(self) -> str:
        """Generate LinkedIn OAuth authorization URL."""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "w_member_social"
        }
        return f"{LINKEDIN_AUTH_URL}?" + "&".join([f"{k}={v}" for k, v in params.items()])

    def exchange_code_for_token(self, code: str) -> dict:
        """Exchange authorization code for access token."""
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri
        }

        resp = requests.post(LINKEDIN_TOKEN_URL, data=payload)
        resp.raise_for_status()
        token_data = resp.json()

        # Save token for later use
        self.access_token = token_data["access_token"]
        self._save_token(token_data)

        return token_data

    def _save_token(self, token_data: dict):
        """Save token data to file for refresh later."""
        with open(self.token_file, "w") as f:
            json.dump(token_data, f)

    def _load_token(self) -> dict:
        """Load token data from file."""
        if os.path.exists(self.token_file):
            with open(self.token_file, "r") as f:
                return json.load(f)
        return {}

    def refresh_access_token(self) -> bool:
        """Refresh expired access token."""
        token_data = self._load_token()
        if "refresh_token" not in token_data:
            print("No refresh token available")
            return False

        payload = {
            "grant_type": "refresh_token",
            "refresh_token": token_data["refresh_token"],
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        try:
            resp = requests.post(LINKEDIN_TOKEN_URL, data=payload)
            resp.raise_for_status()
            new_token_data = resp.json()
            self.access_token = new_token_data["access_token"]
            self._save_token(new_token_data)
            return True
        except Exception as e:
            print(f"Error refreshing token: {e}")
            return False

    def create_post(self, text: str, image_url: str = None, scheduled_for: str = None) -> str:
        """
        Create a LinkedIn post.

        Note: Share on LinkedIn API only supports immediate publishing, not scheduling.
        Posts are published immediately upon creation.

        Args:
            text: Post content
            image_url: Optional image URL (will be used as-is for now)
            scheduled_for: Ignored (Share on LinkedIn doesn't support scheduling)

        Returns: Post ID
        """
        if not self.access_token:
            raise ValueError("No access token. Complete OAuth flow first")

        # Fix user URN format - should be urn:li:member: not urn:li:person:
        author_urn = self.user_urn
        if author_urn and author_urn.startswith("urn:li:person:"):
            # Convert person URN to member URN
            user_id = author_urn.replace("urn:li:person:", "")
            author_urn = f"urn:li:member:{user_id}"

        if not author_urn:
            raise ValueError("LINKEDIN_USER_URN not set. Run setup_user_urn() first")

        # Build post content
        content = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "IMAGE" if image_url else "NONE"
                }
            }
        }

        # Add image if provided
        if image_url:
            # For now, use the image URL directly as the media field
            # LinkedIn's Share on LinkedIn API may require pre-uploading images
            # but we'll attempt direct URL usage first
            content["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                {
                    "status": "READY",
                    "description": {
                        "text": "LinkedIn post image"
                    },
                    "media": image_url,
                    "title": {
                        "text": "Post image"
                    }
                }
            ]

        # Note: Share on LinkedIn API does not support scheduling (firstPublishedAt, distribution fields)
        # Posts are published immediately upon creation
        # For scheduled posting, Marketing Developer Platform would be needed (different tier)

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }

        try:
            resp = requests.post(
                f"{LINKEDIN_API_BASE}/ugcPosts",
                json=content,
                headers=headers
            )
            resp.raise_for_status()
            response_data = resp.json()

            # Extract post ID from response
            post_id = response_data.get("id") or response_data.get("$id", "")
            return post_id

        except requests.exceptions.HTTPError as e:
            print(f"Error creating post: {e.response.status_code}")
            print(f"Response: {e.response.text}")
            raise

    def setup_user_urn(self, user_id: str):
        """Set the user URN (format: urn:li:person:{id})."""
        self.user_urn = f"urn:li:person:{user_id}"
        os.environ["LINKEDIN_USER_URN"] = self.user_urn

    def get_me(self) -> dict:
        """Get current user info to retrieve user ID."""
        if not self.access_token:
            raise ValueError("No access token. Complete OAuth flow first")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-Restli-Protocol-Version": "2.0.0"
        }

        try:
            resp = requests.get(f"{LINKEDIN_API_BASE}/me", headers=headers)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            print(f"Note: /me endpoint requires additional scopes. You can set LINKEDIN_USER_URN manually.")
            print(f"Format: urn:li:person:YOUR_LINKEDIN_USER_ID")
            raise
