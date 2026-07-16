#!/bin/bash

# START_HERE.sh
# Run this to start the complete system

set -e

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        DEMAND DISCOVERY SYSTEM - COMPLETE STARTUP             ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

echo "📊 Step 1: Scanning all platforms for opportunities..."
echo "   (Twitter, Quora, YouTube, Indie Hackers, Product Hunt)"
echo ""
python multiplatform_discovery.py

echo ""
echo "─────────────────────────────────────────────────────────────────"
echo ""

echo "✉️  Step 2: Generating platform-specific outreach messages..."
echo ""
python message_templates.py

echo ""
echo "─────────────────────────────────────────────────────────────────"
echo ""

echo "📋 Step 3: Initializing conversation tracker..."
echo ""
python conversation_tracker.py dashboard

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    🎯 YOU'RE ALL SET!                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

echo "NEXT STEPS:"
echo ""
echo "1. 📖 Read the complete workflow:"
echo "   • cat COMPLETE_WORKFLOW.md"
echo ""
echo "2. 📋 Review your messages (copy-paste ready):"
echo "   • cat message_templates.json | jq '.messages[] | {title, message, cta}'"
echo ""
echo "3. 🚀 Send your first 5 messages TODAY:"
echo "   • Open the URLs from above"
echo "   • Copy messages from message_templates.json"
echo "   • Send on Twitter/Quora/YouTube"
echo ""
echo "4. 📊 Track responses as they come in:"
echo "   • python conversation_tracker.py dashboard"
echo ""
echo "5. ⏰ Setup daily automation (runs every morning at 9am):"
echo "   • crontab -e"
echo "   • Add: 0 9 * * * cd $(pwd) && python daily_scanner.py"
echo ""
echo "EXPECTED RESULTS (This Week):"
echo "   ✓ 5-10 messages sent"
echo "   ✓ 2-5 responses"
echo "   ✓ 1-2 conversations"
echo "   ✓ First customer revenue: \$500-2,000"
echo ""
echo "FILES CREATED:"
echo "   • multiplatform_opportunities.json (15+ opportunities)"
echo "   • message_templates.json (10 ready-to-send messages)"
echo "   • conversations.json (empty tracker, ready for data)"
echo ""
echo "QUICK COMMANDS:"
echo "   python daily_scanner.py        # Run daily scan"
echo "   python conversation_tracker.py dashboard  # View progress"
echo "   python conversation_tracker.py export     # Export to CSV"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "You have everything you need to start making money today."
echo "═══════════════════════════════════════════════════════════════════"
echo ""
