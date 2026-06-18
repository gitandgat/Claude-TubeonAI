#!/usr/bin/env bash
#
# One-command lead-magnet pipeline: generate PDF -> social PNG -> (optional) deliver.
#
# Usage:
#   ./run.sh                                  # rebuild PDF + social from default JSON
#   ./run.sh other.json                       # use a different schema JSON
#   ./run.sh --topic "..." --summary "..."    # generate fresh content first, then build
#   ./run.sh --email lead@x.com --name "Dr. Asha" [--dry-run]   # also deliver
#
# Flags can be combined. Delivery only runs when --email is provided.
set -euo pipefail
cd "$(dirname "$0")"

JSON="crosswalk-img-pivot-map.json"
TOPIC=""; SUMMARY=""; EMAIL=""; NAME=""; DRYRUN=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --topic)    TOPIC="$2"; shift 2 ;;
    --summary)  SUMMARY="$2"; shift 2 ;;
    --email)    EMAIL="$2"; shift 2 ;;
    --name)     NAME="$2"; shift 2 ;;
    --dry-run)  DRYRUN="--dry-run"; shift ;;
    -h|--help)  grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *.json)     JSON="$1"; shift ;;
    *)          echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

# 1) Content + PDF -------------------------------------------------------------
if [[ -n "$TOPIC" ]]; then
  echo "==> Generating content for: $TOPIC"
  python3 generate_lead_magnet.py --topic "$TOPIC" --summary "$SUMMARY" --out generated
  JSON="generated.json"
else
  echo "==> Rendering PDF from $JSON"
  python3 generate_lead_magnet.py "$JSON"
fi

STEM="$(basename "${JSON%.json}")"
PDF="${STEM}.pdf"

# 2) Social visual -------------------------------------------------------------
echo "==> Rendering 1080x1080 social visual"
python3 generate_social_visual.py --json "$JSON"

# 3) Delivery (optional) -------------------------------------------------------
if [[ -n "$EMAIL" ]]; then
  if [[ -z "$DRYRUN" ]]; then
    echo "==> Preflight: Encharge + SMTP reachability"
    python3 deliver_lead_magnet.py --check   # set -e aborts the run if this fails
  fi
  echo "==> Delivering to $EMAIL ${DRYRUN:+(dry run)}"
  python3 deliver_lead_magnet.py --email "$EMAIL" --name "$NAME" --pdf "$PDF" $DRYRUN
else
  echo "==> Skipping delivery (no --email). Run deliver_lead_magnet.py --check to test integrations."
fi

echo "==> Done. Artifacts: $PDF, ${STEM}-social.png"
