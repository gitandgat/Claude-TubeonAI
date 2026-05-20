/**
 * Instagram Carousel — 1:1 (1080x1080)
 * Renders all slides of a carousel as a single video,
 * each slide displayed for ~3 seconds with a smooth slide transition.
 *
 * Usage: Pass `carouselId` prop to select which carousel to render.
 * carouselId: 'md-to-crossing-guard' | 'not-your-job-title' | 'nobody-tells-you'
 */
import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate, Easing, Sequence, staticFile } from 'remotion';
import { theme } from '../theme';
import { Logo } from '../components/Logo';
import { PhotoBackground } from '../components/PhotoBackground';
import { AnimatedLines } from '../components/AnimatedLines';

const PHOTO_BACKGROUNDS: Record<string, string> = {
  'md-to-crossing-guard': staticFile('assets/bg-carousel-md-to-crossing-guard.jpg'),
  'not-your-job-title': staticFile('assets/bg-carousel-not-your-job-title.jpg'),
  'nobody-tells-you': staticFile('assets/bg-carousel-nobody-tells-you.jpg'),
  'five-fears-inside-cant-leave': staticFile('assets/bg-carousel-md-to-crossing-guard.jpg'),
  'four-stages-of-stuck': staticFile('assets/bg-carousel-nobody-tells-you.jpg'),
  'sunk-cost-trap': staticFile('assets/post-sunk-cost.jpg'),
};

// ─── Carousel data ─────────────────────────────────────────────────────────────

