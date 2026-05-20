/**
 * "Your Body Quit Before You Did" — Educational Explainer (1080×1920, 30fps, 30s = 900 frames)
 *
 * 5 scenes × ~180 frames each with fade transitions.
 * Scene 1: Hook — title reveal
 * Scene 2: The Problem — habit loop flowchart
 * Scene 3: The Reframe — two comparison cards
 * Scene 4: The Rule — traffic light loop diagram
 * Scene 5: The Break/CTA — particles + CTA pill
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

// ─── Constants ───────────────────────────────────────────────────────────────
const BG     = '#0a0a0a';
const INDIGO = '#6366f1';
const AMBER  = '#f59e0b';
const GREEN  = '#22c55e';
const RED    = '#ef4444';
const WHITE  = '#ffffff';
const DIM    = 'rgba(255,255,255,0.5)';
const FONT   = '"Inter", system-ui, sans-serif';

const SCENE_FRAMES = 180;
const FADE         = 12;
const TOTAL        = 900;

const TOP_SAFE = 150;
const BOT_SAFE = 170;
const SIDE     = 60;

// ─── Helpers ─────────────────────────────────────────────────────────────────
const sp = (frame: number, fps: number, delay = 0) =>
  spring({ frame: frame - delay, fps, config: { damping: 200 } });

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));

const fadeInOut = (localFrame: number, dur: number) => {
  const fadeIn  = interpolate(localFrame, [0, FADE],        [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const fadeOut = interpolate(localFrame, [dur - FADE, dur], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return fadeIn * fadeOut;
};

// ─── Scene 1: Hook ────────────────────────────────────────────────────────────
const Scene1: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity     = fadeInOut(frame, SCENE_FRAMES);
  const iconIn      = sp(frame, fps, 10);
  const line1In     = sp(frame, fps, 40);
  const line2In     = sp(frame, fps, 60);
  const subIn       = sp(frame, fps, 85);
  const underlineW  = interpolate(frame, [50, 100], [0, 960 - SIDE * 2], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  return (
    <div style={{ opacity, width: '100%', height: '100%', position: 'absolute' }}>
      {/* Body / signal icon */}
      <div style={{
        position: 'absolute',
        top: TOP_SAFE + 160,
        left: 0, right: 0,
        display: 'flex', justifyContent: 'center',
        opacity: iconIn,
        transform: `scale(${iconIn})`,
      }}>
        <svg width="160" height="160" viewBox="0 0 80 80" fill="none">
          {/* Body silhouette */}
          <circle cx="40" cy="18" r="10" stroke={AMBER} strokeWidth="2.5" fill="none" />
          <path d="M40 28 L40 55 M28 38 L52 38 M40 55 L30 72 M40 55 L50 72"
            stroke={AMBER} strokeWidth="2.5" strokeLinecap="round" fill="none" />
          {/* Signal waves radiating */}
          <path d="M58 22 C64 28 64 38 58 44" stroke={INDIGO} strokeWidth="2" fill="none"
            strokeDasharray="20"
            strokeDashoffset={interpolate(iconIn, [0, 1], [20, 0])} />
          <path d="M64 16 C74 26 74 40 64 50" stroke={INDIGO} strokeWidth="2" fill="none" opacity="0.6"
            strokeDasharray="30"
            strokeDashoffset={interpolate(iconIn, [0, 1], [30, 0])} />
          <path d="M22 22 C16 28 16 38 22 44" stroke={INDIGO} strokeWidth="2" fill="none"
            strokeDasharray="20"
            strokeDashoffset={interpolate(iconIn, [0, 1], [20, 0])} />
        </svg>
      </div>

      {/* Headline line 1 */}
      <div style={{
        position: 'absolute',
        top: TOP_SAFE + 390,
        left: SIDE, right: SIDE,
        textAlign: 'center',
        opacity: line1In,
        transform: `translateY(${(1 - line1In) * 40}px)`,
      }}>
        <span style={{ fontFamily: FONT, fontSize: 80, fontWeight: 800, color: WHITE, lineHeight: 1.05 }}>
          Your body
        </span>
      </div>

      {/* Headline line 2 — amber */}
      <div style={{
        position: 'absolute',
        top: TOP_SAFE + 490,
        left: SIDE, right: SIDE,
        textAlign: 'center',
        opacity: line2In,
        transform: `translateY(${(1 - line2In) * 40}px)`,
      }}>
        <span style={{ fontFamily: FONT, fontSize: 80, fontWeight: 800, color: AMBER, lineHeight: 1.05 }}>
          quit first.
        </span>
      </div>

      {/* Amber underline */}
      <div style={{
        position: 'absolute',
        top: TOP_SAFE + 598,
        left: SIDE,
        width: underlineW,
        height: 4,
        background: AMBER,
        borderRadius: 2,
      }} />

      {/* Subtitle */}
      <div style={{
        position: 'absolute',
        top: TOP_SAFE + 640,
        left: SIDE + 20, right: SIDE + 20,
        textAlign: 'center',
        opacity: subIn,
        transform: `translateY(${(1 - subIn) * 25}px)`,
      }}>
        <span style={{ fontFamily: FONT, fontSize: 38, fontWeight: 400, color: DIM, lineHeight: 1.5 }}>
          These 10 habits are why{'\n'}it couldn't come back.
        </span>
      </div>
    </div>
  );
};

