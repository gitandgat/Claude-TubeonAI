/**
 * LinkedIn Video — 16:9 (1920x1080)
 * Animated text storytelling format matching Sahawat's LinkedIn voice.
 * postId selects which LinkedIn post to animate.
 */
import React from 'react';
import { useCurrentFrame, interpolate, Easing, Sequence, staticFile } from 'remotion';
import { theme } from '../theme';
import { Logo } from '../components/Logo';
import { PhotoBackground } from '../components/PhotoBackground';

const PHOTO_BACKGROUNDS: Record<string, string> = {
  'sunk-cost': staticFile('assets/bg-linkedin-sunk-cost.jpg'),
  'what-will-people-think': staticFile('assets/bg-linkedin-what-will-people-think.jpg'),
  'quitting-is-not-failure': staticFile('assets/bg-linkedin-quitting-is-not-failure.jpg'),
  'fear-audit-intro': staticFile('assets/bg-linkedin-fear-audit-intro.jpg'),
  'naming-fear': staticFile('assets/bg-linkedin-what-will-people-think.jpg'),
  'five-fears': staticFile('assets/bg-linkedin-sunk-cost.jpg'),
  'four-stages': staticFile('assets/bg-linkedin-quitting-is-not-failure.jpg'),
  'why-i-built-it': staticFile('assets/bg-linkedin-fear-audit-intro.jpg'),
};

// ─── Post data ─────────────────────────────────────────────────────────────────
// Each block shows on screen for its durationFrames, then fades out as next appears.

type Block = {
  lines: string[];
  style: 'large' | 'normal' | 'quote' | 'emphasis';
  durationFrames: number;
};

