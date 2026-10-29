# Encharge flow build — browser automation instructions

GOAL: Build 5 tag-triggered nurture flows in Encharge. The emails already exist
(created via API) — only SELECT them by name; never create new emails.

APP: https://app.encharge.io  (assume logged in; if a login screen appears, log in first)

Run the PROCEDURE once for each row in the DATA table. Match buttons/steps by their
visible text — Encharge labels can vary slightly (e.g. "Time Delay" vs "Wait",
"Set live" vs "Activate", "Create flow" vs "New flow").

## PROCEDURE (one flow)

1. Click "Flows" in the left sidebar.
2. Click "Create flow" (or "New flow"). If a template chooser appears, choose
   "Start from scratch" / blank flow.
3. Set the flow name to {FLOW_NAME} (click the flow title at the top-left and type it).
4. On the canvas, click the starting node ("Add a trigger" / the top circle). In the
   trigger picker, choose the trigger named "Tag added" (it's under People / Tags).
5. In the trigger settings, set the tag to {TAG}. Save/confirm the trigger.
6. Click the "+" button beneath the trigger → choose action "Send Email".
7. In the Send Email step, pick the EXISTING email named exactly "{EMAIL_1}". Save the step.
8. Click "+" → add "Time Delay" (Wait). Set the delay to 2 days. Save.
9. Click "+" → "Send Email" → pick "{EMAIL_2}". Save.
10. Click "+" → "Time Delay" → 2 days. Save.
11. Click "+" → "Send Email" → pick "{EMAIL_3}". Save.
12. Click "Save" (top-right). Then switch the flow status to "Live" / "Active"
    (top-right toggle; confirm any "Set flow live" dialog).
13. Verify the flow reads: Trigger "Tag added: {TAG}" → Email → Wait 2 days → Email
    → Wait 2 days → Email, and the status badge says Live.

## DATA (repeat PROCEDURE for each)

Row 1
  FLOW_NAME: Pivot Map Nurture
  TAG:       lead-magnet-pivot-map
  EMAIL_1:   Pivot Map - 01 Deliver
  EMAIL_2:   Pivot Map - 02 Reframe
  EMAIL_3:   Pivot Map - 03 Bridge

Row 2
  FLOW_NAME: Inner Voices Nurture
  TAG:       lead-magnet-inner-voices
  EMAIL_1:   Inner Voices - 01 Deliver
  EMAIL_2:   Inner Voices - 02 The Realist
  EMAIL_3:   Inner Voices - 03 Identity

Row 3
  FLOW_NAME: Train Like a Clinician Nurture
  TAG:       lead-magnet-train-like-a-clinician
  EMAIL_1:   Train Like a Clinician - 01 Deliver
  EMAIL_2:   Train Like a Clinician - 02 Soreness
  EMAIL_3:   Train Like a Clinician - 03 Coaching

Row 4
  FLOW_NAME: Marginal Decade Nurture
  TAG:       lead-magnet-marginal-decade
  EMAIL_1:   Marginal Decade - 01 Deliver
  EMAIL_2:   Marginal Decade - 02 Muscle
  EMAIL_3:   Marginal Decade - 03 Screening

Row 5
  FLOW_NAME: Clinic to Coaching Nurture
  TAG:       lead-magnet-clinic-to-coaching
  EMAIL_1:   Clinic to Coaching - 01 Deliver
  EMAIL_2:   Clinic to Coaching - 02 Not a step down
  EMAIL_3:   Clinic to Coaching - 03 Map

## AFTER BUILDING — test (optional but recommended)

For one flow, go to People → add a new contact with a Gmail plus-alias
(e.g. totomakus+pmtest@gmail.com), then add the tag (e.g. lead-magnet-pivot-map) to that
contact. The Day-0 email should send within a couple of minutes. Use a fresh alias each
test — Encharge will not re-send an email to a contact that already received it.
