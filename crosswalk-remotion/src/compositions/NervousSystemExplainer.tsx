/**
 * "Why Your Body Blocks Career Change" — Educational Explainer (1080×1920, 30fps, 30s = 900 frames)
 *
 * 5 scenes × ~180 frames each with 12-frame fade transitions.
 * Visual style: dark (#0a0a0a), indigo accent, green emphasis, Inter font.
 * All icons/diagrams are inline SVG — no external assets needed.
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

// ─── Constants ────────────────────────────────────────────────────────────────
const BG     = '#0a0a0a';
const INDIGO  = '#6366f1';
const GREEN   = '#22c55e';
const RED     = '#ef4444';
const AMBER   = '#f59e0b';
const BLUE    = '#3b82f6';
const WHITE   = '#ffffff';
const DIM     = 'rgba(255,255,255,0.5)';
const FONT    = '"Inter", system-ui, sans-serif';

const SCENE_FRAMES = 180;   // 6 s per scene
const FADE         = 12;    // cross-fade overlap
const TOTAL        = 900;   // 30 s at 30 fps

const TOP_SAFE = 150;
const BOT_SAFE = 170;
const SIDE     = 60;

// ─── Helpers ──────────────────────────────────────────────────────────────────
const sp = (frame: number, fps: number, delay = 0) =>
  spring({ frame: frame - delay, fps, config: { damping: 200 } });

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));

const fadeInOut = (localFrame: number, dur: number) => {
  const fadeIn  = interpolate(localFrame, [0, FADE],        [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const fadeOut = interpolate(localFrame, [dur - FADE, dur],[1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return fadeIn * fadeOut;
};

// ─── Scene 1: "Why You're Stuck" ─────────────────────────────────────────────
const Scene1: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  // Road-block sign morphs into brain
  const morphProgress  = sp(frame, fps, 20);
  const signOpacity    = interpolate(morphProgress, [0, 0.6, 1], [1, 1, 0], { extrapolateRight: 'clamp' });
  const brainOpacity   = interpolate(morphProgress, [0.5, 1],    [0, 1],    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const brainScale     = sp(frame, fps, 55);
  const pulse          = interpolate(frame % 40, [0, 20, 40], [1, 1.05, 1]);

  // Text
  const titleIn = sp(frame, fps, 50);
  const bodyIn  = sp(frame, fps, 70);

  // "BLOCKED" tag that fades in under brain
  const tagIn = sp(frame, fps, 90);

  return (
    <div style={{ opacity, width: '100%', height: '100%', position: 'absolute' }}>

      {/* Icon area — explicit 260×260 stacking container */}
      <div style={{ position: 'absolute', top: TOP_SAFE + 180, left: 0, right: 0, display: 'flex', justifyContent: 'center' }}>
        <div style={{ position: 'relative', width: 260, height: 260 }}>

          {/* Road block sign — absolutely stacked, centered */}
          <div style={{
            position: 'absolute', top: 0, left: 0, width: 260, height: 260,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            opacity: signOpacity,
            transform: `scale(${1 + morphProgress * 0.15})`,
          }}>
            <svg width="220" height="220" viewBox="0 0 100 110">
              <polygon points="30,10 70,10 90,30 90,70 70,90 30,90 10,70 10,30" fill="#1c1917" stroke={RED} strokeWidth="3" />
              <rect x="20" y="44" width="60" height="12" rx="6" fill={RED} />
              <rect x="46" y="90" width="8" height="20" fill={RED} opacity={0.6} />
            </svg>
          </div>

          {/* Brain SVG — absolutely stacked, centered */}
          <div style={{
            position: 'absolute', top: 0, left: 0, width: 260, height: 260,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            opacity: brainOpacity,
            transform: `scale(${brainScale * pulse})`,
          }}>
            <svg width="220" height="200" viewBox="0 0 110 100" fill="none">
              <path d="M55 12 C28 12 10 30 10 52 C10 74 30 88 55 88 C80 88 100 74 100 52 C100 30 82 12 55 12Z"
                stroke={INDIGO} strokeWidth="2.5" fill="none"
                strokeDasharray="300" strokeDashoffset={interpolate(brainOpacity, [0, 1], [300, 0])} />
              <path d="M55 18 C42 35 38 55 55 68 M55 18 C68 35 72 55 55 68"
                stroke={INDIGO} strokeWidth="1.8" fill="none" opacity={brainOpacity}
                strokeDasharray="100" strokeDashoffset={interpolate(brainOpacity, [0, 1], [100, 0])} />
              <line x1="55" y1="14" x2="55" y2="86" stroke={INDIGO} strokeWidth="1.2" opacity={brainOpacity * 0.4} />
              <circle cx="38" cy="55" r="7" fill={`${INDIGO}30`} stroke={INDIGO} strokeWidth="1.5" opacity={brainOpacity} />
              <circle cx="72" cy="55" r="7" fill={`${INDIGO}30`} stroke={INDIGO} strokeWidth="1.5" opacity={brainOpacity} />
            </svg>
          </div>

        </div>
      </div>

      {/* PROTECTED tag */}
      <div style={{
        position: 'absolute',
        top: TOP_SAFE + 400,
        left: 0, right: 0,
        display: 'flex', justifyContent: 'center',
        opacity: tagIn,
        transform: `scale(${tagIn})`,
      }}>
        <div style={{
          background: `${RED}20`,
          border: `2px solid ${RED}`,
          borderRadius: 40,
          padding: '10px 32px',
        }}>
          <span style={{ fontFamily: FONT, fontSize: 30, fontWeight: 700, color: RED, letterSpacing: 2 }}>
            BLOCKED
          </span>
        </div>
      </div>

      {/* Title */}
      <div style={{
        position: 'absolute',
        top: TOP_SAFE + 490,
        left: SIDE, right: SIDE,
        textAlign: 'center',
        opacity: titleIn,
        transform: `translateY(${(1 - titleIn) * 40}px)`,
      }}>
        <span style={{ fontFamily: FONT, fontSize: 76, fontWeight: 800, color: WHITE, lineHeight: 1.05 }}>
          Why You're{' '}
          <span style={{ color: INDIGO }}>Stuck</span>
        </span>
      </div>

      {/* Body */}
      <div style={{
        position: 'absolute',
        top: TOP_SAFE + 620,
        left: SIDE + 20, right: SIDE + 20,
        textAlign: 'center',
        opacity: bodyIn,
        transform: `translateY(${(1 - bodyIn) * 30}px)`,
      }}>
        <span style={{ fontFamily: FONT, fontSize: 38, fontWeight: 400, color: DIM, lineHeight: 1.5 }}>
          You want to leave. You know something{'\n'}needs to change. But every time you get{'\n'}close — something stops you.
        </span>
      </div>

      {/* Bottom note */}
      <div style={{
        position: 'absolute',
        bottom: BOT_SAFE + 80,
        left: SIDE, right: SIDE,
        textAlign: 'center',
        opacity: sp(frame, fps, 110),
      }}>
        <span style={{ fontFamily: FONT, fontSize: 36, fontWeight: 600, color: WHITE, fontStyle: 'italic' }}>
          Your nervous system is why.
        </span>
      </div>
    </div>
  );
};