const carousels: Record<string, { title: string; slides: { heading?: string; lines: string[]; isHook?: boolean; isCta?: boolean; fontSize?: number; stagger?: number }[] }> = {
  'md-to-crossing-guard': {
    title: 'MD to Crossing Guard',
    slides: [
      {
        isHook: true,
        lines: ['Former MD.', 'Yellow vest.', 'Stop sign.', '', 'Here is what happened.'],
      },
      {
        heading: 'The Before',
        lines: [
          'I was a doctor in Thailand.',
          '',
          'I worked 96-hour shifts.',
          'I slept in hospital stairwells.',
          'I watched colleagues collapse',
          'and get told to keep going.',
        ],
      },
      {
        heading: 'The Breaking Point',
        lines: [
          'I went to a psychiatrist.',
          '',
          'He told me there was nothing',
          'he could do.',
          '',
          '"The system is the system."',
          '',
          'That was the day I stopped',
          'looking for permission.',
        ],
      },
      {
        heading: 'The Decision',
        lines: [
          'I left medicine.',
          'I left Thailand.',
          'I moved to Canada with',
          'no plan and no backup.',
          '',
          'People thought I had lost my mind.',
          '',
          'Maybe I had.',
          'But I had already lost everything else.',
        ],
      },
      {
        heading: 'The Yellow Vest',
        lines: [
          'I became a crossing guard.',
          '',
          'No prestige.',
          'No title.',
          'No one calling me "doctor."',
          '',
          'Just a vest, a stop sign,',
          'and children who wave at me',
          'every morning.',
        ],
      },
      {
        heading: 'The Truth',
        lines: [
          'I have never felt more like myself.',
          '',
          'Not because crossing guard',
          'is my calling.',
          '',
          'But because I finally chose',
          'something instead of',
          'surviving something.',
          '',
          'That is the difference.',
        ],
      },
      {
        isCta: true,
        lines: [
          'I wrote 7 reflections for people',
          'rebuilding after leaving.',
          '',
          '7 Crosswalk Reflections for',
          'Recovering Overachievers.',
          '',
          'Free. Link in bio.',
        ],
      },
    ],
  },

  'not-your-job-title': {
    title: 'You Are Not Your Job Title',
    slides: [
      {
        isHook: true,
        lines: ['You are not your job title.', '', '5 signs your identity is', 'fused with your career.'],
      },
      {
        heading: '1',
        lines: [
          'When someone asks "Who are you?"',
          'the first thing out of your mouth',
          'is your job.',
          '',
          'Not your name.',
          'Not what you care about.',
          'Your title.',
          '',
          'Because without it, you do not',
          'know what to say.',
        ],
      },
      {
        heading: '2',
        lines: [
          'The idea of leaving your career',
          'feels like dying.',
          '',
          'Not like changing direction.',
          'Not like a transition.',
          '',
          'Like an actual death.',
          '',
          'That is not dedication.',
          'That is fusion.',
        ],
      },
      {
        heading: '3',
        lines: [
          'You judge your worth',
          'by your productivity.',
          '',
          'Good day at work?',
          'You are a good person.',
          '',
          'Bad day at work?',
          'You are a failure.',
        ],
      },
      {
        heading: '4',
        lines: [
          'You have no idea what you enjoy',
          'outside of work.',
          '',
          'Hobbies feel pointless.',
          'Rest feels lazy.',
          'Free time feels like wasted time.',
          '',
          'You have optimized yourself',
          'out of your own life.',
        ],
      },
      {
        heading: '5',
        lines: [
          'You stay in something painful',
          'because leaving would mean',
          'you are "nothing."',
          '',
          'If that word is the thing',
          'keeping you in a career that',
          'is breaking you —',
          '',
          'you are not committed.',
          'You are trapped.',
        ],
      },
      {
        isCta: true,
        lines: [
          'The Fear Audit helps you',
          'separate the fear of leaving',
          'from the fear of losing yourself.',
          '',
          'Free. 5 minutes.',
          'Link in bio.',
        ],
      },
    ],
  },

  'nobody-tells-you': {
    title: 'Nobody Tells You',
    slides: [
      {
        isHook: true,
        lines: ['5 things nobody tells you', 'about leaving a "good" career.'],
      },
      {
        heading: '1',
        lines: [
          'Grief hits you even when you',
          'know you made the right choice.',
          '',
          'You will mourn the version of',
          'yourself that believed in it.',
          '',
          'That is normal.',
          'It does not mean you made',
          'a mistake.',
        ],
      },
      {
        heading: '2',
        lines: [
          'Some people will take it personally.',
          '',
          'Your decision to leave will feel',
          'like an accusation to those who stayed.',
          '',
          'They will not say that.',
          'But you will feel it.',
        ],
      },
      {
        heading: '3',
        lines: [
          'The first six months are the loneliest.',
          '',
          'You will have more time than you',
          'know what to do with.',
          '',
          'And the silence where the chaos',
          'used to be will feel wrong.',
          '',
          'It is not wrong. It is withdrawal.',
        ],
      },
      {
        heading: '4',
        lines: [
          'You will question everything,',
          'sometimes in the middle of the night.',
          '',
          '"Did I throw it all away?"',
          '"Am I lazy?"',
          '"What if I could have fixed it?"',
          '',
          'These are not signs you were wrong.',
          'They are signs you are human.',
        ],
      },
      {
        heading: '5',
        lines: [
          'It gets quiet before it gets good.',
          '',
          'There is a gap between',
          'leaving and landing.',
          '',
          'Nobody talks about the gap.',
          '',
          'But the gap is where you',
          'finally meet yourself.',
        ],
      },
      {
        isCta: true,
        lines: [
          'If you are in the gap right now —',
          'the Fear Audit was built',
          'for this exact moment.',
          '',
          'Five minutes to get honest',
          'with yourself.',
          '',
          'Free. Link in bio.',
        ],
      },
    ],
  },

  'five-fears-inside-cant-leave': {
    title: 'The 5 Fears',
    slides: [
      {
        isHook: true,
        lines: ['When someone says "I can\'t leave my job"', 'there are always', '5 fears inside that sentence.'],
      },
      {
        heading: 'Fear 1',
        lines: [
          'FINANCIAL FEAR',
          '',
          '"I won\'t be able to pay my bills."',
          '',
          'Feels most logical.',
          'Almost never the real blocker.',
          '',
          'Most people have never run',
          'the actual numbers.',
        ],
      },
      {
        heading: 'Fear 2',
        lines: [
          'IDENTITY FEAR',
          '',
          '"Who am I without this title?"',
          '',
          'The quiet one.',
          'The fear that without the role,',
          'you lose yourself.',
        ],
      },
      {
        heading: 'Fear 3',
        lines: [
          'JUDGMENT FEAR',
          '',
          '"What will people think?"',
          '',
          'We make enormous life decisions',
          'to avoid conversations',
          'with people we barely like.',
        ],
      },
      {
        heading: 'Fear 4',
        lines: [
          'FAILURE FEAR',
          '',
          '"What if I try something new',
          'and it doesn\'t work?"',
          '',
          'Disguised as realism.',
          'Realism would also ask:',
          '"What if it does?"',
        ],
      },
      {
        heading: 'Fear 5',
        lines: [
          'GRIEF FEAR',
          '',
          '"What if leaving means',
          'I wasted everything?"',
          '',
          'Not fear of the future.',
          'Fear of having to mourn the past.',
          '',
          'This kept me in medicine',
          'two extra years.',
        ],
      },
      {
        isCta: true,
        lines: [
          'The Fear Audit separates these five.',
          '',
          'Each one needs',
          'a different conversation.',
          '',
          'Free. 5 minutes. Link in bio.',
        ],
      },
    ],
  },

  'sunk-cost-trap': {
    title: 'The Sunk Cost Trap',
    slides: [
      {
        isHook: true,
        fontSize: 76,
        stagger: 4,
        lines: [
          '80% of IMGs',
          "won't match.",
          '',
          'The system knew.',
          'Nobody told you.',
        ],
      },
      {
        heading: 'The System',
        fontSize: 52,
        lines: [
          'Canadian grads: 97% match.',
          'IMGs: 10–22% match.',
          '',
          'This is not a skill gap.',
          'This is structural.',
          '',
          'You are not failing.',
          'You are playing a rigged game.',
        ],
      },
      {
        heading: 'The 4 Locks',
        fontSize: 52,
        lines: [
          'Financial — $25,000+ spent.',
          'Time — 4 to 7 years of your life.',
          'Identity — "I am a doctor."',
          'Immigration — losing Canada.',
          '',
          'Every layer feels like a reason.',
          '',
          'Every layer is a lock.',
        ],
      },
      {
        heading: 'The Identity',
        fontSize: 52,
        lines: [
          '"But I AM a doctor."',
          '',
          'Your MD is still an asset.',
          'Clinical reasoning. Credibility.',
          '',
          'In 12 non-clinical roles.',
          'That pay well.',
          'That exist in Canada right now.',
        ],
      },
      {
        heading: 'The Reframe',
        fontSize: 52,
        lines: [
          'You think staying protects',
          'the people who sacrificed for you.',
          '',
          'But ask yourself honestly:',
          '',
          'Who is already being let down',
          'every year on the treadmill?',
          '',
          'That person is you.',
        ],
      },
      {
        isCta: true,
        fontSize: 52,
        lines: [
          'Run the real numbers.',
          'Not the hope math.',
          '',
          'Free MCCQE Reality Calculator.',
          'Match rate. Total cost.',
          '',
          'Link in bio.',
        ],
      },
    ],
  },

  'four-stages-of-stuck': {
    title: 'The 4 Stages of Stuck',
    slides: [
      {
        isHook: true,
        lines: ['Not everyone who\'s stuck', 'looks the same.', '', '4 stages. Which one are you?'],
      },
      {
        heading: 'Stage 1: START',
        lines: [
          'You know something is wrong',
          'but can\'t name it yet.',
          '',
          'Fear feels like background noise.',
          'You keep saying "I just need',
          'to push through."',
          '',
          'Next step: name the vague thing.',
        ],
      },
      {
        heading: 'Stage 2: STOP',
        lines: [
          'You know exactly what\'s wrong.',
          'You\'ve thought about leaving',
          'until it\'s its own exhausting thing.',
          '',
          'But you can\'t move.',
          '',
          'Next step: find what\'s holding',
          'the door closed.',
        ],
      },
      {
        heading: 'Stage 3: ELDER',
        lines: [
          'You\'ve been here a long time.',
          'Fear has become habit.',
          '',
          'It doesn\'t feel like fear anymore.',
          'It just feels like "how work is."',
          '',
          'Next step: notice what you\'ve',
          'stopped noticing.',
        ],
      },
      {
        heading: 'Stage 4: HUMAN',
        lines: [
          'Something broke recently.',
          'A moment. A loss. A conversation.',
          '',
          'You\'re not asking "should I leave?"',
          'You\'re asking "how?"',
          '',
          'Next step: momentum,',
          'not permission.',
        ],
      },
      {
        lines: [
          'Every stage has a path forward.',
          '',
          'The Fear Audit meets you',
          'where you are —',
          'not where you think',
          'you should be.',
        ],
      },
      {
        isCta: true,
        lines: [
          'Take the Fear Audit free.',
          '5 minutes.',
          'Find out your stage.',
          '',
          'Link in bio.',
        ],
      },
    ],
  },
};

