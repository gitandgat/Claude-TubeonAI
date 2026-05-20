/**
 * "Self-Doubt Is Not a Verdict" — Educational Explainer (1080×1920, 30fps, 30s = 900 frames)
 *
 * 5 scenes × ~180 frames each with fade transitions.
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
const BG     = '#0a0a0a';
const INDIGO  = '#6366f1';
const GREEN   = '#22c55e';
const AMBER   = '#f59e0b';
const WHITE   = '#ffffff';
const DIM     = 'rgba(255,255,255,0.5)';
const FONT    = '"Inter", system-ui, sans-serif';

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

// ─── Scene 1: "Self-Doubt Is Not a Verdict" ─────────────────────────────────────
const Scene1: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  // Brain icon morphing from ? to signal wave
  const morphProgress = sp(frame, fps, 20);
  const questionOpacity = interpolate(morphProgress, [0, 0.5, 1], [1, 0.5, 0], { extrapolateRight: 'clamp' });
  const signalOpacity   = interpolate(morphProgress, [0.4, 1], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  const titleIn = sp(frame, fps, 50);
  const subIn   = sp(frame, fps, 70);
  const tagIn   = sp(frame, fps, 90);

  const pulse = interpolate(frame % 40, [0, 20, 40], [1, 1.08, 1]);

  return (
    <div style={{ opacity, width: '100%', height: '100%', position: 'absolute' }}>
      {/* Icon area */}
      <div style={{ position: 'absolute', top: TOP_SAFE + 160, left: 0, right: 0, display: 'flex', justifyContent: 'center' }}>
        {/* Question mark */}
        <div style={{ position: 'absolute', opacity: questionOpacity, fontFamily: FONT, fontSize: 260, fontWeight: 800, color: INDIGO, textShadow: `0 0 60px ${INDIGO}80` }}>
          ?
        </div>
        {/* Signal / nervous system wave SVG */}
        <div style={{ opacity: signalOpacity, transform: `scale(${0.7 + morphProgress * 0.3} ) scale(${pulse})` }}>
          <svg width="240" height="160" viewBox="0 0 240 160" fill="none">
            {/* EKG-style signal wave */}
            <path
              d="M10 80 L50 80 L65 30 L80 130 L95 80 L120 80 L135 50 L150 110 L165 80 L230 80"
              stroke={INDIGO}
              strokeWidth="5"
              strokeLinecap="round"
              strokeLinejoin="round"
              fill="none"
              strokeDasharray="500"
              strokeDashoffset={interpolate(morphProgress, [0.4, 1], [500, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' })}
            />
            {/* Glow dot at peak */}
            <circle cx="80" cy="30" r="8" fill={AMBER} opacity={signalOpacity}>
            </circle>
            <circle cx="80" cy="30" r="14" fill={`${AMBER}30`} opacity={signalOpacity} />
            {/* Label: SIGNAL */}
            <text x="120" y="150" textAnchor="middle" fill={DIM} fontSize="18" fontFamily={FONT} fontWeight="600" opacity={signalOpacity}>
              nervous system signal
            </text>
          </svg>
        </div>
      </div>

      {/* Main title */}
      <div style={{ position: 'absolute', top: TOP_SAFE + 440, left: SIDE, right: SIDE, textAlign: 'center', opacity: titleIn, transform: `translateY(${(1 - titleIn) * 40}px)` }}>
        <span style={{ fontFamily: FONT, fontSize: 68, fontWeight: 800, color: WHITE, lineHeight: 1.1 }}>
          Self-Doubt Is{'\n'}<span style={{ color: INDIGO }}>Not a Verdict</span>
        </span>
      </div>

      {/* Subtitle */}
      <div style={{ position: 'absolute', top: TOP_SAFE + 620, left: SIDE + 20, right: SIDE + 20, textAlign: 'center', opacity: subIn, transform: `translateY(${(1 - subIn) * 30}px)` }}>
        <span style={{ fontFamily: FONT, fontSize: 38, fontWeight: 400, color: DIM, lineHeight: 1.4 }}>
          It's a body-based signal that you're{'\n'}stepping into an unfamiliar identity.
        </span>
      </div>

      {/* Tag pill */}
      <div style={{ position: 'absolute', top: TOP_SAFE + 790, left: 0, right: 0, display: 'flex', justifyContent: 'center', opacity: tagIn, transform: `scale(${tagIn})` }}>
        <div style={{ background: `${AMBER}20`, border: `2px solid ${AMBER}`, borderRadius: 40, padding: '10px 32px' }}>
          <span style={{ fontFamily: FONT, fontSize: 30, fontWeight: 600, color: AMBER }}>
            It means you're early.
          </span>
        </div>
      </div>
    </div>
  );
};

// ─── Scene 2: "Your Brain Scans for Familiar, Not True" ────────────────────────
const Scene2: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  const titleIn = sp(frame, fps, 5);

  // Flowchart nodes
  const node1 = sp(frame, fps, 30);
  const node2 = sp(frame, fps, 48);
  const node3 = sp(frame, fps, 66);
  const node4 = sp(frame, fps, 84);

  const arrow1 = clamp01(interpolate(frame, [38, 56], [0, 1]));
  const arrow2 = clamp01(interpolate(frame, [56, 74], [0, 1]));
  const arrow3 = clamp01(interpolate(frame, [74, 92], [0, 1]));

  const captionIn = sp(frame, fps, 120);

  const nodeStyle = (color: string) => ({
    fill: `${color}20`,
    stroke: color,
  });

  return (
    <div style={{ opacity, width: '100%', height: '100%', position: 'absolute' }}>
      {/* Title */}
      <div style={{ position: 'absolute', top: TOP_SAFE + 30, left: SIDE, right: SIDE, textAlign: 'center', opacity: titleIn, transform: `translateY(${(1 - titleIn) * 30}px)` }}>
        <span style={{ fontFamily: FONT, fontSize: 54, fontWeight: 800, color: WHITE, lineHeight: 1.15 }}>
          Your Brain Scans for{'\n'}<span style={{ color: INDIGO }}>Familiar</span>, Not True
        </span>
      </div>

      {/* Flowchart SVG */}
      <div style={{ position: 'absolute', top: TOP_SAFE + 260, left: SIDE, right: SIDE }}>
        <svg width={960} height={680} viewBox="0 0 960 680">
          {/* Node 1: New Direction */}
          <g opacity={node1} transform={`translate(${(1 - node1) * -20}, 0)`}>
            <rect x="310" y="20" width="340" height="80" rx="16" {...nodeStyle(GREEN)} strokeWidth="2.5" />
            <text x="480" y="55" textAnchor="middle" fill={GREEN} fontSize="26" fontFamily={FONT} fontWeight="700">New Direction</text>
            <text x="480" y="82" textAnchor="middle" fill={DIM} fontSize="20" fontFamily={FONT}>(career change, speaking up)</text>
          </g>

          {/* Arrow 1 */}
          <line x1="480" y1="100" x2="480" y2="188" stroke={DIM} strokeWidth="2.5" strokeDasharray="220" strokeDashoffset={220 - arrow1 * 220} markerEnd="url(#arrow)" />

          {/* Node 2: Nervous System */}
          <g opacity={node2} transform={`translate(${(1 - node2) * 20}, 0)`}>
            <rect x="290" y="190" width="380" height="80" rx="16" {...nodeStyle(INDIGO)} strokeWidth="2.5" />
            <text x="480" y="225" textAnchor="middle" fill={INDIGO} fontSize="26" fontFamily={FONT} fontWeight="700">Nervous System</text>
            <text x="480" y="252" textAnchor="middle" fill={DIM} fontSize="20" fontFamily={FONT}>scans for: familiar?</text>
          </g>

          {/* Arrow 2 */}
          <line x1="480" y1="270" x2="480" y2="358" stroke={DIM} strokeWidth="2.5" strokeDasharray="220" strokeDashoffset={220 - arrow2 * 220} markerEnd="url(#arrow)" />

          {/* Node 3: UNFAMILIAR = THREAT */}
          <g opacity={node3} transform={`translate(${(1 - node3) * -20}, 0)`}>
            <rect x="270" y="360" width="420" height="80" rx="16" fill="#ef444420" stroke="#ef4444" strokeWidth="2.5" />
            <text x="480" y="397" textAnchor="middle" fill="#ef4444" fontSize="26" fontFamily={FONT} fontWeight="700">UNFAMILIAR = THREAT</text>
            <text x="480" y="424" textAnchor="middle" fill={DIM} fontSize="20" fontFamily={FONT}>even when it's good for you</text>
          </g>

          {/* Arrow 3 */}
          <line x1="480" y1="440" x2="480" y2="528" stroke={DIM} strokeWidth="2.5" strokeDasharray="220" strokeDashoffset={220 - arrow3 * 220} markerEnd="url(#arrow)" />

          {/* Node 4: Self-Doubt Spike */}
          <g opacity={node4} transform={`translate(${(1 - node4) * 20}, 0)`}>
            <rect x="300" y="530" width="360" height="80" rx="16" {...nodeStyle(AMBER)} strokeWidth="2.5" />
            <text x="480" y="567" textAnchor="middle" fill={AMBER} fontSize="26" fontFamily={FONT} fontWeight="700">Self-Doubt Spike</text>
            <text x="480" y="594" textAnchor="middle" fill={DIM} fontSize="20" fontFamily={FONT}>"I'm not ready"</text>
          </g>

          {/* Arrow marker */}
          <defs>
            <marker id="arrow" markerWidth="10" markerHeight="7" refX="10" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill={DIM} />
            </marker>
          </defs>
        </svg>
      </div>

      {/* Caption */}
      <div style={{ position: 'absolute', bottom: BOT_SAFE + 50, left: SIDE, right: SIDE, textAlign: 'center', opacity: captionIn }}>
        <span style={{ fontFamily: FONT, fontSize: 34, fontWeight: 400, color: DIM, fontStyle: 'italic' }}>
          Not a warning. An identity stretch.
        </span>
      </div>
    </div>
  );
};

