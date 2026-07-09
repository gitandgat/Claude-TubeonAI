export interface TranslationRow {
  clinicalSkill: string;
  techEquivalent: string;
}

export interface OfferItem {
  index: string;
  title: string;
  body: string;
}

export const hero = {
  eyebrow: "THE CROSSWALK WISDOM IMG PIVOT PROTOCOL",
  headline:
    "Translate your clinical genius into a high-leverage tech career in 90 days—without going back to school.",
  subhead:
    "The same differential-diagnosis reasoning you use on rounds — ranking causes under incomplete data, prioritizing under pressure, spotting the pattern before anyone else does — is what AI and systems consulting roles pay for. This protocol maps it, packages it, and puts it in front of employers, while keeping your Express Entry file exactly where it is.",
  stat: "10–22% of IMGs match into residency. 97% of Canadian grads do. This is for the other 78–90% of us.",
  ctaLabel: "Book Your Triage Call",
  ctaMicrocopy: "20 minutes. No pitch deck. Just your numbers and your next move.",
};

export const moat = {
  eyebrow: "LAYER 3 OF 4 — IDENTITY",
  headline: "Your Degree Is a Moat, Not a Prison",
  intro:
    "You didn't spend six years learning to be a doctor. You spent six years learning to think under uncertainty with incomplete information and real stakes. That skill doesn't expire when you step off the treadmill — it has a second career, and it pays better than the one you're stuck in now.",
  rows: [
    {
      clinicalSkill:
        "Differential diagnosis — ranking competing explanations under incomplete data",
      techEquivalent: "Root-cause analysis for systems and product failures",
    },
    {
      clinicalSkill: "Triage under time pressure with limited resources",
      techEquivalent: "Prioritization frameworks (ICE/RICE scoring, incident triage)",
    },
    {
      clinicalSkill: "Pattern recognition across thousands of cases",
      techEquivalent: "Training AI agents to flag anomalies and workflow bottlenecks",
    },
    {
      clinicalSkill: "Managing a deteriorating situation with incomplete information",
      techEquivalent: "Incident response and on-call systems design",
    },
    {
      clinicalSkill: "Longitudinal patient management across multiple variables",
      techEquivalent: "Multi-step AI agent orchestration (state, memory, hand-offs)",
    },
    {
      clinicalSkill:
        "Translating complex risk into plain language for a frightened patient",
      techEquivalent: "Technical-to-stakeholder consulting communication",
    },
    {
      clinicalSkill: "Following a protocol while adapting it to the individual case",
      techEquivalent:
        "Customizing no-code AI workflows (n8n, Bolt.new-style tools) to a client's actual process",
    },
  ] satisfies TranslationRow[],
  pullQuote:
    "The treadmill needs you to believe your MD only works one way. It doesn't. The letters after your name were never the point — the mind that earned them is.",
};

export const offerStack = {
  eyebrow: "INSIDE THE PROTOCOL",
  headline: "Not a course. A translation engine.",
  subhead:
    "Three deliverables. Twelve weeks. Everything mapped to your actual clinical history — nothing generic.",
  items: [
    {
      index: "01",
      title: "The 12-Week 1-on-1 Translation Mapping",
      body: "Twelve weekly 1-on-1 sessions where we take your real clinical history — every rotation, every crisis call, every diagnostic call you made under pressure — and map it, line by line, into the language hiring managers in health-tech and consulting actually search for. You leave with a translated resume, a translated LinkedIn narrative, and a bank of interview stories built from cases you already lived.",
    },
    {
      index: "02",
      title: "The Plug-and-Play AI Templates",
      body: "A private library of ready-to-use AI templates and no-code automation frameworks — built in n8n and Bolt.new-style tools — so you can demonstrate real technical proficiency in week 3, not year 3. You don't need to learn Python. You need one working AI agent workflow you can show in an interview. We hand you the starting templates and walk you through customizing them for the exact role you're targeting.",
    },
    {
      index: "03",
      title: "The Boundary Blueprint",
      body: "A dedicated module for the cost nobody prices into a career pivot: what it does to your mental health while you're mid-transition. Scripts and structures for saying no to unpaid ‘just shadow me’ asks, protecting the hours you need for your search, and holding the line with family who still call this ‘giving up.’ Boundaries aren't a soft add-on here — they're the foundation the other two deliverables stand on.",
    },
  ] satisfies OfferItem[],
  ctaLabel: "Book Your Triage Call to See If You Qualify",
};

export const guarantee = {
  eyebrow: "THE BACKSTOP",
  headline: "The 12-Week Backstop.",
  badge: "BOUNDED — 12 WEEKS MAX, NOT OPEN-ENDED",
  body: "Complete the core 90-day / 12-week Translation Mapping protocol. Implement the AI templates as instructed. If you haven't generated at least 3 qualified interviews or consulting leads by the end of those 12 weeks, you get up to 12 additional weeks of continued 1-on-1 coaching at no extra cost — until you hit 3 qualified interviews or leads, or the 12 extra weeks run out, whichever comes first.",
  closingLine:
    "This is a bounded guarantee, not an open-ended one: 12 extra weeks maximum, then the engagement closes either way. We're not promising infinite coaching. We're promising we don't disappear the moment your invoice clears.",
};

export const triageCall = {
  eyebrow: "STEP OFF THE TREADMILL",
  headline: "Not a sales call. A triage call.",
  subhead:
    "20 minutes. We look at your numbers — years on the pathway, dollars spent, current income — and tell you straight whether this protocol is a fit. If it isn't, we'll tell you that too.",
  immigrationLine:
    "Booking this call does not affect any exam registration, licensing application, or Express Entry file. It's a conversation, not a commitment.",
  formLabels: {
    firstName: "First name",
    email: "Email address",
    submit: "Get My Triage Call Link",
  },
  successHeading: (firstName: string) => `${firstName}, pick a time below.`,
  trustLine:
    "No spam. Your info is used to schedule this call and send your confirmation — nothing else.",
};

export const footer = {
  tagline: "From the Treadmill to the World.",
  contactEmail: "sahawat@crosswalkwisdom.com",
  siteLabel: "crosswalkwisdom.com",
};
