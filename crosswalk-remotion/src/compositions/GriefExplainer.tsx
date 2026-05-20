/**
 * "Why Leaving Healthcare Feels Like Grief" — Educational Explainer
 * Format: 1080×1920 (vertical/TikTok), 30fps, 30s = 900 frames
 * Brand: Crosswalk Wisdom by Sahawat
 * 5 scenes × 180 frames each
 *
 * LAYOUT: Safe zone top=150px, bottom=170px, sides=60px.
 * Usable height = 1600px. Every scene uses justifyContent: 'space-between'
 * to fill the full 1600px.
 */
import React from 'react';
import {
  useCurrentFrame,
  interpolate,
  spring,
  useVideoConfig,
  Sequence,
  Audio,
  staticFile,
} from 'remotion';

// ─── Constants ──────────────────────────────────────────────────────────────────
const BG = '#0a0a0a';
const INDIGO = '#6366f1';
const GREEN = '#22c55e';
const WHITE = '#ffffff';
const DIM = 'rgba(255,255,255,0.5)';
const AMBER = '#D4A843';
const FONT = '"Inter", system-ui, sans-serif';

const SCENE_FRAMES = 180;
const FADE = 12;
const TOTAL = 900;
const TOP_SAFE = 150;
const BOT_SAFE = 170;
const SIDE = 60;

// ─── Helpers ────────────────────────────────────────────────────────────────────
const sp = (frame: number, fps: number, delay = 0) =>
  spring({ frame: frame - delay, fps, config: { damping: 200 } });

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));

