#!/bin/bash
# Ottawa Job Agent — daily runner
cd "$(dirname "$0")"
/opt/anaconda3/bin/python3 job_agent.py >> job_agent.log 2>&1
