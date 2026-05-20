import React from 'react';
import { useCurrentFrame, interpolate, spring, useVideoConfig, Sequence, Audio, staticFile } from 'remotion';

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

const sp = (frame: number, fps: number, delay = 0) =>
  spring({ frame: frame - delay, fps, config: { damping: 200 } });

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));

const fadeInOut = (localFrame: number, dur: number) => {
  const fadeIn = interpolate(localFrame, [0, FADE], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const fadeOut = interpolate(localFrame, [dur - FADE, dur], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return fadeIn * fadeOut;
};

// ─── Scene 1: "You have 47 transferable skills" ──────────────────────────────
const Scene1: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);
  const titleScale = sp(frame, fps, 5);
  const numRaw = interpolate(frame, [20, 80], [0, 47], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const num = Math.round(numRaw);
  const subtitleScale = sp(frame, fps, 40);
  const pills = [
    { label: 'Crisis Management', delay: 70 },
    { label: 'Empathy', delay: 80 },
    { label: 'Triage Logic', delay: 90 },
    { label: 'Documentation', delay: 100 },
    { label: 'Leadership', delay: 110 },
    { label: 'Patient Education', delay: 120 },
  ];
  const captionScale = sp(frame, fps, 130);

  return (
    <div style={{
      position: 'absolute', inset: 0, opacity,
      display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
      alignItems: 'center',
      paddingTop: TOP_SAFE, paddingBottom: BOT_SAFE,
      paddingLeft: SIDE, paddingRight: SIDE,
    }}>
      {/* Top block */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 0 }}>
        <div style={{
          transform: `scale(${titleScale})`,
          color: WHITE, fontSize: 80, fontWeight: 700,
          fontFamily: FONT, textAlign: 'center',
        }}>
          You have
        </div>
        <div style={{
          color: GREEN, fontSize: 220, fontWeight: 800,
          fontFamily: FONT, textAlign: 'center',
          fontVariantNumeric: 'tabular-nums', lineHeight: 1,
        }}>
          {num}
        </div>
        <div style={{
          transform: `scale(${subtitleScale})`,
          color: WHITE, fontSize: 80, fontWeight: 700,
          fontFamily: FONT, textAlign: 'center',
        }}>
          transferable skills.
        </div>
      </div>

      {/* Middle block — pill grid */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, justifyContent: 'center' }}>
        {pills.map(({ label, delay }) => {
          const s = sp(frame, fps, delay);
          return (
            <div key={label} style={{
              transform: `scale(${s})`,
              background: 'rgba(99,102,241,0.15)',
              border: `1px solid ${INDIGO}`,
              borderRadius: 24,
              color: WHITE,
              fontSize: 38,
              fontFamily: FONT,
              padding: '14px 28px',
            }}>
              {label}
            </div>
          );
        })}
      </div>

      {/* Bottom block */}
      <div style={{
        transform: `scale(${captionScale})`,
        color: DIM, fontSize: 44,
        fontFamily: FONT, textAlign: 'center',
      }}>
        AI can show you what you can't see.
      </div>
    </div>
  );
};

