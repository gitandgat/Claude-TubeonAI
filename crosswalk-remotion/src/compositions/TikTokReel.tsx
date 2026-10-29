/**
 * TikTok / Instagram Reels — 9:16 (1080x1920)
 * Subtitle-style captions animate word by word over a dark cinematic background.
 * scriptId selects which of the 4 scripts to render.
 */
import React from 'react';
import {
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  Easing,
  Sequence,
  staticFile,
} from 'remotion';
import { theme } from '../theme';
import { Logo } from '../components/Logo';
import { PhotoBackground } from '../components/PhotoBackground';

const PHOTO_BACKGROUNDS: Record<string, string> = {
  'pov-doctor-crossing-guard': staticFile('assets/bg-tiktok-pov-doctor-crossing-guard.jpg'),
  'psychiatrist-story': staticFile('assets/bg-tiktok-psychiatrist-story.jpg'),
  'things-people-say': staticFile('assets/bg-tiktok-things-people-say.jpg'),
  'yellow-vest': staticFile('assets/bg-tiktok-yellow-vest.jpg'),
  'fear-audit-walkthrough': staticFile('assets/bg-tiktok-psychiatrist-story.jpg'),
  'i-thought-i-was-afraid-of-failing': staticFile('assets/bg-tiktok-pov-doctor-crossing-guard.jpg'),
  'the-question-nobody-asks': staticFile('assets/bg-tiktok-things-people-say.jpg'),
  'fear-keeps-physicians-stuck': staticFile('assets/bg-tiktok-pov-doctor-crossing-guard.jpg'),
  'everyone-elses-safe-place': staticFile('assets/bg-tiktok-everyone-elses-safe-place.jpg'),
  'fear-audit-instagram': staticFile('assets/bg-tiktok-pov-doctor-crossing-guard.jpg'),
};

// ─── Script data ───────────────────────────────────────────────────────────────
// Each segment: { text, startFrame, durationFrames }
// At 30fps. Segments auto-stack from startFrame.

export type ScriptSegment = {
  text: string;
  type: 'hook' | 'body' | 'cta' | 'pause';
  durationFrames: number;
};

