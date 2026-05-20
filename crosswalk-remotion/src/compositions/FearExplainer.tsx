/**
 * "The Fear" — Educational Explainer (1080×1920, 30fps, 30s = 900 frames)
 *
 * 5 scenes × ~180 frames each with TransitionSeries-style fade transitions.
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

// ─── Constants ──────────────────────────────────────────────────────────────────
const BG = '#0a0a0a';
const INDIGO = '#6366f1';
const GREEN = '#22c55e';
const WHITE = '#ffffff';
const DIM = 'rgba(255,255,255,0.5)';
const FONT = '"Inter", system-ui, sans-serif';

const SCENE_FRAMES = 180; // 6 seconds per scene
const FADE = 12; // fade-transition overlap in frames
const TOTAL = 900; // 30s at 30fps

// Safe-zone insets
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

// ─── Scene 1: "What Is The Fear?" ───────────────────────────────────────────────
const Scene1: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  // Question mark morph to brain
  const morphProgress = sp(frame, fps, 30);
  const questionOpacity = interpolate(morphProgress, [0, 0.5, 1], [1, 1, 0], {
    extrapolateRight: 'clamp',
  });
  const brainOpacity = interpolate(morphProgress, [0.4, 1], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const brainScale = sp(frame, fps, 50);

  // Title
  const titleSpring = sp(frame, fps, 40);

  // Subtitle
  const subSpring = sp(frame, fps, 60);

  // Pulse on brain
  const pulse = interpolate(frame % 30, [0, 15, 30], [1, 1.06, 1]);

  return (
    <div style={{ opacity, width: '100%', height: '100%', position: 'absolute' }}>
      {/* Question mark / Brain icon */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 200,
          left: 0,
          right: 0,
          display: 'flex',
          justifyContent: 'center',
        }}
      >
        {/* Question Mark */}
        <div
          style={{
            position: 'absolute',
            opacity: questionOpacity,
            transform: `scale(${1 + morphProgress * 0.2})`,
            fontFamily: FONT,
            fontSize: 280,
            fontWeight: 800,
            color: INDIGO,
            textShadow: `0 0 60px ${INDIGO}80`,
          }}
        >
          ?
        </div>
        {/* Brain SVG */}
        <div
          style={{
            opacity: brainOpacity,
            transform: `scale(${brainScale * pulse})`,
          }}
        >
          <svg width="200" height="200" viewBox="0 0 100 100" fill="none">
            {/* Left hemisphere */}
            <path
              d="M50 20 C30 20 15 35 15 50 C15 70 30 85 50 85"
              stroke={INDIGO}
              strokeWidth="3"
              fill="none"
              strokeDasharray="200"
              strokeDashoffset={interpolate(brainOpacity, [0, 1], [200, 0])}
            />
            {/* Right hemisphere */}
            <path
              d="M50 20 C70 20 85 35 85 50 C85 70 70 85 50 85"
              stroke={INDIGO}
              strokeWidth="3"
              fill="none"
              strokeDasharray="200"
              strokeDashoffset={interpolate(brainOpacity, [0, 1], [200, 0])}
            />
            {/* Internal folds */}
            <path
              d="M50 25 C40 40 35 55 50 65 M50 25 C60 40 65 55 50 65"
              stroke={INDIGO}
              strokeWidth="2"
              fill="none"
              opacity={brainOpacity}
              strokeDasharray="120"
              strokeDashoffset={interpolate(brainOpacity, [0, 1], [120, 0])}
            />
            {/* Amygdala highlight */}
            <circle
              cx="42"
              cy="55"
              r="6"
              fill={`${INDIGO}40`}
              stroke={INDIGO}
              strokeWidth="1.5"
              opacity={brainOpacity}
            />
            <circle
              cx="58"
              cy="55"
              r="6"
              fill={`${INDIGO}40`}
              stroke={INDIGO}
              strokeWidth="1.5"
              opacity={brainOpacity}
            />
          </svg>
        </div>
      </div>

      {/* Title */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 500,
          left: SIDE,
          right: SIDE,
          textAlign: 'center',
          transform: `translateY(${(1 - titleSpring) * 40}px)`,
          opacity: titleSpring,
        }}
      >
        <span
          style={{
            fontFamily: FONT,
            fontSize: 72,
            fontWeight: 800,
            color: WHITE,
            lineHeight: 1.1,
          }}
        >
          What Is{' '}
          <span style={{ color: INDIGO }}>The Fear</span>?
        </span>
      </div>

      {/* Subtitle */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 620,
          left: SIDE + 20,
          right: SIDE + 20,
          textAlign: 'center',
          opacity: subSpring,
          transform: `translateY(${(1 - subSpring) * 30}px)`,
        }}
      >
        <span
          style={{
            fontFamily: FONT,
            fontSize: 38,
            fontWeight: 400,
            color: DIM,
            lineHeight: 1.4,
          }}
        >
          It's not cowardice. It's your brain{'\n'}doing its oldest job — keeping you alive.
        </span>
      </div>
    </div>
  );
};

