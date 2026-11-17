#!/bin/bash
# Le Cahier — le moteur de la semaine, sans intervention (lundi 06:00, heure d'Ottawa).
#   1. le-cahier/engine/semaine.py fabrique vingt phrases neuves et leur voix
#      (Claude pour les phrases, VoiSpark « Calm French Woman » pour la voix) ;
#   2. si un lot attend, /le-cahier-publier (claude -p) le publie dans l'artefact
#      Le Cahier et recopie les fichiers dans le miroir le-cahier/.
# Un lot fabriqué mais pas publié reste prêt : la prochaine exécution le reprend
# sans rien redépenser (semaine.py ne refabrique jamais une semaine déjà faite).
# Reprise à la main après un échec : relancer ce script, tout simplement.
# Planifié par ~/Library/LaunchAgents/com.crosswalk.le-cahier-semaine.plist

export PATH="/Users/toto/.local/bin:/Library/Frameworks/Python.framework/Versions/3.14/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
export HOME="/Users/toto"

WORKDIR="/Users/toto/Claude TubeonAI"
LOG="$WORKDIR/logs/le_cahier_semaine.log"
ENGINE="le-cahier/engine/semaine.py"

notify() {
  osascript -e "display notification \"$1\" with title \"✒️ Le Cahier\"" 2>/dev/null || true
}

cd "$WORKDIR" || exit 1
mkdir -p "$WORKDIR/logs"
{
  echo ""
  echo "## Run $(date '+%Y-%m-%d %H:%M %Z')"
} >> "$LOG"

# The engine writes its own log lines to $LOG; only tracebacks need catching here.
python3 "$ENGINE" > /dev/null 2>> "$LOG"
BUILT=$?

if ! python3 "$ENGINE" --pending > /dev/null 2>&1; then
  if [ "$BUILT" -ne 0 ]; then
    notify "La fabrication des phrases a échoué — voir logs/le_cahier_semaine.log"
  fi
  exit "$BUILT"
fi

RESULT=""
for ATTEMPT in 1 2; do
  RESULT="$(claude -p "/le-cahier-publier" \
    --model claude-sonnet-5 \
    --allowedTools "Read" "Bash" "Glob" "Grep" "Artifact" 2>&1)"
  # Retry only transient server errors; a usage limit or a conflict won't clear in two minutes.
  if printf '%s' "$RESULT" | grep -qiE '5[0-9]{2} .*(error|processing your request)|server-side issue|temporarily unavailable'; then
    echo "Essai $ATTEMPT : erreur passagère du serveur, nouvel essai dans 2 min" >> "$LOG"
    [ "$ATTEMPT" -lt 2 ] && sleep 120
    continue
  fi
  break
done
printf '%s\n' "$RESULT" | tail -40 >> "$LOG"

if python3 "$ENGINE" --pending > /dev/null 2>&1; then
  echo "PAS PUBLIÉ — le lot reste prêt ; relancer run_le_cahier_semaine.sh ou /le-cahier-publier." >> "$LOG"
  notify "Phrases prêtes mais pas publiées — voir logs/le_cahier_semaine.log"
  exit 1
fi
notify "Les phrases de la semaine sont dans le cahier"