const scripts: Record<string, { title: string; segments: ScriptSegment[] }> = {
  'pov-doctor-crossing-guard': {
    title: 'POV: Doctor → Crossing Guard',
    segments: [
      { text: 'POV: You are a doctor.', type: 'hook', durationFrames: 40 },
      { text: 'And you just became a crossing guard.', type: 'hook', durationFrames: 50 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'Six years of medical school.', type: 'body', durationFrames: 45 },
      { text: 'Residency. 96-hour shifts.', type: 'body', durationFrames: 45 },
      { text: 'Sleeping in hospital stairwells.', type: 'body', durationFrames: 45 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'And now I am standing on a street corner in Canada', type: 'body', durationFrames: 55 },
      { text: 'wearing a yellow vest, holding a stop sign.', type: 'body', durationFrames: 50 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'People ask me if I miss it.', type: 'body', durationFrames: 45 },
      { text: '', type: 'pause', durationFrames: 10 },
      { text: 'I miss who I thought I would become.', type: 'body', durationFrames: 50 },
      { text: 'I do not miss who I was becoming.', type: 'body', durationFrames: 50 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'Now I watch children cross the street.', type: 'body', durationFrames: 50 },
      { text: 'They wave at me every single morning.', type: 'body', durationFrames: 50 },
      { text: '', type: 'pause', durationFrames: 10 },
      { text: 'Nobody in the hospital ever waved at me.', type: 'body', durationFrames: 55 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'I am not saying this is my forever.', type: 'body', durationFrames: 50 },
      { text: 'I am saying this is the first time in ten years', type: 'body', durationFrames: 55 },
      { text: 'I am not surviving.', type: 'body', durationFrames: 40 },
      { text: 'I am just... here.', type: 'body', durationFrames: 45 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'Fear Audit — free 5-min exercise. Link in bio.', type: 'cta', durationFrames: 70 },
    ],
  },

  'psychiatrist-story': {
    title: 'The Psychiatrist Told Me to Accept It',
    segments: [
      { text: 'The psychiatrist told me to just accept it.', type: 'hook', durationFrames: 55 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'I was working 96-hour shifts in Thailand.', type: 'body', durationFrames: 55 },
      { text: 'Four days straight.', type: 'body', durationFrames: 35 },
      { text: 'The pager went off every thirty minutes.', type: 'body', durationFrames: 50 },
      { text: 'So you never actually slept.', type: 'body', durationFrames: 45 },
      { text: '', type: 'pause', durationFrames: 10 },
      { text: 'I started having chest pain. I was twenty-eight.', type: 'body', durationFrames: 55 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'I went to a psychiatrist.', type: 'body', durationFrames: 40 },
      { text: 'I told him everything.', type: 'body', durationFrames: 40 },
      { text: 'The shifts. The screaming.', type: 'body', durationFrames: 40 },
      { text: 'The attending who threw a surgical clamp across the room.', type: 'body', durationFrames: 60 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'And he said:', type: 'body', durationFrames: 30 },
      { text: '"The system is like this.', type: 'hook', durationFrames: 40 },
      { text: 'You have to learn to accept it."', type: 'hook', durationFrames: 45 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'I sat in my car for forty-five minutes.', type: 'body', durationFrames: 50 },
      { text: '', type: 'pause', durationFrames: 10 },
      { text: 'That was the moment.', type: 'body', durationFrames: 40 },
      { text: 'Nobody was coming to save me.', type: 'body', durationFrames: 50 },
      { text: 'Not the hospital. Not the system.', type: 'body', durationFrames: 50 },
      { text: 'Not the psychiatrist.', type: 'body', durationFrames: 40 },
      { text: '', type: 'pause', durationFrames: 10 },
      { text: 'So I broke the pattern myself.', type: 'body', durationFrames: 50 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'Fear Audit — for people in that exact moment. Link in bio.', type: 'cta', durationFrames: 70 },
    ],
  },

  'things-people-say': {
    title: 'Things People Say When You Quit',
    segments: [
      { text: 'Things people say when you quit a "good" career.', type: 'hook', durationFrames: 55 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: '"But you worked so hard."', type: 'body', durationFrames: 45 },
      { text: 'Yes. That is actually the problem.', type: 'body', durationFrames: 50 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: '"You are throwing it all away."', type: 'body', durationFrames: 45 },
      { text: 'I was throwing myself away. But sure.', type: 'body', durationFrames: 50 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: '"Must be nice to just quit."', type: 'body', durationFrames: 45 },
      { text: 'Oh yes. Very relaxing. Highly recommend for the anxiety.', type: 'body', durationFrames: 60 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: '"What are you going to do now?"', type: 'body', durationFrames: 45 },
      { text: 'Breathe. That is the whole plan. Just breathe.', type: 'body', durationFrames: 55 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: '"You will regret this."', type: 'body', durationFrames: 40 },
      { text: 'Maybe. But I already know what regret feels like.', type: 'body', durationFrames: 55 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: '"I could never do that."', type: 'body', durationFrames: 40 },
      { text: 'You say that like it is a compliment.', type: 'body', durationFrames: 50 },
      { text: '', type: 'pause', durationFrames: 10 },
      { text: 'And my personal favorite:', type: 'body', durationFrames: 40 },
      { text: '"But you are a doctor."', type: 'hook', durationFrames: 40 },
      { text: 'I was a doctor.', type: 'body', durationFrames: 35 },
      { text: 'Now I am a crossing guard.', type: 'body', durationFrames: 40 },
      { text: 'And I sleep eight hours a night.', type: 'body', durationFrames: 50 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'Fear Audit — separate fear from other people\'s opinions. Link in bio.', type: 'cta', durationFrames: 75 },
    ],
  },

  'yellow-vest': {
    title: 'Yellow Vest vs White Coat',
    segments: [
      { text: 'A yellow vest taught me more about vulnerability', type: 'hook', durationFrames: 55 },
      { text: 'than medical school ever did.', type: 'hook', durationFrames: 45 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'When I was a doctor, I had a white coat.', type: 'body', durationFrames: 55 },
      { text: 'The white coat is armor.', type: 'body', durationFrames: 40 },
      { text: 'People assume you are smart.', type: 'body', durationFrames: 45 },
      { text: 'They give you authority you did not earn as a person.', type: 'body', durationFrames: 60 },
      { text: 'Only as a title.', type: 'body', durationFrames: 35 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'When I became a crossing guard,', type: 'body', durationFrames: 45 },
      { text: 'they gave me a yellow vest.', type: 'body', durationFrames: 40 },
      { text: '', type: 'pause', durationFrames: 10 },
      { text: 'A yellow vest does not protect anything.', type: 'body', durationFrames: 55 },
      { text: 'It just makes you visible.', type: 'body', durationFrames: 45 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'And that was the thing I was most afraid of.', type: 'body', durationFrames: 55 },
      { text: 'Being seen.', type: 'hook', durationFrames: 35 },
      { text: 'Not as a doctor.', type: 'body', durationFrames: 35 },
      { text: 'Just as a guy on a corner with a stop sign.', type: 'body', durationFrames: 55 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'The yellow vest is heavier than the white coat.', type: 'body', durationFrames: 60 },
      { text: 'Because it requires something the white coat never did.', type: 'body', durationFrames: 65 },
      { text: 'It requires you to be okay with exactly who you are.', type: 'body', durationFrames: 65 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: '7 Crosswalk Reflections — free guide. Link in bio.', type: 'cta', durationFrames: 70 },
    ],
  },
  'fear-audit-walkthrough': {
    title: 'Fear Audit Walkthrough',
    segments: [
      { text: 'Let me walk you through the Fear Audit.', type: 'hook', durationFrames: 55 },
      { text: 'Five minutes. One piece of paper.', type: 'hook', durationFrames: 45 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'Step one.', type: 'body', durationFrames: 30 },
      { text: 'Write this at the top:', type: 'body', durationFrames: 40 },
      { text: '"I am afraid to leave because..."', type: 'hook', durationFrames: 50 },
      { text: 'Finish the sentence ten times.', type: 'body', durationFrames: 45 },
      { text: "Don't edit. Don't filter. Just write.", type: 'body', durationFrames: 50 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: "You'll get the obvious ones first.", type: 'body', durationFrames: 45 },
      { text: 'Money. Stability. Not knowing what\'s next.', type: 'body', durationFrames: 50 },
      { text: 'Keep going.', type: 'body', durationFrames: 30 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'Somewhere around sentence five or six,', type: 'body', durationFrames: 55 },
      { text: 'the real ones show up.', type: 'body', durationFrames: 40 },
      { text: '', type: 'pause', durationFrames: 10 },
      { text: '"I\'m afraid my mother will be disappointed."', type: 'hook', durationFrames: 55 },
      { text: '"I\'m afraid I\'ll discover I\'m not good at anything else."', type: 'hook', durationFrames: 65 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'Step two.', type: 'body', durationFrames: 30 },
      { text: 'Go back through your list.', type: 'body', durationFrames: 40 },
      { text: 'For each sentence: is this a fact or a fear?', type: 'body', durationFrames: 55 },
      { text: '', type: 'pause', durationFrames: 10 },
      { text: '"I don\'t have another job lined up" — fact.', type: 'body', durationFrames: 55 },
      { text: '"I will never find something I\'m good at" — fear.', type: 'body', durationFrames: 60 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'Most of your list is fear dressed as fact.', type: 'body', durationFrames: 55 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'Step three.', type: 'body', durationFrames: 30 },
      { text: 'Pick the one fear that feels heaviest.', type: 'body', durationFrames: 50 },
      { text: 'Ask it one question:', type: 'body', durationFrames: 40 },
      { text: '"What would have to be true for this fear to be wrong?"', type: 'hook', durationFrames: 70 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: "You don't have to answer it today.", type: 'body', durationFrames: 50 },
      { text: 'Just sit with the question.', type: 'body', durationFrames: 45 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'That is the Fear Audit.', type: 'hook', durationFrames: 45 },
      { text: 'Try it tonight. Tell me what shows up.', type: 'body', durationFrames: 55 },
      { text: 'Guided version free at link in bio.', type: 'cta', durationFrames: 65 },
    ],
  },

  'i-thought-i-was-afraid-of-failing': {
    title: 'I Thought I Was Afraid of Failing',
    segments: [
      { text: 'I thought I was afraid of failing.', type: 'hook', durationFrames: 50 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'I was not afraid of failing.', type: 'hook', durationFrames: 45 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'I was afraid of having to tell my father', type: 'body', durationFrames: 55 },
      { text: 'I had made the wrong choice.', type: 'body', durationFrames: 45 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'Those are completely different fears.', type: 'body', durationFrames: 50 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'If I had been afraid of failing,', type: 'body', durationFrames: 50 },
      { text: 'I would have needed a backup plan.', type: 'body', durationFrames: 45 },
      { text: 'A proof of concept before I left.', type: 'body', durationFrames: 45 },
      { text: '', type: 'pause', durationFrames: 10 },
      { text: 'But that is not what I needed.', type: 'body', durationFrames: 45 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'What I needed was to call my father.', type: 'hook', durationFrames: 50 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'So I called him.', type: 'body', durationFrames: 35 },
      { text: 'I told him I was leaving medicine.', type: 'body', durationFrames: 50 },
      { text: 'I was a crossing guard now.', type: 'body', durationFrames: 45 },
      { text: 'I waited.', type: 'body', durationFrames: 30 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'He said: "Are you sleeping better?"', type: 'hook', durationFrames: 55 },
      { text: 'I said yes.', type: 'body', durationFrames: 30 },
      { text: 'He said: "Good."', type: 'hook', durationFrames: 35 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'The fear I had carried for three years', type: 'body', durationFrames: 55 },
      { text: 'lived inside a five-minute phone call', type: 'body', durationFrames: 50 },
      { text: 'I had been refusing to make.', type: 'body', durationFrames: 45 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'Your fear has a specific shape.', type: 'body', durationFrames: 45 },
      { text: 'It is not general dread.', type: 'body', durationFrames: 40 },
      { text: 'It is a specific scene.', type: 'body', durationFrames: 40 },
      { text: 'A specific conversation. A specific face.', type: 'body', durationFrames: 50 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'The Fear Audit helps you find the shape.', type: 'body', durationFrames: 55 },
      { text: 'Free exercise. Link in bio.', type: 'cta', durationFrames: 60 },
    ],
  },

  'fear-keeps-physicians-stuck': {
    title: 'The Fear That Keeps Physicians Stuck',
    segments: [
      // Scene 1 — Hook
      { text: 'Most physicians don\'t leave medicine because they hate it.', type: 'hook', durationFrames: 65 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'They stay.', type: 'hook', durationFrames: 35 },
      { text: '', type: 'pause', durationFrames: 10 },
      { text: 'Because they\'re terrified of who they\'ll be without it.', type: 'hook', durationFrames: 70 },
      // Scene 2 — The fear named
      { text: '', type: 'pause', durationFrames: 25 },
      { text: 'I know.', type: 'body', durationFrames: 30 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'I was one of them.', type: 'body', durationFrames: 45 },
      // Scene 3 — The pivot
      { text: '', type: 'pause', durationFrames: 25 },
      { text: 'I spent a decade building a medical identity in Thailand.', type: 'body', durationFrames: 65 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'Then I walked away.', type: 'body', durationFrames: 40 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'I became a crossing guard.', type: 'body', durationFrames: 45 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'Most people thought I\'d lost my mind.', type: 'body', durationFrames: 55 },
      { text: '', type: 'pause', durationFrames: 10 },
      { text: 'I thought I\'d finally found it.', type: 'hook', durationFrames: 55 },
      // Scene 4 — The invitation
      { text: '', type: 'pause', durationFrames: 25 },
      { text: 'If you\'re a physician quietly asking yourself—', type: 'body', durationFrames: 55 },
      { text: '"Is this all there is?"', type: 'hook', durationFrames: 45 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'That voice isn\'t weakness.', type: 'body', durationFrames: 45 },
      { text: 'It\'s the most honest thing you\'ve felt in years.', type: 'body', durationFrames: 60 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'I built something for you.', type: 'body', durationFrames: 45 },
      // Scene 5 — CTA
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'It\'s called the Fear Audit.', type: 'hook', durationFrames: 50 },
      { text: '3 minutes.', type: 'body', durationFrames: 30 },
      { text: 'It shows you exactly which fear is keeping you stuck.', type: 'body', durationFrames: 65 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'And it might be the most honest conversation', type: 'body', durationFrames: 55 },
      { text: 'you\'ll have with yourself this year.', type: 'body', durationFrames: 50 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'Fear Audit — free. 3 minutes. Link in bio.', type: 'cta', durationFrames: 70 },
    ],
  },

  'everyone-elses-safe-place': {
    title: "You're Everyone's Safe Place. Who's Yours?",
    segments: [
      { text: "If you're always the strong one —", type: 'hook', durationFrames: 50 },
      { text: 'this is for you.', type: 'hook', durationFrames: 35 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: "You're the one everyone calls when something falls apart.", type: 'body', durationFrames: 65 },
      { text: 'The 2am panic. The post-shift venting.', type: 'body', durationFrames: 55 },
      { text: 'And you look completely fine doing it.', type: 'body', durationFrames: 55 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: "There's a specific exhaustion that doesn't come from doing too much.", type: 'body', durationFrames: 70 },
      { text: 'It comes from being too much', type: 'hook', durationFrames: 45 },
      { text: 'for too many people.', type: 'hook', durationFrames: 40 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'The more composed you look,', type: 'body', durationFrames: 45 },
      { text: 'the less anyone checks on you.', type: 'body', durationFrames: 50 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: "That's not a flaw in the people around you.", type: 'body', durationFrames: 55 },
      { text: "It's what happens when you become the structural support", type: 'body', durationFrames: 65 },
      { text: 'for everyone else.', type: 'body', durationFrames: 35 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'Your nervous system is working,', type: 'body', durationFrames: 50 },
      { text: 'even when you look calm.', type: 'body', durationFrames: 45 },
      { text: '', type: 'pause', durationFrames: 10 },
      { text: 'Masked activation is still activation.', type: 'hook', durationFrames: 55 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'One thing that helps:', type: 'body', durationFrames: 35 },
      { text: 'stop saying yes', type: 'hook', durationFrames: 40 },
      { text: "before you've finished taking a breath.", type: 'body', durationFrames: 55 },
      { text: '', type: 'pause', durationFrames: 10 },
      { text: 'Try this: "Let me check and get back to you."', type: 'hook', durationFrames: 65 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'That pause is where you get to choose.', type: 'body', durationFrames: 55 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'Full article — link in bio. crosswalkwisdom.com/blog', type: 'cta', durationFrames: 70 },
    ],
  },

  'the-question-nobody-asks': {
    title: 'The Question Nobody Asks',
    segments: [
      { text: 'There is one question I ask every professional', type: 'hook', durationFrames: 55 },
      { text: 'who says they are stuck.', type: 'hook', durationFrames: 40 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'Not "what do you want to do instead?"', type: 'body', durationFrames: 55 },
      { text: 'Not "have you updated your resume?"', type: 'body', durationFrames: 50 },
      { text: 'Not "what is your financial runway?"', type: 'body', durationFrames: 50 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'This:', type: 'body', durationFrames: 25 },
      { text: '', type: 'pause', durationFrames: 10 },
      { text: '"What, specifically, are you afraid will happen', type: 'hook', durationFrames: 60 },
      { text: 'if you leave?"', type: 'hook', durationFrames: 35 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'Not "leaving is scary."', type: 'body', durationFrames: 45 },
      { text: 'Specifically. What will happen.', type: 'body', durationFrames: 45 },
      { text: 'Give me the scene. The conversation.', type: 'body', durationFrames: 50 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'Most people cannot answer it.', type: 'body', durationFrames: 45 },
      { text: '', type: 'pause', durationFrames: 10 },
      { text: 'Not because they do not have an answer.', type: 'body', durationFrames: 55 },
      { text: 'Because they have never been asked', type: 'body', durationFrames: 50 },
      { text: 'to be specific.', type: 'body', durationFrames: 35 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'The fear lives in the vague.', type: 'body', durationFrames: 45 },
      { text: 'It is enormous when it is unnamed.', type: 'body', durationFrames: 50 },
      { text: 'It is manageable when you name it.', type: 'body', durationFrames: 50 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'In every case, the specific fear', type: 'body', durationFrames: 50 },
      { text: 'turned out to be smaller than the dread.', type: 'body', durationFrames: 55 },
      { text: '', type: 'pause', durationFrames: 10 },
      { text: 'Not small. Just smaller.', type: 'hook', durationFrames: 40 },
      { text: 'Small enough to work with.', type: 'body', durationFrames: 45 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'That is what the Fear Audit does.', type: 'body', durationFrames: 50 },
      { text: 'It asks you to be specific.', type: 'body', durationFrames: 45 },
      { text: 'Five minutes. Free. Link in bio.', type: 'cta', durationFrames: 65 },
    ],
  },

  'fear-audit-instagram': {
    title: 'The Fear That Keeps Physicians Stuck',
    segments: [
      // Scene 1 — Hook
      { text: 'Most physicians don\'t leave medicine because they hate it.', type: 'hook', durationFrames: 70 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'They stay.', type: 'hook', durationFrames: 35 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'Because they\'re terrified of who they\'ll be without it.', type: 'hook', durationFrames: 70 },
      { text: '', type: 'pause', durationFrames: 20 },
      // Scene 2 — The fear named
      { text: 'I know.', type: 'body', durationFrames: 30 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'I was one of them.', type: 'body', durationFrames: 45 },
      { text: '', type: 'pause', durationFrames: 25 },
      { text: 'I spent a decade building a medical identity in Thailand.', type: 'body', durationFrames: 65 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: '"Dr." was the only title I allowed myself to have.', type: 'body', durationFrames: 60 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'And then I walked away.', type: 'body', durationFrames: 45 },
      { text: '', type: 'pause', durationFrames: 15 },
      // Scene 3 — The pivot
      { text: 'I moved to Toronto.', type: 'body', durationFrames: 40 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'And I became a crossing guard.', type: 'body', durationFrames: 50 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'People thought I\'d lost my mind.', type: 'body', durationFrames: 50 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'What I\'d actually lost was the fear.', type: 'hook', durationFrames: 55 },
      { text: '', type: 'pause', durationFrames: 25 },
      { text: 'Standing at those intersections—', type: 'body', durationFrames: 45 },
      { text: 'waving kids across, watching the city breathe—', type: 'body', durationFrames: 55 },
      { text: 'I started to see what I\'d been too busy to notice.', type: 'body', durationFrames: 60 },
      { text: '', type: 'pause', durationFrames: 20 },
      // Scene 4 — The invitation
      { text: 'If you\'re a physician quietly asking yourself—', type: 'body', durationFrames: 55 },
      { text: '"Is this all there is?"', type: 'hook', durationFrames: 45 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'That voice isn\'t weakness.', type: 'body', durationFrames: 45 },
      { text: 'It\'s the most honest thing you\'ve felt in years.', type: 'body', durationFrames: 60 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'I built something for you.', type: 'body', durationFrames: 45 },
      { text: '', type: 'pause', durationFrames: 25 },
      // Scene 5 — CTA
      { text: 'It\'s called the Fear Audit.', type: 'hook', durationFrames: 50 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: '3 minutes.', type: 'body', durationFrames: 35 },
      { text: 'Shows you exactly which fear is keeping you stuck.', type: 'body', durationFrames: 65 },
      { text: '', type: 'pause', durationFrames: 20 },
      { text: 'And it might be the most honest conversation', type: 'body', durationFrames: 55 },
      { text: 'you\'ll have with yourself this year.', type: 'body', durationFrames: 50 },
      { text: '', type: 'pause', durationFrames: 15 },
      { text: 'Free. 3 minutes. fear-audit.vercel.app', type: 'cta', durationFrames: 70 },
    ],
  },

  'fear-audit': {
    title: 'The Fear That Keeps Physicians Stuck',
    segments: [
      // Scene 1 — Hook (0–8s = 240 frames)
      { text: 'Most physicians don\'t leave medicine because they hate it.', type: 'hook', durationFrames: 180 },
      { text: '', type: 'pause', durationFrames: 60 },

      // Scene 2 — Fear Named (8–20s = 360 frames)
      { text: 'They stay because they\'re terrified of who they\'ll be without it.', type: 'hook', durationFrames: 240 },
      { text: '', type: 'pause', durationFrames: 120 },

      // Scene 3 — Pivot (20–35s = 450 frames)
      { text: 'I was one of them.', type: 'body', durationFrames: 90 },
      { text: 'I became a crossing guard.', type: 'body', durationFrames: 90 },
      { text: '', type: 'pause', durationFrames: 30 },
      { text: 'Most people thought I\'d lost my mind.', type: 'body', durationFrames: 90 },
      { text: 'I thought I\'d finally found it.', type: 'hook', durationFrames: 90 },
      { text: '', type: 'pause', durationFrames: 60 },

      // Scene 4 — Invitation (35–48s = 390 frames)
      { text: 'If you\'re a physician quietly asking yourself—', type: 'body', durationFrames: 100 },
      { text: '"Is this all there is?"', type: 'hook', durationFrames: 80 },
      { text: '', type: 'pause', durationFrames: 30 },
      { text: 'That voice isn\'t weakness.', type: 'body', durationFrames: 80 },
      { text: 'It\'s the most honest thing you\'ve felt in years.', type: 'body', durationFrames: 100 },

      // Scene 5 — CTA (48–60s = 360 frames)
      { text: '', type: 'pause', durationFrames: 30 },
      { text: 'The Fear Audit.', type: 'hook', durationFrames: 80 },
      { text: '3 minutes.', type: 'body', durationFrames: 60 },
      { text: 'fear-audit.vercel.app', type: 'cta', durationFrames: 190 },
    ],
  },
};

