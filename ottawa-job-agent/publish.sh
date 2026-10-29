#!/bin/bash
# Publish all generated microsites to Vercel as a single public static site.
# Each pitch is live at: https://microsites-gitandgats-projects.vercel.app/<job-slug>

cd "$(dirname "$0")" || exit 1

# Load VERCEL_TOKEN from the repo-root .env
TOKEN=$(/opt/anaconda3/bin/python3 -c "from dotenv import dotenv_values; print(dotenv_values('../.env').get('VERCEL_TOKEN',''))" 2>/dev/null | tr -d '[:space:]')

if [ -z "$TOKEN" ]; then
  echo "[publish] VERCEL_TOKEN not found in .env — falling back to interactive login"
  cd microsites && npx --yes vercel deploy --prod --yes --scope gitandgats-projects
  exit $?
fi

cd microsites || exit 1
npx --yes vercel deploy --prod --yes --token "$TOKEN" --scope gitandgats-projects
