"""
Crosswalk Wisdom Lead Magnet PDF Generator
"5 AI Prompts" guide by Sahawat Nilwatcharamanee
"""

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether, Frame, BaseDocTemplate,
    PageTemplate, NextPageTemplate,
)
from reportlab.platypus.flowables import Flowable
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas as pdfcanvas
import os

# ---------------------------------------------------------------------------
# Brand palette
# ---------------------------------------------------------------------------
WARM_WHITE   = HexColor("#FAF7F2")
CHARCOAL     = HexColor("#2C2C2C")
AMBER        = HexColor("#D4A843")
ORANGE       = HexColor("#E8834A")
TEAL         = HexColor("#5B9A8B")
BLACK        = HexColor("#1A1A1A")
PROMPT_BG    = HexColor("#F2EBE0")   # warm amber-tinted box background
RULE_COLOR   = HexColor("#D4A843")   # amber divider
LIGHT_AMBER  = HexColor("#FBF5E8")   # very light amber for copy box border
MEDIUM_GREY  = HexColor("#8A8A8A")   # footer / meta text

# ---------------------------------------------------------------------------
# Page geometry
# ---------------------------------------------------------------------------
PAGE_W, PAGE_H = letter                 # 612 x 792 pt
MARGIN_L = 0.85 * inch
MARGIN_R = 0.85 * inch
MARGIN_T = 0.75 * inch
MARGIN_B = 0.75 * inch
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R

