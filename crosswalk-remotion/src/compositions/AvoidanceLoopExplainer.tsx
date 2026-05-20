/**
 * "The Avoidance Loop" — Educational Explainer (1080×1920, 30fps, 30s = 900 frames)
 *
 * 5 scenes × ~180 frames each with fade transitions.
 * Based on: dream-big-do-nothing-neuroscience blog post.
 * Visual style: dark (#0a0a0a), indigo accent, green emphasis, Inter font.
 * All diagrams are inline SVG — no external assets needed.
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
const AMBER = '#f59e0b';
const WHITE = '#ffffff';
const DIM = 'rgba(255,255,255,0.5)';
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

// ─── Scene 1: Hook ───────────────────────────────────────────────────────────────
const Scene1: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  const line1 = sp(frame, fps, 10);
  const line2 = sp(frame, fps, 28);
  const line3 = sp(frame, fps, 50);
  const sub = sp(frame, fps, 70);

  // Pulsing loop icon
  const loopScale = interpolate(frame % 40, [0, 20, 40], [1, 1.05, 1]);
  const loopOpacity = sp(frame, fps, 20);

  return (
    <div style={{ opacity, width: '100%', height: '100%', position: 'absolute' }}>
      {/* Loop icon — circular arrow SVG */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 80,
          left: 0,
          right: 0,
          display: 'flex',
          justifyContent: 'center',
          opacity: loopOpacity,
          transform: `scale(${loopScale})`,
        }}
      >
        <svg width="220" height="220" viewBox="0 0 100 100" fill="none">
          <circle cx="50" cy="50" r="38" stroke={INDIGO} strokeWidth="4" fill="none" strokeDasharray="239" strokeDashoffset={interpolate(loopOpacity, [0, 1], [239, 0])} />
          {/* Arrow head at top */}
          <polygon points="44,16 50,6 56,16" fill={INDIGO} opacity={loopOpacity} />
          {/* Brain dot in center */}
          <circle cx="50" cy="50" r="10" fill={`${INDIGO}30`} stroke={INDIGO} strokeWidth="2" />
          <text x="50" y="54" textAnchor="middle" fill={INDIGO} fontSize="9" fontFamily={FONT} fontWeight="800">
            LOOP
          </text>
        </svg>
      </div>

      {/* Headline line 1 */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 360,
          left: SIDE,
          right: SIDE,
          textAlign: 'center',
          opacity: line1,
          transform: `translateY(${(1 - line1) * 40}px)`,
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 68, fontWeight: 800, color: WHITE, lineHeight: 1.1 }}>
          You don't have a
        </span>
      </div>

      {/* Headline line 2 */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 448,
          left: SIDE,
          right: SIDE,
          textAlign: 'center',
          opacity: line2,
          transform: `translateY(${(1 - line2) * 40}px)`,
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 68, fontWeight: 800, color: WHITE, lineHeight: 1.1 }}>
          motivation problem.
        </span>
      </div>

      {/* Highlighted line 3 */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 560,
          left: SIDE,
          right: SIDE,
          textAlign: 'center',
          opacity: line3,
          transform: `translateY(${(1 - line3) * 40}px)`,
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 68, fontWeight: 800, color: INDIGO, lineHeight: 1.1 }}>
          You have an avoidance loop.
        </span>
      </div>

      {/* Sub */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 700,
          left: SIDE + 20,
          right: SIDE + 20,
          textAlign: 'center',
          opacity: sub,
          transform: `translateY(${(1 - sub) * 30}px)`,
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 36, fontWeight: 400, color: DIM, lineHeight: 1.45 }}>
          Your brain built it. And it has been{'\n'}rewarding itself for years.
        </span>
      </div>
    </div>
  );
};

