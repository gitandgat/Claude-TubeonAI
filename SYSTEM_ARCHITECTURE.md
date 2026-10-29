# Demand Discovery System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEMAND DISCOVERY PIPELINE                     │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  PHASE 1: SCRAPE │
│  Reddit Posts    │
│  (5 subreddits,  │
│   100 posts each)│
└────────┬─────────┘
         │
    ✅ 500 posts
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│         PHASE 2: VALIDATE DEMAND + SOLVABILITY           │
├──────────────────────────────────────────────────────────┤
│ For each post:                                           │
│ • Detect demand intent (regex + patterns)                │
│ • Use Claude to evaluate if Claude can solve it          │
│ • Score engagement (upvotes + comments × recency)        │
│ • Composite score 0-100                                  │
└────────┬─────────────────────────────────────────────────┘
         │
    ✅ 0-100 score
    ✅ Solvability: Yes/No
    ✅ Skill type identified
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│  PHASE 3: PATTERN DETECTION (Historical Analysis)        │
├──────────────────────────────────────────────────────────┤
│ • Cluster by semantic similarity                         │
│ • Calculate frequency across cycles                      │
│ • Identify emerging trends                               │
│ • Estimate confidence (80%+ = strong signal)             │
└────────┬─────────────────────────────────────────────────┘
         │
    ✅ Recurring patterns found
    ✅ Confidence scores
    ✅ Trend velocities
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│  PHASE 4: MONETIZATION EVALUATION                        │
├──────────────────────────────────────────────────────────┤
│ For each top opportunity:                                │
│ • Score SaaS viability (0-10)                            │
│ • Score Services viability (0-10)                        │
│ • Score Products viability (0-10)                        │
│ • Recommend best model                                   │
│ • List next steps                                        │
└────────┬─────────────────────────────────────────────────┘
         │
    ✅ Business model recommended
    ✅ Price range estimated
    ✅ Build effort calculated
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│              OUTPUTS (JSON + Summary)                     │
├──────────────────────────────────────────────────────────┤
│ • demand_discoveries.json                                │
│ • pattern_analysis.json                                  │
│ • monetization_evals.json                                │
│ • discovery_summary.txt                                  │
│ • discovery_history.json (cumulative)                    │
└──────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│        OPTIONAL: AGENT INTEGRATION PIPELINE              │
├──────────────────────────────────────────────────────────┤
│ Feed top 1-3 opportunities to downstream agents:         │
│ • Market Research Agent → TAM/SAM/SOM, competitors      │
│ • PRD Generator → Feature list, acceptance criteria      │
│ • Launch Planner → 4-week execution plan                 │
│ • Positioning Agent → Messaging, value prop              │
│ • Validation Planner → Customer interview script         │
└──────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### reddit_demand_scraper.py
**Responsibility:** Scrape, detect, validate, and score

```python
class RedditPost:
    id: str
    subreddit: str
    title: str
    selftext: str
    upvotes: int
    num_comments: int
    is_demand_signal: bool      # Regex + pattern matching
    claude_solvable: bool        # Claude evaluation
    demand_level: str            # low/medium/high
    skill_required: str          # What skill type
    score: int                   # 0-100 composite
```

**Key Functions:**
- `scrape_subreddit_posts()` — Fetch from Reddit API
- `detect_demand_intent()` — Pattern matching for demand signals
- `evaluate_claude_solvability()` — Claude call for solvability
- `score_demand_level()` — Engagement-based scoring
- `validate_post()` — Full pipeline for one post
- `run_discovery_cycle()` — Main entry point (run all subreddits)

**Output:** `demand_discoveries.json` (sorted by score descending)

---

### pattern_detector.py
**Responsibility:** Find recurring patterns and emerging trends

```python
def detect_topic_clustering(opportunities) → clusters
def calculate_pattern_frequency(cluster, history) → pattern_strength
def identify_emerging_trends(current_cycle) → trends
```