const posts: Record<string, { title: string; blocks: Block[] }> = {
  'sunk-cost': {
    title: 'The Sunk Cost Trap',
    blocks: [
      { lines: ['I stayed in medicine', '2 years longer than I should have.'], style: 'large', durationFrames: 70 },
      { lines: ['Not because I loved it.', '', 'Because I had already given too much to leave.'], style: 'normal', durationFrames: 75 },
      { lines: ['6 years of medical school.', 'Residency.', 'The sleepless rotations.', 'The money. The time.', 'The youth I spent studying', 'while everyone else was living.'], style: 'normal', durationFrames: 90 },
      { lines: ['"You\'ve come too far to quit now."', '', 'That sentence almost killed me.'], style: 'quote', durationFrames: 75 },
      { lines: ['The investment becomes the cage.', '', 'Every year you stay, the cage gets smaller.'], style: 'emphasis', durationFrames: 75 },
      { lines: ['Two years of 96-hour shifts.', 'Two years of being screamed at.', 'Two years of falling asleep', 'in hospital stairwells.'], style: 'normal', durationFrames: 80 },
      { lines: ['The day I finally left,', 'I did not feel like I was throwing anything away.', '', 'I felt like I had finally stopped', 'throwing myself away.'], style: 'emphasis', durationFrames: 90 },
      { lines: ['Fear Audit', 'Free. 5 minutes.', 'Link in comments.'], style: 'large', durationFrames: 80 },
    ],
  },

  'what-will-people-think': {
    title: 'What Will People Think',
    blocks: [
      { lines: ['When I told my mother I was leaving medicine,', 'she cried.'], style: 'large', durationFrames: 75 },
      { lines: ['Not because she was sad.', 'Because she was scared for me.'], style: 'normal', durationFrames: 65 },
      { lines: ['"My son is a doctor."', '', 'Four words that carry the weight', 'of generations.'], style: 'quote', durationFrames: 75 },
      { lines: ['My friends did not know what to say.', 'Some stopped calling.', 'Some gave me the look.'], style: 'normal', durationFrames: 75 },
      { lines: ['Here is what I have learned:', '', '"What will people think"', 'lasts five minutes.', '', 'The life you are not living?', 'That stays with you every day.'], style: 'emphasis', durationFrames: 95 },
      { lines: ['I chose to disappoint some people', 'so I could stop disappointing myself.', '', 'That is not selfish.', 'That is survival.'], style: 'emphasis', durationFrames: 85 },
      { lines: ['Fear Audit', 'Separate real risk from social pressure.', 'Link in comments.'], style: 'large', durationFrames: 80 },
    ],
  },

  'quitting-is-not-failure': {
    title: 'Quitting Is Not Failure',
    blocks: [
      { lines: ['Quitting is not the opposite of success.'], style: 'large', durationFrames: 65 },
      { lines: ['Staying in something that is destroying you', 'is not strength.', '', 'It is just endurance', 'with no finish line.'], style: 'normal', durationFrames: 80 },
      { lines: ['I pushed through 96-hour shifts.', 'I pushed through supervisors', 'who threw instruments in the OR.', 'I pushed through a system that treated', 'sleep as a luxury.'], style: 'normal', durationFrames: 90 },
      { lines: ['And when I finally stopped pushing,', 'people called it quitting.', '', 'I call it the single hardest decision', 'I have ever made.'], style: 'emphasis', durationFrames: 85 },
      { lines: ['Staying was autopilot.', 'Leaving was a choice.'], style: 'large', durationFrames: 65 },
      { lines: ['And choice — real, terrifying,', 'deliberate choice — is not weakness.', '', 'It is the first honest thing', 'I did in years.'], style: 'emphasis', durationFrames: 85 },
      { lines: ['Fear Audit', 'The difference between commitment and captivity.', 'Link in comments.'], style: 'large', durationFrames: 80 },
    ],
  },

  'fear-audit-intro': {
    title: 'Introducing the Fear Audit',
    blocks: [
      { lines: ['Most people don\'t leave bad careers', 'because of logistics.'], style: 'large', durationFrames: 70 },
      { lines: ['They leave when they finally name', 'what they\'re actually afraid of.'], style: 'normal', durationFrames: 70 },
      { lines: ['"I\'m afraid my parents will think', 'I wasted their sacrifice."', '"I\'m afraid I\'m not good enough', 'to do anything else."', '"I\'m afraid people will stop', 'respecting me."'], style: 'quote', durationFrames: 95 },
      { lines: ['Those aren\'t logistics.', 'Those are fears.', '', 'And unnamed fears', 'have all the power.'], style: 'emphasis', durationFrames: 80 },
      { lines: ['The Fear Audit.', 'A 5-minute exercise.', '', 'Write "I\'m afraid that..."', '5 to 7 times.', 'Don\'t filter.'], style: 'normal', durationFrames: 85 },
      { lines: ['Circle the one that hits hardest.', 'Then ask it:', '"Is this true,', 'or is this a story I\'m telling myself?"'], style: 'normal', durationFrames: 85 },
      { lines: ['Fog with a name is something', 'you can walk through.'], style: 'emphasis', durationFrames: 70 },
      { lines: ['Download the Fear Audit', 'Free. Link in comments.'], style: 'large', durationFrames: 80 },
    ],
  },

  'naming-fear': {
    title: 'Named Fear',
    blocks: [
      { lines: ['I named my fear out loud', 'for the first time on a Tuesday morning.'], style: 'large', durationFrames: 80 },
      { lines: ['No app. No therapist.', 'Just a pen and a question:', '"What, specifically,', 'am I afraid of?"'], style: 'normal', durationFrames: 85 },
      { lines: ['"I am afraid that without the title', 'of doctor, my parents will stop', 'being proud of me."'], style: 'quote', durationFrames: 85 },
      { lines: ['When fear is unnamed,', 'it feels like the truth.', '', 'When it is named,', 'it feels like a sentence', 'you can examine.'], style: 'normal', durationFrames: 90 },
      { lines: ['Is that actually true?', 'Has my father ever said his love', 'was conditional on my job title?', '', 'No.', 'He said it was conditional', 'on my being kind.'], style: 'normal', durationFrames: 100 },
      { lines: ['Fear named is fear', 'that can be questioned.', '', 'Fear unnamed is fear', 'that cannot be beaten.'], style: 'emphasis', durationFrames: 90 },
      { lines: ['The Fear Audit.', 'Free. 5 minutes. Link in comments.'], style: 'large', durationFrames: 80 },
    ],
  },

  'five-fears': {
    title: 'The 5 Fears Inside Can\'t Leave',
    blocks: [
      { lines: ['"I can\'t leave."', '', 'There are always 5 fears', 'inside that sentence.'], style: 'large', durationFrames: 80 },
      { lines: ['FINANCIAL FEAR', '"I won\'t be able to pay my bills."', '', 'Real. Deserves a real plan.', 'Almost never the actual blocker.', 'Most people have never run', 'the actual numbers.'], style: 'normal', durationFrames: 100 },
      { lines: ['IDENTITY FEAR', '"Who am I without this title?"', '', 'The silent one.', 'The fear the career is you.', 'That without it,', 'you are unrecognizable.'], style: 'normal', durationFrames: 100 },
      { lines: ['JUDGMENT FEAR', '"What will people think?"', '', 'Not your closest friends.', 'The peripheral people.', 'We make enormous life decisions', 'to avoid conversations', 'with people we barely like.'], style: 'normal', durationFrames: 110 },
      { lines: ['FAILURE FEAR', '"What if I try and it doesn\'t work?"', '', 'Disguised as realism.', '', 'Realism would also ask:', '"What if it does?"'], style: 'normal', durationFrames: 100 },
      { lines: ['GRIEF FEAR', '"What if I leave and feel like', 'I wasted everything?"', '', 'Not fear of the future.', 'Fear of having to mourn the past.', '', 'This kept me in medicine', 'two extra years.'], style: 'quote', durationFrames: 110 },
      { lines: ['Each fear needs', 'a different conversation.', '', 'The Fear Audit separates them.', 'Free. Link in comments.'], style: 'emphasis', durationFrames: 90 },
    ],
  },

  'four-stages': {
    title: 'The 4 Stages of Stuck',
    blocks: [
      { lines: ['Not everyone who\'s stuck', 'looks the same.', '', '4 stages.', 'Different fears.', 'Different next step.'], style: 'large', durationFrames: 90 },
      { lines: ['START', 'You know something is wrong', 'but can\'t name it yet.', '', 'Fear feels like background noise.', 'You keep saying:', '"I just need to push through."'], style: 'normal', durationFrames: 100 },
      { lines: ['STOP', 'You know exactly what\'s wrong.', 'You\'ve thought about leaving', 'until it\'s its own exhausting thing.', '', 'But you can\'t move.'], style: 'normal', durationFrames: 95 },
      { lines: ['ELDER', 'You\'ve been here a long time.', 'Fear has become habit.', '', 'It doesn\'t feel like fear anymore.', 'It just feels like', '"how work is."'], style: 'normal', durationFrames: 100 },
      { lines: ['HUMAN', 'Something broke recently.', 'A moment. A loss. A conversation.', '', 'You\'re not asking', '"Should I leave?"', 'You\'re asking "How?"'], style: 'normal', durationFrames: 100 },
      { lines: ['Every stage has a path forward.', '', 'The Fear Audit meets you', 'where you are —', 'not where you think', 'you should be.'], style: 'emphasis', durationFrames: 90 },
      { lines: ['Take the Fear Audit free.', '5 minutes.', 'Find your stage.', 'Link in comments.'], style: 'large', durationFrames: 85 },
    ],
  },

  'why-i-built-it': {
    title: 'Why I Built the Fear Audit',
    blocks: [
      { lines: ['I did not build the Fear Audit', 'because I am a coach.', '', 'I built it because I needed it', 'and it didn\'t exist.'], style: 'large', durationFrames: 90 },
      { lines: ['When I was trying to leave medicine,', 'I searched for something that would help', 'me figure out what I was actually afraid of.'], style: 'normal', durationFrames: 85 },
      { lines: ['I found:', 'Career counselors who wanted', 'to talk about skills assessments.', 'Books that assumed I already knew', 'what I wanted.', 'Nobody who helped with', 'my specific problem.'], style: 'normal', durationFrames: 105 },
      { lines: ['I knew what I wanted.', 'I wanted out.', '', 'I didn\'t know', 'what was stopping me.', '', 'That is a different problem.'], style: 'emphasis', durationFrames: 95 },
      { lines: ['Fear of career change is not one thing.', '', 'It is a cluster of distinct fears', 'that feel like one fog.', '', 'Until you separate them,', 'every move feels impossible.'], style: 'normal', durationFrames: 105 },
      { lines: ['I eventually built the separation', 'exercise myself.', '', 'On a piece of paper,', 'at a kitchen table,', 'with a pen.'], style: 'quote', durationFrames: 95 },
      { lines: ['That is all it does.', 'That is all I needed.', '', 'Free. 5 minutes. Link in comments.'], style: 'large', durationFrames: 85 },
    ],
  },
};