// ─── Scene 3: "Confidence Comes After Proof. Not Before." ───────────────────────
const Scene3: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  const titleIn = sp(frame, fps, 5);

  // Two cards
  const card1In = sp(frame, fps, 30);
  const card2In = sp(frame, fps, 50);

  // Three count-up examples
  const ex1In = sp(frame, fps, 80);
  const ex2In = sp(frame, fps, 96);
  const ex3In = sp(frame, fps, 112);

  return (
    <div style={{ opacity, width: '100%', height: '100%', position: 'absolute' }}>
      {/* Title */}
      <div style={{ position: 'absolute', top: TOP_SAFE + 30, left: SIDE, right: SIDE, textAlign: 'center', opacity: titleIn, transform: `translateY(${(1 - titleIn) * 30}px)` }}>
        <span style={{ fontFamily: FONT, fontSize: 54, fontWeight: 800, color: WHITE, lineHeight: 1.15 }}>
          Confidence Comes{'\n'}<span style={{ color: GREEN }}>After Proof.</span>{'\n'}Not Before.
        </span>
      </div>

      {/* Two comparison cards */}
      <div style={{ position: 'absolute', top: TOP_SAFE + 310, left: SIDE, right: SIDE, display: 'flex', gap: 28 }}>
        {/* Card A — Encouragement (red x) */}
        <div style={{ flex: 1, opacity: card1In, transform: `translateX(${(1 - card1In) * -60}px)`, background: '#ef444415', border: '2px solid #ef4444', borderRadius: 20, padding: '28px 20px', textAlign: 'center' }}>
          <div style={{ fontFamily: FONT, fontSize: 52, color: '#ef4444', marginBottom: 12 }}>X</div>
          <div style={{ fontFamily: FONT, fontSize: 30, fontWeight: 700, color: WHITE, marginBottom: 8 }}>Affirmations</div>
          <div style={{ fontFamily: FONT, fontSize: 24, color: DIM, lineHeight: 1.4 }}>
            "I am confident."{'\n'}Brain: not convinced.
          </div>
        </div>

        {/* Card B — Proof (green check) */}
        <div style={{ flex: 1, opacity: card2In, transform: `translateX(${(1 - card2In) * 60}px)`, background: `${GREEN}15`, border: `2px solid ${GREEN}`, borderRadius: 20, padding: '28px 20px', textAlign: 'center' }}>
          <div style={{ fontFamily: FONT, fontSize: 52, color: GREEN, marginBottom: 12 }}>✓</div>
          <div style={{ fontFamily: FONT, fontSize: 30, fontWeight: 700, color: WHITE, marginBottom: 8 }}>Adjacent Proof</div>
          <div style={{ fontFamily: FONT, fontSize: 24, color: DIM, lineHeight: 1.4 }}>
            One action taken.{'\n'}Brain: noted.
          </div>
        </div>
      </div>

      {/* Three proof examples */}
      <div style={{ position: 'absolute', top: TOP_SAFE + 760, left: SIDE, right: SIDE }}>
        {[
          { label: 'Say one sentence', spring: ex1In },
          { label: 'Post before polished', spring: ex2In },
          { label: 'Decide without certainty', spring: ex3In },
        ].map((ex, i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 20, marginBottom: 24, opacity: ex.spring, transform: `translateX(${(1 - ex.spring) * 30}px)` }}>
            <div style={{ width: 40, height: 40, borderRadius: '50%', background: `${GREEN}30`, border: `2px solid ${GREEN}`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
              <span style={{ fontFamily: FONT, fontSize: 22, fontWeight: 800, color: GREEN }}>{i + 1}</span>
            </div>
            <span style={{ fontFamily: FONT, fontSize: 36, fontWeight: 500, color: WHITE }}>{ex.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// ─── Scene 4: "The 24-Hour Rule" — Circular Loop + Break Arrow ─────────────────
const Scene4: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  const titleIn = sp(frame, fps, 5);
  const captionIn = sp(frame, fps, 20);

  const nodes = [
    { label: 'Doubt\nAppears',   color: AMBER   },
    { label: 'Wait',             color: '#ef4444' },
    { label: 'Story\nBuilds',    color: '#8b5cf6' },
    { label: 'Feels\nPermanent', color: '#ec4899' },
    { label: 'Paralysis',        color: '#ef4444' },
  ];

  const cx = 480, cy = 540, radius = 240;
  const totalNodes = nodes.length;

  // Staggered node appearances
  const nodeEnter = nodes.map((_, i) => sp(frame, fps, 40 + i * 15));
  // Arrows draw
  const arrowDraw = nodes.map((_, i) =>
    clamp01(interpolate(frame, [50 + i * 15, 70 + i * 15], [0, 1]))
  );

  // Break arrow from "Wait" node
  const breakIn = sp(frame, fps, 130);
  const breakPulse = interpolate(frame % 20, [0, 10, 20], [1, 1.15, 1]);

  return (
    <div style={{ opacity, width: '100%', height: '100%', position: 'absolute' }}>
      {/* Title */}
      <div style={{ position: 'absolute', top: TOP_SAFE + 20, left: SIDE, right: SIDE, textAlign: 'center', opacity: titleIn, transform: `translateY(${(1 - titleIn) * 30}px)` }}>
        <span style={{ fontFamily: FONT, fontSize: 64, fontWeight: 800, color: AMBER }}>
          The 24-Hour Rule
        </span>
      </div>

      {/* Caption: milk analogy */}
      <div style={{ position: 'absolute', top: TOP_SAFE + 120, left: SIDE + 20, right: SIDE + 20, textAlign: 'center', opacity: captionIn }}>
        <span style={{ fontFamily: FONT, fontSize: 32, fontWeight: 400, color: DIM, lineHeight: 1.5 }}>
          Self-doubt is like milk — manageable{'\n'}fresh, hardens when left sitting.
        </span>
      </div>

      {/* Circular node diagram */}
      <div style={{ position: 'absolute', top: TOP_SAFE + 230, left: 0, right: 0, display: 'flex', justifyContent: 'center' }}>
        <svg width={960} height={620} viewBox="0 0 960 620">
          {nodes.map((node, i) => {
            const angle = (i / totalNodes) * Math.PI * 2 - Math.PI / 2;
            const nx = cx + Math.cos(angle) * radius;
            const ny = cy - TOP_SAFE - 230 + Math.sin(angle) * radius;
            const nextAngle = ((i + 1) / totalNodes) * Math.PI * 2 - Math.PI / 2;
            const nx2 = cx + Math.cos(nextAngle) * radius;
            const ny2 = cy - TOP_SAFE - 230 + Math.sin(nextAngle) * radius;

            const lines = node.label.split('\n');

            return (
              <g key={i}>
                {/* Arc arrow to next node */}
                <line
                  x1={nx} y1={ny} x2={nx2} y2={ny2}
                  stroke={node.color}
                  strokeWidth="2.5"
                  opacity={0.4}
                  strokeDasharray="200"
                  strokeDashoffset={200 - arrowDraw[i] * 200}
                  markerEnd="url(#arrow2)"
                />
                {/* Node circle */}
                <g opacity={nodeEnter[i]} transform={`translate(${(1 - nodeEnter[i]) * 10}, 0)`}>
                  <circle cx={nx} cy={ny} r={52} fill={`${node.color}20`} stroke={node.color} strokeWidth="2.5" />
                  {lines.map((line, li) => (
                    <text key={li} x={nx} y={ny + (li - (lines.length - 1) / 2) * 22} textAnchor="middle" fill={node.color} fontSize="22" fontFamily={FONT} fontWeight="700">
                      {line}
                    </text>
                  ))}
                </g>
              </g>
            );
          })}

          {/* Center label */}
          <text x={cx} y={cy - TOP_SAFE - 230 + 8} textAnchor="middle" fill={DIM} fontSize="28" fontFamily={FONT} fontWeight="600" opacity={sp(frame, fps, 100)}>
            ∞ LOOP
          </text>

          {/* BREAK HERE arrow from "Wait" node outward */}
          {(() => {
            const waitAngle = (1 / totalNodes) * Math.PI * 2 - Math.PI / 2;
            const wx = cx + Math.cos(waitAngle) * radius;
            const wy = cy - TOP_SAFE - 230 + Math.sin(waitAngle) * radius;
            return (
              <g opacity={breakIn} transform={`scale(${breakPulse})`} style={{ transformOrigin: `${wx}px ${wy}px` }}>
                <line x1={wx + 40} y1={wy - 40} x2={wx + 140} y2={wy - 130} stroke={GREEN} strokeWidth="4" strokeLinecap="round" markerEnd="url(#arrow3)" />
                <rect x={wx + 100} y={wy - 190} width={200} height={54} rx="12" fill={`${GREEN}25`} stroke={GREEN} strokeWidth="2" />
                <text x={wx + 200} y={wy - 158} textAnchor="middle" fill={GREEN} fontSize="24" fontFamily={FONT} fontWeight="700">ACT NOW</text>
              </g>
            );
          })()}

          <defs>
            <marker id="arrow2" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
              <polygon points="0 0, 8 3, 0 6" fill={DIM} />
            </marker>
            <marker id="arrow3" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
              <polygon points="0 0, 8 3, 0 6" fill={GREEN} />
            </marker>
          </defs>
        </svg>
      </div>

      {/* Rule pill */}
      <div style={{ position: 'absolute', bottom: BOT_SAFE + 60, left: 0, right: 0, display: 'flex', justifyContent: 'center', opacity: breakIn }}>
        <div style={{ background: `${GREEN}20`, border: `2px solid ${GREEN}`, borderRadius: 40, padding: '14px 40px' }}>
          <span style={{ fontFamily: FONT, fontSize: 34, fontWeight: 700, color: GREEN }}>
            Take one step within 24 hours.
          </span>
        </div>
      </div>
    </div>
  );
};

// ─── Scene 5: "Outgrow It. Don't Fight It." + Particles ─────────────────────────
const PARTICLES = Array.from({ length: 14 }, (_, i) => ({
  x:       80 + (i * 73) % 920,
  size:    6  + (i % 5) * 4,
  speed:   0.6 + (i % 4) * 0.3,
  delay:   (i * 7) % 30,
  opacity: 0.08 + (i % 5) * 0.04,
}));

const Scene5: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  const titleIn = sp(frame, fps, 5);

  const steps = [
    { num: '1', label: 'Ask: what identity is being stretched?', color: INDIGO },
    { num: '2', label: 'Take one next step within 24 hours',    color: AMBER  },
    { num: '3', label: 'Repeat until the doubt has nowhere to live', color: GREEN },
  ];

  const stepEnter = steps.map((_, i) => sp(frame, fps, 50 + i * 20));
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
              top: 1920 - yOffset,
              width:  p.size,
              height: p.size,
              borderRadius: '50%',
              backgroundColor: INDIGO,
              opacity: p.opacity,
            }}
          />
        );
      })}

      {/* Title */}
      <div style={{ position: 'absolute', top: TOP_SAFE + 30, left: SIDE, right: SIDE, textAlign: 'center', opacity: titleIn, transform: `translateY(${(1 - titleIn) * 30}px)` }}>
        <span style={{ fontFamily: FONT, fontSize: 64, fontWeight: 800, color: WHITE, lineHeight: 1.1 }}>
          Outgrow It.{'\n'}<span style={{ color: INDIGO }}>Don't Fight It.</span>
        </span>
      </div>

      {/* Three steps */}
      <div style={{ position: 'absolute', top: TOP_SAFE + 340, left: SIDE, right: SIDE }}>
        {steps.map((step, i) => (
          <div
            key={i}
            style={{
              display: 'flex',
              alignItems: 'flex-start',
              gap: 24,
              marginBottom: 52,
              opacity: stepEnter[i],
              transform: `translateX(${(1 - stepEnter[i]) * 40}px)`,
            }}
          >
            <div style={{ width: 60, height: 60, borderRadius: '50%', background: `${step.color}25`, border: `2px solid ${step.color}`, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, marginTop: 4 }}>
              <span style={{ fontFamily: FONT, fontSize: 32, fontWeight: 800, color: step.color }}>{step.num}</span>
            </div>
            <span style={{ fontFamily: FONT, fontSize: 36, fontWeight: 600, color: WHITE, lineHeight: 1.35 }}>
              {step.label}
            </span>
          </div>
        ))}
      </div>

      {/* Tagline */}
      <div style={{ position: 'absolute', bottom: BOT_SAFE + 200, left: SIDE, right: SIDE, textAlign: 'center', opacity: sp(frame, fps, 110) }}>
        <span style={{ fontFamily: FONT, fontSize: 36, fontWeight: 600, color: WHITE, fontStyle: 'italic' }}>
          The gap closes. The doubt loses its hold.
        </span>
      </div>

      {/* CTA */}
      <div style={{ position: 'absolute', bottom: BOT_SAFE + 50, left: SIDE + 20, right: SIDE + 20, textAlign: 'center', opacity: ctaIn, transform: `scale(${ctaIn})` }}>
        <div style={{ display: 'inline-block', background: `${GREEN}20`, border: `2px solid ${GREEN}`, borderRadius: 16, padding: '18px 44px' }}>
          <span style={{ fontFamily: FONT, fontSize: 36, fontWeight: 700, color: GREEN }}>
            Take the Fear Audit — Link in bio
          </span>
        </div>
      </div>
    </div>
  );
};