// ─── Single slide component ─────────────────────────────────────────────────────

const SLIDE_DURATION = 90; // 3 seconds at 30fps
const TRANSITION_FRAMES = 15;

const Slide: React.FC<{
  slide: (typeof carousels)[string]['slides'][number];
  index: number;
  total: number;
}> = ({ slide, index, total }) => {
  const isHook = slide.isHook;
  const isCta = slide.isCta;

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: isHook ? 'center' : 'flex-start',
        padding: isHook ? 80 : 70,
        paddingTop: isHook ? 80 : 110,
      }}
    >
      {/* Slide number badge (not on hook/cta) */}
      {!isHook && !isCta && (
        <div
          style={{
            position: 'absolute',
            top: 60,
            right: 70,
            width: 56,
            height: 56,
            borderRadius: '50%',
            backgroundColor: theme.colors.amber,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontFamily: theme.fonts.serif,
            fontSize: 22,
            fontWeight: 700,
            color: theme.colors.charcoal,
          }}
        >
          {index}
        </div>
      )}

      {/* Heading */}
      {slide.heading && !['1', '2', '3', '4', '5'].includes(slide.heading) && (
        <div
          style={{
            fontFamily: theme.fonts.serif,
            fontSize: 28,
            color: theme.colors.amber,
            fontWeight: 600,
            marginBottom: 24,
            letterSpacing: '0.05em',
            textTransform: 'uppercase',
          }}
        >
          {slide.heading}
        </div>
      )}

      {/* Content */}
      <AnimatedLines
        lines={slide.lines}
        startFrame={8}
        staggerFrames={slide.stagger ?? (isHook ? 10 : 7)}
        fontSize={slide.fontSize ?? (isHook ? 64 : isCta ? 46 : 42)}
        color={isHook ? theme.colors.warmWhite : isCta ? theme.colors.amber : theme.colors.warmWhite}
        fontFamily={isHook ? theme.fonts.serif : theme.fonts.sans}
        fontWeight={isHook ? 700 : 400}
        lineHeight={1.35}
      />

      {/* Progress dots */}
      <div
        style={{
          position: 'absolute',
          bottom: 50,
          left: 0,
          right: 0,
          display: 'flex',
          justifyContent: 'center',
          gap: 8,
        }}
      >
        {Array.from({ length: total }).map((_, i) => (
          <div
            key={i}
            style={{
              width: i === index ? 24 : 8,
              height: 8,
              borderRadius: 4,
              backgroundColor: i === index ? theme.colors.amber : 'rgba(212,168,67,0.3)',
              transition: 'all 0.3s',
            }}
          />
        ))}
      </div>
    </div>
  );
};