// ─── Scene 2: "Your Brain's Safety Scanner" ──────────────────────────────────
const Scene2: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);
  const titleIn = sp(frame, fps, 5);

  // Flowchart draw progress — 4 nodes
  const node1  = sp(frame, fps, 20);
  const arr1   = clamp01(interpolate(frame, [35, 55],  [0, 1]));
  const node2  = sp(frame, fps, 50);
  const arr2   = clamp01(interpolate(frame, [65, 85],  [0, 1]));
  const node3  = sp(frame, fps, 80);
  const arr3   = clamp01(interpolate(frame, [95, 115], [0, 1]));
  const node4  = sp(frame, fps, 110);

  // Count-up: 12ms
  const countVal = Math.round(interpolate(frame, [115, 155], [0, 12], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }));
  const countIn  = sp(frame, fps, 112);

  return (
    <div style={{ opacity, width: '100%', height: '100%', position: 'absolute' }}>

      {/* Title */}
      <div style={{
        position: 'absolute',
        top: TOP_SAFE + 30,
        left: SIDE, right: SIDE,
        textAlign: 'center',
        opacity: titleIn,
        transform: `translateY(${(1 - titleIn) * 30}px)`,
      }}>
        <span style={{ fontFamily: FONT, fontSize: 58, fontWeight: 800, color: WHITE }}>
          Your Brain's{' '}
          <span style={{ color: INDIGO }}>Safety Scanner</span>
        </span>
      </div>

      {/* Flowchart — viewBox tall enough to show all 4 nodes without clipping */}
      <div style={{ position: 'absolute', top: TOP_SAFE + 180, left: 0, right: 0 }}>
        <svg width={1080} height={680} viewBox="0 0 1080 680">

          {/* Node 1: New Goal */}
          <g opacity={node1} transform={`translate(0, ${(1 - node1) * -20})`}>
            <rect x="340" y="20" width="400" height="80" rx="18" fill={INDIGO} />
            <text x="540" y="70" textAnchor="middle" fill={WHITE} fontSize="34" fontFamily={FONT} fontWeight="700">New Goal</text>
          </g>

          {/* Arrow 1 */}
          <line x1="540" y1="100" x2="540" y2={100 + arr1 * 80} stroke={INDIGO} strokeWidth="3"
            strokeDasharray="80" strokeDashoffset={80 - arr1 * 80} />
          <polygon points="528,175 540,192 552,175" fill={INDIGO} opacity={arr1} />

          {/* Node 2: Safety Scan */}
          <g opacity={node2} transform={`translate(${(1 - node2) * -30}, 0)`}>
            <rect x="280" y="192" width="520" height="80" rx="18" fill="#1e1b4b" stroke={INDIGO} strokeWidth="2" />
            <text x="540" y="242" textAnchor="middle" fill={INDIGO} fontSize="34" fontFamily={FONT} fontWeight="700">Safety Scan</text>
          </g>

          {/* Arrow 2 */}
          <line x1="540" y1="272" x2="540" y2={272 + arr2 * 90} stroke={INDIGO} strokeWidth="3"
            strokeDasharray="90" strokeDashoffset={90 - arr2 * 90} />
          <polygon points="528,357 540,374 552,357" fill={INDIGO} opacity={arr2} />

          {/* Node 3: Past Pain Database */}
          <g opacity={node3} transform={`translate(${(1 - node3) * 30}, 0)`}>
            <rect x="200" y="374" width="680" height="80" rx="18" fill="#1c1917" stroke={AMBER} strokeWidth="2" />
            <text x="540" y="424" textAnchor="middle" fill={AMBER} fontSize="30" fontFamily={FONT} fontWeight="700">Past Pain Database</text>
          </g>

          {/* Arrow 3 */}
          <line x1="540" y1="454" x2="540" y2={454 + arr3 * 80} stroke={RED} strokeWidth="3"
            strokeDasharray="80" strokeDashoffset={80 - arr3 * 80} />
          <polygon points="528,529 540,546 552,529" fill={RED} opacity={arr3} />

          {/* Node 4: BLOCKED */}
          <g opacity={node4} transform={`translate(0, ${(1 - node4) * 20})`}>
            <rect x="340" y="546" width="400" height="90" rx="18" fill={`${RED}20`} stroke={RED} strokeWidth="3" />
            <text x="540" y="603" textAnchor="middle" fill={RED} fontSize="42" fontFamily={FONT} fontWeight="800" letterSpacing="4">
              BLOCKED
            </text>
          </g>
        </svg>
      </div>

      {/* Count-up */}
      <div style={{
        position: 'absolute',
        bottom: BOT_SAFE + 60,
        left: SIDE, right: SIDE,
        textAlign: 'center',
        opacity: countIn,
      }}>
        <span style={{ fontFamily: FONT, fontSize: 96, fontWeight: 800, color: GREEN, fontVariantNumeric: 'tabular-nums' }}>
          {countVal}ms
        </span>
        <br />
        <span style={{ fontFamily: FONT, fontSize: 36, fontWeight: 400, color: DIM }}>
          Faster than conscious thought
        </span>
      </div>
    </div>
  );
};