// ─── Scene 2: The Problem — habit loop ───────────────────────────────────────
const Scene2: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity  = fadeInOut(frame, SCENE_FRAMES);
  const titleIn  = sp(frame, fps, 5);
  const bodyIn   = sp(frame, fps, 25);

  const node1 = sp(frame, fps, 40);
  const node2 = sp(frame, fps, 58);
  const node3 = sp(frame, fps, 76);
  const node4 = sp(frame, fps, 94);
  const arrow1 = clamp01(interpolate(frame, [50, 68], [0, 1]));
  const arrow2 = clamp01(interpolate(frame, [68, 86], [0, 1]));
  const arrow3 = clamp01(interpolate(frame, [86, 104], [0, 1]));

  const nodes = [
    { label: 'Override signal', color: INDIGO, x: 480, y: 60,  n: node1 },
    { label: 'Push through',    color: INDIGO, x: 480, y: 180, n: node2 },
    { label: 'Collapse',        color: RED,    x: 480, y: 300, n: node3 },
    { label: 'Start again',     color: INDIGO, x: 480, y: 420, n: node4 },
  ];

  return (
    <div style={{ opacity, width: '100%', height: '100%', position: 'absolute' }}>
      {/* Title */}
      <div style={{
        position: 'absolute', top: TOP_SAFE + 30,
        left: SIDE, right: SIDE, textAlign: 'center',
        opacity: titleIn, transform: `translateY(${(1 - titleIn) * 30}px)`,
      }}>
        <span style={{ fontFamily: FONT, fontSize: 58, fontWeight: 800, color: WHITE }}>
          The habits{' '}
          <span style={{ color: INDIGO }}>keeping you stuck.</span>
        </span>
      </div>

      {/* Body */}
      <div style={{
        position: 'absolute', top: TOP_SAFE + 140,
        left: SIDE + 10, right: SIDE + 10, textAlign: 'center',
        opacity: bodyIn, transform: `translateY(${(1 - bodyIn) * 20}px)`,
      }}>
        <span style={{ fontFamily: FONT, fontSize: 36, fontWeight: 400, color: DIM, lineHeight: 1.5 }}>
          You're not failing at recovery.{'\n'}You're succeeding at the wrong habits.
        </span>
      </div>

      {/* Flowchart */}
      <div style={{
        position: 'absolute', top: TOP_SAFE + 310,
        left: 0, right: 0,
        display: 'flex', justifyContent: 'center',
      }}>
        <svg width={960} height={480} viewBox="0 0 960 480">
          {/* Arrows */}
          <line x1="480" y1="100" x2="480" y2="160"
            stroke={INDIGO} strokeWidth="2" strokeDasharray="60"
            strokeDashoffset={60 - arrow1 * 60} />
          <line x1="480" y1="220" x2="480" y2="280"
            stroke={INDIGO} strokeWidth="2" strokeDasharray="60"
            strokeDashoffset={60 - arrow2 * 60} />
          <line x1="480" y1="340" x2="480" y2="400"
            stroke={INDIGO} strokeWidth="2" strokeDasharray="60"
            strokeDashoffset={60 - arrow3 * 60} />
          {/* Loop-back arrow */}
          <path d="M640 430 C760 430 760 60 640 60"
            stroke={`${AMBER}80`} strokeWidth="2" fill="none"
            strokeDasharray="400"
            strokeDashoffset={400 - arrow3 * 400} />
          <polygon points="640,52 630,68 650,68"
            fill={AMBER} opacity={arrow3} />

          {nodes.map(({ label, color, x, y, n }) => (
            <g key={label} opacity={n} transform={`translate(${(1 - n) * 20}, 0)`}>
              <rect x={x - 160} y={y} width={320} height={60} rx={12}
                fill={`${color}20`} stroke={color} strokeWidth="2" />
              <text x={x} y={y + 36} textAnchor="middle"
                fill={WHITE} fontSize="26" fontFamily={FONT} fontWeight="600">
                {label}
              </text>
            </g>
          ))}
        </svg>
      </div>
    </div>
  );
};

