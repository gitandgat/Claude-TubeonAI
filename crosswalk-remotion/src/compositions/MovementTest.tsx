import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
} from 'remotion';
import { MovementFigure } from '../components/MovementFigure';

/**
 * MovementTest — a vertical (1080×1920) demo of one check from the
 * 60-Second Movement Self-Test. Deterministic kinetic text over the case's
 * porcelain render — no voiceover/whisper dependency. MoveAssess clinical
 * brand (sage/beige, serif display). Data-driven: one composition per test
 * via defaultProps `slug`.
 */

// ── MoveAssess clinical brand ────────────────────────────────────────────────
const SURFACE = '#faf7f2';
const SURFACE_1 = '#f3eee5';
const SAGE_400 = '#8ea085';
const SAGE_500 = '#6f8768';
const SAGE_600 = '#57694f';
const SAGE_700 = '#435442';
const TERRA = '#c2503d';
const INK = '#232b24';
const INK_SOFT = '#4a544b';
const WARM = '#faf7f2';

const SERIF = 'Georgia, "Times New Roman", serif';
const SANS = '"IBM Plex Sans", system-ui, -apple-system, Arial, sans-serif';

// ── Content ──────────────────────────────────────────────────────────────────
export interface MovementTestData {
  slug: string;
  numeral: string;
  region: string;
  name: string;
  image: string; // staticFile path
  steps: string[];
  tell: string;
  means: string;
  handle: string;
}

export const MOVEMENT_TESTS: Record<string, MovementTestData> = {
  'single-leg': {
    slug: 'single-leg',
    numeral: '03',
    region: 'Hips & pelvis',
    name: 'The Single-Leg Stand',
    image: 'assets/moveassess/right-hip-drop-left-shoulder.jpg',
    steps: ['Stand on one leg', 'Hold for ten seconds', 'Watch the lifted hip'],
    tell: 'The hip on the lifted side drops — or your torso lurches to stay upright.',
    means:
      'The standing-leg glute has gone quiet, so the pelvis can’t stay level. This is the leak behind low-back ache, IT-band pain, and a gait that reads “getting old” long before it has to.',
    handle: 'physical-assessment-app.vercel.app',
  },
  'chair-rise': {
    slug: 'chair-rise',
    numeral: '07',
    region: 'Hips & core',
    name: 'The Chair Rise',
    image: 'assets/moveassess/flat-back-posture.jpg',
    steps: [
      'Sit in a normal chair',
      'Stand up without your hands',
      'No rocking for momentum',
    ],
    tell: 'You need your hands, a rock forward, or a push off the thighs to get up.',
    means:
      'The glutes and core aren’t producing the power, so momentum stands in. Rising from a chair unaided is one of the strongest known predictors of staying independent into your seventies.',
    handle: 'physical-assessment-app.vercel.app',
  },
  'knee-cave': {
    slug: 'knee-cave',
    numeral: '02',
    region: 'Knees',
    name: 'The Overhead Squat',
    image: 'assets/moveassess/patellofemoral-pain.jpg',
    steps: ['Arms straight overhead', 'Squat, watching your knees', 'In a mirror'],
    tell: 'One or both knees drift inward, tracking inside the line of your big toe.',
    means:
      'The knee is only doing what it’s told. It caves because the hip above it isn’t steering the leg. This is the most common driver of the knee pain that ends running and hiking in the fifties.',
    handle: 'physical-assessment-app.vercel.app',
  },
  'forward-head': {
    slug: 'forward-head',
    numeral: '01',
    region: 'Neck & upper back',
    name: 'The Wall Head Test',
    image: 'assets/moveassess/forward-head-posture.jpg',
    steps: ['Back to a wall', 'Heels, hips, shoulders touching', 'Touch your head back, chin level'],
    tell: 'Your head won’t reach the wall without craning your chin toward the ceiling.',
    means:
      'Your head has drifted forward of your spine, and every inch multiplies the load your neck carries all day. That’s the stiff neck, and the headaches that follow it.',
    handle: 'physical-assessment-app.vercel.app',
  },
  hamstrings: {
    slug: 'hamstrings',
    numeral: '04',
    region: 'Low back & pelvis',
    name: 'The Belt-Line Check',
    image: 'assets/moveassess/apt-tight-hamstrings.jpg',
    steps: ['Stand sideways to a mirror', 'Relax', 'Look at your belt line'],
    tell: 'The front of your belt line tips down and forward, with a hard arch in your low back.',
    means:
      'Your pelvis is tilted forward, holding your hamstrings long all day so they feel tight. Stretch them and you pull on the victim, not the cause.',
    handle: 'physical-assessment-app.vercel.app',
  },
  arch: {
    slug: 'arch',
    numeral: '05',
    region: 'Feet & ankles',
    name: 'The Arch Test',
    image: 'assets/moveassess/pes-planus.jpg',
    steps: ['Stand barefoot', 'Feet under your hips', 'Look down at your arches'],
    tell: 'Your arches sink toward the floor and your ankles roll inward.',
    means:
      'Your base is collapsing. The shin turns to follow it, the knee gets pulled in, and the low back settles the tab at the top.',
    handle: 'physical-assessment-app.vercel.app',
  },
  'wall-reach': {
    slug: 'wall-reach',
    numeral: '06',
    region: 'Shoulders',
    name: 'The Wall Reach',
    image: 'assets/moveassess/upper-crossed.jpg',
    steps: ['Back to a wall, low back flat', 'Raise both arms overhead', 'Reach the wall, back flat'],
    tell: 'Your hands won’t reach the wall, or your low back peels off to let them through.',
    means:
      'Your shoulders can’t get cleanly overhead, so your spine arches to finish the reach. Every overhead move borrows from your lower back.',
    handle: 'physical-assessment-app.vercel.app',
  },
};

