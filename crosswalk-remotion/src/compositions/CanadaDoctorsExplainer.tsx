/**
 * "The 52,000" — Educational Explainer (1080×1920, 30fps, 30s = 900 frames)
 *
 * 5 scenes × ~180 frames each with fade transitions.
 * Visual style: dark (#0a0a0a), indigo accent, amber emphasis, Inter font.
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
const BG     = '#0a0a0a';
const INDIGO = '#6366f1';
const GREEN  = '#22c55e';
const AMBER  = '#f59e0b';
const WHITE  = '#ffffff';
const DIM    = 'rgba(255,255,255,0.5)';
const FONT   = '"Inter", system-ui, sans-serif';

const SCENE_FRAMES = 180;
const FADE         = 12;
const TOTAL        = 900;

const TOP_SAFE = 150;
const BOT_SAFE = 170;
const SIDE     = 60;

// ─── Helpers ────────────────────────────────────────────────────────────────────
const sp = (frame: number, fps: number, delay = 0) =>
  spring({ frame: frame - delay, fps, config: { damping: 200 } });

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));

const fadeInOut = (localFrame: number, dur: number) => {
  const fadeIn  = interpolate(localFrame, [0, FADE], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const fadeOut = interpolate(localFrame, [dur - FADE, dur], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return fadeIn * fadeOut;
};

// ─── Scene 1: Hook + Numbers ────────────────────────────────────────────────────
const Scene1: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  // Hook lines — slam in immediately
  const hook1In    = sp(frame, fps, 2);
  const hook2In    = sp(frame, fps, 10);

  // Number cards — fast stagger right after hook
  const doctorsIn  = sp(frame, fps, 30);
  const nursesIn   = sp(frame, fps, 42);

  // Bottom tag
  const tagIn      = sp(frame, fps, 65);

  return (
    <div style={{ opacity, width: '100%', height: '100%', position: 'absolute' }}>

      {/* Hook line 1 */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 80,
          left: SIDE,
          right: SIDE,
          textAlign: 'center',
          opacity: hook1In,
          transform: `translateY(${(1 - hook1In) * 40}px)`,
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 84, fontWeight: 800, color: WHITE, lineHeight: 1.1 }}>
          This isn't just
        </span>
      </div>

      {/* Hook line 2 */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 200,
          left: SIDE,
          right: SIDE,
          textAlign: 'center',
          opacity: hook2In,
          transform: `translateY(${(1 - hook2In) * 40}px)`,
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 84, fontWeight: 800, color: INDIGO, lineHeight: 1.1 }}>
          a healthcare crisis.
        </span>
      </div>

      {/* 20,000 DOCTORS card */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 430,
          left: SIDE,
          right: SIDE,
          opacity: doctorsIn,
          transform: `translateX(${(1 - doctorsIn) * -60}px)`,
          background: `${INDIGO}20`,
          border: `3px solid ${INDIGO}`,
          borderRadius: 24,
          padding: '36px 44px',
          textAlign: 'center',
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 96, fontWeight: 800, color: INDIGO, fontVariantNumeric: 'tabular-nums', display: 'block' }}>
          20,000
        </span>
        <span style={{ fontFamily: FONT, fontSize: 44, fontWeight: 700, color: WHITE, display: 'block', marginTop: 4 }}>
          IMMIGRANT DOCTORS
        </span>
        <span style={{ fontFamily: FONT, fontSize: 34, fontWeight: 400, color: DIM, display: 'block', marginTop: 6 }}>
          can't see a single patient
        </span>
      </div>

      {/* 32,000 NURSES card */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 770,
          left: SIDE,
          right: SIDE,
          opacity: nursesIn,
          transform: `translateX(${(1 - nursesIn) * 60}px)`,
          background: `${AMBER}20`,
          border: `3px solid ${AMBER}`,
          borderRadius: 24,
          padding: '36px 44px',
          textAlign: 'center',
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 96, fontWeight: 800, color: AMBER, fontVariantNumeric: 'tabular-nums', display: 'block' }}>
          32,000
        </span>
        <span style={{ fontFamily: FONT, fontSize: 44, fontWeight: 700, color: WHITE, display: 'block', marginTop: 4 }}>
          IMMIGRANT NURSES
        </span>
        <span style={{ fontFamily: FONT, fontSize: 34, fontWeight: 400, color: DIM, display: 'block', marginTop: 6 }}>
          can't treat a single patient
        </span>
      </div>

      {/* Bottom tag */}
      <div
        style={{
          position: 'absolute',
          bottom: BOT_SAFE + 60,
          left: SIDE,
          right: SIDE,
          textAlign: 'center',
          opacity: tagIn,
          transform: `translateY(${(1 - tagIn) * 20}px)`,
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 44, fontWeight: 700, color: AMBER, fontStyle: 'italic' }}>
          Not incompetence.{' '}
        </span>
        <span style={{ fontFamily: FONT, fontSize: 44, fontWeight: 700, color: WHITE, fontStyle: 'italic' }}>
          Licensing barriers.
        </span>
      </div>
    </div>
  );
};

