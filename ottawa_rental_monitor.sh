#!/bin/bash
# Ottawa rental monitor — headless sweep for Sahawat (auto-ramps weekly -> 3x/week).
# Part A: web-search for in-budget Centretown/Sandy Hill studios near operational LRT.
# Part B: watch the Building Investments portal for any OCTOBER 2026 studio/1-bed (any price)
#         and fire a desktop + ottawa-rental-ALERTS.md alert when one appears.
# Scheduled via ~/Library/LaunchAgents/com.crosswalk.ottawa-rental-monitor.plist

export PATH="/Users/toto/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export HOME="/Users/toto"

WORKDIR="/Users/toto/Claude TubeonAI"
OUT="$WORKDIR/ottawa-rental-candidates.md"
STAMP="$(date '+%Y-%m-%d %H:%M %Z')"

# Cadence auto-bump (no memory needed): weekly (Mondays) until late July, then
# 2-3x/week (Mon/Wed/Fri) through the Oct-1 peak, then back to weekly.
TODAY="$(date +%Y%m%d)"
DOW="$(date +%u)"   # 1=Mon ... 7=Sun
RAMP_START=20260721
RAMP_END=20260930
if ! { [ "$TODAY" -ge "$RAMP_START" ] && [ "$TODAY" -le "$RAMP_END" ]; }; then
    # Outside the peak window: run weekly (Mondays only); skip other fire days.
    if [ "$DOW" != "1" ]; then
        echo "$STAMP — weekly mode; skipping non-Monday run (no token spend)." >> "$OUT"
        exit 0
    fi
fi

read -r -d '' PROMPT <<'EOF'
You are a rental-listing monitor for someone relocating to Ottawa for an October 1, 2026 move-in.

PART A — General web search (budget-aware):
Find CURRENTLY LISTED studio, bachelor, or 1-bedroom apartments in Ottawa in: Centretown,
Centretown West / Chinatown, and Sandy Hill. Criteria: rent <= CAD $1,500/month; near an
OPERATIONAL O-Train Line 1 station (Lyon, Parliament, uOttawa, Lees, Bayview); available
around October 1, 2026 or flexible. For each genuine candidate output a markdown row:
Address/Building | Area | Rent | Type | Availability | Nearest LRT | Likely landlord type | Source URL
Prefer Kijiji/Facebook (independent landlords). Only list real results with a real source
URL — do NOT invent anything. If none, write "No matching candidates found this sweep."

PART B — Watch the Building Investments portal (IGNORE budget):
Fetch this page: https://buildinginvestments.managebuilding.com/Resident/public/rentals
List ALL studio and 1-bedroom units there as a table: Address | Rent | Availability date —
regardless of price. Clearly highlight any unit whose availability date is in OCTOBER 2026.

Be concise — tables only, then the queries used. After everything, output EXACTLY ONE final
line and nothing after it:
OCT1_BUILDINGINVESTMENTS: YES   — only if Part B found a studio/1-bed available in October 2026
                                  (units available September 2026 or earlier do NOT count)
OCT1_BUILDINGINVESTMENTS: NO    — otherwise
EOF

# Run the sweep, capturing output so we can detect an October alert.
cd "$WORKDIR" || exit 1
RESULT="$(claude -p "$PROMPT" \
    --model claude-haiku-4-5-20251001 \
    --allowedTools "WebSearch" "WebFetch" 2>&1)"

{
  echo ""
  echo "## Sweep $STAMP"
  echo "$RESULT"
  echo ""
  echo "---"
} >> "$OUT"

# Alert when Building Investments lists a studio/1-bed available in October 2026.
if printf '%s' "$RESULT" | grep -qi "OCT1_BUILDINGINVESTMENTS: YES"; then
    {
      echo ""
      echo "## 🔔 $STAMP — Building Investments has an OCTOBER 2026 studio/1-bed"
      echo "Review: https://buildinginvestments.managebuilding.com/Resident/public/rentals"
      echo "Details: latest sweep in ottawa-rental-candidates.md. Draft email: ottawa-rental-application-packet.md."
    } >> "$WORKDIR/ottawa-rental-ALERTS.md"
    osascript -e 'display notification "Building Investments has an Oct 2026 studio/1-bed — see ottawa-rental-ALERTS.md" with title "🏠 Ottawa rental alert"' 2>/dev/null || true
fi