const fadeInOut = (localFrame: number, dur: number) => {
  const fadeIn = interpolate(localFrame, [0, FADE], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const fadeOut = interpolate(localFrame, [dur - FADE, dur], [1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  return fadeIn * fadeOut;
};

// ─── Scene 1: "It feels like a death" ───────────────────────────────────────────
const Scene1: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  const line1Scale = sp(frame, fps, 5);
  const line2Scale = sp(frame, fps, 20);

  const brainProgress = interpolate(frame, [35, 110], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const dot1Scale = sp(frame, fps, 55);
  const dot2Scale = sp(frame, fps, 65);
  const label1Scale = sp(frame, fps, 70);
  const label2Scale = sp(frame, fps, 80);
  const equalsScale = sp(frame, fps, 90);
  const body1Scale = sp(frame, fps, 100);
  const body2Scale = sp(frame, fps, 110);

  // Brain SVG — larger path for 400×280 viewBox
  const brainPath =
    'M60,140 C40,130 20,110 18,85 C16,60 35,40 60,46 C65,30 85,20 105,32 C115,18 135,14 150,28 C170,14 195,20 200,42 C215,36 234,52 232,76 C230,100 208,120 185,130 C175,148 155,160 130,158 C105,162 80,155 60,140 Z';
  const brainPathLength = 780;
  const dashOffset = interpolate(brainProgress, [0, 1], [brainPathLength, 0]);

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        opacity,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingTop: TOP_SAFE,
        paddingBottom: BOT_SAFE,
        paddingLeft: SIDE,
        paddingRight: SIDE,
        fontFamily: FONT,
      }}
    >
      {/* TOP BLOCK */}
      <div style={{ textAlign: 'center' }}>
        <div
          style={{
            fontSize: 80,
            color: WHITE,
            fontWeight: 600,
            lineHeight: 1.2,
            opacity: clamp01(line1Scale),
            transform: `scale(${line1Scale})`,
            transformOrigin: 'center',
          }}
        >
          It feels like
        </div>
        <div
          style={{
            fontSize: 96,
            color: INDIGO,
            fontWeight: 800,
            lineHeight: 1.2,
            opacity: clamp01(line2Scale),
            transform: `scale(${line2Scale})`,
            transformOrigin: 'center',
          }}
        >
          a death.
        </div>
      </div>

      {/* MIDDLE BLOCK — Brain SVG + labels + equals */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        {/* Brain container with float labels */}
        <div style={{ position: 'relative', width: 400, height: 280 }}>
          <svg
            viewBox="0 0 400 280"
            width={400}
            height={280}
            style={{ overflow: 'visible' }}
          >
            {/* Brain outline draws itself */}
            <path
              d={brainPath}
              fill="none"
              stroke={INDIGO}
              strokeWidth={3}
              strokeDasharray={brainPathLength}
              strokeDashoffset={dashOffset}
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            {/* Dot 1: Bereavement region ~(120,150) */}
            <circle
              cx={120}
              cy={150}
              r={10}
              fill={INDIGO}
              opacity={clamp01(dot1Scale)}
              transform={`scale(${Math.max(0, dot1Scale)})`}
              style={{ transformOrigin: '120px 150px' }}
            />
            {/* Dot 2: Career Loss region ~(280,130) */}
            <circle
              cx={280}
              cy={130}
              r={10}
              fill={GREEN}
              opacity={clamp01(dot2Scale)}
              transform={`scale(${Math.max(0, dot2Scale)})`}
              style={{ transformOrigin: '280px 130px' }}
            />
          </svg>

          {/* Label: Bereavement — left of dot 1 */}
          <div
            style={{
              position: 'absolute',
              left: -10,
              top: 155,
              fontSize: 36,
              color: DIM,
              fontWeight: 500,
              opacity: clamp01(label1Scale),
              transform: `translateY(${interpolate(label1Scale, [0, 1], [8, 0])}px)`,
              whiteSpace: 'nowrap',
            }}
          >
            Bereavement
          </div>

          {/* Label: Career Loss — right of dot 2 */}
          <div
            style={{
              position: 'absolute',
              right: -10,
              top: 136,
              fontSize: 36,
              color: DIM,
              fontWeight: 500,
              opacity: clamp01(label2Scale),
              transform: `translateY(${interpolate(label2Scale, [0, 1], [8, 0])}px)`,
              whiteSpace: 'nowrap',
              textAlign: 'right',
            }}
          >
            Career Loss
          </div>
        </div>

        {/* Equals sign */}
        <div
          style={{
            fontSize: 80,
            color: GREEN,
            fontWeight: 800,
            textAlign: 'center',
            opacity: clamp01(equalsScale),
            transform: `scale(${equalsScale})`,
            transformOrigin: 'center',
            marginTop: 16,
          }}
        >
          =
        </div>
      </div>

      {/* BOTTOM BLOCK */}
      <div style={{ textAlign: 'center', maxWidth: 940 }}>
        <div
          style={{
            fontSize: 48,
            color: WHITE,
            fontWeight: 600,
            lineHeight: 1.4,
            marginBottom: 16,
            opacity: clamp01(body1Scale),
            transform: `translateY(${interpolate(body1Scale, [0, 1], [12, 0])}px)`,
          }}
        >
          Neuroscience confirms it:
        </div>
        <div
          style={{
            fontSize: 44,
            color: DIM,
            fontWeight: 400,
            lineHeight: 1.5,
            opacity: clamp01(body2Scale),
            transform: `translateY(${interpolate(body2Scale, [0, 1], [12, 0])}px)`,
          }}
        >
          Leaving a career activates the same brain regions as losing a loved one.
        </div>
      </div>
    </div>
  );
};

// ─── Scene 2: "The 5 Stages Hit Different Here" ─────────────────────────────────
const Scene2: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  const title1Scale = sp(frame, fps, 5);
  const title2Scale = sp(frame, fps, 15);

  const lineProgress = interpolate(frame, [10, 60], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  // Line from y=60 to y=860 = 800px
  const timelineHeight = 800;
  const lineDash = timelineHeight;
  const lineOffset = interpolate(lineProgress, [0, 1], [lineDash, 0]);

  const stages = [
    { label: 'Denial',     color: WHITE,  quote: '"I\'m just tired."',           delay: 40 },
    { label: 'Anger',      color: AMBER,  quote: '"The system failed me."',       delay: 60 },
    { label: 'Bargaining', color: GREEN,  quote: '"Maybe one more year."',        delay: 80 },
    { label: 'Depression', color: INDIGO, quote: '"I don\'t know who I am."',     delay: 100 },
    { label: 'Acceptance', color: WHITE,  quote: '"I can choose something new."', delay: 120, quoteColor: GREEN, bold: true },
  ];

  const nodeScales = stages.map((s) => sp(frame, fps, s.delay));

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        opacity,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingTop: TOP_SAFE,
        paddingBottom: BOT_SAFE,
        paddingLeft: SIDE,
        paddingRight: SIDE,
        fontFamily: FONT,
      }}
    >
      {/* TOP BLOCK */}
      <div style={{ textAlign: 'center' }}>
        <span
          style={{
            fontSize: 72,
            color: WHITE,
            fontWeight: 700,
            display: 'inline',
            opacity: clamp01(title1Scale),
          }}
        >
          The 5 stages hit{' '}
        </span>
        <span
          style={{
            fontSize: 72,
            color: INDIGO,
            fontWeight: 700,
            display: 'inline',
            opacity: clamp01(title2Scale),
          }}
        >
          different here.
        </span>
      </div>

      {/* MIDDLE BLOCK — Timeline SVG fills the space */}
      <svg
        viewBox="0 0 960 880"
        width={960}
        height={880}
        style={{ overflow: 'visible' }}
      >
        {/* Vertical center line y=60 to y=860 */}
        <line
          x1={480}
          y1={60}
          x2={480}
          y2={860}
          stroke={INDIGO}
          strokeWidth={2}
          strokeDasharray={lineDash}
          strokeDashoffset={lineOffset}
        />

        {stages.map((stage, i) => {
          // Evenly spaced: y = 100, 260, 420, 580, 740
          const cy = 100 + i * 160;
          const s = nodeScales[i];
          const nodeOpacity = clamp01(s);
          const offsetY = interpolate(s, [0, 1], [14, 0]);

          return (
            <g key={stage.label} opacity={nodeOpacity} transform={`translate(0, ${offsetY})`}>
              {/* Node circle */}
              <circle cx={480} cy={cy} r={14} fill={stage.color} />

              {/* Stage name — LEFT side, right-aligned at x=455 */}
              <text
                x={455}
                y={cy + 6}
                textAnchor="end"
                fontSize={42}
                fontWeight={stage.bold ? 700 : 700}
                fill={stage.color}
                fontFamily={FONT}
              >
                {stage.label}
              </text>

              {/* Quote — RIGHT side, left-aligned at x=510 */}
              <text
                x={510}
                y={cy + 6}
                textAnchor="start"
                fontSize={34}
                fontStyle="italic"
                fill={stage.quoteColor ?? DIM}
                fontFamily={FONT}
              >
                {stage.quote}
              </text>
            </g>
          );
        })}
      </svg>

      {/* BOTTOM SPACER — SVG fills the space above */}
      <div style={{ height: 1 }} />
    </div>
  );
};