// ─── Scene 2: "Your Brain's Alarm System" ───────────────────────────────────────
const Scene2: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  const titleIn = sp(frame, fps, 5);

  // Brain with amygdala glow
  const brainDraw = clamp01(interpolate(frame, [15, 60], [0, 1]));

  // Flowchart nodes staggered
  const node1 = sp(frame, fps, 50);
  const node2 = sp(frame, fps, 60);
  const node3 = sp(frame, fps, 70);
  const node4 = sp(frame, fps, 80);
  const node5 = sp(frame, fps, 90);

  // Arrow draw progress
  const arrowDraw1 = clamp01(interpolate(frame, [60, 78], [0, 1]));
  const arrowDraw2 = clamp01(interpolate(frame, [70, 88], [0, 1]));
  const arrowDraw3 = clamp01(interpolate(frame, [85, 103], [0, 1]));

  // Count-up: 12ms
  const countVal = Math.round(
    interpolate(frame, [100, 140], [0, 12], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    })
  );
  const countOpacity = sp(frame, fps, 95);

  return (
    <div style={{ opacity, width: '100%', height: '100%', position: 'absolute' }}>
      {/* Title */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 40,
          left: SIDE,
          right: SIDE,
          textAlign: 'center',
          opacity: titleIn,
          transform: `translateY(${(1 - titleIn) * 30}px)`,
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 56, fontWeight: 800, color: WHITE }}>
          Your Brain's{' '}
          <span style={{ color: INDIGO }}>Alarm System</span>
        </span>
      </div>

      {/* Brain SVG — centered */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 160,
          left: 0,
          right: 0,
          display: 'flex',
          justifyContent: 'center',
        }}
      >
        <svg width="220" height="180" viewBox="0 0 110 90" fill="none">
          <path
            d="M55 10 C30 10 10 30 10 50 C10 72 30 85 55 85 C80 85 100 72 100 50 C100 30 80 10 55 10Z"
            stroke={INDIGO}
            strokeWidth="2.5"
            fill="none"
            strokeDasharray="300"
            strokeDashoffset={300 - brainDraw * 300}
          />
          {/* Amygdala — glowing */}
          <circle cx="45" cy="52" r="8" fill={`${INDIGO}50`} stroke={INDIGO} strokeWidth="2" opacity={brainDraw}>
            <animate attributeName="r" values="8;10;8" dur="1.5s" repeatCount="indefinite" />
          </circle>
          <text
            x="45"
            y="56"
            textAnchor="middle"
            fill={WHITE}
            fontSize="6"
            fontFamily={FONT}
            fontWeight="600"
            opacity={brainDraw}
          >
            AMY
          </text>
        </svg>
      </div>

      {/* Flowchart: Stimulus → Amygdala → Fight / Flight / Freeze */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 420,
          left: SIDE,
          right: SIDE,
        }}
      >
        <svg width={960} height={380} viewBox="0 0 960 380">
          {/* Stimulus node */}
          <g opacity={node1} transform={`translate(${(1 - node1) * 20}, 0)`}>
            <rect x="350" y="10" width="260" height="70" rx="16" fill={INDIGO} />
            <text x="480" y="55" textAnchor="middle" fill={WHITE} fontSize="32" fontFamily={FONT} fontWeight="600">
              Stimulus
            </text>
          </g>

          {/* Arrow 1 */}
          <line
            x1="480"
            y1="80"
            x2="480"
            y2="140"
            stroke={INDIGO}
            strokeWidth="3"
            strokeDasharray="60"
            strokeDashoffset={60 - arrowDraw1 * 60}
          />
          <polygon
            points="470,135 480,150 490,135"
            fill={INDIGO}
            opacity={arrowDraw1}
          />

          {/* Amygdala node */}
          <g opacity={node2} transform={`translate(${(1 - node2) * 20}, 0)`}>
            <rect x="330" y="150" width="300" height="70" rx="16" fill="#1e1b4b" stroke={INDIGO} strokeWidth="2" />
            <text x="480" y="195" textAnchor="middle" fill={INDIGO} fontSize="32" fontFamily={FONT} fontWeight="700">
              Amygdala
            </text>
          </g>

          {/* Arrow 2 — splits into 3 */}
          <line x1="380" y1="220" x2="200" y2="290" stroke={INDIGO} strokeWidth="2.5" strokeDasharray="120" strokeDashoffset={120 - arrowDraw2 * 120} />
          <line x1="480" y1="220" x2="480" y2="290" stroke={INDIGO} strokeWidth="2.5" strokeDasharray="70" strokeDashoffset={70 - arrowDraw2 * 70} />
          <line x1="580" y1="220" x2="760" y2="290" stroke={INDIGO} strokeWidth="2.5" strokeDasharray="120" strokeDashoffset={120 - arrowDraw2 * 120} />

          {/* Fight */}
          <g opacity={node3} transform={`translate(0, ${(1 - node3) * 20})`}>
            <rect x="100" y="290" width="200" height="65" rx="14" fill="#1c1917" stroke="#ef4444" strokeWidth="2" />
            <text x="200" y="330" textAnchor="middle" fill="#ef4444" fontSize="30" fontFamily={FONT} fontWeight="700">
              Fight
            </text>
          </g>

          {/* Flight */}
          <g opacity={node4} transform={`translate(0, ${(1 - node4) * 20})`}>
            <rect x="380" y="290" width="200" height="65" rx="14" fill="#1c1917" stroke="#f59e0b" strokeWidth="2" />
            <text x="480" y="330" textAnchor="middle" fill="#f59e0b" fontSize="30" fontFamily={FONT} fontWeight="700">
              Flight
            </text>
          </g>

          {/* Freeze */}
          <g opacity={node5} transform={`translate(0, ${(1 - node5) * 20})`}>
            <rect x="660" y="290" width="200" height="65" rx="14" fill="#1c1917" stroke="#3b82f6" strokeWidth="2" />
            <text x="760" y="330" textAnchor="middle" fill="#3b82f6" fontSize="30" fontFamily={FONT} fontWeight="700">
              Freeze
            </text>
          </g>
        </svg>
      </div>

      {/* Count-up: 12ms */}
      <div
        style={{
          position: 'absolute',
          bottom: BOT_SAFE + 120,
          left: SIDE,
          right: SIDE,
          textAlign: 'center',
          opacity: countOpacity,
        }}
      >
        <span
          style={{
            fontFamily: FONT,
            fontSize: 88,
            fontWeight: 800,
            color: GREEN,
            fontVariantNumeric: 'tabular-nums',
          }}
        >
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