// ─── Scene 2: The Problem — Avoidance Loop Flowchart ─────────────────────────────
const Scene2: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);
  const titleIn = sp(frame, fps, 5);

  const node1 = sp(frame, fps, 20);
  const node2 = sp(frame, fps, 35);
  const node3 = sp(frame, fps, 50);
  const node4 = sp(frame, fps, 65);
  const node5 = sp(frame, fps, 80);
  const node6 = sp(frame, fps, 95);

  const arr1 = clamp01(interpolate(frame, [30, 46], [0, 1]));
  const arr2 = clamp01(interpolate(frame, [45, 61], [0, 1]));
  const arr3 = clamp01(interpolate(frame, [60, 76], [0, 1]));
  const arr4 = clamp01(interpolate(frame, [75, 91], [0, 1]));
  const arr5 = clamp01(interpolate(frame, [90, 110], [0, 1]));

  const subIn = sp(frame, fps, 120);

  return (
    <div style={{ opacity, width: '100%', height: '100%', position: 'absolute' }}>
      {/* Title */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 30,
          left: SIDE,
          right: SIDE,
          textAlign: 'center',
          opacity: titleIn,
          transform: `translateY(${(1 - titleIn) * 30}px)`,
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 52, fontWeight: 800, color: WHITE }}>
          Procrastination is an{' '}
          <span style={{ color: INDIGO }}>emotion problem.</span>
        </span>
      </div>

      {/* Flowchart */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 170,
          left: SIDE,
          right: SIDE,
        }}
      >
        <svg width={960} height={820} viewBox="0 0 960 820">
          {/* Node 1: Hard Task */}
          <g opacity={node1} transform={`translate(${(1 - node1) * 20}, 0)`}>
            <rect x="330" y="0" width="300" height="70" rx="16" fill={INDIGO} />
            <text x="480" y="44" textAnchor="middle" fill={WHITE} fontSize="28" fontFamily={FONT} fontWeight="700">Hard Task Appears</text>
          </g>

          {/* Arrow 1 */}
          <line x1="480" y1="70" x2="480" y2="130" stroke={INDIGO} strokeWidth="3" strokeDasharray="60" strokeDashoffset={60 - arr1 * 60} />
          <polygon points="471,125 480,140 489,125" fill={INDIGO} opacity={arr1} />

          {/* Node 2: Amygdala */}
          <g opacity={node2} transform={`translate(${(1 - node2) * 20}, 0)`}>
            <rect x="320" y="140" width="320" height="70" rx="16" fill="#1e1b4b" stroke={INDIGO} strokeWidth="2" />
            <text x="480" y="184" textAnchor="middle" fill={INDIGO} fontSize="28" fontFamily={FONT} fontWeight="700">Amygdala Fires</text>
          </g>

          {/* Arrow 2 */}
          <line x1="480" y1="210" x2="480" y2="270" stroke={INDIGO} strokeWidth="3" strokeDasharray="60" strokeDashoffset={60 - arr2 * 60} />
          <polygon points="471,265 480,280 489,265" fill={INDIGO} opacity={arr2} />

          {/* Node 3: Dread */}
          <g opacity={node3} transform={`translate(${(1 - node3) * 20}, 0)`}>
            <rect x="330" y="280" width="300" height="70" rx="16" fill="#1c1917" stroke="#ef4444" strokeWidth="2" />
            <text x="480" y="324" textAnchor="middle" fill="#ef4444" fontSize="28" fontFamily={FONT} fontWeight="700">Dread / Anxiety</text>
          </g>

          {/* Arrow 3 */}
          <line x1="480" y1="350" x2="480" y2="410" stroke="#ef4444" strokeWidth="3" strokeDasharray="60" strokeDashoffset={60 - arr3 * 60} />
          <polygon points="471,405 480,420 489,405" fill="#ef4444" opacity={arr3} />

          {/* Node 4: Avoidance */}
          <g opacity={node4} transform={`translate(${(1 - node4) * 20}, 0)`}>
            <rect x="320" y="420" width="320" height="70" rx="16" fill="#1c1917" stroke={AMBER} strokeWidth="2" />
            <text x="480" y="464" textAnchor="middle" fill={AMBER} fontSize="28" fontFamily={FONT} fontWeight="700">Avoidance</text>
          </g>

          {/* Arrow 4 */}
          <line x1="480" y1="490" x2="480" y2="550" stroke={AMBER} strokeWidth="3" strokeDasharray="60" strokeDashoffset={60 - arr4 * 60} />
          <polygon points="471,545 480,560 489,545" fill={AMBER} opacity={arr4} />

          {/* Node 5: Relief = Reward */}
          <g opacity={node5} transform={`translate(${(1 - node5) * 20}, 0)`}>
            <rect x="300" y="560" width="360" height="70" rx="16" fill="#052e16" stroke={GREEN} strokeWidth="2" />
            <text x="480" y="604" textAnchor="middle" fill={GREEN} fontSize="28" fontFamily={FONT} fontWeight="700">Relief = Reward</text>
          </g>

          {/* Arrow 5 — loops back up the right side */}
          <path
            d="M 640 595 Q 820 595 820 350 Q 820 70 640 35"
            stroke={INDIGO}
            strokeWidth="3"
            fill="none"
            strokeDasharray="700"
            strokeDashoffset={700 - arr5 * 700}
          />
          <polygon points="630,26 640,42 650,26" fill={INDIGO} opacity={arr5} />
          <text x="835" y="360" textAnchor="start" fill={INDIGO} fontSize="22" fontFamily={FONT} fontWeight="600" opacity={arr5}>
            Repeat
          </text>
        </svg>
      </div>

      {/* Footer note */}
      <div
        style={{
          position: 'absolute',
          bottom: BOT_SAFE + 40,
          left: SIDE,
          right: SIDE,
          textAlign: 'center',
          opacity: subIn,
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 32, fontWeight: 400, color: DIM, lineHeight: 1.4 }}>
          Tim Pychyl: "An emotion regulation problem,{'\n'}not a time management problem."
        </span>
      </div>
    </div>
  );
};

