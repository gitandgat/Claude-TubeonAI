import requests
from typing import List
from bs4 import BeautifulSoup
import os

# Add parent directories to path if needed (for future use)
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class LinkedInScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })

    def search_viral_posts(self, query: str = "IMG career pivot OR medical license") -> list:
        """
        Search for viral LinkedIn posts using Google search syntax.
        Returns list of posts with title and og:description preview.
        """
        search_url = "https://www.google.com/search"
        params = {
            "q": f'site:linkedin.com/posts "{query}"',
            "num": 10
        }

        try:
            resp = self.session.get(search_url, params=params)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, "html.parser")

            posts = []
            for link in soup.find_all("a", href=True)[:10]:
                href = link["href"]
                if "linkedin.com/posts" in href and "url?q=" in href:
                    # Extract actual URL from Google redirect
                    url = href.split("url?q=")[1].split("&")[0]
                    if url.startswith("https://"):
                        posts.append({
                            "url": url,
                            "title": link.get_text(strip=True)[:100],
                            "source": "linkedin"
                        })
            return posts
        except Exception as e:
            print(f"Error searching viral posts: {e}")
            return []

    def extract_post_preview(self, url: str) -> dict:
        """
        Attempt to fetch LinkedIn post and extract og:description.
        Note: LinkedIn may block direct requests. Fallback to title.
        """
        try:
            resp = self.session.get(url, timeout=5)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, "html.parser")

            og_desc = soup.find("meta", property="og:description")
            og_title = soup.find("meta", property="og:title")

            return {
                "url": url,
                "description": og_desc.get("content") if og_desc else "",
                "title": og_title.get("content") if og_title else "",
            }
        except Exception as e:
            # LinkedIn blocks direct scraping; return minimal info
            return {
                "url": url,
                "description": "",
                "title": "LinkedIn post"
            }

    def fetch_viral_post_templates(self) -> list:
        """
        Fetch and extract viral LinkedIn post templates.
        Returns top 3-5 posts with extracted text.
        """
        search_queries = [
            "IMG career pivot Canada",
            "medical license sunk cost",
            "career change physician burnout"
        ]

        all_posts = []
        for query in search_queries:
            print(f"  Searching: {query}...")
            posts = self.search_viral_posts(query)
            all_posts.extend(posts)

        # Extract previews (best effort; LinkedIn blocks scraping)
        templates = []
        for post in all_posts[:5]:
            preview = self.extract_post_preview(post["url"])
            templates.append({
                "url": preview["url"],
                "hook": preview["title"][:80] if preview["title"] else "LinkedIn post",
                "source": "linkedin"
            })

        return templates