**Key Insight:** If a problem appears in multiple cycles across different subreddits with consistent engagement, it's a high-confidence opportunity.

**Confidence Formula:**
```
confidence = min(total_occurrences / 5, 1.0)
→ 5+ appearances = 100% confidence
→ 3-4 appearances = 80% confidence
→ 1-2 appearances = 20-60% confidence
```

**Output:** `pattern_analysis.json` (patterns + trends)

---

### monetization_evaluator.py
**Responsibility:** Determine which business model fits best

**For each opportunity:**
1. **SaaS (Recurring)** — Score based on: market size, scalability, recurring revenue potential
2. **Services (Done-for-you)** — Score based on: pricing power, margin, customization needs
3. **Products (Digital)** — Score based on: evergreen appeal, leverage, one-time cost

**Output:** `monetization_evals.json` with:
- Recommended model
- Reasoning
- Next steps (concrete actions)

---

### demand_discovery_orchestrator.py
**Responsibility:** Orchestrate all phases, generate executive summary

```
Phase 1 → scrape & score
    ↓
Phase 2 → pattern detection
    ↓
Phase 3 → monetization eval
    ↓
Phase 4 → executive summary & file outputs
```

---

### agent_integration_example.py
**Responsibility:** Show how to feed results to downstream agents

```python
# Example workflow
top_opp = load_discoveries()[0]

# Deepen analysis
market_research = create_market_research_agent(top_opp)
prd = create_prd_generator_agent(top_opp, market_research)
launch_plan = create_launch_plan_agent(top_opp, prd)
positioning = create_positioning_agent(top_opp)
validation = create_validation_plan_agent(top_opp)
```

---

## Data Flow

```
Reddit API
   ↓
ScraperAgent → 500 posts
   ↓
   ├→ detect_demand_intent() ─→ 100-200 posts with intent
   │  (filter out noise)
   │
   ├→ evaluate_claude_solvability() ─→ 50-100 solvable
   │  (filter to Claude-doable problems)
   │
   ├→ score_demand_level() ─→ Ranked 0-100
   │  (calculate engagement score)
   │
   └→ validate_post() ─→ Final score assigned
      (composite)
                     ↓
            demand_discoveries.json
                     ↓
            pattern_detector.py
         (cluster by topic)
                     ↓
       Recurring patterns + trends
                     ↓
         pattern_analysis.json
                     ↓
         monetization_evaluator.py
      (evaluate 3 business models)
                     ↓
         monetization_evals.json
                     ↓
      discovery_summary.txt
```

## Scoring Logic Deep Dive

### Step 1: Demand Intent Detection

Regex patterns matched (need 2+):

| Pattern | Regex | Example |
|---------|-------|---------|
| **tool_request** | "anyone know a tool\|does.*exist\|looking for" | "Does anyone know a tool for X?" |
| **service_request** | "need help\|looking for service\|done-for-you" | "Need someone to do X" |
| **ai_interest** | "AI\|chatgpt\|claude\|automation" | "Can AI do this?" |
| **pain_point** | "struggling\|tedious\|repetitive\|time-consuming" | "This is so tedious" |
| **problem_solving** | "how do i\|any tips\|best practice" | "Any tips on X?" |

**Result:** `is_demand_signal = (2+ patterns matched)`

### Step 2: Claude Solvability Check

Claude evaluates:
- Can Claude solve this problem?
- What skill type? (writing, automation, analysis, research, strategy, code, etc.)
- Why or why not?

**Result:** `(solvable: bool, skill_type: str, explanation: str)`

### Step 3: Engagement Scoring

```python
engagement_score = upvotes + (comments × 2)
recency_multiplier = 1.5 if posted_in_last_24h else 1.0
adjusted_score = engagement_score × recency_multiplier

if adjusted_score > 100:     demand_level = "HIGH"
elif adjusted_score > 30:    demand_level = "MEDIUM"
else:                         demand_level = "LOW"
```

