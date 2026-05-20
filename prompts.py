"""
Platform-specific repurpose prompts.
Each prompt tells TubeonAI exactly what to generate.
All prompts include an email list CTA to drive subscribers.
"""

CTA = "End with a CTA inviting readers to join the free email list for more exclusive insights like this."

PLATFORMS = {
    "linkedin": {
        "label": "LinkedIn Post IMG",
        "format": "custom",
        "prompt": (
            "Write a LinkedIn post for Crosswalk Wisdom targeting unmatched International Medical Graduates (IMGs) in Canada.\n\n"
            "AUDIENCE: A 34-year-old IMG from India. Passed MCCQE Part 1. Failed CaRMS twice. Working as a lab assistant at $48K/year. "
            "Family back home thinks he is almost a doctor in Canada. Googles 'IMG unmatched career options' at midnight.\n\n"
            "STRUCTURE — follow this exactly:\n"
            "1. HOOK (2 lines max): Status-drop or vulnerability contrast. Cognitive dissonance. "
            "Example style: 'For 10 years, doctor was not what I did. It was who I was.'\n"
            "2. REFRAME: 'The question is not X. It is Y.' — shift from failure framing to discovery framing.\n"
            "3. SENSORY LIST: 3 lines starting with ✨ — specific and sensory. "
            "Use real details: Tim Hortons, lab coat, $18,000, midnight Google search, parking lot tears, WhatsApp family chat, CaRMS email.\n"
            "4. LESSONS LIST: 3 lines starting with 👣 — lessons as short infinitive phrases.\n"
            "5. BRAND REVEAL: 'I call it Crosswalk Wisdom — [one-line description].' Mid-post only, never at start.\n"
            "6. CTA: End with 'X minutes. 📬 Link in the comments.' Never put URLs in the post body.\n"
            "7. QUESTION: One universal engagement question any professional would answer.\n"
            "8. HASHTAGS: Exactly 4. Always #CrosswalkWisdom #IMGCanada plus 2 contextual.\n\n"
            "RULES:\n"
            "- Never mention the video or source. Write as original lived experience.\n"
            "- Never preach. Share what was found, not what the reader should do.\n"
            "- Sensory specifics only — no abstract burnout language.\n"
            "- Under 1500 characters total."
        ),
    },
    "instagram_carousel": {
        "label": "Instagram Carousel",
        "format": "custom",
        "prompt": (
            "Create a 7-slide Instagram carousel from this content. "
            "Slide 1: Bold hook/title that makes people swipe. "
            "Slides 2-6: One key insight per slide — short headline + 1-2 sentence explanation. "
            "Slide 7: Summary + " + CTA + " "
            "Format each slide as: [Slide N] Headline\\nBody text."
        ),
    },
    "reels": {
        "label": "Instagram Reels Script",
        "format": "custom",
        "prompt": (
            "Write a 30-60 second Instagram Reels video script from this content. "
            "Structure: Hook (0-3s) → 3 punchy key points → Call to action. "
            "Use casual, conversational language. Include [VISUAL CUE] directions. "
            + CTA
        ),
    },
    "facebook": {
        "label": "Facebook Post",
        "format": "custom",
        "prompt": (
            "Write an engaging Facebook post from this content. "
            "Start with a relatable question or bold statement. "
            "Tell a short story or share the key insight in plain language. "
            "Keep it warm and conversational (200-400 words). "
            + CTA
        ),
    },
    "tiktok": {
        "label": "TikTok Video Script",
        "format": "custom",
        "prompt": (
            "Write a 30-60 second TikTok video script from this content. "
            "Open with a pattern interrupt hook in the first 2 seconds. "
            "Deliver value fast — one main insight with a surprising angle. "
            "Close with a curiosity-driven CTA. Use casual Gen-Z friendly language. "
            "Include [ON SCREEN TEXT] and [VISUAL] directions. "
            + CTA
        ),
    },
    "youtube_shorts": {
        "label": "YouTube Shorts Script",
        "format": "custom",
        "prompt": (
            "Write a YouTube Shorts script (under 60 seconds) from this content. "
            "Hook: Start mid-action or with a bold claim — no intro. "
            "Body: 2-3 fast-paced key points with concrete examples. "
            "End screen CTA: Subscribe + join the email list. "
            "Include [VISUAL] directions and keep sentences short and punchy. "
            + CTA
        ),
    },
    "substack": {
        "label": "Substack Newsletter",
        "format": "custom",
        "prompt": (
            "Write a Substack newsletter issue for Crosswalk Wisdom, a healing and burnout recovery brand "
            "for healthcare professionals (nurses, doctors, caregivers). "
            "The brand voice is: warm, contemplative, honest, and grounded — like a trusted colleague "
            "who has walked the same road. Never preachy. Never corporate. "
            "Structure the issue as follows:\n"
            "- SUBJECT LINE: One compelling subject line (under 50 characters, curiosity-driven)\n"
            "- PREVIEW TEXT: One sentence teaser (under 90 characters)\n"
            "- OPENING: A short, personal observation or micro-story (2-3 sentences) that leads into the topic. "
            "Start with 'This week,' or a grounded observation — not a greeting.\n"
            "- THE LESSON: The main insight from the content, written as a 'crosswalk lesson' — "
            "a reflection the reader can apply this week. Use the crosswalk metaphor where it fits naturally. "
            "3-5 paragraphs, short sentences, no jargon.\n"
            "- ONE QUESTION: End the main body with one reflection question for the reader to sit with.\n"
            "- THIS WEEK'S PRACTICE: A single, concrete, small action the reader can take in the next 7 days. "
            "One sentence. Make it specific and achievable.\n"
            "- SIGN OFF: Sign as Sahawat, Crosswalk Wisdom. Keep it warm and brief.\n"
            "Total length: 350-550 words. "
            "Do NOT include any HTML. Plain text only. "
            "End with a P.S. line inviting readers to share the issue with one healthcare professional they know."
        ),
    },
}
