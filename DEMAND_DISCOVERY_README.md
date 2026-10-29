# Reddit Demand Discovery Agent Suite

AI-powered system that automatically discovers market opportunities by scraping Reddit, validating demand, analyzing patterns, and recommending monetization strategies.

## Overview

This system runs a 4-phase pipeline to find Claude-solvable problems with proven market demand:

1. **Phase 1: Reddit Scraping** — Monitors 5 subreddits for demand signals
2. **Phase 2: Demand Validation** — Uses Claude to score opportunities (0-100)
3. **Phase 3: Pattern Detection** — Identifies recurring problems across time/subreddits
4. **Phase 4: Monetization Eval** — Recommends SaaS vs Services vs Digital Products

## Quick Start

### 1. Install Dependencies

```bash
pip install praw anthropic python-dotenv
```

### 2. Set Up Reddit API Credentials

1. Go to https://www.reddit.com/prefs/apps
2. Click "Create an app" at the bottom
3. Fill in:
   - **name:** DemandDiscoveryAgent
   - **app type:** script
   - **redirect uri:** http://localhost:8080
4. Copy the credentials (Client ID and Client Secret)

### 3. Create Environment File

Copy `.env.demand-discovery` to `.env` and fill in your credentials:

```bash
cp .env.demand-discovery .env
```

```env
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USER_AGENT=DemandDiscoveryAgent/1.0 (by your_reddit_username)
ANTHROPIC_API_KEY=your_anthropic_key
```

### 4. Run the Pipeline

```bash
python demand_discovery_orchestrator.py
```

This runs all 4 phases and outputs:
- `demand_discoveries.json` — Scored opportunities
- `pattern_analysis.json` — Recurring themes
- `monetization_evals.json` — MtM recommendations
- `discovery_summary.txt` — Executive summary

## Individual Components

### Reddit Demand Scraper
Scrapes recent posts from 5 target subreddits and scores them.

```bash
python reddit_demand_scraper.py
```

**Output:** `demand_discoveries.json`

**What it does:**
- Scrapes last 7 days of posts from each subreddit (100 posts/sub)
- Detects demand intent using regex patterns
- Uses Claude to evaluate if Claude can solve it
- Scores opportunities 0-100 based on engagement + solvability
- Outputs top opportunities with full context

**Scoring Logic:**
- Post must match 2+ demand intent patterns
- Claude must evaluate it as solvable
- Engagement score = upvotes + (comments × 2) × recency_multiplier
- High demand: score > 100, Medium: > 30, Low: < 30

### Pattern Detector
Finds recurring problems and emerging trends.

```bash
python pattern_detector.py
```

**Output:** `pattern_analysis.json`

**What it does:**
- Clusters opportunities by semantic similarity
- Calculates how often each problem appears across cycles
- Identifies problems just starting to gain traction
- Estimates confidence level based on repetition frequency

### Monetization Evaluator
Analyzes viability of SaaS, Services, and Digital Products.

```bash
python monetization_evaluator.py
```

**Output:** `monetization_evals.json`

**What it does:**
- Evaluates each top opportunity across 3 business models
- Scores each model 0-10 on: market size, build effort, pricing power
- Recommends the best fit with reasoning
- Lists 3 concrete next steps for building

## Sample Output Structure

### demand_discoveries.json
```json
{
  "timestamp": "2026-06-07T14:32:00",
  "total_discovered": 25,
  "opportunities": [
    {
      "id": "abc123",
      "subreddit": "solopreneur",
      "title": "Looking for AI tool to automate LinkedIn posting",
      "upvotes": 142,
      "num_comments": 28,
      "score": 92,
      "demand_level": "high",
      "claude_solvable": true,
      "skill_required": "content automation",
      "explanation": "Market needs AI-powered social media scheduling with voice-to-post capability",
      "url": "https://reddit.com/r/solopreneur/comments/..."
    }
  ]
}
```

### pattern_analysis.json
```json
{
  "timestamp": "2026-06-07T14:35:00",
  "recurring_patterns": [
    {
      "cluster": "AI-powered email marketing automation",
      "total_occurrences": 7,
      "avg_engagement": 145,
      "confidence": 0.95,
      "pattern_strength": "strong"
    }
  ],
  "emerging_trends": [
    {
      "trend": "AI-powered resume optimization for specific job markets",
      "why_emerging": "First appearing in r/freelance and r/HelpMeFind",
      "demand_velocity": "accelerating",
      "early_adopter_indicators": ["career changers", "international applicants"]
    }
  ]
}
```

### monetization_evals.json
```json
{
  "timestamp": "2026-06-07T14:38:00",
  "evaluations": [
    {
      "title": "AI LinkedIn Post Generator",
      "recommended_model": "saas",
      "reasoning": "Large recurring market, easy to scale, $29-99/mo pricing validates demand",
      "next_steps": [
        "Validate: survey 50 LinkedIn creators on willingness to pay",
        "MVP: build Chrome extension that generates posts from YouTube URLs",
        "Launch: tier pricing ($29 starter, $79 pro)"
      ],
      "viability_scores": {
        "saas": 9,
        "services": 5,
        "products": 4
      }
    }
  ]
}
```

## Target Subreddits

The system monitors these communities for demand signals:

| Subreddit | Focus | Signal Type |
|-----------|-------|------------|
| r/solopreneur | Solo business owners | Tool/service requests |
| r/Entrepreneur | Business builders | Growth/automation problems |
| r/freelance | Freelancers | Service demand |
| r/HelpMeFind | Tool seekers | "Does this exist?" requests |
| r/SideProject | Side hustlers | DIY automation demand |