// ─── Progress Bar ────────────────────────────────────────────────────────────────
const ProgressBar: React.FC<{ frame: number }> = ({ frame }) => (
  <div style={{ position: 'absolute', bottom: BOT_SAFE - 30, left: SIDE, right: SIDE, height: 4, backgroundColor: 'rgba(255,255,255,0.1)', borderRadius: 2, zIndex: 100 }}>
    <div style={{ height: '100%', width: `${(frame / TOTAL) * 100}%`, backgroundColor: INDIGO, borderRadius: 2 }} />
  </div>
);

// ─── Main Composition ────────────────────────────────────────────────────────────
export const SelfDoubtExplainer: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const scenes = [
    { start: 0,                        Component: Scene1 },
    { start: SCENE_FRAMES - FADE,      Component: Scene2 },
    { start: (SCENE_FRAMES - FADE) * 2, Component: Scene3 },
    { start: (SCENE_FRAMES - FADE) * 3, Component: Scene4 },
    { start: (SCENE_FRAMES - FADE) * 4, Component: Scene5 },
  ];

  return (
    <div style={{ width: 1080, height: 1920, backgroundColor: BG, position: 'relative', overflow: 'hidden', fontFamily: FONT }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');`}</style>

      {/* Background music */}
      <Audio src={staticFile('music.mp3')} volume={0.07} loop />

      {/* Scenes */}
      {scenes.map(({ start, Component }, i) => (
        <Sequence key={i} from={start}>
          <Component frame={frame - start} fps={fps} />
        </Sequence>
      ))}

      {/* Progress bar always on top */}
      <ProgressBar frame={frame} />
    </div>
  );
};