OUTPUT_PATH = "/Users/toto/Claude TubeonAI/drafts/ai-prompts-lead-magnet/5-prompts-guide.pdf"

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
def build_styles():
    styles = {}

    # --- Cover ---
    styles["cover_title"] = ParagraphStyle(
        "cover_title",
        fontName="Times-Bold",
        fontSize=28,
        leading=36,
        textColor=CHARCOAL,
        alignment=TA_CENTER,
        spaceAfter=18,
    )
    styles["cover_subtitle"] = ParagraphStyle(
        "cover_subtitle",
        fontName="Times-Italic",
        fontSize=14,
        leading=20,
        textColor=CHARCOAL,
        alignment=TA_CENTER,
        spaceAfter=24,
    )
    styles["cover_author"] = ParagraphStyle(
        "cover_author",
        fontName="Helvetica",
        fontSize=12,
        leading=17,
        textColor=AMBER,
        alignment=TA_CENTER,
        spaceAfter=8,
    )
    styles["cover_footer"] = ParagraphStyle(
        "cover_footer",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=MEDIUM_GREY,
        alignment=TA_CENTER,
    )

    # --- Section heading (Prompt number + name) ---
    styles["prompt_heading"] = ParagraphStyle(
        "prompt_heading",
        fontName="Times-Bold",
        fontSize=20,
        leading=26,
        textColor=CHARCOAL,
        spaceAfter=4,
        spaceBefore=10,
    )
    styles["prompt_number"] = ParagraphStyle(
        "prompt_number",
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=14,
        textColor=AMBER,
        spaceAfter=2,
        spaceBefore=8,
    )
    styles["when_to_use"] = ParagraphStyle(
        "when_to_use",
        fontName="Times-Italic",
        fontSize=11,
        leading=16,
        textColor=MEDIUM_GREY,
        spaceAfter=10,
    )

    # --- Body text ---
    styles["body"] = ParagraphStyle(
        "body",
        fontName="Helvetica",
        fontSize=11,
        leading=17,
        textColor=CHARCOAL,
        spaceAfter=10,
        alignment=TA_JUSTIFY,
    )
    styles["body_bold"] = ParagraphStyle(
        "body_bold",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=17,
        textColor=CHARCOAL,
        spaceAfter=10,
    )
    styles["body_italic"] = ParagraphStyle(
        "body_italic",
        fontName="Times-Italic",
        fontSize=11,
        leading=17,
        textColor=CHARCOAL,
        spaceAfter=10,
        alignment=TA_JUSTIFY,
    )
    styles["body_small_italic"] = ParagraphStyle(
        "body_small_italic",
        fontName="Times-Italic",
        fontSize=10,
        leading=15,
        textColor=MEDIUM_GREY,
        spaceAfter=8,
    )

    # --- Copy box label ---
    styles["copy_label"] = ParagraphStyle(
        "copy_label",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=AMBER,
        spaceAfter=4,
        spaceBefore=14,
        letterSpacing=0.8,
    )
    styles["what_label"] = ParagraphStyle(
        "what_label",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=13,
        textColor=TEAL,
        spaceAfter=4,
        spaceBefore=14,
        letterSpacing=0.8,
    )

    # --- Copy box text (inside shaded area) ---
    styles["copy_box"] = ParagraphStyle(
        "copy_box",
        fontName="Courier",
        fontSize=9.5,
        leading=14,
        textColor=CHARCOAL,
        spaceAfter=0,
        leftIndent=0,
        rightIndent=0,
    )

    # --- What to look for bullet ---
    styles["wtlf_body"] = ParagraphStyle(
        "wtlf_body",
        fontName="Helvetica",
        fontSize=10.5,
        leading=16,
        textColor=CHARCOAL,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
    )

    # --- Page 2 letter ---
    styles["letter_body"] = ParagraphStyle(
        "letter_body",
        fontName="Helvetica",
        fontSize=11,
        leading=18,
        textColor=CHARCOAL,
        spaceAfter=10,
        alignment=TA_JUSTIFY,
    )
    styles["letter_bold"] = ParagraphStyle(
        "letter_bold",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=18,
        textColor=CHARCOAL,
        spaceAfter=10,
    )
    styles["letter_italic"] = ParagraphStyle(
        "letter_italic",
        fontName="Times-Italic",
        fontSize=11,
        leading=18,
        textColor=CHARCOAL,
        spaceAfter=10,
        alignment=TA_JUSTIFY,
    )
    styles["letter_sig"] = ParagraphStyle(
        "letter_sig",
        fontName="Times-Italic",
        fontSize=12,
        leading=18,
        textColor=CHARCOAL,
        spaceAfter=6,
    )
    styles["ps_text"] = ParagraphStyle(
        "ps_text",
        fontName="Times-Italic",
        fontSize=10,
        leading=15,
        textColor=MEDIUM_GREY,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
    )

    # --- How to use numbered list ---
    styles["how_number"] = ParagraphStyle(
        "how_number",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=17,
        textColor=AMBER,
        spaceAfter=2,
    )
    styles["how_body"] = ParagraphStyle(
        "how_body",
        fontName="Helvetica",
        fontSize=11,
        leading=17,
        textColor=CHARCOAL,
        leftIndent=20,
        spaceAfter=8,
    )

    # --- Section page title (large, serif) ---
    styles["section_title"] = ParagraphStyle(
        "section_title",
        fontName="Times-Bold",
        fontSize=22,
        leading=28,
        textColor=CHARCOAL,
        spaceAfter=6,
        spaceBefore=4,
    )
    styles["section_subtitle"] = ParagraphStyle(
        "section_subtitle",
        fontName="Times-Italic",
        fontSize=13,
        leading=19,
        textColor=MEDIUM_GREY,
        spaceAfter=16,
    )

    # --- Final page ---
    styles["final_heading"] = ParagraphStyle(
        "final_heading",
        fontName="Times-Bold",
        fontSize=18,
        leading=24,
        textColor=CHARCOAL,
        spaceAfter=10,
        spaceBefore=8,
    )
    styles["final_body"] = ParagraphStyle(
        "final_body",
        fontName="Helvetica",
        fontSize=11,
        leading=17,
        textColor=CHARCOAL,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
    )
    styles["cta_label"] = ParagraphStyle(
        "cta_label",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=16,
        textColor=CHARCOAL,
        spaceAfter=4,
        spaceBefore=14,
    )
    styles["cta_link"] = ParagraphStyle(
        "cta_link",
        fontName="Helvetica",
        fontSize=11,
        leading=16,
        textColor=TEAL,
        spaceAfter=10,
    )
    styles["cta_italic"] = ParagraphStyle(
        "cta_italic",
        fontName="Times-Italic",
        fontSize=11,
        leading=17,
        textColor=CHARCOAL,
        spaceAfter=4,
    )

    return styles


# ---------------------------------------------------------------------------
# Helper: shaded copy box using a Table (most reliable in reportlab)
# ---------------------------------------------------------------------------
def make_copy_box(text_lines, styles):
    """
    Render copy-paste prompt text in a warm amber-tinted rounded box.
    text_lines: list of strings (each will be a paragraph)
    Returns a Table flowable.
    """
    paragraphs = []
    for line in text_lines:
        if line.strip() == "":
            paragraphs.append(Spacer(1, 5))
        else:
            paragraphs.append(Paragraph(line, styles["copy_box"]))

    inner = Table([[p] for p in paragraphs],
                  colWidths=[CONTENT_W - 0.5 * inch],
                  hAlign="LEFT")
    inner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PROMPT_BG),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    outer = Table([[inner]],
                  colWidths=[CONTENT_W],
                  hAlign="LEFT")
    outer.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PROMPT_BG),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LINEABOVE",  (0, 0), (-1, 0), 2, AMBER),
        ("LINEBEFORE", (0, 0), (0, -1), 2, AMBER),
        ("LINEBELOW",  (0, -1), (-1, -1), 1, HexColor("#D4A843")),
        ("LINEAFTER",  (-1, 0), (-1, -1), 1, HexColor("#D4A843")),
    ]))
    return outer


