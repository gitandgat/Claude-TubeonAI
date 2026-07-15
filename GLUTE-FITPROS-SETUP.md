# Glute Longevity — FitPros.io Setup (canonical)

The single source of truth for delivering Glute Longevity on **FitPros.io** (chosen platform). Covers both uses: in-person GoodLife PT (salaried — no in-app payments needed) and the online Glute Longevity product.

- **Build the program:** [GLUTE-FITPROS-BUILD.md](GLUTE-FITPROS-BUILD.md) — build Week 1 (Day A/B/C), auto-progress Weeks 2–6.
- **Reusable engine (any client):** [GLUTE-POSTURE-AI-PROMPTS.md](GLUTE-POSTURE-AI-PROMPTS.md) — meta-prompt + fault→exercise menu.

**Why FitPros:** free with unlimited clients, 1,000+ HD demo videos, drag-and-drop + progression builder. No payments/scheduling needed (GoodLife handles those in-person; Stripe for the online product). Confirm GoodLife permits a third-party client app before relying on it with clients.

---

## 1. Account
1. Create the free account at fitpros.io (no card, unlimited clients).
2. **Branding is optional** — the $15/mo Custom Branding add-on is only worth it for the *online product's* polish. For GoodLife in-person clients, skip it (deliver under your name).

If you do brand it, match these tokens (same as the landing page + intro video):
| Token | Value |
|---|---|
| Accent | `#00A699` (teal) |
| Dark | `#0d0d1a` |
| Font | Inter |
| Wordmark | **GLUTE LONGEVITY** (LONGEVITY in teal) |
| Coach credential | Sahawat — Former Physician |

## 2. Program
Build it per [GLUTE-FITPROS-BUILD.md](GLUTE-FITPROS-BUILD.md): 3 Week-1 workouts → progression builder fills Weeks 2–6. Every movement is a posture-corrective + glute pairing (lower-crossed + upper-crossed). For other client profiles, generate a fresh Week-1 with the meta-prompt and repeat.

## 3. Demonstration-video integrity (non-negotiable)
- Physical demos = FitPros' licensed HD library (real demonstrators, correct form).
- Your avatar = coaching intros only, never performing exercises.
- Never imply Sahawat personally demonstrates moves he can't perform (injury/trust risk in a health product).

## 4. Coaching intro clip
Upload `avatar-engine/out/glute-intro-avatar-hook.mp4` (already rendered — your real face + voiceover, 17.8s) as the program's intro/welcome video. Regenerate weekly intros with `avatar-engine/avatar_hook.py <slug> --text "..."`. For a crisper version, re-render with `--enhancer` overnight (256×256 default is soft).

## 5. Payments (online product only)
FitPros has no built-in checkout. For the $297 / $497 online tiers:
1. Create Stripe Payment Links (one per tier).
2. On enrollment (reply-to-enroll from the Encharge nurture), send the Stripe link.
3. After payment, add the buyer as a FitPros client and assign the program.
In-person GoodLife clients: no payment step (salaried).

## 6. End-to-end flow (online product)
```
Landing /glute → Apply form (firstName,email,source:"glute")
  → POST /api/encharge/subscribe → tag glute-longevity-applicant
  → 3-email Encharge nurture (intro video → enrollment → last call)
  → client replies "I'm in" → send Stripe link → add as FitPros client → assign program
```
In-person flow: add the GoodLife client in FitPros → assign program → coach live, they follow + log in the app between sessions.

## 7. Paste-ready copy

**Program description:**
> A 6-week, clinically-minded protocol that rebuilds glute strength, hip stability, and posture — correcting the rounded-shoulder, forward-head, anterior-pelvic-tilt pattern most people carry. Every movement is demonstrated and scalable. Three short sessions a week. Built by Sahawat, former physician.

**Online product — Founding Member ($297):**
> The full Glute Longevity 6-Week Protocol: 6 progressive weeks, a follow-along demo for every movement, weekly plan, and progress tracking in your training app. Lifetime access. Money-back guarantee — complete it as designed and if your glute strength, posture, or comfort don't improve, full refund.

**Online product — Founding Member + Longevity Lift App ($497):**
> Everything in Founding Member, delivered through the branded Longevity Lift app with in-app coaching, reminders, and progress tracking — train anywhere. Priority application review. Lifetime access + updates.

**Welcome message (first client message):**
> Welcome to Glute Longevity — glad you're here. Start with the intro video, then Week 1, Day A. Week 1 rule: keep loads light, form clean. Every move has a demo and an easier option — use them. Reply any time with a question; I read everything. — Sahawat

## 8. Go-live checklist
- [ ] FitPros free account created
- [ ] (Optional) branding applied for online product
- [ ] Week 1 (A/B/C) built; Weeks 2–6 auto-progressed
- [ ] Intro avatar clip uploaded
- [ ] (Online) Stripe links for $297 / $497 created
- [ ] A test client can open the app, see Week 1, and play a demo video
- [ ] Landing `/glute` live; test application tags `glute-longevity-applicant` in Encharge
- [ ] GoodLife third-party-app policy confirmed