// ─── Main composition ───────────────────────────────────────────────────────────

export const InstagramCarousel: React.FC<{ carouselId?: string }> = ({
  carouselId = 'md-to-crossing-guard',
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const carousel = carousels[carouselId] ?? carousels['md-to-crossing-guard'];
  const slides = carousel.slides;
  const totalSlides = slides.length;

  const currentSlide = Math.floor(frame / SLIDE_DURATION);
  const slideFrame = frame % SLIDE_DURATION;

  const slideProgress = interpolate(slideFrame, [0, TRANSITION_FRAMES], [0, 1], {
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

  const translateX = interpolate(slideProgress, [0, 1], [40, 0]);
  const opacity = interpolate(slideProgress, [0, 1], [0, 1]);

  return (
    <div
      style={{
        width: 1080,
        height: 1080,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <PhotoBackground
        src={PHOTO_BACKGROUNDS[carouselId] ?? PHOTO_BACKGROUNDS['md-to-crossing-guard']}
        overlayOpacity={0.52}
        parallax
      />

      {/* Logo */}
      <div style={{ position: 'absolute', top: 50, left: 70, zIndex: 10 }}>
        <Logo size={28} color={theme.colors.amber} />
      </div>

      {/* Slide content */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          opacity,
          transform: `translateX(${translateX}px)`,
        }}
      >
        {slides[Math.min(currentSlide, totalSlides - 1)] && (
          <Slide
            slide={slides[Math.min(currentSlide, totalSlides - 1)]}
            index={Math.min(currentSlide, totalSlides - 1)}
            total={totalSlides}
          />
        )}
      </div>
    </div>
  );
};
