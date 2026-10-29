#!/bin/bash

set -e

echo "🚀 Demand Discovery Agent Suite - Setup"
echo "========================================"
echo ""

# Step 1: Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements-demand-discovery.txt
echo "✅ Dependencies installed"
echo ""

# Step 2: Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.demand-discovery .env
    echo "✅ .env created - please fill in your credentials:"
    echo "   - REDDIT_CLIENT_ID"
    echo "   - REDDIT_CLIENT_SECRET"
    echo "   - REDDIT_USER_AGENT"
    echo "   - ANTHROPIC_API_KEY"
    echo ""
    echo "Edit .env and then run:"
    echo "  python demand_discovery_orchestrator.py"
else
    echo "✅ .env file exists"
fi

# Step 3: Create output directory
mkdir -p output
echo "✅ Output directory ready"
echo ""

# Step 4: Test imports
echo "🧪 Testing imports..."
python3 << 'EOF'
try:
    import praw
    print("  ✓ praw")
    import anthropic
    print("  ✓ anthropic")
    import dotenv
    print("  ✓ python-dotenv")
except ImportError as e:
    print(f"  ✗ Missing: {e}")
    exit(1)
EOF

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your Reddit API credentials"
echo "2. Run: python demand_discovery_orchestrator.py"
echo ""
echo "Need help?"
echo "  • Reddit API setup: https://www.reddit.com/prefs/apps"
echo "  • Full guide: see DEMAND_DISCOVERY_README.md"