// ─── Scene 3: "Fear ≠ Danger" ───────────────────────────────────────────────────
const Scene3: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  const titleIn = sp(frame, fps, 5);
  const leftIn = sp(frame, fps, 30);
  const rightIn = sp(frame, fps, 40);
  const vsIn = sp(frame, fps, 35);
  const scaleIn = sp(frame, fps, 80);
  const statIn = sp(frame, fps, 110);
  const equalIn = sp(frame, fps, 65);

  const statVal = Math.round(
    interpolate(frame, [115, 155], [0, 90], {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    })
  );

  return (
    <div style={{ opacity, width: '100%', height: '100%', position: 'absolute' }}>
      {/* Title */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 40,
          left: SIDE,
          right: SIDE,
          textAlign: 'center',
          opacity: titleIn,
          transform: `translateY(${(1 - titleIn) * 30}px)`,
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 60, fontWeight: 800, color: WHITE }}>
          Fear{' '}
          <span style={{ color: '#ef4444' }}>≠</span>{' '}
          Danger
        </span>
      </div>

      {/* Split comparison */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 180,
          left: SIDE,
          right: SIDE,
          display: 'flex',
          gap: 24,
        }}
      >
        {/* Left: Real Danger */}
        <div
          style={{
            flex: 1,
            background: '#1c1917',
            border: '2px solid #ef4444',
            borderRadius: 20,
            padding: '40px 24px',
            textAlign: 'center',
            opacity: leftIn,
            transform: `translateX(${(1 - leftIn) * -40}px)`,
          }}
        >
          {/* Lightning bolt icon */}
          <svg width="80" height="80" viewBox="0 0 80 80" style={{ marginBottom: 16 }}>
            <polygon points="45,5 20,45 38,45 35,75 60,35 42,35" fill="#ef4444" />
          </svg>
          <div style={{ fontFamily: FONT, fontSize: 36, fontWeight: 700, color: '#ef4444', marginBottom: 12 }}>
            REAL DANGER
          </div>
          <div style={{ fontFamily: FONT, fontSize: 28, color: DIM, lineHeight: 1.4 }}>
            A truck running{'\n'}a red light
          </div>
        </div>

        {/* VS divider */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            opacity: vsIn,
          }}
        >
          <span style={{ fontFamily: FONT, fontSize: 36, fontWeight: 800, color: DIM }}>vs</span>
        </div>

        {/* Right: Perceived Fear */}
        <div
          style={{
            flex: 1,
            background: '#1c1917',
            border: `2px solid ${INDIGO}`,
            borderRadius: 20,
            padding: '40px 24px',
            textAlign: 'center',
            opacity: rightIn,
            transform: `translateX(${(1 - rightIn) * 40}px)`,
          }}
        >
          {/* Thought bubble icon */}
          <svg width="80" height="80" viewBox="0 0 80 80" style={{ marginBottom: 16 }}>
            <ellipse cx="40" cy="34" rx="30" ry="22" fill="none" stroke={INDIGO} strokeWidth="3" />
            <circle cx="25" cy="62" r="5" fill={INDIGO} opacity={0.6} />
            <circle cx="18" cy="72" r="3" fill={INDIGO} opacity={0.4} />
            <text x="40" y="40" textAnchor="middle" fill={INDIGO} fontSize="18" fontFamily={FONT}>?!</text>
          </svg>
          <div style={{ fontFamily: FONT, fontSize: 36, fontWeight: 700, color: INDIGO, marginBottom: 12 }}>
            PERCEIVED FEAR
          </div>
          <div style={{ fontFamily: FONT, fontSize: 28, color: DIM, lineHeight: 1.4 }}>
            Quitting your job,{'\n'}raising your hand
          </div>
        </div>
      </div>

      {/* Equal sign — brain treats them the same */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 700,
          left: SIDE,
          right: SIDE,
          textAlign: 'center',
          opacity: equalIn,
          transform: `scale(${equalIn})`,
        }}
      >
        <div
          style={{
            display: 'inline-block',
            background: '#1e1b4b',
            border: `2px solid ${INDIGO}`,
            borderRadius: 16,
            padding: '16px 40px',
          }}
        >
          <span style={{ fontFamily: FONT, fontSize: 32, fontWeight: 600, color: INDIGO }}>
            Your brain treats them the same
          </span>
        </div>
      </div>

      {/* Stat: 90% */}
      <div
        style={{
          position: 'absolute',
          bottom: BOT_SAFE + 80,
          left: SIDE,
          right: SIDE,
          textAlign: 'center',
          opacity: statIn,
        }}
      >
        <span
          style={{
            fontFamily: FONT,
            fontSize: 80,
            fontWeight: 800,
            color: GREEN,
            fontVariantNumeric: 'tabular-nums',
          }}
        >
          {statVal}%
        </span>
        <br />
        <span style={{ fontFamily: FONT, fontSize: 34, fontWeight: 400, color: DIM }}>
          of feared outcomes never happen
        </span>
      </div>
    </div>
  );
};

