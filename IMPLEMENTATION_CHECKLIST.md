# Implementation Checklist

Use this checklist to verify your demand discovery system is working correctly.

## Setup Phase

- [ ] **Dependencies Installed**
  ```bash
  pip install -r requirements-demand-discovery.txt
  ```
  Verify: `python -c "import praw, anthropic; print('✅ Dependencies OK')"`

- [ ] **Reddit API Credentials Obtained**
  - [ ] Go to https://www.reddit.com/prefs/apps
  - [ ] Create new app (type: "script")
  - [ ] Copy Client ID
  - [ ] Copy Client Secret
  - [ ] Create User Agent string

- [ ] **.env File Created**
  ```bash
  cp .env.demand-discovery .env
  # Edit .env with your actual credentials
  ```
  Verify: `cat .env | grep -E "REDDIT_|ANTHROPIC_" | wc -l` → Should show 4

- [ ] **Anthropic API Key Valid**
  - [ ] Log in to https://console.anthropic.com
  - [ ] Create or copy API key
  - [ ] Add to .env
  Verify: `python -c "import os; os.getenv('ANTHROPIC_API_KEY')" | grep -q "sk-" && echo "✅"`

## First Run Phase

- [ ] **Test Individual Components**

  **Scraper Test:**
  ```bash
  python -c "
from reddit_demand_scraper import scrape_subreddit_posts
posts = scrape_subreddit_posts('HelpMeFind', limit=5)
print(f'✅ Scraped {len(posts)} posts')
  "
  ```
  Expected: "✅ Scraped 5 posts"

  **Validation Test:**
  ```bash
  python -c "
from reddit_demand_scraper import detect_demand_intent, RedditPost
post = RedditPost('1', 'test', 'does anyone know a tool for X?', '', 0, 0, 0, '', '')
is_demand, _ = detect_demand_intent(post)
print(f'✅ Intent detection: {is_demand}')
  "
  ```
  Expected: "✅ Intent detection: True"

- [ ] **Run Full Pipeline**
  ```bash
  python demand_discovery_orchestrator.py
  ```
  Expected:
  - ✅ Phase 1 complete (scrape)
  - ✅ Phase 2 complete (validate)
  - ✅ Phase 3 complete (pattern detect)
  - ✅ Phase 4 complete (monetization)
  - 🎯 TOP OPPORTUNITIES section shows opportunities
  - 💾 Results saved to 4 JSON files

- [ ] **Check Output Files Exist**
  ```bash
  ls -lh demand_discoveries.json pattern_analysis.json \
         monetization_evals.json discovery_summary.txt
  ```
  All 4 files should exist and be > 1KB

- [ ] **Verify Output Quality**

  **Check discoveries scored correctly:**
  ```bash
  python -c "
import json
with open('demand_discoveries.json') as f:
    data = json.load(f)
opp = data['opportunities'][0] if data['opportunities'] else {}
print(f\"Top: {opp.get('score', 0)}/100 | {opp.get('demand_level', 'N/A')}\")
  "
  ```
  Expected: Score > 50, demand_level is one of high/medium/low

  **Check patterns found:**
  ```bash
  python -c "
import json
with open('pattern_analysis.json') as f:
    data = json.load(f)
patterns = data.get('recurring_patterns', [])
print(f\"✅ Found {len(patterns)} patterns\")
  "
  ```
  Expected: Find at least 1-2 patterns (0 is OK on first run)

  **Check monetization evals:**
  ```bash
  python -c "
import json
with open('monetization_evals.json') as f:
    data = json.load(f)
evals = data.get('evaluations', [])
if evals:
    print(f\"✅ {evals[0]['title'][:40]} → {evals[0]['recommended_model']}\")
  "
  ```
  Expected: Shows recommended model (saas, services, or products)

- [ ] **Review Executive Summary**
  ```bash
  head -30 discovery_summary.txt
  ```
  Expected: Shows top 3 opportunities with scores and demand levels

## Validation Phase

- [ ] **Spot Check Top Opportunity**
  - [ ] Open Reddit URL from discovery
  - [ ] Confirm post actually asks for this problem
  - [ ] Confirm engagement numbers match (upvotes/comments)
  - [ ] Confirm demand is real (not spam/troll)

- [ ] **Verify Solvability Assessment**
  - [ ] Read the "why" explanation for top opportunity
  - [ ] Ask yourself: "Could Claude solve this?"
  - [ ] Compare to skill_required field
  - [ ] Mark ✅ if assessment seems accurate

- [ ] **Check Pattern Confidence**
  - [ ] Look at highest-confidence pattern
  - [ ] Verify confidence > 60% 
  - [ ] If confidence < 50%, understand why (new/rare problem)
  - [ ] Mark ✅ if confidence levels make sense

- [ ] **Validate Monetization Recommendation**
  - [ ] Read recommended model for top opportunity
  - [ ] Read the "reasoning" field
  - [ ] Ask: "Does this model make sense?"
  - [ ] Mark ✅ if recommendation is defensible

## Ongoing Operation

- [ ] **Schedule Regular Runs**
  
  **Option A: Manual (Weekly)**
  ```bash
  # Run every Monday at 9am
  0 9 * * 1 cd /path/to/repo && python demand_discovery_orchestrator.py
  ```
  Add to crontab: `crontab -e`

  **Option B: Check Manually**
  ```bash
  # When you want to check for new opportunities
  python demand_discovery_orchestrator.py
  ```

