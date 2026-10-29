#!/usr/bin/env bash
# Rebel Campaign Monitor
# Runs every 30 min via LaunchAgent com.crosswalk.rebel-campaign-monitor
# Checks for completed SadTalker renders and runs video-edit post-processing.
# Self-disables when all 5 reels are fully edited.

set -euo pipefail

REPO="/Users/toto/Claude TubeonAI"
REBEL="$REPO/rebel-campaign"
LOG="$REBEL/monitor.log"
PYTHON="/opt/anaconda3/envs/avatar/bin/python"
PLIST="$HOME/Library/LaunchAgents/com.crosswalk.rebel-campaign-monitor.plist"

# Ensure ffmpeg + brew tools are findable; fix Mac OpenMP conflict for whisper env
export PATH="/opt/homebrew/bin:$PATH"
export KMP_DUPLICATE_LIB_OK=TRUE

echo "──────────────────────────────────────────" >> "$LOG"
echo "$(date '+%Y-%m-%d %H:%M:%S') monitor run"  >> "$LOG"

# Show current status
"$PYTHON" "$REBEL/post_process.py" --status >> "$LOG" 2>&1

# Run post-processing for any source.mp4 that is ready
"$PYTHON" "$REBEL/post_process.py" >> "$LOG" 2>&1

# Count how many are fully done
DONE=$("$PYTHON" "$REBEL/post_process.py" --status 2>/dev/null | grep -c "edited ✓" || true)
echo "  Done: $DONE/5" >> "$LOG"

# Self-disable when all 5 are edited
if [ "$DONE" -eq 5 ]; then
    echo "  All 5 reels edited — disabling monitor LaunchAgent" >> "$LOG"
    launchctl unload "$PLIST" 2>/dev/null || true
    osascript -e 'display notification "All 5 rebel campaign reels are edited ✓" with title "Crosswalk Campaign"' 2>/dev/null || true
fi