// ─── Scene 3: The Reframe — Two Comparison Cards ─────────────────────────────────
const Scene3: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);
  const titleIn = sp(frame, fps, 5);
  const leftIn = sp(frame, fps, 25);
  const rightIn = sp(frame, fps, 38);
  const ex1 = sp(frame, fps, 70);
  const ex2 = sp(frame, fps, 82);
  const ex3 = sp(frame, fps, 94);

  return (
    <div style={{ opacity, width: '100%', height: '100%', position: 'absolute' }}>
      {/* Title */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 30,
          left: SIDE,
          right: SIDE,
          textAlign: 'center',
          opacity: titleIn,
          transform: `translateY(${(1 - titleIn) * 30}px)`,
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 52, fontWeight: 800, color: WHITE, lineHeight: 1.2 }}>
          You're not avoiding{' '}
          <span style={{ color: INDIGO }}>the task.</span>
        </span>
      </div>

      {/* Sub-title */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 160,
          left: SIDE,
          right: SIDE,
          textAlign: 'center',
          opacity: titleIn,
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 38, fontWeight: 400, color: DIM }}>
          You're avoiding{' '}
          <span style={{ color: AMBER, fontWeight: 700 }}>how you expect it will feel.</span>
        </span>
      </div>

      {/* Two comparison cards */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 300,
          left: SIDE,
          right: SIDE,
          display: 'flex',
          gap: 24,
        }}
      >
        {/* Left: What you think */}
        <div
          style={{
            flex: 1,
            background: '#1c1917',
            border: `2px solid #ef4444`,
            borderRadius: 20,
            padding: '36px 28px',
            opacity: leftIn,
            transform: `translateX(${(1 - leftIn) * -30}px)`,
          }}
        >
          <div style={{ fontFamily: FONT, fontSize: 24, fontWeight: 700, color: '#ef4444', marginBottom: 16 }}>
            WHAT YOU THINK
          </div>
          <div style={{ fontFamily: FONT, fontSize: 86, textAlign: 'center', color: '#ef4444', lineHeight: 1 }}>
            !!
          </div>
          <div style={{ fontFamily: FONT, fontSize: 30, fontWeight: 700, color: WHITE, textAlign: 'center', marginTop: 16, lineHeight: 1.3 }}>
            Overwhelming{'\n'}Dangerous{'\n'}Too Hard
          </div>
        </div>

        {/* Right: What it actually is */}
        <div
          style={{
            flex: 1,
            background: '#052e16',
            border: `2px solid ${GREEN}`,
            borderRadius: 20,
            padding: '36px 28px',
            opacity: rightIn,
            transform: `translateX(${(1 - rightIn) * 30}px)`,
          }}
        >
          <div style={{ fontFamily: FONT, fontSize: 24, fontWeight: 700, color: GREEN, marginBottom: 16 }}>
            WHAT IT IS
          </div>
          <div style={{ fontFamily: FONT, fontSize: 86, textAlign: 'center', color: GREEN, lineHeight: 1 }}>
            ok
          </div>
          <div style={{ fontFamily: FONT, fontSize: 30, fontWeight: 700, color: WHITE, textAlign: 'center', marginTop: 16, lineHeight: 1.3 }}>
            Manageable{'\n'}Survivable{'\n'}Just a start
          </div>
        </div>
      </div>

      {/* 3 examples */}
      <div
        style={{
          position: 'absolute',
          bottom: BOT_SAFE + 60,
          left: SIDE,
          right: SIDE,
        }}
      >
        {[
          { label: '1', text: 'Applying for a new role', spring: ex1 },
          { label: '2', text: 'Having the career conversation', spring: ex2 },
          { label: '3', text: 'Doing 10 minutes of research', spring: ex3 },
        ].map(({ label, text, spring: s }) => (
          <div
            key={label}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: 20,
              marginBottom: 20,
              opacity: s,
              transform: `translateX(${(1 - s) * 20}px)`,
            }}
          >
            <div
              style={{
                width: 44,
                height: 44,
                borderRadius: '50%',
                background: INDIGO,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontFamily: FONT,
                fontSize: 24,
                fontWeight: 800,
                color: WHITE,
                flexShrink: 0,
              }}
            >
              {label}
            </div>
            <span style={{ fontFamily: FONT, fontSize: 34, fontWeight: 500, color: WHITE }}>{text}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// ─── Scene 4: The Pattern — Two Pathways ─────────────────────────────────────────
const Scene4: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);
  const titleIn = sp(frame, fps, 5);

  // Avoidance pathway grows thick
  const avoidThickness = interpolate(frame, [20, 120], [4, 28], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const avoidOpacity = sp(frame, fps, 20);

  // Action pathway shrinks
  const actionThickness = interpolate(frame, [20, 120], [18, 4], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const actionOpacity = sp(frame, fps, 30);

  const label1 = sp(frame, fps, 40);
  const label2 = sp(frame, fps, 55);
  const caption = sp(frame, fps, 110);

  return (
    <div style={{ opacity, width: '100%', height: '100%', position: 'absolute' }}>
      {/* Title */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 30,
          left: SIDE,
          right: SIDE,
          textAlign: 'center',
          opacity: titleIn,
          transform: `translateY(${(1 - titleIn) * 30}px)`,
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 52, fontWeight: 800, color: WHITE }}>
          Every avoided step{' '}
          <span style={{ color: AMBER }}>deepens the loop.</span>
        </span>
      </div>

      {/* Pathway diagram */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 220,
          left: SIDE,
          right: SIDE,
        }}
      >
        <svg width={960} height={620} viewBox="0 0 960 620">

          {/* Avoidance pathway — growing thicker */}
          <g opacity={avoidOpacity}>
            <text x="480" y="50" textAnchor="middle" fill={AMBER} fontSize="30" fontFamily={FONT} fontWeight="700" opacity={label1}>
              Avoidance Pathway (getting stronger)
            </text>
            <line x1="60" y1="100" x2="900" y2="100" stroke={AMBER} strokeWidth={avoidThickness} strokeLinecap="round" />
            {/* Dots showing strength */}
            {[120, 240, 360, 480, 600, 720, 840].map((x, i) => (
              <circle
                key={x}
                cx={x}
                cy={100}
                r={interpolate(frame, [20 + i * 10, 100 + i * 5], [3, 3 + i * 2], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })}
                fill={AMBER}
                opacity={avoidOpacity}
              />
            ))}
          </g>

          {/* Label: grows */}
          <text x="900" y="105" textAnchor="end" fill={AMBER} fontSize="24" fontFamily={FONT} fontWeight="600" opacity={label1}>
            automatic
          </text>

          {/* Divider */}
          <line x1="60" y1="310" x2="900" y2="310" stroke="rgba(255,255,255,0.1)" strokeWidth="1" />

          {/* Action pathway — growing thinner */}
          <g opacity={actionOpacity}>
            <text x="480" y="380" textAnchor="middle" fill={DIM} fontSize="30" fontFamily={FONT} fontWeight="700" opacity={label2}>
              Action Pathway (atrophying)
            </text>
            <line x1="60" y1="430" x2="900" y2="430" stroke={INDIGO} strokeWidth={actionThickness} strokeLinecap="round" opacity={0.6} />
          </g>

          {/* Label: shrinks */}
          <text x="900" y="435" textAnchor="end" fill={INDIGO} fontSize="24" fontFamily={FONT} fontWeight="600" opacity={label2}>
            harder
          </text>
        </svg>
      </div>

      {/* Caption */}
      <div
        style={{
          position: 'absolute',
          bottom: BOT_SAFE + 60,
          left: SIDE,
          right: SIDE,
          textAlign: 'center',
          opacity: caption,
          transform: `translateY(${(1 - caption) * 20}px)`,
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 34, fontWeight: 400, color: DIM, lineHeight: 1.5 }}>
          Until not moving starts to feel{'\n'}like just how things are.
        </span>
      </div>
    </div>
  );
};

