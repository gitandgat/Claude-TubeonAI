# Viral Hooks Research & Repurpose App

A React app for researching viral short-form hook patterns and repurposing them in Crosswalk Wisdom brand voice.

## Quick Start

### Option 1: Use the HTML File (Easiest)
1. Open `viral-hooks.html` in your browser
2. Paste your Anthropic API key (stored securely in localStorage)
3. Choose a mode and start creating hooks

**To open the file:**
```bash
# macOS
open viral-hooks.html

# Or drag into your browser
```

### Option 2: Use with a React Project
1. Copy `viral-hooks.jsx` into your React project
2. Import and use:
```jsx
import ViralHooksApp from './viral-hooks.jsx';

export default ViralHooksApp;
```

## Modes

### Topic Mode
Enter a topic (e.g., "identity transition", "fear of failure") and the app:
1. **Stage 1:** Researches 5 viral hook patterns from top creators (Dan Koe, Ali Abdaal, Jay Shetty, etc.)
2. **Stage 2:** Rewrites each hook in Crosswalk Wisdom voice

Example output:
```
Pattern: Contrast Hook
Example: "Everyone talks about passion. Nobody talks about discipline."
Why it works: Creates cognitive dissonance that demands resolution.

Repurposed:
"Everyone tells you to follow your passion. Nobody tells you what to do when that passion was your prison."
```

### Paste Mode
Paste a hook or transcript and the app:
1. **Stage 1:** Analyzes the pattern, psychological trigger, and core message
2. **Stage 2:** Generates 5 new hooks using the same pattern in Crosswalk Wisdom voice

## Features

- **Copy buttons** on each hook and video script
- **Platform selector:** All / YouTube Shorts / TikTok / Instagram Reels
- **Optional 60-second video script:** Structure (Hook → Story → Insight → CTA) with time markers
- **Loading stages:** Clear feedback on what's happening
- **Error handling:** Graceful failure with actionable messages
- **Smooth scroll:** Auto-scroll to results

## Styling

Brand palette:
- Background: `#f5f0e8` (cream)
- Accent: `#b8860b` (amber)
- Text: `#1a1a1a` (dark)

Fonts:
- Playfair Display (headings)
- DM Sans (body)

## API Requirements

- **Model:** `claude-sonnet-4-20250514`
- **Max tokens:** 1000 (base calls), 500 (video scripts)
- **Cost:** ~$0.01 per hook research + optional $0.005 for video script

## Brand Voice

The app injects this voice into every API call:

> You are a creative content strategist for Crosswalk Wisdom — a wellness and storytelling brand built by Sahawat, a former physician from Thailand who left clinical medicine, worked as a crossing guard in Toronto, and now helps burned-out high achievers navigate identity and career transitions.
>
> Voice: Warm, grounded, a little playful. Elizabeth Gilbert's register — story-first, accessible, no jargon. Short sentences. Punchy and honest.
>
> Key story assets:
> - COVID night shifts as a physician
> - First week after leaving medicine
> - The crosswalk moment in a yellow vest holding a stop sign
> - The fear of disappointing his younger self
>
> Target audience: Burned-out high achievers (doctors, lawyers, engineers) who feel trapped in the identity they built to survive.

## Workflow Example

1. Enter topic: "The day I realized I had to leave medicine"
2. Select platform: "All"
3. Check "Generate video script"
4. Click "Research Hooks"
5. Get 5 patterns + 5 repurposed hooks + 60-second script
6. Copy any hook to your clipboard
7. Use in LinkedIn, TikTok, etc.

## Security Notes

- API key stored in browser localStorage only
- Never sent anywhere except Anthropic's API
- Clear it anytime via "Change API Key" button
- All processing happens in real-time (no backend server)

## Troubleshooting

**"API Error: 401"** → Check your API key is correct and valid

**"Failed to parse response"** → Claude returned non-JSON; try simpler input or try again

**Long load times** → API calls are taking time; be patient (usually <5s per stage)

**Hooks feel generic** → Paste mode usually works better for specific hooks; Topic mode works best with specific, detailed topics

## Future Enhancements

- Save favorite hooks to local storage
- Export as markdown/PDF
- Multi-language support
- Batch mode (multiple topics at once)
- Integration with Zernio scheduler
- Performance metrics (which hooks perform best)

---

**Built for Crosswalk Wisdom.** Questions? Check the CLAUDE.md for project context.