- [ ] **Monitor Output History**
  ```bash
  # After 4+ runs, check pattern confidence
  python pattern_detector.py
  ```
  Expected: Recurring patterns have confidence > 80%

- [ ] **Archive Results**
  ```bash
  mkdir -p discovery_archive/$(date +%Y-%m-%d)
  cp *discoveries.json discovery_archive/$(date +%Y-%m-%d)/
  ```
  Keep history to track emerging trends

## Integration Phase

- [ ] **Feed to Market Research Agent**
  ```bash
  python agent_integration_example.py
  ```
  Expected: Generates market research, PRD, launch plan for top opportunity

- [ ] **Export to Product Management Tool**
  - [ ] Create Coda/Notion/Linear integration
  - [ ] Auto-create issues from high-scoring opportunities
  - [ ] Link back to Reddit source

- [ ] **Set Up Slack Notifications**
  - [ ] Create webhook at https://api.slack.com/apps
  - [ ] Post high-confidence (80%+) opportunities to Slack
  - [ ] Create daily digest of new discoveries

- [ ] **Create Monitoring Dashboard**
  - [ ] Track: # of opportunities per week
  - [ ] Track: Average score trend
  - [ ] Track: Pattern confidence growth
  - [ ] Track: Model recommendation breakdown

## Troubleshooting Checklist

### Issue: "No opportunities found"
- [ ] Check that posts actually exist on subreddit
- [ ] Verify Reddit API credentials work
- [ ] Try increasing limit: `run_discovery_cycle(limit=200)`
- [ ] Check if subreddit requires authentication
- [ ] Try different subreddit: `TARGET_SUBREDDITS = ["HelpMeFind"]`

### Issue: "API rate limited"
- [ ] Wait 1 hour
- [ ] Add delay between API calls
- [ ] Reduce `limit` parameter (100 → 50)
- [ ] Space out runs by several hours

### Issue: "Claude refuses evaluation"
- [ ] Check if post contains sensitive content
- [ ] Try on a different post
- [ ] Add safeguards to evaluation prompt
- [ ] Increase `max_tokens` in API call

### Issue: "Pattern detection finds nothing"
- [ ] This is normal on first run
- [ ] Run scraper 2-3 times over several days
- [ ] Pattern detection needs historical data
- [ ] Check discovery_history.json has multiple cycles

### Issue: "Monetization eval fails"
- [ ] Check Anthropic API key is valid
- [ ] Verify you have credits available
- [ ] Try smaller opportunity list (top 3 only)
- [ ] Check error message for specific reason

### Issue: "Can't find .env file"
- [ ] Verify file exists: `ls -la .env`
- [ ] Verify in correct directory (repo root)
- [ ] Verify readable: `cat .env | head -1`
- [ ] Check `python-dotenv` is installed

## Quality Metrics

Track these metrics to ensure system health:

| Metric | Target | Current |
|--------|--------|---------|
| Opportunities found per run | 15-50 | __ |
| Avg top opportunity score | > 70 | __ |
| High-demand posts (level=HIGH) | > 5 | __ |
| Patterns with 80%+ confidence | > 0 | __ |
| Solvable posts (%) | > 50% | __ |
| Avg engagement (upvotes) | > 50 | __ |
| Runtime (minutes) | < 10 | __ |
| API cost per run | < $1 | __ |

## Post-Launch Validation

After running for 4+ weeks:

- [ ] **Trend Analysis**
  - [ ] Run pattern_detector.py
  - [ ] Are the same problems recurring? (good sign)
  - [ ] Are new trends emerging? (volatility check)
  - [ ] Is confidence improving? (signal quality)

- [ ] **Build One MVP**
  - [ ] Pick highest-confidence opportunity
  - [ ] Build minimal MVP (2-4 weeks)
  - [ ] Get real customers from Reddit threads
  - [ ] Track: conversion from discovery to customer

- [ ] **Measure Accuracy**
  - [ ] What % of discovered opportunities had real demand?
  - [ ] What % did Claude correctly assess?
  - [ ] What % monetization model recommendations were right?
  - [ ] Feedback loop: update prompts based on learnings

- [ ] **Calculate ROI**
  ```
  ROI = (Value from successful launch - Discovery cost) / Discovery cost × 100%
  
  Example:
  - Discovery cost: $5/month × 4 months = $20
  - Product revenue: $1000/month × 4 months = $4000
  - ROI = ($4000 - $20) / $20 × 100% = 19,900%
  ```

## Success Criteria

You've successfully implemented the system when:

- ✅ Running the orchestrator takes < 10 minutes
- ✅ Top opportunity has score > 75 and demand_level = HIGH
- ✅ Pattern analysis shows 80%+ confidence for top 3 patterns
- ✅ Monetization evaluation recommends a clear model with reasoning
- ✅ Manual spot-check: Reddit post confirms demand is real
- ✅ After 4+ runs: Patterns show recurring themes (not random)
- ✅ Successfully run agent integration on top opportunity
- ✅ Have clear next steps documented for building

---

You're now ready to discover market opportunities automatically!
