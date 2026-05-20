# Bolt.new Prompt: Burnout Crosswalk Assessment Quiz

Copy and paste the entire prompt below into bolt.new:

---

Build a beautiful, mobile-first single-page web app called "The Burnout Crosswalk Assessment" for the brand Crosswalk Wisdom (https://www.crosswalkwisdom.com).

## Brand Identity
- **Brand:** Crosswalk Wisdom
- **Tagline:** "Real-world reflections on healing"
- **Mission:** "The sidewalk is the classroom. You are the student. Healing is the lesson."
- **Founder:** Sahawat
- **Target audience:** Healthcare professionals (nurses, doctors, caregivers, pharmacists) experiencing burnout
- **Color palette:** Warm cinematic tones — deep amber/gold (#D4A843), charcoal (#2C2C2C), warm white (#FAF7F2), soft orange accent (#E8834A), muted teal for calm (#5B9A8B)
- **Typography:** Clean, modern serif for headings (use Google Font "Playfair Display"), sans-serif for body (use "Inter")
- **Visual mood:** Urban, contemplative, warm light, cinematic — like walking through a city at golden hour

## App Structure

### Landing / Start Screen
- Large heading: "The Burnout Crosswalk Assessment"
- Subheading: "Discover where you are on your healing journey"
- Body text: "This 2-minute assessment maps your burnout to the 4 stages of the Crosswalk Method — Start, Stop, Elder, and Human. Your results are personalized and private."
- A "For nurses, doctors, caregivers & healthcare professionals" label/badge
- CTA button: "Begin Your Assessment" (amber/gold, rounded, with subtle hover animation)
- Small footer: "By Crosswalk Wisdom — crosswalkwisdom.com"

### Quiz Flow (12 Questions)
- Show one question at a time with smooth fade/slide transition
- Progress bar at top showing completion (styled as a crosswalk/road visual if possible — otherwise a clean minimal bar)
- Each question has 4 answer options (radio buttons styled as clickable cards)
- Auto-advance to next question 0.5s after selection (with brief highlight animation on selected card)
- Back button to revisit previous questions
- Question counter: "Question 3 of 12"

#### The 12 Questions

Each answer maps to one of 4 stages: START (1pt), STOP (2pt), ELDER (3pt), HUMAN (4pt). The user's average score determines their stage.

**Question 1: "How often do you feel emotionally drained after a shift?"**
- Rarely — I still feel energized most days (START - 1pt)
- Sometimes — certain days hit harder than others (STOP - 2pt)
- Often — I carry the weight home with me (ELDER - 3pt)
- Almost always — I feel numb before I even clock in (HUMAN - 4pt)

**Question 2: "When someone asks 'how are you?', what's your honest answer?"**
- "I'm good, genuinely" (START - 1pt)
- "I'm fine" — but I know I'm not fully honest (STOP - 2pt)
- "I'm tired" — and I mean it at a soul level (ELDER - 3pt)
- I don't even know anymore — I've lost track of how I feel (HUMAN - 4pt)

**Question 3: "How do you feel about the work you chose?"**
- I still love it — the hard days are worth it (START - 1pt)
- I believe in it, but the system is wearing me down (STOP - 2pt)
- I question whether I can keep doing this (ELDER - 3pt)
- I feel trapped — I don't know who I am without this career (HUMAN - 4pt)

**Question 4: "What happens when you have time off?"**
- I recharge and come back ready (START - 1pt)
- I need the first day just to decompress (STOP - 2pt)
- Time off doesn't feel like enough — I'm still exhausted (ELDER - 3pt)
- I dread going back before the time off even starts (HUMAN - 4pt)

**Question 5: "How connected do you feel to the people around you?"**
- I have strong relationships that sustain me (START - 1pt)
- I'm present but sometimes feel distant (STOP - 2pt)
- I've been pulling away — it takes too much energy (ELDER - 3pt)
- I feel alone even in a room full of people (HUMAN - 4pt)

**Question 6: "When was the last time you did something just for yourself?"**
- This week — I make it a priority (START - 1pt)
- I can't remember exactly, maybe a few weeks ago (STOP - 2pt)
- Months — I keep saying I will but never do (ELDER - 3pt)
- I don't even know what I'd do for myself anymore (HUMAN - 4pt)

**Question 7: "How do you handle mistakes or setbacks at work?"**
- I learn from them and move on (START - 1pt)
- They bother me more than they should (STOP - 2pt)
- I replay them over and over — they confirm my fears (ELDER - 3pt)
- Every mistake feels like proof that I'm failing at everything (HUMAN - 4pt)

**Question 8: "What's your relationship with sleep?"**
- I sleep well most nights (START - 1pt)
- I have trouble falling asleep — my mind races (STOP - 2pt)
- I wake up tired no matter how much I sleep (ELDER - 3pt)
- Sleep feels like my only escape — or I can't sleep at all (HUMAN - 4pt)

**Question 9: "How do you feel about asking for help?"**
- I'm comfortable asking when I need it (START - 1pt)
- I know I should, but I usually push through alone (STOP - 2pt)
- Asking for help feels like admitting failure (ELDER - 3pt)
- I've stopped believing anyone can help (HUMAN - 4pt)

**Question 10: "What does your inner voice sound like most days?"**
- Encouraging — I'm doing my best (START - 1pt)
- Mixed — some days kind, some days critical (STOP - 2pt)
- Mostly critical — I should be doing more, doing better (ELDER - 3pt)
- Silent or cruel — I've stopped listening to myself (HUMAN - 4pt)

**Question 11: "When you think about your future, what do you feel?"**
- Hopeful — there's a path forward (START - 1pt)
- Uncertain — I don't have a clear picture (STOP - 2pt)
- Anxious — I can't see past the next shift (ELDER - 3pt)
- Empty — I've stopped imagining a future (HUMAN - 4pt)

**Question 12: "Why did you take this assessment today?"**
- Curiosity — I want to check in with myself (START - 1pt)
- I've been feeling off and wanted to understand why (STOP - 2pt)
- Someone I trust suggested I might be burned out (ELDER - 3pt)
- I'm desperate — I need something to change (HUMAN - 4pt)

### Scoring Logic

Calculate average score across all 12 questions:
- **1.0 – 1.7 = START stage** ("The Awareness Walk")
- **1.8 – 2.5 = STOP stage** ("The Pause")
- **2.6 – 3.3 = ELDER stage** ("The Seeking")
- **3.4 – 4.0 = HUMAN stage** ("The Reckoning")

### Results Screen

Show results with a smooth reveal animation. The results screen has these sections:

**1. Stage Badge & Title**
Display a large, styled badge showing their stage with an icon:
- START: Footsteps icon — "You're in the START stage: The Awareness Walk"
- STOP: Hand/pause icon — "You're in the STOP stage: The Pause"
- ELDER: Compass icon — "You're in the ELDER stage: The Seeking"
- HUMAN: Heart icon — "You're in the HUMAN stage: The Reckoning"

**2. Stage Description** (show only the matching one):

**START — The Awareness Walk:**
"You're still standing. The cracks haven't become canyons yet — but you're noticing them. This is the most powerful place to be, because awareness is where healing begins. Most people in healthcare ignore the early signs until it's too late. You didn't. The fact that you're here means you're already walking in the right direction. The crosswalk is ahead of you — and you have time to cross it on your own terms."

**STOP — The Pause:**
"You've hit the yellow light. Something in you is saying 'wait' — and you're listening, even if the world around you keeps moving. This stage is uncomfortable because you're caught between what you've been doing and what you know you need. The old coping mechanisms aren't working anymore, but you haven't found new ones yet. This is not a failure. This is the pause before the turn. Every healing journey has this moment — the moment you stop pretending you're fine."

**ELDER — The Seeking:**
"You're looking for answers outside yourself because the answers inside feel depleted. This is the stage where people reach for books, podcasts, coaches, therapists — anything that might show them a way through. You're not weak for seeking. You're wise. The 'Elder' stage is named for the act of looking to those who've walked this road before you. The crosswalk is right in front of you now. You don't have to figure out how to cross it alone."

**HUMAN — The Reckoning:**
"You've reached the place where the armor comes off. This isn't rock bottom — it's the moment of radical honesty. You're no longer the job title, the caregiver, the one who holds it together. You're a human being who has given more than they had to give. This stage feels like the end, but it's actually the beginning. The crosswalk isn't ahead of you anymore — you're standing on it. The only direction left is forward. And you don't have to walk alone."

**3. Visual Score Meter**
A horizontal bar or gauge showing where they fall on the START → STOP → ELDER → HUMAN spectrum. Highlight their position with an animated marker.

**4. "Your Next Step" Section**
- Heading: "Your Personalized Next Step"
- Text: "Based on your results, here's one thing you can do this week:"
  - START: "Journal for 5 minutes after your next shift. Write down one thing that drained you and one thing that filled you up. Awareness is the first lesson of the crosswalk."
  - STOP: "Choose one thing to say 'no' to this week. One meeting, one extra shift, one obligation that isn't yours to carry. The pause is where healing starts."
  - ELDER: "Find one person who has navigated burnout and ask them one question. A mentor, a coach, a colleague who left and came back whole. You don't need all the answers — just the next one."
  - HUMAN: "You don't need another tip. You need someone to walk with. Book a free discovery call and let's talk about where you are and where you want to go."

**5. Email Capture Section**
- Heading: "Get Your Full Crosswalk Healing Plan"
- Subheading: "We'll send you a personalized guide based on your results — plus the 5 Crosswalk Lessons that have helped hundreds of healthcare professionals find their way back."
- Email input field (placeholder: "your email address")
- First name input field (placeholder: "your first name")
- Submit button: "Send My Healing Plan"
- Small text: "No spam. Unsubscribe anytime. We respect your inbox."
- On submit: POST to `https://api.encharge.io/v1/hooks/013bfb98-e932-4336-935c-8135ae235bb0` with JSON body:
  ```json
  {
    "email": "<user email>",
    "firstName": "<user first name>",
    "quizStage": "<stage>",
    "quizScore": "<score>",
    "tags": "quiz-completed, quiz-stage-<stage>"
  }
  ```
  No authentication headers needed — this is a public Encharge hook URL.
- Show success message after submit: "Check your inbox — your healing plan is on its way."

**6. Share Section**
- "Know someone who needs this?"
- Social share buttons for: Facebook, LinkedIn, Twitter/X, WhatsApp, Email
- Share text: "I just took the Burnout Crosswalk Assessment and discovered where I am on my healing journey. Take it free: [URL]"
- Copy link button

**7. CTA to Crosswalk Wisdom**
- "Ready to start walking?"
- Two buttons:
  - "Explore the Crosswalk Method" → links to https://www.crosswalkwisdom.com
  - "Book a Free Discovery Call" → links to https://www.crosswalkwisdom.com/start

### Technical Requirements
- **Framework:** React with Vite (or Next.js)
- **Styling:** Tailwind CSS
- **Animations:** Framer Motion for page transitions, score reveal, and card selections
- **Responsive:** Mobile-first, looks great on phones (most healthcare workers will take this on their phone during a break)
- **Performance:** Fast load, no unnecessary dependencies
- **Accessibility:** All interactive elements keyboard navigable, proper ARIA labels, sufficient color contrast
- **SEO:** Add meta tags — title: "Burnout Crosswalk Assessment | Crosswalk Wisdom", description: "A free 2-minute assessment for healthcare professionals. Discover which stage of burnout you're in and get your personalized healing plan."
- **OG Tags:** og:title, og:description, og:image (use a placeholder image URL for now)
- **Analytics-ready:** Add data attributes on key events (quiz_start, question_answered, quiz_completed, email_submitted, share_clicked) so I can attach analytics later
- **Local storage:** Save quiz state so if someone refreshes mid-quiz, they don't lose progress
- **Retake:** Add a "Retake Assessment" button on the results page that clears state and starts over

### Favicon
Use a simple crosswalk/walking icon or the amber/gold brand color as a favicon.

---

End of prompt. Build the complete app.