// ─── Scene 3: "Identity Loss — The Hidden Wound" ────────────────────────────────
const Scene3: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  const titleScale = sp(frame, fps, 5);
  const subtitleScale = sp(frame, fps, 15);

  // Badge outline draws itself — perimeter of 420×260 rounded rect rx=20 ≈ 1320
  const badgePerimeter = 1320;
  const badgeProgress = interpolate(frame, [25, 60], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const badgeDash = interpolate(badgeProgress, [0, 1], [badgePerimeter, 0]);

  // Erasing name text
  const fullName = 'Dr. Your Name, MD';
  const fullTitle = 'Medicine';
  const nameChars = Math.round(
    interpolate(frame, [40, 100], [fullName.length, 0], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    })
  );
  const titleChars = Math.round(
    interpolate(frame, [50, 105], [fullTitle.length, 0], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    })
  );

  // Glow pulse on empty badge
  const glowPulse = interpolate(Math.sin((frame - 110) * 0.15), [-1, 1], [0.3, 0.9], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const badgeGlow =
    frame >= 110 ? `0 0 ${Math.round(glowPulse * 30)}px ${INDIGO}80` : 'none';

  // "Who am I now?" types itself
  const questionFull = 'Who am I now?';
  const questionChars = Math.round(
    interpolate(frame, [115, 145], [0, questionFull.length], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    })
  );

  const body1Scale = sp(frame, fps, 140);
  const body2Scale = sp(frame, fps, 152);
  const body3Scale = sp(frame, fps, 162);

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        opacity,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingTop: TOP_SAFE,
        paddingBottom: BOT_SAFE,
        paddingLeft: SIDE,
        paddingRight: SIDE,
        fontFamily: FONT,
      }}
    >
      {/* TOP BLOCK */}
      <div style={{ textAlign: 'center' }}>
        <div
          style={{
            fontSize: 88,
            color: WHITE,
            fontWeight: 800,
            lineHeight: 1.15,
            opacity: clamp01(titleScale),
            transform: `scale(${titleScale})`,
            transformOrigin: 'center',
          }}
        >
          The Hidden Wound
        </div>
        <div
          style={{
            fontSize: 60,
            color: INDIGO,
            fontWeight: 600,
            lineHeight: 1.3,
            opacity: clamp01(subtitleScale),
            transform: `translateY(${interpolate(subtitleScale, [0, 1], [10, 0])}px)`,
          }}
        >
          Identity Loss
        </div>
      </div>

      {/* MIDDLE BLOCK — Badge + question */}
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        {/* Name badge */}
        <div style={{ boxShadow: badgeGlow, borderRadius: 20 }}>
          <svg viewBox="0 0 420 260" width={420} height={260}>
            {/* Lanyard hook */}
            <rect
              x={190}
              y={4}
              width={40}
              height={14}
              rx={4}
              ry={4}
              fill="none"
              stroke={WHITE}
              strokeWidth={2}
              opacity={badgeProgress}
            />
            {/* Badge outline draws itself */}
            <rect
              x={4}
              y={18}
              width={412}
              height={234}
              rx={20}
              ry={20}
              fill="none"
              stroke={WHITE}
              strokeWidth={3}
              strokeDasharray={badgePerimeter}
              strokeDashoffset={badgeDash}
            />
            {/* Name erases char by char */}
            <text
              x={210}
              y={118}
              textAnchor="middle"
              fontSize={42}
              fontWeight={700}
              fill={WHITE}
              fontFamily={FONT}
            >
              {fullName.substring(0, nameChars)}
            </text>
            {/* Specialty erases */}
            <text
              x={210}
              y={172}
              textAnchor="middle"
              fontSize={34}
              fontWeight={400}
              fill={DIM}
              fontFamily={FONT}
            >
              {fullTitle.substring(0, titleChars)}
            </text>
          </svg>
        </div>

        {/* "Who am I now?" types itself */}
        <div
          style={{
            fontSize: 64,
            color: INDIGO,
            fontWeight: 800,
            textAlign: 'center',
            marginTop: 32,
            minHeight: 80,
            letterSpacing: -0.5,
          }}
        >
          {questionFull.substring(0, questionChars)}
          {questionChars > 0 && questionChars < questionFull.length && (
            <span style={{ opacity: frame % 10 < 5 ? 1 : 0 }}>|</span>
          )}
        </div>
      </div>

      {/* BOTTOM BLOCK */}
      <div style={{ textAlign: 'center', maxWidth: 960 }}>
        <div
          style={{
            fontSize: 44,
            color: DIM,
            fontWeight: 400,
            lineHeight: 1.5,
            marginBottom: 14,
            opacity: clamp01(body1Scale),
            transform: `translateY(${interpolate(body1Scale, [0, 1], [10, 0])}px)`,
          }}
        >
          You spent a decade answering "I'm a nurse."
        </div>
        <div
          style={{
            fontSize: 44,
            color: WHITE,
            fontWeight: 500,
            lineHeight: 1.5,
            marginBottom: 14,
            opacity: clamp01(body2Scale),
            transform: `translateY(${interpolate(body2Scale, [0, 1], [10, 0])}px)`,
          }}
        >
          When that disappears...
        </div>
        <div
          style={{
            fontSize: 46,
            color: INDIGO,
            fontWeight: 600,
            lineHeight: 1.5,
            opacity: clamp01(body3Scale),
            transform: `translateY(${interpolate(body3Scale, [0, 1], [10, 0])}px)`,
          }}
        >
          ...so does the story you told yourself.
        </div>
      </div>
    </div>
  );
};