// ─── Scene 2: "Step 1: Name Your Fear" ──────────────────────────────────────
const Scene2: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);
  const badgeScale = sp(frame, fps, 5);
  const titleScale = sp(frame, fps, 15);

  const topNodeScale = sp(frame, fps, 20);
  const arrowProgress = interpolate(frame, [25, 45], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const arrowDash = 80;

  const leftNodeScale = sp(frame, fps, 50);
  const centerNodeScale = sp(frame, fps, 58);
  const rightNodeScale = sp(frame, fps, 66);
  const nodeScales = [leftNodeScale, centerNodeScale, rightNodeScale];

  const glowScale = sp(frame, fps, 80);

  const bodyScale = sp(frame, fps, 120);
  const greenScale = sp(frame, fps, 132);

  const nodes = [
    { cx: 240, color: AMBER, title: ['Financial', 'Insecurity'], highlighted: false },
    { cx: 480, color: GREEN, title: ['Fear of', 'Judgment'], highlighted: false },
    { cx: 720, color: INDIGO, title: ['Identity', 'Loss'], highlighted: true },
  ];

  return (
    <div style={{
      position: 'absolute', inset: 0, opacity,
      display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
      alignItems: 'center',
      paddingTop: TOP_SAFE, paddingBottom: BOT_SAFE,
      paddingLeft: SIDE, paddingRight: SIDE,
    }}>
      {/* Top block */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20 }}>
        <div style={{
          transform: `scale(${badgeScale})`,
          background: 'rgba(99,102,241,0.2)', border: `1px solid ${INDIGO}`,
          borderRadius: 999, padding: '10px 28px',
          color: INDIGO, fontSize: 36, fontWeight: 700, fontFamily: FONT,
        }}>
          STEP 1
        </div>
        <div style={{
          transform: `scale(${titleScale})`,
          color: WHITE, fontSize: 88, fontWeight: 800,
          fontFamily: FONT, textAlign: 'center',
        }}>
          Name Your Fear
        </div>
      </div>

      {/* Middle block — SVG flowchart */}
      <svg width={960} height={640} viewBox="0 0 960 640">
        {/* YOU node at top center */}
        <g transform={`translate(480,60)`} style={{ transformOrigin: '480px 60px' }}>
          <rect x={-120} y={-40} width={240} height={80} rx={12} fill={INDIGO}
            transform={`scale(${topNodeScale})`} style={{ transformOrigin: '0px 0px' }} />
          <text x={0} y={10} textAnchor="middle" fill={WHITE} fontSize={40}
            fontFamily={FONT} fontWeight={700}
            opacity={topNodeScale}>YOU</text>
        </g>

        {/* Arrow down from YOU to branch point */}
        <line x1={480} y1={100} x2={480} y2={200}
          stroke={WHITE} strokeWidth={2.5}
          strokeDasharray={arrowDash}
          strokeDashoffset={arrowDash * (1 - arrowProgress)}
          strokeLinecap="round"
        />

        {/* Branch arrows to each node */}
        {[240, 480, 720].map((x, i) => (
          <line key={i} x1={480} y1={200} x2={x} y2={340}
            stroke={WHITE} strokeWidth={2}
            strokeDasharray={arrowDash}
            strokeDashoffset={arrowDash * (1 - arrowProgress)}
            strokeLinecap="round"
          />
        ))}

        {/* Branch nodes */}
        {nodes.map(({ cx, color, title, highlighted }, i) => {
          const s = nodeScales[i];
          return (
            <g key={i} transform={`translate(${cx},380)`}>
              <rect x={-100} y={-45} width={200} height={90} rx={12}
                fill={`${color}33`}
                stroke={highlighted ? GREEN : color}
                strokeWidth={highlighted ? 2.5 : 1.5}
                transform={`scale(${s})`} style={{ transformOrigin: '0px 0px' }}
              />
              {title.map((line, li) => (
                <text key={li} x={0} y={-6 + li * 30} textAnchor="middle"
                  fill={highlighted ? GREEN : color}
                  fontSize={30} fontFamily={FONT} fontWeight={highlighted ? 700 : 600}
                  opacity={s}>
                  {line}
                </text>
              ))}
            </g>
          );
        })}

        {/* Dominant fear label below right node */}
        <g transform={`translate(720,500)`}>
          <text x={0} y={0} textAnchor="middle"
            fill={GREEN} fontSize={28} fontFamily={FONT} fontWeight={700}
            opacity={glowScale}>
            YOUR DOMINANT FEAR
          </text>
        </g>
      </svg>

      {/* Bottom block */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
        <div style={{
          transform: `scale(${bodyScale})`,
          color: WHITE, fontSize: 44,
          fontFamily: FONT, textAlign: 'center',
        }}>
          The Fear Audit identifies yours.
        </div>
        <div style={{
          transform: `scale(${greenScale})`,
          color: GREEN, fontSize: 44, fontWeight: 700,
          fontFamily: FONT, textAlign: 'center',
        }}>
          Takes 2 minutes.
        </div>
      </div>
    </div>
  );
};