// ─── Caption component ──────────────────────────────────────────────────────────

// Kinetic word-by-word reveal — each word springs up into place, staggered.
// This is the core "stop the scroll" motion: text is never static.
const AnimatedWords: React.FC<{
  text: string;
  fps: number;
  localFrame: number;
  wordStyle: React.CSSProperties;
  stagger?: number;
}> = ({ text, fps, localFrame, wordStyle, stagger = 1.5 }) => (
  <>
    {text.split(' ').map((word, i) => {
      const s = spring({
        frame: localFrame - i * stagger,
        fps,
        config: { damping: 13, stiffness: 220, mass: 0.5 },
      });
      const ty = interpolate(s, [0, 1], [40, 0]);
      const sc = interpolate(s, [0, 1], [0.7, 1]);
      return (
        <span
          key={i}
          style={{
            display: 'inline-block',
            opacity: s,
            transform: `translateY(${ty}px) scale(${sc})`,
            marginRight: '0.26em',
            ...wordStyle,
          }}
        >
          {word}
        </span>
      );
    })}
  </>
);

const Caption: React.FC<{ segment: ScriptSegment; localFrame: number }> = ({
  segment,
  localFrame,
}) => {
  const { fps } = useVideoConfig();

  if (segment.type === 'pause' || !segment.text) return null;

  const isHook = segment.type === 'hook';
  const isCta = segment.type === 'cta';

  // Quick exit in the last 5 frames; entrance is handled per-word (spring).
  const opacity = interpolate(
    localFrame,
    [segment.durationFrames - 5, segment.durationFrames],
    [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );
  // Gentle continuous upward drift so the frame is never frozen.
  const drift = interpolate(localFrame, [0, segment.durationFrames], [6, -6]);

  return (
    <div
      style={{
        opacity,
        transform: `translateY(${drift}px)`,
        textAlign: 'center',
        padding: '0 50px',
      }}
    >
      {/* HOOK — huge amber-block words, maximum scroll-stop */}
      {isHook && (
        <div style={{ display: 'inline-block', backgroundColor: theme.colors.amber, borderRadius: 8, padding: '10px 24px' }}>
          <AnimatedWords
            text={segment.text}
            fps={fps}
            localFrame={localFrame}
            stagger={1.2}
            wordStyle={{
              fontFamily: theme.fonts.serif,
              fontSize: 86,
              fontWeight: 800,
              color: theme.colors.charcoal,
              lineHeight: 1.05,
              letterSpacing: '-0.02em',
            }}
          />
        </div>
      )}

      {/* BODY — big bold warm-white words */}
      {!isHook && !isCta && (
        <AnimatedWords
          text={segment.text}
          fps={fps}
          localFrame={localFrame}
          wordStyle={{
            fontFamily: theme.fonts.sans,
            fontSize: 64,
            fontWeight: 700,
            color: theme.colors.warmWhite,
            lineHeight: 1.15,
            textShadow: '0 3px 18px rgba(0,0,0,0.75)',
          }}
        />
      )}

      {/* CTA — amber bordered box */}
      {isCta && (
        <div style={{ backgroundColor: 'rgba(212,168,67,0.18)', border: `3px solid ${theme.colors.amber}`, borderRadius: 16, padding: '24px 34px' }}>
          <AnimatedWords
            text={segment.text}
            fps={fps}
            localFrame={localFrame}
            wordStyle={{
              fontFamily: theme.fonts.sans,
              fontSize: 54,
              fontWeight: 700,
              color: theme.colors.amber,
              lineHeight: 1.2,
            }}
          />
        </div>
      )}
    </div>
  );
};

// ─── Main composition ───────────────────────────────────────────────────────────

export const TikTokReel: React.FC<{
  scriptId?: string;
  // Dynamic mode: the agent passes generated segments + background directly via
  // --props, overriding the hardcoded scriptId map. Enables autonomous video.
  segments?: ScriptSegment[];
  background?: string;
  handle?: string;
}> = ({
  scriptId = 'pov-doctor-crossing-guard',
  segments: segmentsProp,
  background,
  handle = '@crosswalkwisdom',
}) => {
  const frame = useCurrentFrame();
  const script = scripts[scriptId] ?? scripts['pov-doctor-crossing-guard'];
  const segments =
    segmentsProp && segmentsProp.length > 0 ? segmentsProp : script.segments;
  const backgroundSrc = background
    ? staticFile(background)
    : (PHOTO_BACKGROUNDS[scriptId] ?? PHOTO_BACKGROUNDS['pov-doctor-crossing-guard']);

  // Compute start frame for each segment
  let accumulated = 0;
  const segmentStarts = segments.map((seg) => {
    const start = accumulated;
    accumulated += seg.durationFrames;
    return start;
  });

  // Find current segment
  const currentSegIdx = segmentStarts.findIndex(
    (start, i) =>
      frame >= start &&
      (i === segments.length - 1 || frame < segmentStarts[i + 1])
  );
  const currentSeg = segments[currentSegIdx];
  const localFrame = currentSegIdx >= 0 ? frame - segmentStarts[currentSegIdx] : 0;

  // Background motion: a fast zoom-PUNCH at every cut (1.12 → 1.0 over 12f) on
  // top of a slow whole-video drift — so it reads as a scene change and never
  // sits still.
  const bgPunch = interpolate(localFrame, [0, 12], [1.12, 1.0], {
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const bgDrift = interpolate(frame, [0, accumulated || 1], [1.0, 1.09]);
  const bgScale = bgPunch * bgDrift;

  // Brief flash on each cut — the "quick transition" punch (strongest early).
  const flash = interpolate(localFrame, [0, 4], [0.32, 0], { extrapolateRight: 'clamp' });

  return (
    <div
      style={{
        width: 1080,
        height: 1920,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <div style={{ position: 'absolute', inset: 0, transform: `scale(${bgScale})`, transformOrigin: 'center' }}>
        <PhotoBackground
          src={backgroundSrc}
          overlayOpacity={0.58}
          parallax
        />
      </div>

      {/* Cut flash */}
      {flash > 0.01 && (
        <div style={{ position: 'absolute', inset: 0, backgroundColor: theme.colors.warmWhite, opacity: flash, zIndex: 5, pointerEvents: 'none' }} />
      )}

      {/* Logo — top */}
      <div style={{ position: 'absolute', top: 80, left: 60, zIndex: 10 }}>
        <Logo size={24} color={theme.colors.amber} />
      </div>

      {/* Script title — top right */}
      <div
        style={{
          position: 'absolute',
          top: 88,
          right: 60,
          fontFamily: theme.fonts.sans,
          fontSize: 22,
          color: 'rgba(250,247,242,0.4)',
          letterSpacing: '0.08em',
          textTransform: 'uppercase',
        }}
      >
        {handle}
      </div>

      {/* Caption — vertically centered so the bigger text is well framed */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          bottom: 0,
          left: 0,
          right: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 8,
        }}
      >
        {currentSeg && <Caption segment={currentSeg} localFrame={localFrame} />}
      </div>

      {/* Progress bar */}
      <div
        style={{
          position: 'absolute',
          bottom: 140,
          left: 60,
          right: 60,
          height: 3,
          backgroundColor: 'rgba(250,247,242,0.15)',
          borderRadius: 2,
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${(frame / accumulated) * 100}%`,
            backgroundColor: theme.colors.amber,
            borderRadius: 2,
          }}
        />
      </div>
    </div>
  );
};