def make_hr(color=RULE_COLOR, thickness=0.8):
    return HRFlowable(width="100%", thickness=thickness, color=color,
                      spaceAfter=8, spaceBefore=8)


# ---------------------------------------------------------------------------
# Page templates with running footer (skip cover)
# ---------------------------------------------------------------------------
class FooterCanvas(pdfcanvas.Canvas):
    """Canvas that draws a footer on every page except page 1 (cover)."""

    def __init__(self, filename, **kwargs):
        pdfcanvas.Canvas.__init__(self, filename, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            if self._pageNumber > 1:   # skip cover (page 1)
                self._draw_footer()
            pdfcanvas.Canvas.showPage(self)
        pdfcanvas.Canvas.save(self)

    def _draw_footer(self):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(MEDIUM_GREY)

        # Left: page number
        self.drawString(MARGIN_L, 0.45 * inch,
                        str(self._pageNumber))

        # Right: brand name + URL
        brand = "Crosswalk Wisdom  ·  crosswalkwisdom.com"
        self.drawRightString(PAGE_W - MARGIN_R, 0.45 * inch, brand)

        # Thin amber line above footer
        self.setStrokeColor(AMBER)
        self.setLineWidth(0.5)
        self.line(MARGIN_L, 0.60 * inch, PAGE_W - MARGIN_R, 0.60 * inch)

        self.restoreState()


# ---------------------------------------------------------------------------
# Build story
# ---------------------------------------------------------------------------
def build_story(styles):
    story = []

    # =========================================================
    # PAGE 1: COVER
    # =========================================================
    # Top decorative amber stripe (simulated with a table)
    stripe = Table([[""]],
                   colWidths=[CONTENT_W],
                   rowHeights=[6])
    stripe.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), AMBER),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(stripe)
    story.append(Spacer(1, 1.6 * inch))

    # Label above title
    story.append(Paragraph("CROSSWALK WISDOM", ParagraphStyle(
        "label",
        fontName="Helvetica",
        fontSize=10,
        leading=14,
        textColor=AMBER,
        alignment=TA_CENTER,
        spaceAfter=12,
        letterSpacing=2,
    )))

    # Main title — break at natural phrase boundaries
    story.append(Paragraph(
        "What I Asked Claude<br/>When I Was Planning<br/>My Exit From Medicine",
        styles["cover_title"],
    ))

    story.append(Spacer(1, 0.15 * inch))

    # Amber decorative line
    rule_table = Table([[""]], colWidths=[2 * inch], rowHeights=[2])
    rule_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), AMBER),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]))
    # Center it in a wrapper
    centered_rule = Table([[rule_table]], colWidths=[CONTENT_W])
    centered_rule.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(centered_rule)
    story.append(Spacer(1, 0.18 * inch))

    story.append(Paragraph(
        "5 Prompts That Gave Me More Clarity in 30 Minutes<br/>"
        "Than 6 Months of Spinning My Wheels",
        styles["cover_subtitle"],
    ))

    story.append(Spacer(1, 0.5 * inch))

    story.append(Paragraph(
        "Sahawat Nilwatcharamanee &nbsp;·&nbsp; Crosswalk Wisdom",
        styles["cover_author"],
    ))

    # Spacer to push footer to bottom
    story.append(Spacer(1, 2.2 * inch))

    # Bottom amber stripe
    story.append(stripe)
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("crosswalkwisdom.com", styles["cover_footer"]))

    story.append(PageBreak())

    # =========================================================
    # PAGE 2: BEFORE YOU START
    # =========================================================
    story.append(Paragraph("Before You Start", styles["section_title"]))
    story.append(make_hr())
    story.append(Spacer(1, 0.1 * inch))

    letter_paras = [
        ("body", "When I left medicine, Claude didn't exist. Neither did ChatGPT."),
        ("body", "I figured out my next chapter the hard way — two years of spiraling, therapy, parking lot conversations with myself, and a crossing guard vest I didn't expect to teach me anything."),
        ("body", "It worked. Eventually. But it was slow and lonely and full of loops I couldn't break on my own."),
        ("body", "Now I work with burned-out healthcare workers who are standing where I stood. And the thing I keep noticing is this: the questions that took me two years to sit with — they can work through in 30 minutes with the right AI prompts."),
        ("body", "Not because AI is smarter than lived experience. But because it asks you the questions you've been avoiding, without flinching, without judgment, at 2am if that's when you need it."),
        ("body", "These are the 5 prompts I use with every healthcare worker I coach through a career transition."),
        ("letter_italic", "<i>I'm a little jealous they get to use them. I wish they'd existed when I was crossing over.</i>"),
        ("body", "Copy them. Paste them into Claude (free at claude.ai) or ChatGPT. Fill in your details where you see brackets. Let the answer surprise you."),
        ("body", "You've been smart enough to do this job. You're smart enough to find what's next."),
    ]
    for sname, txt in letter_paras:
        story.append(Paragraph(txt, styles[sname]))

    story.append(Spacer(1, 6))
    story.append(Paragraph("— Sahawat", styles["letter_sig"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "<i>P.S. If you haven't taken the Fear Audit yet, do that first. Knowing which fear is loudest for you (financial insecurity, fear of judgment, or identity loss) will help you know which of these five prompts to start with. → fear-audit.vercel.app</i>",
        styles["ps_text"],
    ))

    story.append(PageBreak())

    # =========================================================
    # PAGE 3: HOW TO USE THIS GUIDE
    # =========================================================
    story.append(Paragraph("How to Use This Guide", styles["section_title"]))
    story.append(make_hr())
    story.append(Spacer(1, 0.1 * inch))

    steps = [
        ("1.", "Go to <b>claude.ai</b> (free account works fine)"),
        ("2.", "Start a new conversation"),
        ("3.", "Copy the prompt exactly — including the bracketed instructions"),
        ("4.", "Fill in your own details inside the brackets"),
        ("5.", "Read the response slowly. Highlight what surprises you."),
        ("6.", "Keep the conversation going — Claude remembers context. Ask follow-up questions."),
    ]
    for num, text in steps:
        row_data = [
            [
                Paragraph(num, ParagraphStyle("step_num", fontName="Helvetica-Bold", fontSize=13, leading=18, textColor=AMBER)),
                Paragraph(text, ParagraphStyle("step_txt", fontName="Helvetica", fontSize=11, leading=17, textColor=CHARCOAL)),
            ]
        ]
        row_table = Table(row_data, colWidths=[0.35 * inch, CONTENT_W - 0.35 * inch])
        row_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ]))
        story.append(row_table)
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        "<i>There's no right order. But if you're not sure where to start, begin with Prompt 1.</i>",
        styles["body_italic"],
    ))

    story.append(PageBreak())

    # =========================================================
    # PAGES 4-8: THE 5 PROMPTS
    # =========================================================
    prompts = [
        {
            "number": "PROMPT 1",
            "name": "The Identity Excavator",
            "when": "Use this when: You feel like your career and your identity have become the same thing — and you don't know who you are without it.",
            "copy_lines": [
                "I've spent [X] years as a [your role] in healthcare. I'm seriously considering",
                "a major career transition, but I keep hitting a wall — so much of my sense",
                "of self is tied to being a [nurse/doctor/NP/etc.] that imagining something",
                "different feels disorienting, like I'd be losing a piece of who I am.",
                "",
                "I need your help with this: What core values, strengths, and ways of showing",
                "up in the world do I have that exist independently of my job title? To help",
                "you understand me better, please ask me 5 specific questions first — one at",
                "a time, waiting for my answer before asking the next. After my answers, give",
                "me your honest reflection of who you think I actually am beneath the career.",
            ],
            "wtlf": (
                "Claude will ask you questions about moments of flow, childhood interests, "
                "what energizes you outside work, what you'd do if money weren't the constraint. "
                "Your answers will reveal things you've stopped believing about yourself. The "
                "reflection at the end often reads like someone describing you more accurately "
                "than you've described yourself in years."
            ),
        },
        {
            "number": "PROMPT 2",
            "name": "The Skills Translator",
            "when": "Use this when: You believe you have \"no marketable skills outside healthcare\" — a lie almost every clinician tells themselves.",
            "copy_lines": [
                "I'm a [your role] with [X] years of experience. Here's a description of what",
                "I actually do day-to-day: [paste 3-5 bullet points from your job description",
                "or just describe your typical week in plain language].",
                "",
                "I need you to do two things:",
                "1. Rewrite these skills in non-clinical language — translate them into",
                "   capabilities that would make sense to a hiring manager or client in",
                "   any industry.",
                "2. Based on those translated skills, suggest 7 specific career paths outside",
                "   of healthcare that would genuinely value what I bring — including paths",
                "   I probably haven't considered. For each one, tell me which specific skills",
                "   of mine would transfer directly.",
            ],
            "wtlf": (
                "The translation step is the revelation. Phrases like \"managed life-or-death "
                "decisions under time pressure with incomplete information\" land very differently "
                "than \"made clinical assessments.\" You'll see yourself as an outsider would "
                "for the first time."
            ),
        },
        {
            "number": "PROMPT 3",
            "name": "The Financial Fear Solver",
            "when": "Use this when: \"I can't afford to leave\" is the sentence that ends every conversation you have with yourself about change.",
            "copy_lines": [
                "I currently earn $[your annual income] as a [your role]. My essential monthly",
                "expenses are approximately $[amount], which includes $[student loan payment]",
                "in student loans and [number] dependents.",
                "",
                "I'm considering transitioning away from clinical work — either to [a specific",
                "direction if you have one] or to something I haven't fully defined yet.",
                "",
                "Please help me build a realistic 18-month financial bridge plan. I want you",
                "to include:",
                "- Options for maintaining income during a transition (locum work, consulting,",
                "  per diem, part-time) that are realistic for someone with my background",
                "- What \"minimum viable income\" would look like for me — the number I'd need",
                "  to feel financially safe enough to take a real step",
                "- One specific unconventional income idea that someone with clinical experience",
                "  could realistically start in under 90 days",
            ],
            "wtlf": (
                "Most burned-out clinicians have never done this math in writing. Seeing a real "
                "number — your actual minimum viable income — shrinks the fear considerably. "
                "It becomes a problem to solve rather than a fog to drown in."
            ),
        },
        {
            "number": "PROMPT 4",
            "name": "The Values Compass",
            "when": "Use this when: You know what you're running FROM. You have no idea what you're running TOWARD.",
            "copy_lines": [
                "I've been in healthcare for [X] years. I've reached the point where I know I",
                "need something different — but I keep trying to answer \"what do I want?\" and",
                "drawing a blank. I know what I don't want. I can't seem to access what I",
                "actually do want.",
                "",
                "I need you to act as a thoughtful, direct career coach. Your job is to help",
                "me discover what I truly value in work — not what I think I should value, not",
                "what looks good on paper, but what actually matters to me.",
                "",
                "Ask me 7 questions, one at a time. Wait for my full answer before asking the",
                "next question. Don't rush. After all 7 answers, give me:",
                "1. A summary of what you heard — what seems to matter most to me based on",
                "   what I said",
                "2. Three specific directions (not job titles — directions) that align with",
                "   those values",
                "3. One question I should be sitting with right now that I probably haven't",
                "   asked myself yet",
            ],
            "wtlf": (
                "The 7-question conversation is slower and more generative than any career quiz "
                "you've ever taken. The final question Claude offers — the one you haven't asked "
                "yourself — is usually the one that matters most. Write it down. Sit with it "
                "for a week."
            ),
        },
        {
            "number": "PROMPT 5",
            "name": "The Decision Defogged",
            "when": "Use this when: You've been sitting on the same decision for months (or years) and you can't seem to move in either direction.",
            "copy_lines": [
                "I've been considering leaving [current role/situation] to [describe what you're",
                "considering — a new career, starting something, cutting back hours, anything].",
                "I've been sitting on this decision for approximately [time period].",
                "",
                "I need you to give me two things, completely separately:",
                "",
                "First — argue AGAINST making this move. Give me every legitimate risk, real",
                "concern, and honest reason why this might not work or why staying makes sense.",
                "Don't soften it. I need the real case.",
                "",
                "Second — argue FOR making this move. Not cheerleading. Evidence-based reasons",
                "why this could actually work, given everything you know about someone with my",
                "background and situation. Be specific.",
                "",
                "After both arguments, I want you to do one more thing: Tell me what a wise,",
                "honest mentor who genuinely cared about me — not my comfort, but my growth —",
                "would actually tell me to do with this decision.",
            ],
            "wtlf": (
                "The mentor response at the end is usually the first time you'll read something "
                "that sounds like someone saying what everyone in your life has been too scared "
                "to say. It won't make the decision for you. But it will stop the loop."
            ),
        },
    ]

    for i, p in enumerate(prompts):
        # Force a page break between prompts (except first)
        if i > 0:
            story.append(PageBreak())

        story.append(Paragraph(p["number"], styles["prompt_number"]))
        story.append(Paragraph(p["name"], styles["prompt_heading"]))
        story.append(Paragraph(p["when"], styles["when_to_use"]))

        story.append(make_hr(color=AMBER, thickness=0.6))

        story.append(Paragraph("COPY THIS:", styles["copy_label"]))
        story.append(make_copy_box(p["copy_lines"], styles))

        story.append(make_hr(color=MEDIUM_GREY, thickness=0.4))

        story.append(Paragraph("WHAT TO LOOK FOR IN THE RESPONSE:", styles["what_label"]))
        story.append(Paragraph(p["wtlf"], styles["wtlf_body"]))

    # =========================================================
    # FINAL PAGE: WHAT'S NEXT
    # =========================================================
    story.append(PageBreak())

    story.append(Paragraph("What's Next", styles["final_heading"]))
    story.append(make_hr())
    story.append(Spacer(1, 0.05 * inch))

    story.append(Paragraph(
        "These five prompts are a starting point, not a destination.",
        styles["final_body"],
    ))
    story.append(Paragraph(
        "If a prompt opened something you want to explore further — keep the conversation "
        "going. Add context. Push back. Ask Claude to be harder on you, or more specific, "
        "or to take a completely different angle.",
        styles["final_body"],
    ))
    story.append(Paragraph(
        "The session doesn't have to end when the prompt does.",
        styles["final_body"],
    ))

    story.append(Spacer(1, 0.25 * inch))
    story.append(make_hr(color=AMBER, thickness=1))
    story.append(Spacer(1, 0.15 * inch))

    story.append(Paragraph("If you want to go deeper:", styles["cta_label"]))
    story.append(Paragraph(
        "The Fear Audit names the specific fear that's keeping you stuck — financial insecurity, "
        "fear of judgment, or identity loss. Each fear needs a different response.",
        styles["final_body"],
    ))
    story.append(Paragraph(
        "Take the Fear Audit free: <b>fear-audit.vercel.app</b>",
        styles["cta_link"],
    ))

    story.append(Spacer(1, 0.1 * inch))
    story.append(make_hr(color=MEDIUM_GREY, thickness=0.4))
    story.append(Spacer(1, 0.1 * inch))

    story.append(Paragraph("If you're ready for the next step:", styles["cta_label"]))
    story.append(Paragraph(
        "<i>The Courage to Choose</i> is the short guide I wish I'd had when I was standing "
        "at the crosswalk, not sure which way to walk. It includes the decision framework I "
        "used to move from paralysis to a plan — without blowing up my life.",
        styles["cta_italic"],
    ))
    story.append(Paragraph(
        "Get it for $27: <b>sahawat.gumroad.com/l/courage-to-choose</b>",
        styles["cta_link"],
    ))

    story.append(Spacer(1, 0.4 * inch))

    # Final brand stamp
    brand_block_data = [[
        Paragraph(
            "Crosswalk Wisdom<br/><font size='9' color='#8A8A8A'>crosswalkwisdom.com</font>",
            ParagraphStyle("brand_stamp", fontName="Times-Bold", fontSize=12,
                           leading=18, textColor=CHARCOAL, alignment=TA_CENTER),
        )
    ]]
    brand_block = Table(brand_block_data, colWidths=[CONTENT_W])
    brand_block.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HexColor("#F5F0E8")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 20),
        ("RIGHTPADDING", (0, 0), (-1, -1), 20),
        ("TOPPADDING", (0, 0), (-1, -1), 14),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
        ("LINEABOVE", (0, 0), (-1, 0), 2, AMBER),
        ("LINEBELOW", (0, -1), (-1, -1), 2, AMBER),
    ]))
    story.append(brand_block)

    return story


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def generate():
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    styles = build_styles()
    story = build_story(styles)

    doc = SimpleDocTemplate(
        OUTPUT_PATH,
        pagesize=letter,
        leftMargin=MARGIN_L,
        rightMargin=MARGIN_R,
        topMargin=MARGIN_T,
        bottomMargin=MARGIN_B,
        title="5 AI Prompts – Crosswalk Wisdom",
        author="Sahawat Nilwatcharamanee",
        subject="Career transition prompts for healthcare professionals",
    )

    doc.build(story, canvasmaker=FooterCanvas)
    print(f"PDF saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    generate()