### Step 4: Composite Score

```python
if solvable AND demand_level == HIGH:
    score = 100
elif solvable AND demand_level == MEDIUM:
    score = 75
elif solvable AND is_demand_signal:
    score = 50
else:
    score = 0
```

**Output:** Only posts with score > 0 included in results.

---

## Model Selection Strategy

| Task | Model | Why |
|------|-------|-----|
| Demand intent detection | Haiku 4.5 | Classification, fast |
| Solvability eval | Haiku 4.5 | Classification, cheap |
| Pattern clustering | Haiku 4.5 | Semantic grouping, fast |
| Monetization eval | Opus 4.8 | Complex reasoning needed |

**Cost Estimate (per run):**
- Scraping & validation: ~1000 Haiku calls ≈ $0.30
- Monetization eval: ~5 Opus calls ≈ $0.30
- **Total per cycle: ~$0.60**

---

## Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Total runtime | < 5 min | Mostly API latency |
| API calls | ~1000 | Haiku: 990, Opus: 5 |
| Cost per run | < $1 | Very cheap validation |
| Opportunities found | 15-50 | Depends on subreddit activity |
| High-confidence (80%+) | 3-10 | After pattern analysis |

---

## Failure Modes & Mitigation

| Failure | Cause | Mitigation |
|---------|-------|-----------|
| No demand signals found | Wrong subreddits | Customize TARGET_SUBREDDITS |
| False positives (low quality posts) | Loose scoring | Increase composite score threshold |
| Pattern detection finds nothing | First run | Need 2-3 cycles of history first |
| Reddit API rate limited | Too many calls | Add delay between subreddits |
| Claude refuses some evals | Sensitive topic | Add safeguards in prompt |

---

## Extending the System

### Add New Subreddit
```python
TARGET_SUBREDDITS.append("new_subreddit")
```

### Change Scoring Weights
```python
# Make engagement more important
adjusted_score = engagement_score × (recency_multiplier + 0.5)
```

### Add Custom Intent Patterns
```python
patterns["custom_pattern"] = r"your regex here"
```

### Integrate with External Tools
```python
# Export to Product Hunt, Slack, Discord, etc.
results = load_discoveries()
for opp in results:
    notify_slack(opp)
    update_coda(opp)
    create_trello_card(opp)
```

---

## Testing & Validation

### Unit Test: Demand Detection
```python
test_post = RedditPost(..., title="Anyone know a tool for X?")
assert detect_demand_intent(test_post)[0] == True
```

### Integration Test: Full Pipeline
```python
winners = run_discovery_cycle()
assert len(winners) > 0
assert all(w.score > 0 for w in winners)
assert all(w.claude_solvable for w in winners)
```

### Validation: Manual Review
```
Pick top 3 opportunities:
□ Read actual Reddit posts
□ Confirm demand is real
□ Confirm Claude can solve it
□ Validate monetization model
```

---

## Roadmap for Enhancement

**Phase 1 (Current):**
- ✅ Reddit scraping
- ✅ Demand validation
- ✅ Pattern detection
- ✅ Monetization eval

**Phase 2 (Potential):**
- [ ] Multi-platform scraping (Twitter, Product Hunt, Discord)
- [ ] Real-time alerts when high-confidence opportunity emerges
- [ ] Competitor analysis automation
- [ ] Customer interview guide generation
- [ ] MVP validation checklist

**Phase 3 (Future):**
- [ ] Automated market sizing
- [ ] Sentiment analysis on how people feel about solutions
- [ ] Pricing elasticity estimation
- [ ] Go-to-market strategy generation
- [ ] Pitch deck template creation

---

This architecture is designed to:
1. **Be repeatable** — Run weekly to track trends
2. **Be low-cost** — ~$0.60 per discovery cycle
3. **Be extensible** — Easily add new data sources or agents
4. **Be actionable** — Outputs go straight to product/business teams