### Customizing Subreddits

Edit `TARGET_SUBREDDITS` in `reddit_demand_scraper.py`:

```python
TARGET_SUBREDDITS = [
    "solopreneur",
    "Entrepreneur",
    "freelance",
    "HelpMeFind",
    "SideProject",
]
```

## How the Scoring Works

### Phase 1: Demand Intent Detection

Looks for regex patterns that indicate someone is seeking a solution:

- `"anyone know a tool for..."` → tool_request
- `"looking for a service that..."` → service_request
- `"is there an AI tool?"` → ai_interest
- `"this is so tedious/repetitive"` → pain_point
- `"how do I automate this?"` → problem_solving

**Requires:** 2+ patterns to count as demand signal

### Phase 2: Claude Solvability

Sends each post to Claude with the question: "Can Claude solve this problem?"

Claude returns:
- `solvable` (true/false)
- `skill` (the type of skill needed: "content writing", "automation", "research", etc.)
- `explanation` (1-sentence reasoning)

### Phase 3: Demand Level Scoring

```
engagement_score = upvotes + (comments × 2)
recency_multiplier = 1.5 if posted in last 24h else 1.0
adjusted_score = engagement_score × recency_multiplier

HIGH:    adjusted_score > 100
MEDIUM:  adjusted_score > 30
LOW:     adjusted_score < 30
```

### Phase 4: Composite Score

```
IF (solvable AND demand_level = HIGH):
    score = 100
ELIF (solvable AND demand_level = MEDIUM):
    score = 75
ELIF (solvable AND is_demand_signal):
    score = 50
ELSE:
    score = 0
```

Only opportunities with score > 0 are included in output.

## Monetization Model Evaluation

For each top opportunity, Claude evaluates 3 business models:

### SaaS (Recurring Subscription)
- **Best for:** Problems affecting many users with repeating needs
- **Typical pricing:** $29-$299/month
- **Build effort:** 4-12 weeks (MVP)
- **Examples:** AI writing assistant, automation tool, analytics dashboard

### Services (Done-For-You)
- **Best for:** High-value, one-time problems with customization needs
- **Typical pricing:** $500-$10,000/project
- **Build effort:** Low (sell time/expertise)
- **Examples:** Content strategy consultation, AI implementation, custom automation

### Digital Products (One-Time Purchase)
- **Best for:** Evergreen knowledge/templates with large target market
- **Typical pricing:** $27-$97 one-time
- **Build effort:** 2-4 weeks
- **Examples:** Email templates, video scripts, prompt libraries, mini-courses

## Running on Schedule

To discover opportunities automatically on a recurring basis:

```bash
# Run daily at 9am
0 9 * * * cd /path/to/repo && python demand_discovery_orchestrator.py

# Run weekly on Monday
0 9 * * 1 cd /path/to/repo && python demand_discovery_orchestrator.py
```

## Interpreting Results

### High-Confidence Opportunities

Look for:
- **Score:** 80+ (high demand + high solvability)
- **Confidence:** 80%+ (appears in pattern analysis)
- **Demand Level:** HIGH
- **Engagement:** 100+ upvotes or 20+ comments

### Red Flags

- Score < 50 (probably not ready)
- Confidence < 40% (weak signal, might be noise)
- Only appears in 1 subreddit (not validated across communities)
- Negative sentiment (people asking "avoid this" not "help me get this")

### Validation Checklist

Before building, manually validate the top 3 with:

- [ ] Search Twitter/Product Hunt for existing solutions
- [ ] Check if it's already saturated
- [ ] Survey 20+ people in the target community
- [ ] Calculate addressable market size
- [ ] Identify 3 competitors
- [ ] Estimate unit economics for your chosen model

## Troubleshooting

### "Reddit API Error: 401 Unauthorized"
→ Check your Reddit credentials in .env

### "Anthropic API Error"
→ Verify your ANTHROPIC_API_KEY is set and has credits

### "No opportunities found"
→ Try increasing the `limit` parameter:
```bash
python reddit_demand_scraper.py  # Default: 50 posts/subreddit
# Or modify in code:
winners = run_discovery_cycle(limit=200)
```

### "Pattern detection finds nothing"
→ Need multiple discovery cycles first. Run the scraper multiple times across different days to build history.

## Next Steps After Discovery

1. **Pick your winner** — Choose the highest-scoring, most confident opportunity
2. **Validate demand** — Survey 20-50 people in the target community
3. **Build MVP** — Create minimal version (2-4 weeks)
4. **Get early customers** — Reach out to people from the Reddit posts
5. **Iterate** — Use real feedback to refine positioning and features

## Files Reference

| File | Purpose |
|------|---------|
| `reddit_demand_scraper.py` | Core scraper + demand validation logic |
| `pattern_detector.py` | Clustering, frequency, trend analysis |
| `monetization_evaluator.py` | Business model evaluation |
| `demand_discovery_orchestrator.py` | Master pipeline runner |
| `.env.demand-discovery` | Template for credentials |
| `demand_discoveries.json` | Output: scored opportunities |
| `pattern_analysis.json` | Output: recurring themes |
| `monetization_evals.json` | Output: MtM recommendations |
| `discovery_history.json` | Historical cycles (auto-created) |

## Architecture Notes

The system uses a phased approach because:

1. **Phase separation** allows running individual components independently
2. **Haiku for scraping/scoring** (fast, cheap, sufficient for classification)
3. **Opus for monetization** (deeper reasoning for business model evaluation)
4. **JSON-based persistence** lets you replay analysis without re-scraping

Each component can be swapped, extended, or run in isolation.

---

Built for finding product-market fit signals in real-time community data.