// ─── Scene 3: "3 Flavors of Stuck" ───────────────────────────────────────────
const Scene3: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);
  const titleIn = sp(frame, fps, 5);

  const cards = [
    {
      label: 'ANXIETY',
      color: RED,
      icon: '⚡',
      desc: 'Racing thoughts\nFrantic action\nCan\'t slow down',
    },
    {
      label: 'SHUTDOWN',
      color: BLUE,
      icon: '🌫',
      desc: 'Numbness\nCan\'t start\nEmotional flatness',
    },
    {
      label: 'FREEZE',
      color: INDIGO,
      icon: '🔒',
      desc: '"I have to,\nbut I can\'t"\nParalysis',
    },
  ];

  const cardSprings = [
    sp(frame, fps, 30),
    sp(frame, fps, 45),
    sp(frame, fps, 60),
  ];

  const xOffsets = [-50, 0, 50];

  const labelIn = sp(frame, fps, 120);

  return (
    <div style={{ opacity, width: '100%', height: '100%', position: 'absolute' }}>

      {/* Title */}
      <div style={{
        position: 'absolute',
        top: TOP_SAFE + 30,
        left: SIDE, right: SIDE,
        textAlign: 'center',
        opacity: titleIn,
        transform: `translateY(${(1 - titleIn) * 30}px)`,
      }}>
        <span style={{ fontFamily: FONT, fontSize: 60, fontWeight: 800, color: WHITE }}>
          3 Flavors of{' '}
          <span style={{ color: INDIGO }}>Stuck</span>
        </span>
      </div>

      {/* Cards */}
      {cards.map((card, i) => {
        const s = cardSprings[i];
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              top: TOP_SAFE + 160 + i * 320,
              left: SIDE,
              right: SIDE,
              opacity: s,
              transform: `translateX(${(1 - s) * xOffsets[i]}px)`,
              background: '#111111',
              border: `2px solid ${card.color}`,
              borderRadius: 24,
              padding: '28px 36px',
              display: 'flex',
              alignItems: 'center',
              gap: 28,
            }}
          >
            {/* Color bar */}
            <div style={{ width: 8, alignSelf: 'stretch', background: card.color, borderRadius: 4, flexShrink: 0 }} />

            {/* Icon */}
            <div style={{ fontSize: 56, flexShrink: 0 }}>{card.icon}</div>

            {/* Text */}
            <div style={{ flex: 1 }}>
              <div style={{ fontFamily: FONT, fontSize: 38, fontWeight: 800, color: card.color, marginBottom: 8, letterSpacing: 1 }}>
                {card.label}
              </div>
              {card.desc.split('\n').map((line, li) => (
                <div key={li} style={{ fontFamily: FONT, fontSize: 30, fontWeight: 400, color: DIM, lineHeight: 1.4 }}>
                  {line}
                </div>
              ))}
            </div>
          </div>
        );
      })}

      {/* Bottom label */}
      <div style={{
        position: 'absolute',
        bottom: BOT_SAFE + 50,
        left: SIDE, right: SIDE,
        textAlign: 'center',
        opacity: labelIn,
      }}>
        <div style={{
          display: 'inline-block',
          background: `${GREEN}15`,
          border: `2px solid ${GREEN}`,
          borderRadius: 16,
          padding: '14px 36px',
        }}>
          <span style={{ fontFamily: FONT, fontSize: 34, fontWeight: 700, color: GREEN }}>
            None of these are failure.
          </span>
        </div>
      </div>
    </div>
  );
};