// ─── Scene 4: "Grief Is Not a Reason to Stay" ───────────────────────────────────
const Scene4: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  const title1Scale = sp(frame, fps, 5);
  const title2Scale = sp(frame, fps, 15);

  // Crosswalk stripes draw left-to-right
  const stripeProgress = interpolate(frame, [20, 60], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const stripeW = 600; // x=180 to x=780
  const stripeDash = stripeW;
  const stripeOffset = interpolate(stripeProgress, [0, 1], [stripeDash, 0]);

  // Hospital cross spring in
  const crossScale = sp(frame, fps, 5);

  // Door opens
  const doorAngle = interpolate(frame, [70, 120], [0, -30], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // Walking figure x: 180 → 780 over frames [30, 155]
  const figureX = interpolate(frame, [30, 155], [180, 780], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const legSwing = Math.sin(frame * 0.35) * 15;

  const body1Scale = sp(frame, fps, 90);
  const body2Scale = sp(frame, fps, 102);
  const body3Scale = sp(frame, fps, 120);

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        opacity,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingTop: TOP_SAFE,
        paddingBottom: BOT_SAFE,
        paddingLeft: SIDE,
        paddingRight: SIDE,
        fontFamily: FONT,
      }}
    >
      {/* TOP BLOCK */}
      <div style={{ textAlign: 'center' }}>
        <div
          style={{
            fontSize: 80,
            color: WHITE,
            fontWeight: 700,
            lineHeight: 1.2,
            opacity: clamp01(title1Scale),
            transform: `translateY(${interpolate(title1Scale, [0, 1], [14, 0])}px)`,
          }}
        >
          Grief is not a reason
        </div>
        <div
          style={{
            fontSize: 96,
            color: INDIGO,
            fontWeight: 800,
            lineHeight: 1.2,
            opacity: clamp01(title2Scale),
            transform: `scale(${title2Scale})`,
            transformOrigin: 'center',
          }}
        >
          to stay.
        </div>
      </div>

      {/* MIDDLE BLOCK — Crosswalk SVG, minimum 600px tall */}
      <svg
        viewBox="0 0 960 360"
        width={960}
        height={600}
        style={{ overflow: 'visible' }}
      >
        {/* 5 crosswalk stripes at y=60,120,180,240,300 */}
        {[60, 120, 180, 240, 300].map((y) => (
          <line
            key={y}
            x1={180}
            y1={y}
            x2={780}
            y2={y}
            stroke={DIM}
            strokeWidth={36}
            strokeDasharray={stripeDash}
            strokeDashoffset={stripeOffset}
            strokeLinecap="butt"
          />
        ))}

        {/* Hospital cross — LEFT (cx=80, cy=180) */}
        <g
          transform={`translate(80, 180) scale(${Math.max(0, crossScale)})`}
          style={{ transformOrigin: '0px 0px' }}
        >
          <rect x={-14} y={-36} width={28} height={72} rx={4} fill="none" stroke={DIM} strokeWidth={3} />
          <rect x={-36} y={-14} width={72} height={28} rx={4} fill="none" stroke={DIM} strokeWidth={3} />
        </g>

        {/* Door frame + panel — RIGHT (x=830, y=60) */}
        <g transform="translate(830, 60)">
          {/* Door frame */}
          <rect
            x={0}
            y={0}
            width={80}
            height={140}
            rx={4}
            fill="none"
            stroke={WHITE}
            strokeWidth={3}
            opacity={clamp01(stripeProgress)}
          />
          {/* Door panel rotates open around left edge */}
          <g transform={`rotate(${doorAngle}, 2, 70)`}>
            <rect
              x={2}
              y={4}
              width={74}
              height={132}
              rx={3}
              fill="none"
              stroke={INDIGO}
              strokeWidth={2.5}
              opacity={clamp01(stripeProgress)}
            />
            <circle cx={64} cy={72} r={6} fill={INDIGO} opacity={clamp01(stripeProgress)} />
          </g>
        </g>

        {/* Walking stick figure — traverses x=180→780 at y=180 */}
        <g transform={`translate(${figureX}, 180)`}>
          <circle cx={0} cy={-60} r={12} fill={WHITE} />
          <line x1={0} y1={-48} x2={0} y2={-10} stroke={WHITE} strokeWidth={3} strokeLinecap="round" />
          <line x1={0} y1={-36} x2={-18} y2={-20} stroke={WHITE} strokeWidth={2.5} strokeLinecap="round" />
          <line x1={0} y1={-36} x2={18} y2={-24} stroke={WHITE} strokeWidth={2.5} strokeLinecap="round" />
          <line x1={0} y1={-10} x2={-12 + legSwing} y2={16} stroke={WHITE} strokeWidth={3} strokeLinecap="round" />
          <line x1={0} y1={-10} x2={12 - legSwing} y2={16} stroke={WHITE} strokeWidth={3} strokeLinecap="round" />
        </g>
      </svg>

      {/* BOTTOM BLOCK */}
      <div style={{ textAlign: 'center', maxWidth: 960 }}>
        <div
          style={{
            fontSize: 44,
            color: WHITE,
            fontWeight: 400,
            lineHeight: 1.5,
            marginBottom: 16,
            opacity: clamp01(body1Scale),
            transform: `translateY(${interpolate(body1Scale, [0, 1], [10, 0])}px)`,
          }}
        >
          The pain you feel isn't proof you should stay.
        </div>
        <div
          style={{
            fontSize: 48,
            color: GREEN,
            fontWeight: 700,
            lineHeight: 1.5,
            marginBottom: 16,
            opacity: clamp01(body2Scale),
            transform: `translateY(${interpolate(body2Scale, [0, 1], [10, 0])}px)`,
          }}
        >
          It's proof that what you built mattered.
        </div>
        <div
          style={{
            fontSize: 46,
            color: WHITE,
            fontWeight: 600,
            lineHeight: 1.5,
            opacity: clamp01(body3Scale),
            transform: `translateY(${interpolate(body3Scale, [0, 1], [10, 0])}px)`,
          }}
        >
          Honor what was. Choose what's next.
        </div>
      </div>
    </div>
  );
};

