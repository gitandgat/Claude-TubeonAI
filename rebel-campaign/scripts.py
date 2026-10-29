"""
Rebel Campaign — "The First Generation to Choose"
5 reel scripts split into hook / middle / close segments.

hook  → SadTalker avatar (face on screen, builds trust)
middle → VoiSpark voice only + b-roll overlays (no avatar needed)
close → SadTalker avatar (face returns for CTA)

Speaking rate: ~2.3 words/sec (deliberate, paused delivery).
Estimated durations are used for broll_plan.json timings;
actual durations come from ffprobe after WAV generation.

Reel 3 hook is payoff-first per competitor research (contrarian hook = highest score).
"""

REELS: list[dict] = [
    {
        "slug": "reel1-whose-dream",
        "title": "Who Was It For?",
        "hook_text": (
            "Every aunty who told you to become a doctor at a family dinner? "
            "She wasn't thinking about you. "
            "She was thinking about never paying for a consultation again. "
            "Status. Access. A doctor in the family."
        ),
        "middle_text": (
            "Your whole career was built on someone else's needs. "
            "That's not a moral failing. "
            "That's how survival cultures work. "
            "The system ran perfectly. You got in. You got through. You got licensed."
        ),
        "close_text": (
            "The question is: now that you're safe — "
            "what do you want? "
            "Not what was realistic. What did you actually want."
        ),
        # video-edit word_pop overlay specs (speech_anchor = exact spoken phrase)
        "overlays": [
            {
                "kind": "hook_title",
                "align": "flank",
                "left_text": "WHOSE\nDREAM",
                "right_text": "WAS\nIT?",
                "speech_anchor": "Every aunty who told you to become a doctor",
                "vertical": 0.66,
                "behind_subject": True,
                "reason": "Opens with the core tension to hook viewers in the first 2 seconds",
            },
            {
                "kind": "word_pop",
                "speech_anchor": "Status Access A doctor in the family",
                "vertical": 0.72,
                "items": [
                    {"text": "STATUS", "offset_sec": 0.0},
                    {"text": "ACCESS", "offset_sec": 1.3},
                    {"text": "SECURITY", "offset_sec": 2.6},
                ],
                "reason": "Kinetic text burns the three motivators into memory — not explained, felt",
            },
            {
                "kind": "image_card",
                "speech_anchor": "Your whole career was built on someone else",
                "image_query": "south asian family dinner conversation",
                "caption": "Not your dream. Theirs.",
                "reason": "Visual anchor grounds the abstract claim in a recognizable family scene",
            },
            {
                "kind": "word_pop",
                "speech_anchor": "now that you're safe what do you want",
                "vertical": 0.72,
                "items": [{"text": "{what do you want?}", "offset_sec": 1.0}],
                "reason": "Italicized question lands the entire reel's CTA in a single frame",
            },
        ],
    },
    {
        "slug": "reel2-the-timeline",
        "title": "The Timeline",
        "hook_text": (
            "Walk the timeline with me. "
            "High school: take the sciences. "
            "Undergrad: MCAT, GPA, everything for the application. "
            "Med school: just get through it."
        ),
        "middle_text": (
            "Residency: this is temporary. "
            "Licensing: now you're free. "
            "You're thirty-five. You're licensed. You're not free. "
            "Because every single decision in that timeline "
            "was made inside a framework handed to you "
            "before you were old enough to question it."
        ),
        "close_text": (
            "The framework wasn't designed for your happiness. "
            "It was designed for your parents' survival. "
            "Those are different objectives. "
            "And you were never told there was a difference."
        ),
        "overlays": [
            {
                "kind": "hook_title",
                "align": "flank",
                "left_text": "THE\nTIMELINE",
                "right_text": "THEY\nCHOSE",
                "speech_anchor": "Walk the timeline with me",
                "vertical": 0.66,
                "behind_subject": True,
                "reason": "Frames the entire reel: this is someone else's plan, not yours",
            },
            {
                "kind": "vertical_timeline",
                "speech_anchor": "High school take the sciences",
                "steps": [
                    {"heading": "High school", "description": "Take the sciences", "offset_sec": 0.0},
                    {"heading": "Undergrad", "description": "MCAT. GPA. The application.", "offset_sec": 2.5},
                    {"heading": "Med school", "description": "Just get through it", "offset_sec": 5.0},
                    {"heading": "Residency", "description": "This is temporary", "offset_sec": 7.5},
                    {"heading": "Licensing", "description": "Now you're free", "offset_sec": 10.0},
                ],
                "reason": "Shows the full 15-year pipeline as a visual trap — each step feels inevitable",
            },
            {
                "kind": "vs_split",
                "speech_anchor": "designed for your happiness designed for your parents survival",
                "top_label": "YOUR FRAMEWORK",
                "top_items": ["Happiness", "Flourishing", "Your choices"],
                "bottom_label": "THEIR FRAMEWORK",
                "bottom_items": ["Stability", "Status", "Survival"],
                "reason": "Contrasting frameworks makes the mismatch undeniable — two different operating systems",
            },
            {
                "kind": "word_pop",
                "speech_anchor": "Those are different objectives",
                "vertical": 0.72,
                "items": [{"text": "STABILITY ≠ {FLOURISHING}", "offset_sec": 0.5}],
                "reason": "Math symbol makes the abstract distinction concrete and shareable",
            },
        ],
    },
    {
        "slug": "reel3-the-code",
        "title": "The Code",
        # Payoff-first per research: boldest statement in first 2 seconds
        "hook_text": (
            "You're running 1985 survival logic on a 2025 life. "
            "And you're wondering why nothing fits. "
            "Your parents weren't wrong. "
            "They installed survival code."
        ),
        "middle_text": (
            "Medicine equals safety. "
            "Safety equals never being powerless again. "
            "Never being turned away. Never being other. "
            "The code worked. You became a doctor."
        ),
        "close_text": (
            "The code has one problem. "
            "It was written for their threat environment. "
            "Not yours."
        ),
        "overlays": [
            {
                "kind": "hook_title",
                "align": "flank",
                "left_text": "SURVIVAL",
                "right_text": "CODE",
                "speech_anchor": "You're running 1985 survival logic",
                "vertical": 0.66,
                "behind_subject": True,
                "reason": "Payoff-first hook — boldest claim in the first 2 seconds per competitor research",
            },
            {
                "kind": "stat_punch",
                "speech_anchor": "1985 survival logic",
                "value": "1985",
                "caption": "The year the code was written",
                "reason": "Specific year makes the outdated logic feel concrete, not abstract",
            },
            {
                "kind": "word_pop",
                "speech_anchor": "Medicine equals safety safety equals never being powerless",
                "vertical": 0.72,
                "items": [
                    {"text": "SAFETY", "offset_sec": 0.0},
                    {"text": "STATUS", "offset_sec": 1.3},
                    {"text": "BELONGING", "offset_sec": 2.6},
                ],
                "reason": "Three-word sequence mirrors the immigrant survival triad — recognizable to the ICP",
            },
            {
                "kind": "word_pop",
                "speech_anchor": "It was written for their threat environment not yours",
                "vertical": 0.72,
                "items": [{"text": "{wrong era.}", "offset_sec": 0.8}],
                "reason": "The punchline that reframes the entire reel — written for italics emphasis",
            },
        ],
    },
    {
        "slug": "reel4-the-sacrifice",
        "title": "The Sacrifice",
        "hook_text": (
            "Here's the thing no one says out loud. "
            "Your parents sacrificed so you wouldn't have to make the same sacrifice. "
            "That was the whole point."
        ),
        "middle_text": (
            "They came with nothing. They built something. "
            "So that you would have choices they never had. "
            "And somewhere along the way, that story got flipped. "
            "The sacrifice became the reason you can't leave. "
            "You can't quit — do you know what we gave up for this?"
        ),
        "close_text": (
            "But that's backwards. "
            "The sacrifice was supposed to give you options. Not obligations. "
            "They survived so you could choose. "
            "That's not disrespecting what they built. "
            "That's the mission completing."
        ),
        "overlays": [
            {
                "kind": "hook_title",
                "align": "flank",
                "left_text": "THE\nSACRIFICE",
                "right_text": "THEY\nMADE",
                "speech_anchor": "Here's the thing no one says out loud",
                "vertical": 0.66,
                "behind_subject": True,
                "reason": "Confronts the unspoken rule immediately — creates emotional tension to hold attention",
            },
            {
                "kind": "vs_split",
                "speech_anchor": "the sacrifice became the reason you can't leave",
                "top_label": "WHAT IT WAS",
                "top_items": ["Freedom", "Options", "Permission to choose"],
                "bottom_label": "WHAT IT BECAME",
                "bottom_items": ["Obligation", "Guilt", "Can't leave"],
                "reason": "Shows the inversion — the gift became a trap — without blaming anyone",
            },
            {
                "kind": "word_pop",
                "speech_anchor": "options not obligations",
                "vertical": 0.72,
                "items": [{"text": "OPTIONS | {not obligations}", "offset_sec": 0.5}],
                "reason": "The reframe in five words — pipe separator creates visual contrast between concepts",
            },
            {
                "kind": "word_pop",
                "speech_anchor": "the mission completing",
                "vertical": 0.72,
                "items": [{"text": "{the mission completing.}", "offset_sec": 0.3}],
                "reason": "Italics on the close redefine leaving as completing the sacrificial mission, not betraying it",
            },
        ],
    },
    {
        "slug": "reel5-different-question",
        "title": "Different Question",
        "hook_text": (
            "Most doctors ask: can I leave medicine? "
            "Wrong question. "
            "The right question is: what am I actually built for?"
        ),
        "middle_text": (
            "Your training gave you precision. "
            "Capacity for complexity. "
            "The ability to hold high stakes without falling apart. "
            "The system said those skills are only for clinical work."
        ),
        "close_text": (
            "The system was wrong. "
            "What you can do with what you have — "
            "that's a much more interesting question "
            "than whether you're allowed to stop."
        ),
        "overlays": [
            {
                "kind": "hook_title",
                "align": "flank",
                "left_text": "WRONG",
                "right_text": "QUESTION",
                "speech_anchor": "Most doctors ask can I leave medicine",
                "vertical": 0.66,
                "behind_subject": True,
                "reason": "Calls out the wrong frame in two words — makes the viewer feel implicated immediately",
            },
            {
                "kind": "vs_split",
                "speech_anchor": "wrong question right question",
                "top_label": "WRONG QUESTION",
                "top_items": ["Can I leave?", "Am I allowed?", "What will they think?"],
                "bottom_label": "RIGHT QUESTION",
                "bottom_items": ["What am I built for?", "Where do my skills go?", "What do I choose?"],
                "reason": "The reframe in one visual — wrong questions are passive, right questions are agentic",
            },
            {
                "kind": "word_pop",
                "speech_anchor": "precision capacity for complexity high stakes",
                "vertical": 0.72,
                "items": [
                    {"text": "PRECISION", "offset_sec": 0.0},
                    {"text": "COMPLEXITY", "offset_sec": 1.4},
                    {"text": "{high stakes}", "offset_sec": 2.8},
                ],
                "reason": "Names the doctor's transferable identity — reframes training as an asset, not a cage",
            },
            {
                "kind": "word_pop",
                "speech_anchor": "more interesting question than whether you're allowed to stop",
                "vertical": 0.72,
                "items": [{"text": "{better question.}", "offset_sec": 0.5}],
                "reason": "CTA close — italics signal the invitation is for the viewer to ask it themselves",
            },
        ],
    },
]
