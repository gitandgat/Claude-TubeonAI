import requests
import os
from typing import List

# Add parent directories to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from linkedin_agent.config import REDDIT_BASE_URL, TARGET_SUBREDDITS, REDDIT_FETCH_LIMIT, REDDIT_TIME_FILTER, REDDIT_FILTER_KEYWORDS

class RedditClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

    def fetch_subreddit_posts(self, subreddit: str, limit: int = REDDIT_FETCH_LIMIT) -> list:
        """
        Fetch top posts from a subreddit in the past week.
        Returns list of posts with: title, selftext, score, num_comments, url
        """
        url = f"{REDDIT_BASE_URL}/r/{subreddit}/top.json"
        params = {
            "t": REDDIT_TIME_FILTER,
            "limit": limit
        }

        try:
            resp = self.session.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

            posts = []
            for post in data.get("data", {}).get("children", []):
                post_data = post.get("data", {})
                posts.append({
                    "title": post_data.get("title"),
                    "body": post_data.get("selftext"),
                    "score": post_data.get("score"),
                    "comments": post_data.get("num_comments"),
                    "url": post_data.get("url"),
                    "subreddit": subreddit
                })
            return posts
        except Exception as e:
            print(f"Error fetching r/{subreddit}: {e}")
            return []

    def fetch_all_target_subreddits(self) -> list:
        """Fetch posts from all target subreddits."""
        all_posts = []
        for subreddit in TARGET_SUBREDDITS:
            print(f"  Scanning r/{subreddit}...")
            posts = self.fetch_subreddit_posts(subreddit)
            all_posts.extend(posts)
        return all_posts

    def filter_by_keywords(self, posts: list) -> list:
        """Filter posts that contain IMG-relevant keywords."""
        filtered = []
        for post in posts:
            text = (post.get("title", "") + " " + post.get("body", "")).lower()
            if any(keyword.lower() in text for keyword in REDDIT_FILTER_KEYWORDS):
                filtered.append(post)
        return filtered

    def rank_by_engagement(self, posts: list) -> list:
        """Rank posts by engagement (score + comments)."""
        return sorted(
            posts,
            key=lambda p: p.get("score", 0) + p.get("comments", 0) * 2,
            reverse=True
        )

    def extract_pain_points(self, posts: list) -> list:
        """Extract top 5 pain points from highest-engagement posts."""
        ranked = self.rank_by_engagement(posts)
        pain_points = []

        for post in ranked[:10]:  # Top 10 posts
            title = post.get("title", "")
            if title and len(pain_points) < 5:
                pain_points.append({
                    "topic": title,
                    "engagement": post.get("score", 0) + post.get("comments", 0),
                    "source": f"r/{post.get('subreddit')}",
                    "url": post.get("url")
                })

        return pain_points