// ─── Scene 5: CTA + Particles ────────────────────────────────────────────────────
const Scene5: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  // 12 deterministic particles
  const particleXs =    [90,  220, 340, 460, 580, 700, 820, 140, 280, 530, 650, 960];
  const particleSizes = [ 8,    6,  12,   5,  10,   7,  14,   6,   9,  11,   5,   8];
  const particleColors = [INDIGO, GREEN, AMBER, INDIGO, GREEN, AMBER, INDIGO, GREEN, INDIGO, AMBER, GREEN, INDIGO];

  const title1Scale = sp(frame, fps, 10);
  const title2Scale = sp(frame, fps, 25);
  const body1Scale  = sp(frame, fps, 60);
  const body2Scale  = sp(frame, fps, 72);

  const dividerWidth = interpolate(frame, [80, 100], [0, 960], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const ctaScale   = sp(frame, fps, 110);
  const urlScale   = sp(frame, fps, 120);
  const brandScale = sp(frame, fps, 135);

  const urlGlow = `0 0 24px rgba(99,102,241,0.8)`;

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        opacity,
        fontFamily: FONT,
        overflow: 'hidden',
      }}
    >
      {/* Particle layer */}
      <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
        {particleXs.map((x, i) => {
          const y = interpolate(frame, [0, 180], [1920 + i * 80, -200]);
          return (
            <div
              key={i}
              style={{
                position: 'absolute',
                left: x,
                top: y,
                width: particleSizes[i],
                height: particleSizes[i],
                borderRadius: '50%',
                background: particleColors[i],
                opacity: 0.35,
              }}
            />
          );
        })}
      </div>

      {/* Main content — fills full safe zone with space-between */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          zIndex: 1,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
          alignItems: 'center',
          paddingTop: TOP_SAFE,
          paddingBottom: BOT_SAFE,
          paddingLeft: SIDE,
          paddingRight: SIDE,
        }}
      >
        {/* TOP BLOCK */}
        <div style={{ textAlign: 'center' }}>
          <div
            style={{
              fontSize: 88,
              color: WHITE,
              fontWeight: 800,
              lineHeight: 1.15,
              opacity: clamp01(title1Scale),
              transform: `scale(${title1Scale})`,
              transformOrigin: 'center',
            }}
          >
            You're not quitting.
          </div>
          <div
            style={{
              fontSize: 88,
              color: GREEN,
              fontWeight: 800,
              lineHeight: 1.15,
              opacity: clamp01(title2Scale),
              transform: `scale(${title2Scale})`,
              transformOrigin: 'center',
            }}
          >
            You're choosing.
          </div>
        </div>

        {/* MIDDLE BLOCK */}
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            width: '100%',
          }}
        >
          <div
            style={{
              fontSize: 48,
              color: DIM,
              fontWeight: 400,
              textAlign: 'center',
              lineHeight: 1.5,
              marginBottom: 12,
              opacity: clamp01(body1Scale),
              transform: `translateY(${interpolate(body1Scale, [0, 1], [10, 0])}px)`,
            }}
          >
            The Crosswalk Method was built
          </div>
          <div
            style={{
              fontSize: 50,
              color: WHITE,
              fontWeight: 600,
              textAlign: 'center',
              lineHeight: 1.5,
              marginBottom: 40,
              opacity: clamp01(body2Scale),
              transform: `translateY(${interpolate(body2Scale, [0, 1], [10, 0])}px)`,
            }}
          >
            for this exact moment.
          </div>

          {/* Divider */}
          <div
            style={{
              width: dividerWidth,
              height: 2,
              background: INDIGO,
              borderRadius: 1,
              boxShadow: `0 0 8px ${INDIGO}80`,
            }}
          />
        </div>

        {/* BOTTOM BLOCK */}
        <div style={{ textAlign: 'center', width: '100%' }}>
          <div
            style={{
              fontSize: 52,
              color: INDIGO,
              fontWeight: 800,
              marginBottom: 20,
              opacity: clamp01(ctaScale),
              transform: `scale(${ctaScale})`,
              transformOrigin: 'center',
            }}
          >
            Name the fear. Start walking.
          </div>
          <div
            style={{
              fontSize: 64,
              color: WHITE,
              fontWeight: 800,
              marginBottom: 20,
              textShadow: urlGlow,
              opacity: clamp01(urlScale),
              transform: `scale(${urlScale})`,
              transformOrigin: 'center',
            }}
          >
            crosswalkwisdom.com
          </div>
          <div
            style={{
              fontSize: 34,
              color: DIM,
              letterSpacing: 6,
              textTransform: 'uppercase' as const,
              opacity: clamp01(brandScale),
              transform: `translateY(${interpolate(brandScale, [0, 1], [8, 0])}px)`,
            }}
          >
            CROSSWALK WISDOM
          </div>
        </div>
      </div>
    </div>
  );
};

