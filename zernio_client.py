import requests
import os


BASE_URL = "https://zernio.com/api/v1"


class ZernioClient:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("ZERNIO_API_KEY")
        if not api_key:
            raise ValueError("ZERNIO_API_KEY not provided and not found in environment")

        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        })

    def get_presigned_url(self, filename: str, content_type: str = "image/jpeg", size: int = None) -> dict:
        """
        Get a presigned URL for uploading a file.
        Returns: {uploadUrl, publicUrl}
        """
        payload = {
            "filename": filename,
            "contentType": content_type,
        }
        if size:
            payload["size"] = size

        resp = self.session.post(f"{BASE_URL}/media/presign", json=payload)
        resp.raise_for_status()
        data = resp.json()

        # Handle both direct response and nested data
        return {
            "uploadUrl": data.get("uploadUrl") or data.get("data", {}).get("uploadUrl"),
            "publicUrl": data.get("publicUrl") or data.get("data", {}).get("publicUrl"),
        }

    def upload_file(self, filepath: str, presigned_url: str, content_type: str = "image/jpeg") -> bool:
        """Upload a file to a presigned URL."""
        with open(filepath, "rb") as f:
            resp = requests.put(
                presigned_url,
                data=f,
                headers={"Content-Type": content_type},
                timeout=(30, 120),  # 30s connect, 120s read — presigned PUT to S3 can be slow
            )
            resp.raise_for_status()
        return True

    def upload_image(self, filepath: str) -> str:
        """
        Upload an image file and return its public URL.
        Handles getting presigned URL and uploading in one call.
        """
        filename = os.path.basename(filepath)
        file_size = os.path.getsize(filepath)

        presign_data = self.get_presigned_url(filename, "image/jpeg", file_size)

        if not presign_data["uploadUrl"] or not presign_data["publicUrl"]:
            raise ValueError(f"Missing URLs in presign response: {presign_data}")

        self.upload_file(filepath, presign_data["uploadUrl"], "image/jpeg")
        return presign_data["publicUrl"]

    def upload_video(self, filepath: str) -> str:
        """Upload an mp4 and return its public URL (same presigned flow, video type)."""
        filename = os.path.basename(filepath)
        file_size = os.path.getsize(filepath)

        presign_data = self.get_presigned_url(filename, "video/mp4", file_size)
        if not presign_data["uploadUrl"] or not presign_data["publicUrl"]:
            raise ValueError(f"Missing URLs in presign response: {presign_data}")

        self.upload_file(filepath, presign_data["uploadUrl"], "video/mp4")
        return presign_data["publicUrl"]

    def delete_post(self, post_id: str) -> bool:
        """Delete a post by ID."""
        resp = self.session.delete(f"{BASE_URL}/posts/{post_id}")
        return resp.status_code in (200, 204)

    def schedule_post(
        self,
        content: str,
        scheduled_for: str,
        timezone: str,
        platforms: list,
        media_items: list = None,
        title: str = None,
    ) -> dict:
        """
        Schedule a post to one or more platforms.

        Args:
            content: Default content for all platforms
            scheduled_for: ISO 8601 datetime (e.g., "2026-03-24T09:00:00")
            timezone: Timezone string (e.g., "America/New_York")
            platforms: List of platform configs, each with:
                {
                    "platform": "linkedin|instagram|facebook|tiktok|youtube",
                    "accountId": "...",
                    "customContent": "..." (optional, overrides default content)
                }
            media_items: List of media, each with {"url": "...", "type": "image|video"}
            title: Optional post title

        Returns: API response dict
        """
        payload = {
            "content": content,
            "scheduledFor": scheduled_for,
            "timezone": timezone,
            "platforms": platforms,
        }

        if media_items:
            payload["mediaItems"] = media_items

        if title:
            payload["title"] = title

        resp = self.session.post(f"{BASE_URL}/posts", json=payload)
        resp.raise_for_status()
        return resp.json()

    def get_post(self, post_id: str) -> dict:
        """Get details of a specific post."""
        resp = self.session.get(f"{BASE_URL}/posts/{post_id}")
        resp.raise_for_status()
        return resp.json()

    def list_posts(self, account_id: str = None, limit: int = 50, offset: int = 0) -> dict:
        """List posts, optionally filtered by account."""
        params = {"limit": limit, "offset": offset}
        if account_id:
            params["accountId"] = account_id

        resp = self.session.get(f"{BASE_URL}/posts", params=params)
        resp.raise_for_status()
        return resp.json()

    def update_post(self, post_id: str, **kwargs) -> dict:
        """Update a post (content, scheduledFor, etc.)."""
        resp = self.session.patch(f"{BASE_URL}/posts/{post_id}", json=kwargs)
        resp.raise_for_status()
        return resp.json()

    def get_accounts(self) -> dict:
        """List all connected social media accounts."""
        resp = self.session.get(f"{BASE_URL}/accounts")
        resp.raise_for_status()
        return resp.json()