// ─── Scene 4: "The Loop That Traps You" ──────────────────────────────────────
const Scene4: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);
  const titleIn = sp(frame, fps, 5);

  const nodes = [
    { label: 'Dream',      color: GREEN },
    { label: 'Alarm',      color: RED },
    { label: 'Protection', color: AMBER },
    { label: 'Avoidance',  color: INDIGO },
    { label: 'Shame',      color: '#ec4899' },
  ];

  // 1:1 SVG viewBox — center the ring within a 1080×1000 canvas
  const cx = 540;
  const cy = 480;
  const rx = 340;
  const ry = 340;

  const positions = nodes.map((_, i) => {
    const angle = (i / nodes.length) * Math.PI * 2 - Math.PI / 2;
    return { x: cx + rx * Math.cos(angle), y: cy + ry * Math.sin(angle) };
  });

  const captionIn = sp(frame, fps, 120);

  return (
    <div style={{ opacity, width: '100%', height: '100%', position: 'absolute' }}>

      {/* Title */}
      <div style={{
        position: 'absolute',
        top: TOP_SAFE + 30,
        left: SIDE, right: SIDE,
        textAlign: 'center',
        opacity: titleIn,
        transform: `translateY(${(1 - titleIn) * 30}px)`,
      }}>
        <span style={{ fontFamily: FONT, fontSize: 58, fontWeight: 800, color: WHITE }}>
          The Loop That{' '}
          <span style={{ color: INDIGO }}>Traps You</span>
        </span>
      </div>

      {/* Cycle diagram — 1:1 viewBox so nodes never clip */}
      <div style={{ position: 'absolute', top: TOP_SAFE + 120, left: 0, right: 0 }}>
        <svg width={1080} height={1000} viewBox="0 0 1080 1000">

          {/* Arrows */}
          {positions.map((pos, i) => {
            const next  = positions[(i + 1) % nodes.length];
            const delay = 25 + i * 14;
            const prog  = clamp01(interpolate(frame, [delay + 15, delay + 38], [0, 1]));
            return (
              <line
                key={`arr-${i}`}
                x1={pos.x} y1={pos.y}
                x2={pos.x + (next.x - pos.x) * prog}
                y2={pos.y + (next.y - pos.y) * prog}
                stroke={nodes[i].color}
                strokeWidth="3.5"
                opacity={0.65}
              />
            );
          })}

          {/* Nodes */}
          {nodes.map((node, i) => {
            const pos      = positions[i];
            const delay    = 20 + i * 14;
            const ns       = sp(frame, fps, delay);
            const isActive = frame > 90 && Math.floor((frame - 90) / 18) % nodes.length === i;
            return (
              <g key={i} opacity={ns} transform={`translate(${pos.x}, ${pos.y}) scale(${ns * (isActive ? 1.12 : 1)})`}>
                <circle r="90" fill="#1a1a1a" stroke={node.color} strokeWidth={isActive ? 4 : 2.5} />
                {isActive && (
                  <circle r="90" fill="none" stroke={node.color} strokeWidth="2" opacity={0.3}>
                    <animate attributeName="r"       from="90"  to="112" dur="0.8s" repeatCount="indefinite" />
                    <animate attributeName="opacity" from="0.3" to="0"   dur="0.8s" repeatCount="indefinite" />
                  </circle>
                )}
                <text x="0" y="12" textAnchor="middle" fill={node.color} fontSize="32" fontFamily={FONT} fontWeight="700">
                  {node.label}
                </text>
              </g>
            );
          })}

          {/* Center label */}
          <text x={cx} y={cy + 12} textAnchor="middle" fill={DIM} fontSize="32" fontFamily={FONT} fontWeight="600" opacity={sp(frame, fps, 95)}>
            ∞ REPEAT
          </text>
        </svg>
      </div>

      {/* Caption */}
      <div style={{
        position: 'absolute',
        bottom: BOT_SAFE + 50,
        left: SIDE + 20, right: SIDE + 20,
        textAlign: 'center',
        opacity: captionIn,
      }}>
        <span style={{ fontFamily: FONT, fontSize: 34, fontWeight: 400, color: DIM, lineHeight: 1.5 }}>
          This isn't a mindset problem.{'\n'}It's biology.
        </span>
      </div>
    </div>
  );
};