// ─── Scene 2: Flowchart — credential blocked at border ──────────────────────────
const Scene2: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  const titleIn = sp(frame, fps, 5);

  const node1 = sp(frame, fps, 20);
  const node2 = sp(frame, fps, 40);
  const node3 = sp(frame, fps, 60);
  const node4 = sp(frame, fps, 80);

  const arrow1 = clamp01(interpolate(frame, [30, 48], [0, 1]));
  const arrow2 = clamp01(interpolate(frame, [50, 68], [0, 1]));
  const arrow3 = clamp01(interpolate(frame, [70, 88], [0, 1]));

  const stat1In = sp(frame, fps, 100);
  const stat2In = sp(frame, fps, 112);
  const stat3In = sp(frame, fps, 124);

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
        <span style={{ fontFamily: FONT, fontSize: 52, fontWeight: 800, color: WHITE, lineHeight: 1.2 }}>
          The credential doesn't{'\n'}
          <span style={{ color: INDIGO }}>cross the border.</span>
        </span>
      </div>

      {/* Flowchart SVG */}
      <div style={{ position: 'absolute', top: TOP_SAFE + 280, left: 0, right: 0 }}>
        <svg width={1080} height={480} viewBox="0 0 1080 480">
          {/* Node 1: Qualified Professional */}
          <g opacity={node1} transform={`translate(${(1 - node1) * -30}, 0)`}>
            <rect x="60" y="50" width="260" height="80" rx="16" fill={`${INDIGO}22`} stroke={INDIGO} strokeWidth="2.5" />
            <text x="190" y="85" textAnchor="middle" fill={WHITE} fontSize="28" fontFamily={FONT} fontWeight="700">Qualified</text>
            <text x="190" y="113" textAnchor="middle" fill={INDIGO} fontSize="24" fontFamily={FONT} fontWeight="600">Professional</text>
          </g>

          {/* Arrow 1 */}
          <line x1="320" y1="90" x2={320 + arrow1 * 100} y2="90" stroke={INDIGO} strokeWidth="3" />
          <polygon points={`${320 + arrow1 * 100 - 8},82 ${320 + arrow1 * 100 + 2},90 ${320 + arrow1 * 100 - 8},98`} fill={INDIGO} opacity={arrow1} />

          {/* Node 2: Canada */}
          <g opacity={node2} transform={`translate(0, ${(1 - node2) * 20})`}>
            <rect x="420" y="50" width="240" height="80" rx="16" fill={`${GREEN}18`} stroke={GREEN} strokeWidth="2.5" />
            <text x="540" y="85" textAnchor="middle" fill={WHITE} fontSize="28" fontFamily={FONT} fontWeight="700">Arrives in</text>
            <text x="540" y="113" textAnchor="middle" fill={GREEN} fontSize="24" fontFamily={FONT} fontWeight="600">Canada</text>
          </g>

          {/* Arrow 2 */}
          <line x1="660" y1="90" x2={660 + arrow2 * 100} y2="90" stroke={GREEN} strokeWidth="3" />
          <polygon points={`${660 + arrow2 * 100 - 8},82 ${660 + arrow2 * 100 + 2},90 ${660 + arrow2 * 100 - 8},98`} fill={GREEN} opacity={arrow2} />

          {/* Node 3: Licensing Body */}
          <g opacity={node3} transform={`translate(0, ${(1 - node3) * 20})`}>
            <rect x="760" y="50" width="260" height="80" rx="16" fill={`${AMBER}18`} stroke={AMBER} strokeWidth="2.5" />
            <text x="890" y="85" textAnchor="middle" fill={WHITE} fontSize="28" fontFamily={FONT} fontWeight="700">Licensing</text>
            <text x="890" y="113" textAnchor="middle" fill={AMBER} fontSize="24" fontFamily={FONT} fontWeight="600">Body</text>
          </g>

          {/* Arrow down from Licensing Body */}
          <line x1="890" y1="130" x2="890" y2={130 + arrow3 * 110} stroke="#ef4444" strokeWidth="3" />
          <polygon points={`882,${130 + arrow3 * 110 - 8} 890,${130 + arrow3 * 110 + 2} 898,${130 + arrow3 * 110 - 8}`} fill="#ef4444" opacity={arrow3} />

          {/* Node 4: Blocked */}
          <g opacity={node4} transform={`translate(0, ${(1 - node4) * 20})`}>
            <rect x="740" y="240" width="300" height="90" rx="16" fill="#1c1917" stroke="#ef4444" strokeWidth="3" />
            <text x="890" y="275" textAnchor="middle" fill="#ef4444" fontSize="32" fontFamily={FONT} fontWeight="800">BLOCKED</text>
            <text x="890" y="310" textAnchor="middle" fill={DIM} fontSize="22" fontFamily={FONT}>Cannot practice</text>
          </g>

          {/* X mark */}
          <g opacity={node4}>
            <line x1="862" y1="257" x2="882" y2="277" stroke="#ef4444" strokeWidth="3" />
            <line x1="882" y1="257" x2="862" y2="277" stroke="#ef4444" strokeWidth="3" />
          </g>
        </svg>
      </div>

      {/* 3 stats */}
      <div
        style={{
          position: 'absolute',
          bottom: BOT_SAFE + 80,
          left: SIDE,
          right: SIDE,
          display: 'flex',
          flexDirection: 'column',
          gap: 16,
        }}
      >
        {[
          { stat: 'Last in G7', label: 'for homes per capita', opacity: stat1In, color: INDIGO },
          { stat: 'Worst food inflation', label: 'in the G7', opacity: stat2In, color: AMBER },
          { stat: '30-year high', label: 'youth unemployment', opacity: stat3In, color: '#ef4444' },
        ].map(({ stat, label, opacity: o, color }, i) => (
          <div
            key={i}
            style={{
              opacity: o,
              transform: `translateX(${(1 - o) * -30}px)`,
              display: 'flex',
              alignItems: 'center',
              gap: 16,
            }}
          >
            <div style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: color, flexShrink: 0 }} />
            <span style={{ fontFamily: FONT, fontSize: 28, fontWeight: 700, color }}>
              {stat}
            </span>
            <span style={{ fontFamily: FONT, fontSize: 28, fontWeight: 400, color: DIM }}>
              {label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

// ─── Scene 3: Two comparison cards ──────────────────────────────────────────────
const Scene3: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  const titleIn = sp(frame, fps, 5);
  const sub1In  = sp(frame, fps, 20);
  const leftIn  = sp(frame, fps, 35);
  const rightIn = sp(frame, fps, 47);

  const ex1In = sp(frame, fps, 90);
  const ex2In = sp(frame, fps, 102);
  const ex3In = sp(frame, fps, 114);

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
        <span style={{ fontFamily: FONT, fontSize: 58, fontWeight: 800, color: WHITE, lineHeight: 1.2 }}>
          The system can verify{'\n'}
          <span style={{ color: INDIGO }}>your degree.</span>
        </span>
      </div>

      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 240,
          left: SIDE,
          right: SIDE,
          textAlign: 'center',
          opacity: sub1In,
          transform: `translateY(${(1 - sub1In) * 20}px)`,
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 48, fontWeight: 600, color: AMBER, fontStyle: 'italic' }}>
          Not your depth.
        </span>
      </div>

      {/* Two cards */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 380,
          left: SIDE,
          right: SIDE,
          display: 'flex',
          gap: 20,
        }}
      >
        {/* Left card — what system sees */}
        <div
          style={{
            flex: 1,
            background: '#1c1917',
            border: `2px solid ${DIM}`,
            borderRadius: 20,
            padding: '36px 28px',
            opacity: leftIn,
            transform: `translateX(${(1 - leftIn) * -50}px)`,
          }}
        >
          <div style={{ fontFamily: FONT, fontSize: 26, fontWeight: 600, color: DIM, marginBottom: 20, textTransform: 'uppercase', letterSpacing: 2 }}>
            What it sees
          </div>
          {['Credentials', 'Forms', 'Compliance checkboxes'].map((item, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
              <div style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: DIM, flexShrink: 0 }} />
              <span style={{ fontFamily: FONT, fontSize: 34, fontWeight: 500, color: WHITE }}>{item}</span>
            </div>
          ))}
        </div>

        {/* Right card — what it can't see */}
        <div
          style={{
            flex: 1,
            background: `${INDIGO}14`,
            border: `2px solid ${INDIGO}`,
            borderRadius: 20,
            padding: '36px 28px',
            opacity: rightIn,
            transform: `translateX(${(1 - rightIn) * 50}px)`,
          }}
        >
          <div style={{ fontFamily: FONT, fontSize: 26, fontWeight: 600, color: INDIGO, marginBottom: 20, textTransform: 'uppercase', letterSpacing: 2 }}>
            What it can't
          </div>
          {['Clinical judgment', '10,000+ hours', 'Depth under pressure'].map((item, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
              <div style={{ width: 6, height: 6, borderRadius: '50%', backgroundColor: INDIGO, flexShrink: 0 }} />
              <span style={{ fontFamily: FONT, fontSize: 34, fontWeight: 500, color: WHITE }}>{item}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Bottom: 3 examples */}
      <div
        style={{
          position: 'absolute',
          bottom: BOT_SAFE + 60,
          left: SIDE,
          right: SIDE,
          display: 'flex',
          justifyContent: 'space-between',
          gap: 12,
        }}
      >
        {[
          { label: '10,000 Hours of Practice', opacity: ex1In },
          { label: 'High-Stakes Decisions', opacity: ex2In },
          { label: 'Presence Under Pressure', opacity: ex3In },
        ].map(({ label, opacity: o }, i) => (
          <div
            key={i}
            style={{
              flex: 1,
              textAlign: 'center',
              opacity: o,
              transform: `translateY(${(1 - o) * 20}px)`,
              background: `${AMBER}12`,
              border: `1px solid ${AMBER}40`,
              borderRadius: 14,
              padding: '16px 12px',
            }}
          >
            <span style={{ fontFamily: FONT, fontSize: 26, fontWeight: 600, color: AMBER, lineHeight: 1.3 }}>
              {label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

// ─── Scene 4: Circular loop — structural pattern ─────────────────────────────────
const Scene4: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  const titleIn = sp(frame, fps, 5);
  const subIn   = sp(frame, fps, 20);

  const nodes = [
    { label: 'Systemic\nBarrier',        color: '#ef4444' },
    { label: 'Institutional\nInvisibility', color: AMBER  },
    { label: 'Identity\nErosion',         color: INDIGO   },
    { label: 'Burnout',                   color: '#8b5cf6' },
  ];

  const cx = 540;
  const cy = 980;
  const rx = 290;
  const ry = 260;

  const positions = nodes.map((_, i) => {
    const angle = (i / nodes.length) * Math.PI * 2 - Math.PI / 2;
    return { x: cx + rx * Math.cos(angle), y: cy + ry * Math.sin(angle) };
  });

  const captionIn = sp(frame, fps, 120);

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
        <span style={{ fontFamily: FONT, fontSize: 58, fontWeight: 800, color: WHITE, lineHeight: 1.2 }}>
          This isn't new.{'\n'}
          <span style={{ color: INDIGO }}>It's structural.</span>
        </span>
      </div>

      {/* Subtitle */}
      <div
        style={{
          position: 'absolute',
          top: TOP_SAFE + 240,
          left: SIDE + 20,
          right: SIDE + 20,
          textAlign: 'center',
          opacity: subIn,
          transform: `translateY(${(1 - subIn) * 20}px)`,
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 34, fontWeight: 400, color: DIM, lineHeight: 1.5 }}>
          The same loop runs outside{'\n'}the gate and inside it.
        </span>
      </div>

      {/* Cycle diagram */}
      <div style={{ position: 'absolute', top: TOP_SAFE + 340, left: 0, right: 0 }}>
        <svg width={1080} height={760} viewBox="0 0 1080 760">
          {/* Connecting arrows */}
          {positions.map((pos, i) => {
            const next  = positions[(i + 1) % nodes.length];
            const delay = 25 + i * 12;
            const prog  = clamp01(interpolate(frame, [delay + 15, delay + 40], [0, 1]));
            const mx = pos.x + (next.x - pos.x) * 0.5;
            const my = pos.y + (next.y - pos.y) * 0.5;
            return (
              <line
                key={`line-${i}`}
                x1={pos.x}
                y1={pos.y}
                x2={pos.x + (next.x - pos.x) * prog}
                y2={pos.y + (next.y - pos.y) * prog}
                stroke={nodes[i].color}
                strokeWidth="3"
                opacity={0.5}
              />
            );
          })}

          {/* Nodes */}
          {nodes.map((node, i) => {
            const pos       = positions[i];
            const delay     = 20 + i * 12;
            const nodeSpring = sp(frame, fps, delay);
            const isActive  = frame > 80 && Math.floor((frame - 80) / 22) % nodes.length === i;

            return (
              <g key={i} opacity={nodeSpring} transform={`translate(${pos.x}, ${pos.y}) scale(${nodeSpring * (isActive ? 1.1 : 1)})`}>
                <circle r="80" fill="#1c1917" stroke={node.color} strokeWidth={isActive ? 4 : 2.5} />
                {isActive && (
                  <circle r="80" fill="none" stroke={node.color} strokeWidth="2" opacity={0.25}>
                    <animate attributeName="r" from="80" to="100" dur="0.9s" repeatCount="indefinite" />
                    <animate attributeName="opacity" from="0.25" to="0" dur="0.9s" repeatCount="indefinite" />
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

          {/* Center label */}
          <text x={cx} y={cy + 8} textAnchor="middle" fill={DIM} fontSize="28" fontFamily={FONT} fontWeight="600" opacity={sp(frame, fps, 90)}>
            ∞ REPEAT
          </text>
        </svg>
      </div>

      {/* Caption */}
      <div
        style={{
          position: 'absolute',
          bottom: BOT_SAFE + 60,
          left: SIDE + 20,
          right: SIDE + 20,
          textAlign: 'center',
          opacity: captionIn,
        }}
      >
        <span style={{ fontFamily: FONT, fontSize: 32, fontWeight: 400, color: DIM, fontStyle: 'italic', lineHeight: 1.5 }}>
          The institution doesn't see you.{'\n'}After a while, it's easy to stop seeing yourself.
        </span>
      </div>
    </div>
  );
};

// ─── Particles ───────────────────────────────────────────────────────────────────
const PARTICLES = Array.from({ length: 14 }, (_, i) => ({
  x:       80 + (i * 73) % 920,
  size:    6 + (i % 5) * 4,
  speed:   0.6 + (i % 4) * 0.3,
  delay:   (i * 7) % 30,
  opacity: 0.08 + (i % 5) * 0.04,
}));

// ─── Scene 5: The Break + CTA ────────────────────────────────────────────────────
const Scene5: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  const titleIn = sp(frame, fps, 5);
  const ctaIn   = sp(frame, fps, 130);

  const steps = [
    { num: '1', label: 'Name the barrier', desc: 'Structural — not personal',       color: INDIGO  },
    { num: '2', label: 'Map the gap',       desc: 'What you know vs. what\'s authorized', color: AMBER   },
    { num: '3', label: 'Build from here',   desc: 'Start with what\'s already yours', color: GREEN   },
  ];

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
              backgroundColor: i % 3 === 0 ? INDIGO : i % 3 === 1 ? AMBER : '#8b5cf6',
              opacity: p.opacity,
            }}
          />
        );
      })}

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
        <span style={{ fontFamily: FONT, fontSize: 64, fontWeight: 800, color: WHITE, lineHeight: 1.15 }}>
          The crosswalk is there.{'\n'}
          <span style={{ color: GREEN }}>Both sides are real.</span>
        </span>
      </div>

      {/* 3 Steps */}
      {steps.map((step, i) => {
        const stepIn = sp(frame, fps, 50 + i * 12);
        const yBase  = TOP_SAFE + 320 + i * 210;
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
              <span style={{ fontFamily: FONT, fontSize: 40, fontWeight: 800, color: step.color }}>
                {step.num}
              </span>
            </div>
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

      {/* CTA pill */}
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
          <span style={{ fontFamily: FONT, fontSize: 30, fontWeight: 700, color: GREEN }}>
            crosswalkwisdom.com/blog/canada-doctors-sidelined
          </span>
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
export const CanadaDoctorsExplainer: React.FC = () => {
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