// ─── Main Export ─────────────────────────────────────────────────────────────────
export const GriefExplainer: React.FC = () => {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();
  const progressWidth = interpolate(frame, [0, TOTAL], [0, 1080 - 2 * SIDE], {
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        width: 1080,
        height: 1920,
        background: BG,
        overflow: 'hidden',
        fontFamily: FONT,
        position: 'relative',
      }}
    >
      <Audio src={staticFile('voiceover-grief-explainer.wav')} volume={1.0} />
      <Audio src={staticFile('music.mp3')} volume={0.07} loop />

      <Sequence from={0} durationInFrames={SCENE_FRAMES}>
        <Scene1 frame={frame} fps={fps} />
      </Sequence>
      <Sequence from={SCENE_FRAMES} durationInFrames={SCENE_FRAMES}>
        <Scene2 frame={frame - SCENE_FRAMES} fps={fps} />
      </Sequence>
      <Sequence from={SCENE_FRAMES * 2} durationInFrames={SCENE_FRAMES}>
        <Scene3 frame={frame - SCENE_FRAMES * 2} fps={fps} />
      </Sequence>
      <Sequence from={SCENE_FRAMES * 3} durationInFrames={SCENE_FRAMES}>
        <Scene4 frame={frame - SCENE_FRAMES * 3} fps={fps} />
      </Sequence>
      <Sequence from={SCENE_FRAMES * 4} durationInFrames={SCENE_FRAMES}>
        <Scene5 frame={frame - SCENE_FRAMES * 4} fps={fps} />
      </Sequence>

      {/* Progress bar */}
      <div
        style={{
          position: 'absolute',
          bottom: BOT_SAFE - 30,
          left: SIDE,
          width: progressWidth,
          height: 6,
          background: INDIGO,
          borderRadius: 3,
          boxShadow: `0 0 10px ${INDIGO}80`,
        }}
      />
    </div>
  );
};