// ─── Scene 5: The Break — Name it. Shrink it. Start. ─────────────────────────────
const Scene5: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);
  const titleIn = sp(frame, fps, 5);
  const step1 = sp(frame, fps, 30);
  const step2 = sp(frame, fps, 50);
  const step3 = sp(frame, fps, 70);
  const ctaIn = sp(frame, fps, 100);

  // Particles
  const particleProgress = clamp01(interpolate(frame, [90, 160], [0, 1]));
  const particles = Array.from({ length: 14 }, (_, i) => {
    const angle = (i / 14) * Math.PI * 2;
    const radius = 80 + i * 8;
    return {
      x: 540 + Math.cos(angle) * radius * particleProgress,
      y: 980 + Math.sin(angle) * radius * particleProgress,
      r: 4 + (i % 3) * 2,
      opacity: particleProgress * (0.4 + (i % 4) * 0.15),
    };
  });

  return (
    <div style={{ opacity, width: '100%', height: '100%', position: 'absolute' }}>
      {/* Title */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 30,
          left: SIDE,
          right: SIDE,
          textAlign: 'center',
          opacity: titleIn,
          transform: `translateY(${(1 - titleIn) * 30}px)`,
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 68, fontWeight: 800, color: GREEN, lineHeight: 1.1 }}>
          Name it.{' '}
          <span style={{ color: INDIGO }}>Shrink it.</span>{' '}
          <span style={{ color: AMBER }}>Start.</span>
        </span>
      </div>

      {/* Steps */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 250,
          left: SIDE,
          right: SIDE,
        }}
      >
        {[
          {
            num: '1',
            title: 'Name the emotion',
            body: 'Say it out loud: "I\'m anxious. I\'m afraid I\'ll fail." Naming it shifts you from reactive to responsive.',
            color: GREEN,
            s: step1,
          },
          {
            num: '2',
            title: 'Shrink the action',
            body: 'Reduce it until the amygdala won\'t flag it. Not "research a pivot" — open one job posting and read it.',
            color: INDIGO,
            s: step2,
          },
          {
            num: '3',
            title: 'Start for five minutes',
            body: 'You don\'t need to finish. You need to begin. That one act breaks the reward cycle.',
            color: AMBER,
            s: step3,
          },
        ].map(({ num, title, body, color, s }) => (
          <div
            key={num}
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: 24,
              marginBottom: 36,
              opacity: s,
              transform: `translateX(${(1 - s) * 30}px)`,
            }}
          >
            <div
              style={{
                width: 56,
                height: 56,
                borderRadius: '50%',
                background: color,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontFamily: FONT,
                fontSize: 28,
                fontWeight: 800,
                color: '#0a0a0a',
                flexShrink: 0,
                marginTop: 4,
              }}
            >
              {num}
            </div>
            <div>
              <div style={{ fontFamily: FONT, fontSize: 38, fontWeight: 800, color, lineHeight: 1.2 }}>{title}</div>
              <div style={{ fontFamily: FONT, fontSize: 30, fontWeight: 400, color: DIM, lineHeight: 1.4, marginTop: 8 }}>{body}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Particles */}
      <svg
        width={1080}
        height={1920}
        style={{ position: 'absolute', top: 0, left: 0, pointerEvents: 'none' }}
      >
        {particles.map((p, i) => (
          <circle key={i} cx={p.x} cy={p.y} r={p.r} fill={i % 3 === 0 ? INDIGO : i % 3 === 1 ? GREEN : AMBER} opacity={p.opacity} />
        ))}
      </svg>

      {/* CTA pill */}
      <div
        style={{
          position: 'absolute',
          bottom: BOT_SAFE + 30,
          left: SIDE,
          right: SIDE,
          display: 'flex',
          justifyContent: 'center',
          opacity: ctaIn,
          transform: `scale(${0.8 + ctaIn * 0.2})`,
        }}
      >
        <div
          style={{
            background: GREEN,
            borderRadius: 60,
            padding: '24px 60px',
            fontFamily: FONT,
            fontSize: 34,
            fontWeight: 800,
            color: '#0a0a0a',
            textAlign: 'center',
            lineHeight: 1.3,
          }}
        >
          crosswalkwisdom.com/start
        </div>
      </div>
    </div>
  );
};