// ─── Scene 3: "Step 2: Ask AI the Right Question" ───────────────────────────
const Scene3: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);
  const badgeScale = sp(frame, fps, 5);
  const titleScale = sp(frame, fps, 15);
  const chatScale = sp(frame, fps, 20);

  const promptText = "I'm a nurse, 12 years. My biggest fear is identity loss. Show me 5 careers that use my skills.";
  const charsToShow = Math.floor(
    interpolate(frame, [30, 120], [0, promptText.length], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })
  );
  const displayText = promptText.slice(0, charsToShow);

  const careers = [
    { delay: 110, label: 'Healthcare Educator' },
    { delay: 120, label: 'Health Coach' },
    { delay: 130, label: 'Clinical Writer' },
    { delay: 140, label: 'Medical Consultant' },
    { delay: 150, label: 'Wellness Program Lead' },
  ];

  const warningScale = sp(frame, fps, 155);
  const mapScale = sp(frame, fps, 165);

  return (
    <div style={{
      position: 'absolute', inset: 0, opacity,
      display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
      alignItems: 'center',
      paddingTop: TOP_SAFE, paddingBottom: BOT_SAFE,
      paddingLeft: SIDE, paddingRight: SIDE,
    }}>
      {/* Top block */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20 }}>
        <div style={{
          transform: `scale(${badgeScale})`,
          background: 'rgba(99,102,241,0.2)', border: `1px solid ${INDIGO}`,
          borderRadius: 999, padding: '10px 28px',
          color: INDIGO, fontSize: 36, fontWeight: 700, fontFamily: FONT,
        }}>
          STEP 2
        </div>
        <div style={{
          transform: `scale(${titleScale})`,
          color: WHITE, fontSize: 80, fontWeight: 800,
          fontFamily: FONT, textAlign: 'center',
        }}>
          Ask AI the right question
        </div>
      </div>

      {/* Middle block — chat mockup */}
      <div style={{
        transform: `scale(${chatScale})`,
        background: 'rgba(255,255,255,0.05)',
        border: '1px solid rgba(255,255,255,0.1)',
        borderRadius: 24,
        padding: 40,
        width: '100%',
      }}>
        <div style={{ marginBottom: 32 }}>
          <span style={{ color: GREEN, fontSize: 36, fontWeight: 700, fontFamily: FONT }}>You: </span>
          <span style={{ color: WHITE, fontSize: 36, fontFamily: FONT }}>{displayText}</span>
          <span style={{ color: INDIGO, opacity: charsToShow < promptText.length ? 1 : 0 }}>|</span>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {careers.map(({ delay, label }) => {
            const s = sp(frame, fps, delay);
            return (
              <div key={label} style={{
                transform: `scale(${s})`,
                display: 'flex', alignItems: 'center', gap: 16,
              }}>
                <span style={{ color: INDIGO, fontSize: 34, fontFamily: FONT }}>→</span>
                <span style={{ color: GREEN, fontSize: 34, fontFamily: FONT }}>{label}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Bottom block */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
        <div style={{
          transform: `scale(${warningScale})`,
          color: 'rgba(239,68,68,0.8)', fontSize: 40,
          fontFamily: FONT, textAlign: 'center',
        }}>
          Generic prompts = generic answers.
        </div>
        <div style={{
          transform: `scale(${mapScale})`,
          color: GREEN, fontSize: 44, fontWeight: 700,
          fontFamily: FONT, textAlign: 'center',
        }}>
          Specific fear + skills = your map.
        </div>
      </div>
    </div>
  );
};

// ─── Scene 4: "Step 3: Prototype Before You Quit" ───────────────────────────
const Scene4: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);
  const badgeScale = sp(frame, fps, 5);
  const titleScale = sp(frame, fps, 15);

  const nurseScale = sp(frame, fps, 20);
  const clockScale = sp(frame, fps, 25);
  const leftDescScale = sp(frame, fps, 35);

  const dividerHeight = interpolate(frame, [30, 70], [0, 600], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  const cards = [
    { delay: 60, icon: '📄', label: 'Business Plan' },
    { delay: 85, icon: '📝', label: 'Rewritten Resume' },
    { delay: 110, icon: '🔍', label: 'Market Research' },
  ];

  const bottomScale = sp(frame, fps, 125);
  const bottom2Scale = sp(frame, fps, 137);

  return (
    <div style={{
      position: 'absolute', inset: 0, opacity,
      display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
      alignItems: 'center',
      paddingTop: TOP_SAFE, paddingBottom: BOT_SAFE,
      paddingLeft: SIDE, paddingRight: SIDE,
    }}>
      {/* Top block */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20 }}>
        <div style={{
          transform: `scale(${badgeScale})`,
          background: 'rgba(99,102,241,0.2)', border: `1px solid ${INDIGO}`,
          borderRadius: 999, padding: '10px 28px',
          color: INDIGO, fontSize: 36, fontWeight: 700, fontFamily: FONT,
        }}>
          STEP 3
        </div>
        <div style={{
          transform: `scale(${titleScale})`,
          color: WHITE, fontSize: 88, fontWeight: 800,
          fontFamily: FONT, textAlign: 'center',
        }}>
          Prototype. Don't quit.
        </div>
      </div>

      {/* Middle block — horizontal split */}
      <div style={{
        display: 'flex', gap: 40, width: '100%', alignItems: 'stretch',
      }}>
        {/* LEFT column */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 32 }}>
          {/* Nurse stick figure */}
          <div style={{ transform: `scale(${nurseScale})` }}>
            <svg width={120} height={150} viewBox="0 0 120 150">
              <circle cx={60} cy={24} r={20} fill="none" stroke={WHITE} strokeWidth={3.5} />
              <line x1={60} y1={44} x2={60} y2={98} stroke={WHITE} strokeWidth={3.5} strokeLinecap="round" />
              <line x1={25} y1={68} x2={95} y2={68} stroke={WHITE} strokeWidth={3.5} strokeLinecap="round" />
              <line x1={60} y1={98} x2={32} y2={140} stroke={WHITE} strokeWidth={3.5} strokeLinecap="round" />
              <line x1={60} y1={98} x2={88} y2={140} stroke={WHITE} strokeWidth={3.5} strokeLinecap="round" />
              {/* Green cross on chest */}
              <line x1={50} y1={16} x2={70} y2={16} stroke={GREEN} strokeWidth={4} strokeLinecap="round" />
              <line x1={60} y1={6} x2={60} y2={26} stroke={GREEN} strokeWidth={4} strokeLinecap="round" />
            </svg>
          </div>

          {/* Clock + time */}
          <div style={{ transform: `scale(${clockScale})`, display: 'flex', alignItems: 'center', gap: 16 }}>
            <svg width={60} height={60} viewBox="0 0 60 60">
              <circle cx={30} cy={30} r={26} fill="none" stroke={INDIGO} strokeWidth={3} />
              <line x1={30} y1={30} x2={30} y2={10} stroke={INDIGO} strokeWidth={3} strokeLinecap="round" />
              <line x1={30} y1={30} x2={46} y2={40} stroke={INDIGO} strokeWidth={3} strokeLinecap="round" />
            </svg>
            <span style={{ color: INDIGO, fontSize: 52, fontWeight: 700, fontFamily: FONT }}>30 min</span>
          </div>

          {/* Left desc */}
          <div style={{
            transform: `scale(${leftDescScale})`,
            color: DIM, fontSize: 40,
            fontFamily: FONT, textAlign: 'center',
          }}>
            Before you hand in your badge
          </div>
        </div>

        {/* Vertical divider */}
        <div style={{
          width: 2, height: dividerHeight,
          background: 'rgba(99,102,241,0.3)',
          alignSelf: 'center',
          flexShrink: 0,
        }} />

        {/* RIGHT column */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 28 }}>
          {cards.map(({ delay, icon, label }) => {
            const s = sp(frame, fps, delay);
            return (
              <div key={label} style={{
                transform: `scale(${s})`,
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid rgba(34,197,94,0.3)',
                borderRadius: 16,
                padding: 28,
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                  <span style={{ fontSize: 40 }}>{icon}</span>
                  <span style={{ color: GREEN, fontSize: 36, fontWeight: 700, fontFamily: FONT }}>{label}</span>
                </div>
                <span style={{ color: GREEN, fontSize: 40, fontWeight: 700 }}>✓</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* Bottom block */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
        <div style={{
          transform: `scale(${bottomScale})`,
          color: WHITE, fontSize: 44, fontWeight: 700,
          fontFamily: FONT, textAlign: 'center',
        }}>
          No risk. No resignation letter.
        </div>
        <div style={{
          transform: `scale(${bottom2Scale})`,
          color: DIM, fontSize: 42,
          fontFamily: FONT, textAlign: 'center',
        }}>
          Just a map of what's possible.
        </div>
      </div>
    </div>
  );
};

// ─── Scene 5: CTA with particles ─────────────────────────────────────────────
const Scene5: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  const particleColors = [INDIGO, GREEN, AMBER];
  const particleXPositions = [90, 220, 340, 460, 580, 700, 820, 140, 280, 530, 650, 960];
  const particleSizes = [8, 6, 12, 5, 10, 7, 14, 6, 9, 11, 5, 8];
  const particles = Array.from({ length: 12 }, (_, i) => {
    const y = interpolate(frame, [0, 180], [1920 + i * 100, -200], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
    return { x: particleXPositions[i], y, size: particleSizes[i], color: particleColors[i % 3] };
  });

  const cursorOpacity = Math.sin(frame * 0.2) > 0 ? 1 : 0;

  const titleScale = sp(frame, fps, 10);
  const title2Scale = sp(frame, fps, 20);
  const bodyScale = sp(frame, fps, 50);
  const permScale = sp(frame, fps, 62);
  const promptScale = sp(frame, fps, 74);
  const urlScale = sp(frame, fps, 90);
  const brandScale = sp(frame, fps, 100);

  return (
    <div style={{ position: 'absolute', inset: 0, opacity, overflow: 'hidden' }}>
      {/* Particle background */}
      <svg width={1080} height={1920} style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
        {particles.map((p, i) => (
          <circle key={i} cx={p.x} cy={p.y} r={p.size / 2}
            fill={p.color} opacity={0.35} />
        ))}
      </svg>

      {/* Main content */}
      <div style={{
        position: 'absolute', inset: 0,
        display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
        alignItems: 'center',
        paddingTop: TOP_SAFE, paddingBottom: BOT_SAFE,
        paddingLeft: SIDE, paddingRight: SIDE,
        zIndex: 1,
      }}>
        {/* Top — blinking cursor */}
        <div style={{
          color: INDIGO, fontSize: 96,
          fontFamily: FONT, opacity: cursorOpacity,
          alignSelf: 'flex-start',
        }}>
          |
        </div>

        {/* Upper-middle — headline */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
          <div style={{
            transform: `scale(${titleScale})`,
            color: WHITE, fontSize: 80, fontWeight: 800,
            fontFamily: FONT, textAlign: 'center',
          }}>
            Your next chapter
          </div>
          <div style={{
            transform: `scale(${title2Scale})`,
            color: INDIGO, fontSize: 80, fontWeight: 800,
            fontFamily: FONT, textAlign: 'center',
          }}>
            starts with one prompt.
          </div>
        </div>

        {/* Lower-middle — body copy */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
          <div style={{
            transform: `scale(${bodyScale})`,
            color: DIM, fontSize: 44,
            fontFamily: FONT, textAlign: 'center',
          }}>
            Take the Fear Audit. Let AI show you what's possible.
          </div>
          <div style={{
            transform: `scale(${permScale})`,
            color: WHITE, fontSize: 48,
            fontFamily: FONT, textAlign: 'center',
          }}>
            You don't need permission.
          </div>
          <div style={{
            transform: `scale(${promptScale})`,
            color: GREEN, fontSize: 52, fontWeight: 800,
            fontFamily: FONT, textAlign: 'center',
          }}>
            You need a prompt.
          </div>
        </div>

        {/* Bottom — branding */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
          <div style={{
            transform: `scale(${urlScale})`,
            color: WHITE, fontSize: 60, fontWeight: 800,
            fontFamily: FONT, textAlign: 'center',
            textShadow: '0 0 20px rgba(99,102,241,0.8)',
          }}>
            crosswalkwisdom.com
          </div>
          <div style={{
            transform: `scale(${brandScale})`,
            color: DIM, fontSize: 32,
            fontFamily: FONT, letterSpacing: 6,
            textAlign: 'center',
          }}>
            CROSSWALK WISDOM
          </div>
        </div>
      </div>
    </div>
  );
};

// ─── Main Export ──────────────────────────────────────────────────────────────
export const AIBridgeExplainer: React.FC = () => {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();
  const progressWidth = interpolate(frame, [0, TOTAL], [0, 1080 - 2 * SIDE], { extrapolateRight: 'clamp' });

  return (
    <div style={{ width: 1080, height: 1920, background: BG, overflow: 'hidden', fontFamily: FONT, position: 'relative' }}>
      <Audio src={staticFile('voiceover-ai-bridge.wav')} volume={1.0} />
      <Audio src={staticFile('music.mp3')} volume={0.07} loop />
      <Sequence from={0} durationInFrames={SCENE_FRAMES}><Scene1 frame={frame} fps={fps} /></Sequence>
      <Sequence from={SCENE_FRAMES} durationInFrames={SCENE_FRAMES}><Scene2 frame={frame - SCENE_FRAMES} fps={fps} /></Sequence>
      <Sequence from={SCENE_FRAMES * 2} durationInFrames={SCENE_FRAMES}><Scene3 frame={frame - SCENE_FRAMES * 2} fps={fps} /></Sequence>
      <Sequence from={SCENE_FRAMES * 3} durationInFrames={SCENE_FRAMES}><Scene4 frame={frame - SCENE_FRAMES * 3} fps={fps} /></Sequence>
      <Sequence from={SCENE_FRAMES * 4} durationInFrames={SCENE_FRAMES}><Scene5 frame={frame - SCENE_FRAMES * 4} fps={fps} /></Sequence>
      <div style={{
        position: 'absolute',
        bottom: BOT_SAFE - 30,
        left: SIDE,
        width: progressWidth,
        height: 6,
        background: INDIGO,
        borderRadius: 3,
        boxShadow: `0 0 10px ${INDIGO}80`,
      }} />
    </div>
  );
};