// ─── Scene 3: The Reframe — two cards ────────────────────────────────────────
const Scene3: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);
  const titleIn = sp(frame, fps, 5);
  const bodyIn  = sp(frame, fps, 25);
  const card1   = sp(frame, fps, 45);
  const card2   = sp(frame, fps, 60);
  const card3   = sp(frame, fps, 75);

  const pairs = [
    { myth: '"Push through."', truth: 'Your body is signalling, not failing.' },
    { myth: '"Do it alone."',  truth: 'Recovery requires one honest conversation.' },
    { myth: '"Red = giving up."', truth: 'Red = the smallest version that counts.' },
  ];
  const cards = [card1, card2, card3];

  return (
    <div style={{ opacity, width: '100%', height: '100%', position: 'absolute' }}>
      {/* Title */}
      <div style={{
        position: 'absolute', top: TOP_SAFE + 30,
        left: SIDE, right: SIDE, textAlign: 'center',
        opacity: titleIn, transform: `translateY(${(1 - titleIn) * 30}px)`,
      }}>
        <span style={{ fontFamily: FONT, fontSize: 58, fontWeight: 800, color: WHITE }}>
          Stopping is the{' '}
          <span style={{ color: AMBER }}>advanced move.</span>
        </span>
      </div>

      {/* Body */}
      <div style={{
        position: 'absolute', top: TOP_SAFE + 145,
        left: SIDE + 10, right: SIDE + 10, textAlign: 'center',
        opacity: bodyIn, transform: `translateY(${(1 - bodyIn) * 20}px)`,
      }}>
        <span style={{ fontFamily: FONT, fontSize: 36, fontWeight: 400, color: DIM, lineHeight: 1.5 }}>
          What you were told vs.{'\n'}what's actually true.
        </span>
      </div>

      {/* Cards */}
      <div style={{
        position: 'absolute', top: TOP_SAFE + 290,
        left: SIDE, right: SIDE,
        display: 'flex', flexDirection: 'column', gap: 24,
      }}>
        {pairs.map(({ myth, truth }, i) => (
          <div key={i} style={{
            opacity: cards[i],
            transform: `translateX(${(1 - cards[i]) * -30}px)`,
            display: 'flex', gap: 16,
          }}>
            {/* Myth */}
            <div style={{
              flex: 1, padding: '20px 22px',
              background: `${RED}15`, border: `1.5px solid ${RED}50`,
              borderRadius: 16,
            }}>
              <div style={{ fontFamily: FONT, fontSize: 22, fontWeight: 600, color: `${RED}cc`, marginBottom: 6 }}>
                MYTH
              </div>
              <div style={{ fontFamily: FONT, fontSize: 28, fontWeight: 600, color: WHITE, lineHeight: 1.3 }}>
                {myth}
              </div>
            </div>
            {/* Truth */}
            <div style={{
              flex: 1, padding: '20px 22px',
              background: `${GREEN}15`, border: `1.5px solid ${GREEN}50`,
              borderRadius: 16,
            }}>
              <div style={{ fontFamily: FONT, fontSize: 22, fontWeight: 600, color: `${GREEN}cc`, marginBottom: 6 }}>
                TRUTH
              </div>
              <div style={{ fontFamily: FONT, fontSize: 28, fontWeight: 600, color: WHITE, lineHeight: 1.3 }}>
                {truth}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// ─── Scene 4: The Rule — traffic light loop ───────────────────────────────────
const Scene4: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity  = fadeInOut(frame, SCENE_FRAMES);
  const titleIn  = sp(frame, fps, 5);
  const bodyIn   = sp(frame, fps, 25);
  const greenIn  = sp(frame, fps, 45);
  const amberIn  = sp(frame, fps, 65);
  const redIn    = sp(frame, fps, 85);
  const ctaIn    = sp(frame, fps, 115);

  // Pulse the current "active" light based on frame
  const activeLight = frame < 90 ? 0 : frame < 130 ? 1 : 2;
  const pulse = interpolate(frame % 20, [0, 10, 20], [1, 1.1, 1]);

  const lights = [
    { color: GREEN, label: 'GREEN',  desc: 'Full version',      delay: greenIn },
    { color: AMBER, label: 'AMBER',  desc: 'Scaled version',    delay: amberIn },
    { color: RED,   label: 'RED',    desc: 'Smallest version',  delay: redIn   },
  ];

  return (
    <div style={{ opacity, width: '100%', height: '100%', position: 'absolute' }}>
      {/* Title */}
      <div style={{
        position: 'absolute', top: TOP_SAFE + 30,
        left: SIDE, right: SIDE, textAlign: 'center',
        opacity: titleIn, transform: `translateY(${(1 - titleIn) * 30}px)`,
      }}>
        <span style={{ fontFamily: FONT, fontSize: 58, fontWeight: 800, color: WHITE }}>
          One stopped habit{' '}
          <span style={{ color: AMBER }}>at a time.</span>
        </span>
      </div>

      {/* Body */}
      <div style={{
        position: 'absolute', top: TOP_SAFE + 145,
        left: SIDE + 10, right: SIDE + 10, textAlign: 'center',
        opacity: bodyIn, transform: `translateY(${(1 - bodyIn) * 20}px)`,
      }}>
        <span style={{ fontFamily: FONT, fontSize: 36, fontWeight: 400, color: DIM, lineHeight: 1.5 }}>
          Traffic light your habits.{'\n'}Red still counts.
        </span>
      </div>

      {/* Traffic light vertical */}
      <div style={{
        position: 'absolute', top: TOP_SAFE + 310,
        left: 0, right: 0,
        display: 'flex', justifyContent: 'center',
      }}>
        <div style={{
          background: '#111', borderRadius: 32, padding: '28px 40px',
          display: 'flex', flexDirection: 'column', gap: 20,
          border: '2px solid #333',
        }}>
          {lights.map(({ color, label, desc, delay }, i) => (
            <div key={i} style={{
              opacity: delay,
              transform: `scale(${delay})`,
              display: 'flex', alignItems: 'center', gap: 28,
            }}>
              <div style={{
                width: 80, height: 80, borderRadius: '50%',
                background: color,
                boxShadow: activeLight === i ? `0 0 40px ${color}` : 'none',
                transform: `scale(${activeLight === i ? pulse : 0.85})`,
                transition: 'box-shadow 0.3s',
              }} />
              <div>
                <div style={{ fontFamily: FONT, fontSize: 30, fontWeight: 800, color }}>
                  {label}
                </div>
                <div style={{ fontFamily: FONT, fontSize: 28, fontWeight: 400, color: WHITE }}>
                  {desc}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Red counts callout */}
      <div style={{
        position: 'absolute', bottom: BOT_SAFE + 40,
        left: SIDE, right: SIDE, textAlign: 'center',
        opacity: ctaIn, transform: `translateY(${(1 - ctaIn) * 20}px)`,
      }}>
        <span style={{ fontFamily: FONT, fontSize: 34, fontWeight: 600, color: AMBER, lineHeight: 1.4 }}>
          2 minutes of stretching instead{'\n'}of a 1-hour workout — Red counts.
        </span>
      </div>
    </div>
  );
};

// ─── Scene 5: CTA — particles + pill ─────────────────────────────────────────
const Scene5: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity  = fadeInOut(frame, SCENE_FRAMES);
  const titleIn  = sp(frame, fps, 10);
  const step1In  = sp(frame, fps, 40);
  const step2In  = sp(frame, fps, 58);
  const step3In  = sp(frame, fps, 76);
  const pillIn   = sp(frame, fps, 105);

  const particles = Array.from({ length: 14 }, (_, i) => {
    const angle  = (i / 14) * Math.PI * 2;
    const radius = interpolate(frame, [0, 60], [0, 320], { extrapolateRight: 'clamp' });
    const cx     = 540 + Math.cos(angle) * radius;
    const cy     = 960 + Math.sin(angle) * radius;
    const pOpacity = interpolate(frame, [0, 20, 140, 180], [0, 0.6, 0.6, 0], {
      extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    });
    return { cx, cy, pOpacity, i };
  });

  const steps = [
    { num: '1', text: 'Name the habit you\'ve been running on empty' },
    { num: '2', text: 'Tell one person what\'s actually happening' },
    { num: '3', text: 'Start at Red — and let that be enough' },
  ];
  const stepSprings = [step1In, step2In, step3In];

  return (
    <div style={{ opacity, width: '100%', height: '100%', position: 'absolute' }}>
      {/* Particle field */}
      <svg style={{ position: 'absolute', top: 0, left: 0 }} width={1080} height={1920}>
        {particles.map(({ cx, cy, pOpacity, i }) => (
          <circle key={i} cx={cx} cy={cy} r={6 + (i % 3) * 3}
            fill={i % 2 === 0 ? AMBER : INDIGO} opacity={pOpacity} />
        ))}
      </svg>

      {/* Title */}
      <div style={{
        position: 'absolute', top: TOP_SAFE + 40,
        left: SIDE, right: SIDE, textAlign: 'center',
        opacity: titleIn, transform: `translateY(${(1 - titleIn) * 30}px)`,
      }}>
        <span style={{ fontFamily: FONT, fontSize: 64, fontWeight: 800, color: WHITE, lineHeight: 1.1 }}>
          Your body{'\n'}already told you.
        </span>
      </div>

      {/* Steps */}
      <div style={{
        position: 'absolute', top: TOP_SAFE + 320,
        left: SIDE, right: SIDE,
        display: 'flex', flexDirection: 'column', gap: 28,
      }}>
        {steps.map(({ num, text }, i) => (
          <div key={i} style={{
            display: 'flex', alignItems: 'flex-start', gap: 24,
            opacity: stepSprings[i],
            transform: `translateX(${(1 - stepSprings[i]) * -30}px)`,
          }}>
            <div style={{
              width: 52, height: 52, borderRadius: '50%',
              background: AMBER,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexShrink: 0,
            }}>
              <span style={{ fontFamily: FONT, fontSize: 28, fontWeight: 800, color: BG }}>
                {num}
              </span>
            </div>
            <span style={{ fontFamily: FONT, fontSize: 36, fontWeight: 500, color: WHITE, lineHeight: 1.4 }}>
              {text}
            </span>
          </div>
        ))}
      </div>

      {/* CTA Pill */}
      <div style={{
        position: 'absolute', bottom: BOT_SAFE + 60,
        left: SIDE, right: SIDE,
        opacity: pillIn, transform: `scale(${pillIn})`,
      }}>
        <div style={{
          background: AMBER,
          borderRadius: 60, padding: '28px 40px',
          textAlign: 'center',
        }}>
          <div style={{ fontFamily: FONT, fontSize: 34, fontWeight: 800, color: BG, lineHeight: 1.2 }}>
            crosswalkwisdom.com
          </div>
          <div style={{ fontFamily: FONT, fontSize: 26, fontWeight: 500, color: `${BG}cc`, marginTop: 6 }}>
            Weekly reflections for healthcare professionals
          </div>
        </div>
      </div>
    </div>
  );
};

// ─── Root Composition ─────────────────────────────────────────────────────────
export const BurnoutHabitsExplainer: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const localFrame = (sceneIndex: number) => frame - sceneIndex * SCENE_FRAMES;

  return (
    <div style={{ width: 1080, height: 1920, background: BG, overflow: 'hidden', position: 'relative' }}>
      <Audio src={staticFile('music.mp3')} volume={0.07} loop />

      <Sequence from={0}               durationInFrames={SCENE_FRAMES + FADE}>
        <Scene1 frame={localFrame(0)} fps={fps} />
      </Sequence>
      <Sequence from={SCENE_FRAMES - FADE}   durationInFrames={SCENE_FRAMES + FADE}>
        <Scene2 frame={localFrame(1)} fps={fps} />
      </Sequence>
      <Sequence from={SCENE_FRAMES * 2 - FADE} durationInFrames={SCENE_FRAMES + FADE}>
        <Scene3 frame={localFrame(2)} fps={fps} />
      </Sequence>
      <Sequence from={SCENE_FRAMES * 3 - FADE} durationInFrames={SCENE_FRAMES + FADE}>
        <Scene4 frame={localFrame(3)} fps={fps} />
      </Sequence>
      <Sequence from={SCENE_FRAMES * 4 - FADE} durationInFrames={SCENE_FRAMES + FADE}>
        <Scene5 frame={localFrame(4)} fps={fps} />
      </Sequence>
    </div>
  );
};