// ─── Scene 5: "Break the Loop" + Particles ────────────────────────────────────
const PARTICLES = Array.from({ length: 14 }, (_, i) => ({
  x:       80 + (i * 73) % 920,
  size:    6  + (i % 5) * 4,
  speed:   0.6 + (i % 4) * 0.3,
  delay:   (i * 7) % 30,
  opacity: 0.07 + (i % 5) * 0.04,
}));

const Scene5: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);
  const titleIn = sp(frame, fps, 5);

  const steps = [
    { num: '1', label: 'Name It',        desc: '"This is protection, not failure."', color: INDIGO },
    { num: '2', label: 'Regulate First', desc: 'Breathe, ground, rest — before deciding.', color: AMBER },
    { num: '3', label: 'Act Small',      desc: 'Safety is built through experience, not logic.', color: GREEN },
  ];

  const shatterProg = clamp01(interpolate(frame, [10, 40], [0, 1]));
  const ctaIn       = sp(frame, fps, 130);

  return (
    <div style={{ opacity, width: '100%', height: '100%', position: 'absolute' }}>

      {/* Particles */}
      {PARTICLES.map((p, i) => {
        const yOffset = ((frame + p.delay) * p.speed * 2) % 2000;
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: p.x,
              bottom: -20 + yOffset,
              width: p.size,
              height: p.size,
              borderRadius: '50%',
              backgroundColor: i % 3 === 0 ? INDIGO : i % 3 === 1 ? GREEN : AMBER,
              opacity: p.opacity,
            }}
          />
        );
      })}

      {/* Shattering loop ring */}
      {shatterProg < 1 && (
        <div style={{
          position: 'absolute',
          top: TOP_SAFE + 100,
          left: 0, right: 0,
          display: 'flex',
          justifyContent: 'center',
          opacity: 1 - shatterProg,
          transform: `scale(${1 + shatterProg * 0.4})`,
        }}>
          <svg width="140" height="140" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="none" stroke={INDIGO} strokeWidth="3"
              strokeDasharray={`${10 + shatterProg * 20} ${5 + shatterProg * 15}`} />
            {[0, 72, 144, 216, 288].map((angle, ci) => (
              <line key={ci}
                x1={50 + 35 * Math.cos((angle * Math.PI) / 180)}
                y1={50 + 35 * Math.sin((angle * Math.PI) / 180)}
                x2={50 + (35 + shatterProg * 35) * Math.cos((angle * Math.PI) / 180)}
                y2={50 + (35 + shatterProg * 35) * Math.sin((angle * Math.PI) / 180)}
                stroke={RED} strokeWidth="2" opacity={shatterProg}
              />
            ))}
          </svg>
        </div>
      )}

      {/* Title */}
      <div style={{
        position: 'absolute',
        top: TOP_SAFE + 60,
        left: SIDE, right: SIDE,
        textAlign: 'center',
        opacity: titleIn,
        transform: `translateY(${(1 - titleIn) * 30}px)`,
      }}>
        <span style={{ fontFamily: FONT, fontSize: 68, fontWeight: 800, color: WHITE }}>
          Break The{' '}
          <span style={{ color: GREEN }}>Loop</span>
        </span>
      </div>

      {/* Steps */}
      {steps.map((step, i) => {
        const stepIn = sp(frame, fps, 50 + i * 14);
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              top: TOP_SAFE + 270 + i * 230,
              left: SIDE + 10,
              right: SIDE + 10,
              opacity: stepIn,
              transform: `translateX(${(1 - stepIn) * 60}px)`,
              display: 'flex',
              alignItems: 'center',
              gap: 28,
            }}
          >
            {/* Number circle */}
            <div style={{
              width: 84,
              height: 84,
              borderRadius: '50%',
              border: `3px solid ${step.color}`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
              background: `${step.color}15`,
            }}>
              <span style={{ fontFamily: FONT, fontSize: 42, fontWeight: 800, color: step.color }}>{step.num}</span>
            </div>

            {/* Text */}
            <div>
              <div style={{ fontFamily: FONT, fontSize: 44, fontWeight: 700, color: WHITE, marginBottom: 6 }}>
                {step.label}
              </div>
              <div style={{ fontFamily: FONT, fontSize: 32, fontWeight: 400, color: DIM, lineHeight: 1.4 }}>
                {step.desc}
              </div>
            </div>
          </div>
        );
      })}

      {/* CTA */}
      <div style={{
        position: 'absolute',
        bottom: BOT_SAFE + 50,
        left: SIDE, right: SIDE,
        textAlign: 'center',
        opacity: ctaIn,
        transform: `scale(${ctaIn})`,
      }}>
        <div style={{
          display: 'inline-block',
          background: `${GREEN}20`,
          border: `2px solid ${GREEN}`,
          borderRadius: 18,
          padding: '18px 44px',
        }}>
          <span style={{ fontFamily: FONT, fontSize: 36, fontWeight: 700, color: GREEN }}>
            Take the Fear Audit — Link in bio
          </span>
        </div>
      </div>
    </div>
  );
};

