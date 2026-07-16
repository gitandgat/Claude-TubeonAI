# Quick Start: Demand Discovery in 5 Minutes

## 1. Install & Setup (2 min)

```bash
# Install dependencies
pip install -r requirements-demand-discovery.txt

# Create .env file
cp .env.demand-discovery .env
```

**Then edit `.env` and add:**
- Reddit Client ID / Secret (get from https://reddit.com/prefs/apps)
- Anthropic API Key

## 2. Run the Pipeline (2-3 min)

```bash
python demand_discovery_orchestrator.py
```

This will:
- ✅ Scrape 5 subreddits (500 posts total)
- ✅ Score each one (0-100)
- ✅ Detect patterns
- ✅ Evaluate monetization models
- ✅ Generate summary

## 3. Review Results (1-2 min)

```bash
# View the summary
cat discovery_summary.txt

# Or open the JSON files
cat demand_discoveries.json | jq '.opportunities[] | {title, score, demand_level}'
```

**Look for:**
- Score > 80 (high confidence)
- demand_level: "high"
- Appears in multiple subreddits

## 4. Pick Your Winner

Example high-confidence opportunity:

```json
{
  "title": "AI tool to write LinkedIn posts from YouTube video transcripts",
  "score": 92,
  "demand_level": "high",
  "skill_required": "content automation",
  "upvotes": 142,
  "num_comments": 28,
  "subreddit": "solopreneur",
  "recommended_model": "saas",
  "price_range": "$29-99/mo"
}
```

## Common Use Cases

### Use Case 1: Validate a Specific Idea
```python
from reddit_demand_scraper import validate_post

# Create a post object with your idea
test_post = RedditPost(
    id="test", subreddit="test", title="Your idea here",
    selftext="Problem description", upvotes=0, num_comments=0,
    created_utc=0, url="", author="test"
)

result = validate_post(test_post)
print(f"Claude thinks this is solvable: {result.claude_solvable}")
print(f"Score: {result.score}/100")
```

### Use Case 2: Monitor One Subreddit Continuously
```bash
# Edit reddit_demand_scraper.py, change:
TARGET_SUBREDDITS = ["HelpMeFind"]  # Just one community

# Run daily:
python -c "from reddit_demand_scraper import run_discovery_cycle; \
  winners = run_discovery_cycle(limit=200); \
  print(f'Found {len(winners)} opportunities today')"
```

### Use Case 3: Feed Results to Product Builder
```python
import json

# Load discoveries
with open("demand_discoveries.json") as f:
    data = json.load(f)

# Get top 3 for product team
top_3 = data["opportunities"][:3]

# Create PRD template
for opp in top_3:
    print(f"""
# PRD: {opp['title']}
## Problem
{opp['explanation']}

## Market Size
- Demand Level: {opp['demand_level']}
- Validation: {opp['upvotes']} upvotes, {opp['num_comments']} comments on Reddit
- Source: r/{opp['subreddit']}

## Recommended Monetization
See monetization_evals.json

## Next Step
1. Survey 30 people in r/{opp['subreddit']}
2. Validate they'd pay for solution
3. Build MVP
""")
```

### Use Case 4: Export to Slack
```python
import json
import os

data = json.load(open("demand_discoveries.json"))
webhook_url = os.getenv("SLACK_WEBHOOK_URL")

for opp in data["opportunities"][:5]:
    message = f"""
🎯 *{opp['title']}*
Score: {opp['score']}/100 | Demand: {opp['demand_level']}
Skill: {opp['skill_required']}
Engagement: {opp['upvotes']}👍 {opp['num_comments']}💬
Source: r/{opp['subreddit']}
<{opp['url']}|View on Reddit>
"""
    # Post to Slack...
```

### Use Case 5: Track Over Time
```bash
# Run weekly discovery
0 9 * * 1 python demand_discovery_orchestrator.py

# After 4 weeks, analyze patterns
python pattern_detector.py

# See which problems keep appearing = highest confidence
```

## Expected Output Files

After running the pipeline, you'll get:

```
📁 Output Files:
├── demand_discoveries.json      ← All scored opportunities
├── pattern_analysis.json        ← Recurring themes (80%+ confidence)
├── monetization_evals.json      ← Business model recommendations
├── discovery_summary.txt        ← Executive summary (human readable)
└── discovery_history.json       ← Historical cycles (grows over time)
```

## Key Metrics to Look For

### Opportunity Scoring
- **80-100:** Ready to build MVP
- **70-79:** Validate further
- **50-69:** Interesting but needs more signals
- **< 50:** Skip for now

### Demand Signals
- **High:** > 100 engagement score
- **Medium:** 30-100 engagement score
- **Low:** < 30 engagement score

### Confidence Levels
- **95-100%:** Pattern appeared 5+ times → Build this
- **80-94%:** Pattern appeared 3-4 times → Validate first
- **< 80%:** Single occurrence → Research more

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "401 Unauthorized" | Check Reddit credentials in .env |
| "API rate limited" | Wait 1 hour, then rerun |
| "No opportunities" | Try limit=200 instead of limit=50 |
| "ImportError: No module praw" | Run: pip install -r requirements-demand-discovery.txt |

## Customization Tips

### Add More Subreddits
Edit `reddit_demand_scraper.py`:
```python
TARGET_SUBREDDITS = [
    "solopreneur",
    "Entrepreneur",
    "freelance",
    "HelpMeFind",
    "SideProject",
    "startups",           # Add here
    "IndieHackers",       # And here
]
```

### Adjust Scoring Threshold
Edit `reddit_demand_scraper.py`:
```python
# Only show opportunities with score >= 60 (default is > 0)
winners = [p for p in validated if p.score >= 60]
```

### Change Monetization Model Priority
Edit `monetization_evaluator.py` prompt to weight models differently:
```python
# Add weight to specific model if it fits your business better
prompt = """...
Rate SaaS (weight: 1.5x) vs Services (weight: 1.0x) vs Products (weight: 0.8x)
"""
```

## Next: From Discovery to Launch

Once you have a winner:

1. **Validate** (1 week)
   - Survey 30+ people from the Reddit thread
   - Build landing page
   - Collect emails

2. **Build MVP** (2-4 weeks)
   - Code MVP using Claude
   - Keep it minimal (one core feature)
   - Ship fast

3. **Get First Users** (1 week)
   - Reply to original Reddit posts with solution
   - Offer free access to early adopters
   - Collect feedback

4. **Iterate** (Ongoing)
   - Use early user feedback
   - Improve 1 thing per week
   - Grow to paid tier

## Resources

- **Full Guide:** DEMAND_DISCOVERY_README.md
- **Reddit API Setup:** https://www.reddit.com/prefs/apps
- **Anthropic API:** https://console.anthropic.com
- **PRAW Docs:** https://praw.readthedocs.io

---

You now have a system that finds high-demand, high-confidence problems every day.
The rest is execution.