// ── Scene timing (30fps) ─────────────────────────────────────────────────────
const INTRO = 66; // 2.2s
const SHOT = 252; // 8.4s — image runs under steps + tell
const STEP = 50; // per step
const TELL_IN = 3 * STEP; // shot-relative: tell appears after the 3 steps
const MEANS = 96; // 3.2s
const CTA = 78; // 2.6s
export const MOVEMENT_TEST_FRAMES = INTRO + SHOT + MEANS + CTA; // 492

// ── Small helpers ────────────────────────────────────────────────────────────
const Kicker: React.FC<{ text: string; color?: string }> = ({ text, color = SAGE_600 }) => (
  <div
    style={{
      fontFamily: SANS,
      fontSize: 26,
      fontWeight: 600,
      letterSpacing: 6,
      textTransform: 'uppercase',
      color,
    }}
  >
    {text}
  </div>
);

const useEnter = (delay: number) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - delay, fps, config: { damping: 200 }, durationInFrames: 22 });
  const opacity = interpolate(s, [0, 1], [0, 1]);
  const ty = interpolate(s, [0, 1], [26, 0]);
  return { opacity, transform: `translateY(${ty}px)` };
};

// ── Scenes ───────────────────────────────────────────────────────────────────
const IntroCard: React.FC<{ t: MovementTestData }> = ({ t }) => {
  const frame = useCurrentFrame();
  const out = interpolate(frame, [INTRO - 12, INTRO], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const kick = useEnter(2);
  const name = useEnter(8);
  const meta = useEnter(16);
  return (
    <AbsoluteFill
      style={{
        backgroundColor: SURFACE,
        justifyContent: 'center',
        alignItems: 'flex-start',
        padding: '0 96px',
        opacity: out,
      }}
    >
      <div style={kick}>
        <Kicker text="Free · 60-second self-test" />
      </div>
      <div style={{ ...name, marginTop: 26 }}>
        <div style={{ fontFamily: SERIF, fontSize: 92, fontWeight: 600, color: INK, lineHeight: 1.02 }}>
          {t.name}
        </div>
      </div>
      <div style={{ ...meta, marginTop: 34, display: 'flex', alignItems: 'center', gap: 20 }}>
        <div style={{ width: 64, height: 2, backgroundColor: SAGE_500 }} />
        <div style={{ fontFamily: SANS, fontSize: 28, color: SAGE_600, letterSpacing: 2 }}>
          Check {t.numeral} · {t.region}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// The demonstration stage: a clean clinical backdrop with the rigged figure
// actually performing the test in the upper two-thirds, captions below.
const MovementStage: React.FC<{ slug: string }> = ({ slug }) => (
  <AbsoluteFill style={{ backgroundColor: SURFACE }}>
    {/* soft atmosphere: a warm top light and a grounded base */}
    <AbsoluteFill
      style={{
        background:
          'radial-gradient(120% 70% at 50% 30%, #fdfbf7 0%, rgba(243,238,229,0) 60%), linear-gradient(180deg, rgba(243,238,229,0) 62%, rgba(226,220,205,0.9) 100%)',
      }}
    />
    {/* figure occupies the top ~62% so step/tell captions have clear space below */}
    <div style={{ position: 'absolute', top: 40, left: 0, right: 0, height: 1190 }}>
      <MovementFigure slug={slug} shotFrames={SHOT} />
    </div>
    {/* legibility scrim at the very base, under the captions only */}
    <AbsoluteFill
      style={{
        background:
          'linear-gradient(180deg, rgba(30,37,31,0) 68%, rgba(30,37,31,0.14) 100%)',
      }}
    />
  </AbsoluteFill>
);

// Shot-relative: one step at a time, each bottom-anchored over the dark scrim.
// (Each <Sequence> is its own full-screen layer, so anchoring must live inside
// the StepLine, not on a shared flex parent.)
const StepOverlay: React.FC<{ steps: string[] }> = ({ steps }) => (
  <>
    {steps.map((s, i) => (
      <Sequence key={i} from={i * STEP} durationInFrames={STEP}>
        <StepLine index={i} text={s} total={steps.length} />
      </Sequence>
    ))}
  </>
);

const StepLine: React.FC<{ index: number; text: string; total: number }> = ({ index, text, total }) => {
  const enter = useEnter(0);
  return (
    <AbsoluteFill style={{ justifyContent: 'flex-end', alignItems: 'flex-start', padding: '0 72px 200px' }}>
      <div
        style={{
          ...enter,
          background: 'rgba(22,28,23,0.85)',
          borderRadius: 18,
          padding: '22px 30px',
          maxWidth: 900,
        }}
      >
        <div
          style={{
            fontFamily: SANS,
            fontSize: 24,
            fontWeight: 700,
            letterSpacing: 4,
            textTransform: 'uppercase',
            color: '#dfe6da',
            marginBottom: 10,
            textShadow: '0 2px 14px rgba(20,26,20,0.7)',
          }}
        >
          Step {index + 1} / {total}
        </div>
        <div
          style={{
            fontFamily: SERIF,
            fontSize: 72,
            fontWeight: 600,
            color: WARM,
            lineHeight: 1.05,
            textShadow: '0 2px 20px rgba(20,26,20,0.75)',
          }}
        >
          {text}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const TellOverlay: React.FC<{ tell: string }> = ({ tell }) => {
  const frame = useCurrentFrame();
  // Fades in over the darkening bottom of the shot, after the steps.
  const start = TELL_IN;
  const op = interpolate(frame, [start, start + 16], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const ty = interpolate(frame, [start, start + 20], [24, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  if (frame < start) return null;
  return (
    <AbsoluteFill style={{ justifyContent: 'flex-end', alignItems: 'flex-start', padding: '0 72px 180px' }}>
      <div
        style={{
          opacity: op,
          transform: `translateY(${ty}px)`,
          background: 'rgba(22,28,23,0.82)',
          borderRadius: 18,
          padding: '24px 32px',
          maxWidth: 940,
        }}
      >
        <div
          style={{
            fontFamily: SANS,
            fontSize: 26,
            fontWeight: 700,
            letterSpacing: 6,
            textTransform: 'uppercase',
            color: TERRA,
            marginBottom: 14,
          }}
        >
          The tell
        </div>
        <div
          style={{
            fontFamily: SERIF,
            fontSize: 62,
            fontWeight: 600,
            color: WARM,
            lineHeight: 1.12,
            textShadow: '0 2px 20px rgba(20,26,20,0.75)',
          }}
        >
          {tell}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const MeansCard: React.FC<{ t: MovementTestData }> = ({ t }) => {
  const frame = useCurrentFrame();
  const inOp = interpolate(frame, [0, 14], [0, 1], { extrapolateRight: 'clamp' });
  const out = interpolate(frame, [MEANS - 12, MEANS], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return (
    <AbsoluteFill
      style={{
        backgroundColor: SAGE_700,
        justifyContent: 'center',
        alignItems: 'flex-start',
        padding: '0 96px',
        opacity: inOp * out,
      }}
    >
      <Kicker text="What it means" color={SAGE_400} />
      <div
        style={{
          fontFamily: SERIF,
          fontSize: 56,
          fontWeight: 600,
          color: WARM,
          lineHeight: 1.22,
          marginTop: 28,
        }}
      >
        {t.means}
      </div>
    </AbsoluteFill>
  );
};

const CtaCard: React.FC<{ t: MovementTestData }> = ({ t }) => {
  const frame = useCurrentFrame();
  const inOp = interpolate(frame, [0, 14], [0, 1], { extrapolateRight: 'clamp' });
  const line = interpolate(frame, [8, 30], [0, 1], { extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill
      style={{
        backgroundColor: SURFACE,
        justifyContent: 'center',
        alignItems: 'flex-start',
        padding: '0 96px',
        opacity: inOp,
      }}
    >
      <Kicker text="The next 60 seconds" />
      <div
        style={{
          fontFamily: SERIF,
          fontSize: 78,
          fontWeight: 600,
          color: INK,
          lineHeight: 1.06,
          marginTop: 26,
        }}
      >
        See your exact
        <br />
        pattern in 3D.
      </div>
      <div style={{ width: 520 * line, height: 3, backgroundColor: TERRA, margin: '34px 0' }} />
      <div style={{ fontFamily: SANS, fontSize: 34, color: INK_SOFT }}>Free · no equipment</div>
      <div style={{ fontFamily: SANS, fontSize: 30, fontWeight: 600, color: SAGE_600, marginTop: 14 }}>
        {t.handle}
      </div>
      <div
        style={{
          position: 'absolute',
          bottom: 90,
          left: 96,
          fontFamily: SANS,
          fontSize: 24,
          letterSpacing: 4,
          textTransform: 'uppercase',
          color: SAGE_400,
        }}
      >
        MoveAssess · Crosswalk Wisdom
      </div>
    </AbsoluteFill>
  );
};

// ── Composition ──────────────────────────────────────────────────────────────
export const MovementTest: React.FC<{ slug?: string }> = ({ slug = 'single-leg' }) => {
  const t = MOVEMENT_TESTS[slug] ?? MOVEMENT_TESTS['single-leg'];
  return (
    <AbsoluteFill style={{ backgroundColor: SURFACE }}>
      {/* onyx narration (Sahawat's register) + a very soft bed under it */}
      <Audio src={staticFile(`moveassess-vo-${t.slug}.wav`)} volume={1} />
      <Audio src={staticFile('music.mp3')} volume={0.045} loop />
      <Sequence durationInFrames={INTRO}>
        <IntroCard t={t} />
      </Sequence>

      {/* One shot: image + step + tell overlays share a shot-relative clock,
          so everything clips cleanly to the SHOT window. */}
      <Sequence from={INTRO} durationInFrames={SHOT}>
        <MovementStage slug={t.slug} />
        <StepOverlay steps={t.steps} />
        <TellOverlay tell={t.tell} />
      </Sequence>

      <Sequence from={INTRO + SHOT} durationInFrames={MEANS}>
        <MeansCard t={t} />
      </Sequence>

      <Sequence from={INTRO + SHOT + MEANS} durationInFrames={CTA}>
        <CtaCard t={t} />
      </Sequence>
    </AbsoluteFill>
  );
};

// ── Hub reel (cod-08): the whole 60-second self-test in one video ────────────
const HUB_INTRO = 72;
const HUB_ITEM = 34;
const HUB_LIST = HUB_ITEM * 7; // 238
const HUB_CTA = 100;
export const MOVEMENT_HUB_FRAMES = HUB_INTRO + HUB_LIST + HUB_CTA; // 410

const HubIntro: React.FC = () => {
  const frame = useCurrentFrame();
  const out = interpolate(frame, [HUB_INTRO - 12, HUB_INTRO], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const k = useEnter(2);
  const h = useEnter(8);
  const s = useEnter(18);
  return (
    <AbsoluteFill
      style={{ backgroundColor: SURFACE, justifyContent: 'center', alignItems: 'flex-start', padding: '0 96px', opacity: out }}
    >
      <div style={k}>
        <Kicker text="The 60-second self-test" />
      </div>
      <div style={{ ...h, marginTop: 26 }}>
        <div style={{ fontFamily: SERIF, fontSize: 96, fontWeight: 600, color: INK, lineHeight: 1.0 }}>
          Give me
          <br />
          60 seconds.
        </div>
      </div>
      <div style={{ ...s, marginTop: 30, fontFamily: SANS, fontSize: 36, color: SAGE_600 }}>
        A wall. A chair. A mirror.
      </div>
    </AbsoluteFill>
  );
};

const HubItem: React.FC<{ t: MovementTestData; idx: number }> = ({ t, idx }) => {
  const enter = useEnter(0);
  const dark = idx % 2 === 1;
  return (
    <AbsoluteFill
      style={{
        backgroundColor: dark ? SAGE_700 : SURFACE,
        justifyContent: 'center',
        alignItems: 'flex-start',
        padding: '0 96px',
      }}
    >
      <div style={enter}>
        <div style={{ fontFamily: SERIF, fontSize: 150, fontWeight: 600, color: dark ? SAGE_400 : SAGE_500, lineHeight: 0.9 }}>
          {t.numeral}
        </div>
        <div
          style={{
            fontFamily: SANS,
            fontSize: 24,
            fontWeight: 700,
            letterSpacing: 4,
            textTransform: 'uppercase',
            color: dark ? '#c6d0c0' : SAGE_600,
            margin: '24px 0 10px',
          }}
        >
          {t.region}
        </div>
        <div style={{ fontFamily: SERIF, fontSize: 68, fontWeight: 600, color: dark ? WARM : INK, lineHeight: 1.05 }}>
          {t.name}
        </div>
      </div>
      {/* the test's figure, frozen at its tell pose, as a recap thumbnail —
          kept in a narrow right column so it clears even the longest title */}
      <div style={{ position: 'absolute', left: 762, top: 540, width: 296, height: 900, opacity: 0.97 }}>
        <MovementFigure slug={t.slug} fixedProgress={0.92} showLabel={false} />
      </div>
    </AbsoluteFill>
  );
};

const HubCta: React.FC = () => {
  const frame = useCurrentFrame();
  const inOp = interpolate(frame, [0, 14], [0, 1], { extrapolateRight: 'clamp' });
  const line = interpolate(frame, [10, 34], [0, 1], { extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ backgroundColor: SURFACE, justifyContent: 'center', alignItems: 'flex-start', padding: '0 96px', opacity: inOp }}>
      <Kicker text="Reading your score" />
      <div style={{ fontFamily: SERIF, fontSize: 76, fontWeight: 600, color: INK, lineHeight: 1.08, marginTop: 26 }}>
        Three or more tells,
        <br />
        you’re carrying
        <br />
        movement debt.
      </div>
      <div style={{ width: 520 * line, height: 3, backgroundColor: TERRA, margin: '34px 0' }} />
      <div style={{ fontFamily: SANS, fontSize: 34, color: INK_SOFT }}>Take all seven, free</div>
      <div style={{ fontFamily: SANS, fontSize: 30, fontWeight: 600, color: SAGE_600, marginTop: 14 }}>
        physical-assessment-app.vercel.app/self-test
      </div>
      <div
        style={{
          position: 'absolute',
          bottom: 90,
          left: 96,
          fontFamily: SANS,
          fontSize: 24,
          letterSpacing: 4,
          textTransform: 'uppercase',
          color: SAGE_400,
        }}
      >
        MoveAssess · Crosswalk Wisdom
      </div>
    </AbsoluteFill>
  );
};

export const MovementHub: React.FC = () => {
  const tests = Object.values(MOVEMENT_TESTS).sort((a, b) => a.numeral.localeCompare(b.numeral));
  return (
    <AbsoluteFill style={{ backgroundColor: SURFACE }}>
      {/* onyx narration + soft bed */}
      <Audio src={staticFile('moveassess-vo-hub.wav')} volume={1} />
      <Audio src={staticFile('music.mp3')} volume={0.045} loop />
      <Sequence durationInFrames={HUB_INTRO}>
        <HubIntro />
      </Sequence>
      <Sequence from={HUB_INTRO} durationInFrames={HUB_LIST}>
        {tests.map((t, i) => (
          <Sequence key={t.slug} from={i * HUB_ITEM} durationInFrames={HUB_ITEM}>
            <HubItem t={t} idx={i} />
          </Sequence>
        ))}
      </Sequence>
      <Sequence from={HUB_INTRO + HUB_LIST} durationInFrames={HUB_CTA}>
        <HubCta />
      </Sequence>
    </AbsoluteFill>
  );
};