// ─── Progress bar ─────────────────────────────────────────────────────────────
const ProgressBar: React.FC<{ frame: number }> = ({ frame }) => (
  <div style={{
    position: 'absolute',
    bottom: BOT_SAFE - 30,
    left: SIDE,
    right: SIDE,
    height: 4,
    backgroundColor: 'rgba(255,255,255,0.1)',
    borderRadius: 2,
    zIndex: 100,
  }}>
    <div style={{
      height: '100%',
      width: `${(frame / TOTAL) * 100}%`,
      backgroundColor: INDIGO,
      borderRadius: 2,
    }} />
  </div>
);

// ─── Main composition ─────────────────────────────────────────────────────────
export const NervousSystemExplainer: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scenes = [
    { start: 0,                          Component: Scene1 },
    { start: (SCENE_FRAMES - FADE) * 1,  Component: Scene2 },
    { start: (SCENE_FRAMES - FADE) * 2,  Component: Scene3 },
    { start: (SCENE_FRAMES - FADE) * 3,  Component: Scene4 },
    { start: (SCENE_FRAMES - FADE) * 4,  Component: Scene5 },
  ];

  return (
    <div style={{
      width: 1080,
      height: 1920,
      backgroundColor: BG,
      position: 'relative',
      overflow: 'hidden',
      fontFamily: FONT,
    }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');`}</style>

      <Audio src={staticFile('voiceover-nervous-system.wav')} volume={1.0} />
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