// ─── Progress bar ────────────────────────────────────────────────────────────────
const ProgressBar: React.FC<{ frame: number }> = ({ frame }) => (
  <div
    style={{
      position: 'absolute',
      bottom: BOT_SAFE - 30,
      left: SIDE,
      right: SIDE,
      height: 4,
      backgroundColor: 'rgba(255,255,255,0.1)',
      borderRadius: 2,
      zIndex: 100,
    }}
  >
    <div
      style={{
        height: '100%',
        width: `${(frame / TOTAL) * 100}%`,
        backgroundColor: INDIGO,
        borderRadius: 2,
      }}
    />
  </div>
);

// ─── Main composition ─────────────────────────────────────────────────────────────
export const AvoidanceLoopExplainer: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scenes = [
    { start: 0, Component: Scene1 },
    { start: SCENE_FRAMES - FADE, Component: Scene2 },
    { start: (SCENE_FRAMES - FADE) * 2, Component: Scene3 },
    { start: (SCENE_FRAMES - FADE) * 3, Component: Scene4 },
    { start: (SCENE_FRAMES - FADE) * 4, Component: Scene5 },
  ];

  return (
    <div
      style={{
        width: 1080,
        height: 1920,
        backgroundColor: BG,
        position: 'relative',
        overflow: 'hidden',
        fontFamily: FONT,
      }}
    >
      <style>
        {`@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');`}
      </style>

      {/* Background music */}
      <Audio src={staticFile('music.mp3')} volume={0.07} loop />

      {scenes.map(({ start, Component }, i) => (
        <Sequence key={i} from={start} durationInFrames={SCENE_FRAMES}>
          <Component frame={frame - start} fps={fps} />
        </Sequence>
      ))}

      <ProgressBar frame={frame} />
    </div>
  );
};