// ─── Block renderer ─────────────────────────────────────────────────────────────

const BlockView: React.FC<{ block: Block; localFrame: number }> = ({ block, localFrame }) => {
  const fadeIn = interpolate(localFrame, [0, 20], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.quad),
  });
  const fadeOut = interpolate(
    localFrame,
    [block.durationFrames - 20, block.durationFrames],
    [1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );
  const opacity = Math.min(fadeIn, fadeOut);
  const translateY = interpolate(localFrame, [0, 20], [24, 0], {
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

  const styleMap = {
    large: { fontSize: 72, fontFamily: theme.fonts.serif, fontWeight: 700, color: theme.colors.warmWhite },
    normal: { fontSize: 52, fontFamily: theme.fonts.sans, fontWeight: 400, color: theme.colors.warmWhite },
    quote: { fontSize: 56, fontFamily: theme.fonts.serif, fontWeight: 400, color: theme.colors.amber, fontStyle: 'italic' as const },
    emphasis: { fontSize: 56, fontFamily: theme.fonts.sans, fontWeight: 600, color: theme.colors.warmWhite },
  };

  const s = styleMap[block.style];

  return (
    <div
      style={{
        opacity,
        transform: `translateY(${translateY}px)`,
        textAlign: 'center',
        padding: '0 120px',
        maxWidth: 1400,
        margin: '0 auto',
      }}
    >
      {block.lines.map((line, i) => (
        <div
          key={i}
          style={{
            ...s,
            lineHeight: 1.35,
            marginBottom: line === '' ? s.fontSize * 0.5 : s.fontSize * 0.15,
            textShadow: block.style === 'quote' ? 'none' : '0 2px 8px rgba(0,0,0,0.4)',
          }}
        >
          {line}
        </div>
      ))}
    </div>
  );
};

// ─── Main composition ───────────────────────────────────────────────────────────

export const LinkedInVideo: React.FC<{ postId?: string }> = ({
  postId = 'sunk-cost',
}) => {
  const frame = useCurrentFrame();
  const post = posts[postId] ?? posts['sunk-cost'];
  const blocks = post.blocks;

  let accumulated = 0;
  const blockStarts = blocks.map((b) => {
    const start = accumulated;
    accumulated += b.durationFrames;
    return start;
  });

  const currentBlockIdx = blockStarts.findIndex(
    (start, i) =>
      frame >= start && (i === blocks.length - 1 || frame < blockStarts[i + 1])
  );
  const currentBlock = blocks[currentBlockIdx];
  const localFrame = currentBlockIdx >= 0 ? frame - blockStarts[currentBlockIdx] : 0;

  // Chapter progress dots
  const progress = frame / accumulated;

  return (
    <div
      style={{
        width: 1920,
        height: 1080,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <PhotoBackground
        src={PHOTO_BACKGROUNDS[postId] ?? PHOTO_BACKGROUNDS['sunk-cost']}
        overlayOpacity={0.50}
        parallax
      />

      {/* Logo — top left */}
      <div style={{ position: 'absolute', top: 60, left: 80, zIndex: 10 }}>
        <Logo size={32} color={theme.colors.amber} />
      </div>

      {/* Chapter indicator — top right */}
      <div
        style={{
          position: 'absolute',
          top: 72,
          right: 80,
          fontFamily: theme.fonts.sans,
          fontSize: 24,
          color: 'rgba(250,247,242,0.4)',
          letterSpacing: '0.1em',
          textTransform: 'uppercase',
        }}
      >
        {currentBlockIdx + 1} / {blocks.length}
      </div>

      {/* Content — vertically centered */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {currentBlock && <BlockView block={currentBlock} localFrame={localFrame} />}
      </div>

      {/* Progress bar — bottom */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: 6,
          backgroundColor: 'rgba(212,168,67,0.15)',
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${progress * 100}%`,
            backgroundColor: theme.colors.amber,
          }}
        />
      </div>

      {/* Bottom tagline */}
      <div
        style={{
          position: 'absolute',
          bottom: 30,
          left: 0,
          right: 0,
          textAlign: 'center',
          fontFamily: theme.fonts.sans,
          fontSize: 22,
          color: 'rgba(250,247,242,0.3)',
          letterSpacing: '0.12em',
          textTransform: 'uppercase',
        }}
      >
        crosswalkwisdom.com
      </div>
    </div>
  );
};