// ─── Scene 4: "The Fear Cycle" ──────────────────────────────────────────────────
const Scene4: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  const titleIn = sp(frame, fps, 5);

  const nodes = [
    { label: 'Trigger', color: '#ef4444' },
    { label: 'Anxious\nThought', color: '#f59e0b' },
    { label: 'Body\nResponse', color: INDIGO },
    { label: 'Avoidance', color: '#8b5cf6' },
    { label: 'Reinforcement', color: '#ec4899' },
  ];

  const cx = 480;
  const cy = 520;
  const rx = 300;
  const ry = 280;

  const positions = nodes.map((_, i) => {
    const angle = (i / nodes.length) * Math.PI * 2 - Math.PI / 2;
    return {
      x: cx + rx * Math.cos(angle),
      y: cy + ry * Math.sin(angle),
    };
  });

  return (
    <div style={{ opacity, width: '100%', height: '100%', position: 'absolute' }}>
      {/* Title */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 40,
          left: SIDE,
          right: SIDE,
          textAlign: 'center',
          opacity: titleIn,
          transform: `translateY(${(1 - titleIn) * 30}px)`,
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 60, fontWeight: 800, color: WHITE }}>
          The <span style={{ color: INDIGO }}>Fear Cycle</span>
        </span>
      </div>

      {/* Cycle diagram */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 130,
          left: 0,
          right: 0,
        }}
      >
        <svg width={960} height={820} viewBox="0 0 960 820">
          {/* Arrows between nodes */}
          {positions.map((pos, i) => {
            const next = positions[(i + 1) % nodes.length];
            const delay = 30 + i * 12;
            const progress = clamp01(interpolate(frame, [delay + 20, delay + 45], [0, 1]));

            return (
              <line
                key={`arrow-${i}`}
                x1={pos.x}
                y1={pos.y}
                x2={pos.x + (next.x - pos.x) * progress}
                y2={pos.y + (next.y - pos.y) * progress}
                stroke={nodes[i].color}
                strokeWidth="3"
                opacity={0.6}
              />
            );
          })}

          {/* Nodes */}
          {nodes.map((node, i) => {
            const pos = positions[i];
            const delay = 25 + i * 12;
            const nodeSpring = sp(frame, fps, delay);
            const isActive =
              frame > 80 &&
              Math.floor((frame - 80) / 20) % nodes.length === i;

            return (
              <g
                key={i}
                opacity={nodeSpring}
                transform={`translate(${pos.x}, ${pos.y}) scale(${nodeSpring * (isActive ? 1.12 : 1)})`}
              >
                <circle
                  r="72"
                  fill="#1c1917"
                  stroke={node.color}
                  strokeWidth={isActive ? 4 : 2.5}
                />
                {isActive && (
                  <circle r="72" fill="none" stroke={node.color} strokeWidth="2" opacity={0.3}>
                    <animate attributeName="r" from="72" to="90" dur="0.8s" repeatCount="indefinite" />
                    <animate attributeName="opacity" from="0.3" to="0" dur="0.8s" repeatCount="indefinite" />
                  </circle>
                )}
                {node.label.split('\n').map((line, li) => (
                  <text
                    key={li}
                    x="0"
                    y={li * 28 - (node.label.split('\n').length - 1) * 14 + 8}
                    textAnchor="middle"
                    fill={node.color}
                    fontSize="24"
                    fontFamily={FONT}
                    fontWeight="700"
                  >
                    {line}
                  </text>
                ))}
              </g>
            );
          })}

          {/* Center label: REPEAT */}
          <text
            x={cx}
            y={cy + 8}
            textAnchor="middle"
            fill={DIM}
            fontSize="28"
            fontFamily={FONT}
            fontWeight="600"
            opacity={sp(frame, fps, 100)}
          >
            ∞ REPEAT
          </text>
        </svg>
      </div>

      {/* Bottom caption */}
      <div
        style={{
          position: 'absolute',
          bottom: BOT_SAFE + 60,
          left: SIDE + 20,
          right: SIDE + 20,
          textAlign: 'center',
          opacity: sp(frame, fps, 120),
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 34, fontWeight: 400, color: DIM, lineHeight: 1.5 }}>
          Fear feeds itself. Avoidance{'\n'}reinforces the threat.
        </span>
      </div>
    </div>
  );
};

// ─── Scene 5: "Break The Cycle" + Particles ─────────────────────────────────────

// Particle data — seeded positions so they're deterministic
const PARTICLES = Array.from({ length: 14 }, (_, i) => ({
  x: 80 + (i * 73) % 920,
  size: 6 + (i % 5) * 4,
  speed: 0.6 + (i % 4) * 0.3,
  delay: (i * 7) % 30,
  opacity: 0.08 + (i % 5) * 0.04,
}));

const Scene5: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  const titleIn = sp(frame, fps, 5);

  const steps = [
    { num: '1', label: 'Name It', desc: 'Get specific about your fear', icon: 'tag', color: INDIGO },
    { num: '2', label: 'Question It', desc: 'Is this fact or fiction?', icon: 'help', color: '#f59e0b' },
    { num: '3', label: 'Act Anyway', desc: 'Move before the feeling passes', icon: 'bolt', color: GREEN },
  ];

  // Crack/shatter effect on old cycle
  const shatterProgress = clamp01(interpolate(frame, [15, 45], [0, 1]));

  const ctaIn = sp(frame, fps, 130);

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
              backgroundColor: i % 3 === 0 ? INDIGO : i % 3 === 1 ? GREEN : '#8b5cf6',
              opacity: p.opacity,
            }}
          />
        );
      })}

      {/* Shattering cycle ring */}
      {shatterProgress < 1 && (
        <div
          style={{
            position: 'absolute',
            top: TOP_SAFE + 150,
            left: 0,
            right: 0,
            display: 'flex',
            justifyContent: 'center',
            opacity: 1 - shatterProgress,
            transform: `scale(${1 + shatterProgress * 0.3})`,
          }}
        >
          <svg width="160" height="160" viewBox="0 0 100 100">
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke={INDIGO}
              strokeWidth="3"
              strokeDasharray={`${10 + shatterProgress * 20} ${5 + shatterProgress * 15}`}
            />
            {/* Crack lines */}
            {[0, 72, 144, 216, 288].map((angle, ci) => (
              <line
                key={ci}
                x1={50 + 35 * Math.cos((angle * Math.PI) / 180)}
                y1={50 + 35 * Math.sin((angle * Math.PI) / 180)}
                x2={50 + (35 + shatterProgress * 30) * Math.cos((angle * Math.PI) / 180)}
                y2={50 + (35 + shatterProgress * 30) * Math.sin((angle * Math.PI) / 180)}
                stroke="#ef4444"
                strokeWidth="2"
                opacity={shatterProgress}
              />
            ))}
          </svg>
        </div>
      )}

      {/* Title */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 60,
          left: SIDE,
          right: SIDE,
          textAlign: 'center',
          opacity: titleIn,
          transform: `translateY(${(1 - titleIn) * 30}px)`,
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 64, fontWeight: 800, color: WHITE }}>
          Break The{' '}
          <span style={{ color: GREEN }}>Cycle</span>
        </span>
      </div>

      {/* 3 Steps */}
      {steps.map((step, i) => {
        const stepIn = sp(frame, fps, 50 + i * 12);
        const yBase = TOP_SAFE + 280 + i * 220;

        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              top: yBase,
              left: SIDE + 20,
              right: SIDE + 20,
              opacity: stepIn,
              transform: `translateX(${(1 - stepIn) * 60}px)`,
              display: 'flex',
              alignItems: 'center',
              gap: 28,
            }}
          >
            {/* Number circle */}
            <div
              style={{
                width: 80,
                height: 80,
                borderRadius: '50%',
                border: `3px solid ${step.color}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}
            >
              <span
                style={{
                  fontFamily: FONT,
                  fontSize: 40,
                  fontWeight: 800,
                  color: step.color,
                }}
              >
                {step.num}
              </span>
            </div>

            {/* Text */}
            <div>
              <div style={{ fontFamily: FONT, fontSize: 44, fontWeight: 700, color: WHITE, marginBottom: 6 }}>
                {step.label}
              </div>
              <div style={{ fontFamily: FONT, fontSize: 32, fontWeight: 400, color: DIM }}>
                {step.desc}
              </div>
            </div>
          </div>
        );
      })}

      {/* Tagline */}
      <div
        style={{
          position: 'absolute',
          bottom: BOT_SAFE + 200,
          left: SIDE,
          right: SIDE,
          textAlign: 'center',
          opacity: sp(frame, fps, 110),
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 36, fontWeight: 600, color: WHITE, fontStyle: 'italic' }}>
          Fear shrinks when you stop running.
        </span>
      </div>

      {/* CTA */}
      <div
        style={{
          position: 'absolute',
          bottom: BOT_SAFE + 60,
          left: SIDE + 20,
          right: SIDE + 20,
          textAlign: 'center',
          opacity: ctaIn,
          transform: `scale(${ctaIn})`,
        }}
      >
        <div
          style={{
            display: 'inline-block',
            background: `${GREEN}20`,
            border: `2px solid ${GREEN}`,
            borderRadius: 16,
            padding: '18px 44px',
          }}
        >
          <span style={{ fontFamily: FONT, fontSize: 36, fontWeight: 700, color: GREEN }}>
            Take the Fear Audit — Link in bio
          </span>
        </div>
      </div>
    </div>
  );
};

// ─── Progress bar ───────────────────────────────────────────────────────────────
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

// ─── Main composition ───────────────────────────────────────────────────────────
export const FearExplainer: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // Scene boundaries (with overlap for fade transitions)
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
      {/* Load Inter via Google Fonts */}
      <style>
        {`@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');`}
      </style>

      {/* Voiceover */}
      <Audio src={staticFile('voiceover-fear-explainer.wav')} volume={1.0} />
      {/* Background music */}
      <Audio src={staticFile('music.mp3')} volume={0.07} loop />

      {/* Scenes */}
      {scenes.map(({ start, Component }, i) => (
        <Sequence key={i} from={start} durationInFrames={SCENE_FRAMES}>
          <Component frame={frame - start} fps={fps} />
        </Sequence>
      ))}

      {/* Progress bar */}
      <ProgressBar frame={frame} />
    </div>
  );
};
