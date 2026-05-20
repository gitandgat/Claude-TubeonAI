/**
 * "The Crosswalk Method" — Educational Explainer (1080×1920, 30fps, 30s = 900 frames)
 *
 * 5 scenes × 180 frames each. Kurzgesagt meets Fireship.
 * Dark (#0a0a0a), indigo accent, green emphasis, Inter font.
 * All icons/diagrams are inline SVG — no external assets.
 *
 * LAYOUT: Full 1600px safe zone per scene (top=150, bottom=170 from edges).
 * Every scene uses justifyContent: 'space-between' to fill the entire height.
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
const BG = '#0a0a0a';
const INDIGO = '#6366f1';
const GREEN = '#22c55e';
const AMBER = '#D4A843';
const TEAL = '#5B9A8B';
const WHITE = '#ffffff';
const DIM = 'rgba(255,255,255,0.5)';
const FONT = '"Inter", system-ui, sans-serif';

const SCENE_FRAMES = 180;
const FADE = 12;
const TOTAL = 900;
const TOP_SAFE = 150;
const BOT_SAFE = 170;
const SIDE = 60;

// ─── Helpers ──────────────────────────────────────────────────────────────────
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

// ─── Stage Pill ───────────────────────────────────────────────────────────────
const StagePill: React.FC<{
  label: string;
  color: string;
  opacity?: number;
  scale?: number;
}> = ({ label, color, opacity = 1, scale = 1 }) => (
  <div
    style={{
      display: 'inline-flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '12px 28px',
      borderRadius: 999,
      border: `2px solid ${color}`,
      background: `${color}26`,
      color: color,
      fontSize: 36,
      fontWeight: 700,
      letterSpacing: 2,
      opacity,
      transform: `scale(${scale})`,
      fontFamily: FONT,
    }}
  >
    {label}
  </div>
);

// ─── Scene 1: "Healthcare burnout is a crisis" ────────────────────────────────
const Scene1: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  const titleScale1 = sp(frame, fps, 5);
  const titleScale2 = sp(frame, fps, 15);
  const countRaw = interpolate(frame, [20, 80], [0, 63], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const countNum = Math.round(countRaw);
  const subtitleScale = sp(frame, fps, 50);

  const pillDelays = [90, 100, 110, 120];
  const pillLabels = ['START', 'STOP', 'ELDER', 'HUMAN'];
  const pillColors = [GREEN, AMBER, TEAL, INDIGO];
  const taglineScale = sp(frame, fps, 135);

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
      {/* Top block */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
        <div
          style={{
            color: WHITE,
            fontSize: 80,
            fontWeight: 700,
            textAlign: 'center',
            transform: `scale(${titleScale1})`,
            lineHeight: 1.1,
          }}
        >
          Healthcare burnout
        </div>
        <div
          style={{
            color: INDIGO,
            fontSize: 80,
            fontWeight: 800,
            textAlign: 'center',
            transform: `scale(${titleScale2})`,
            lineHeight: 1.1,
          }}
        >
          is a crisis.
        </div>
      </div>

      {/* Middle block */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 24 }}>
        <div
          style={{
            color: GREEN,
            fontSize: 240,
            fontWeight: 800,
            textAlign: 'center',
            fontVariantNumeric: 'tabular-nums',
            lineHeight: 1,
            textShadow: '0 0 40px rgba(34,197,94,0.5)',
          }}
        >
          {countNum}%
        </div>
        <div
          style={{
            color: DIM,
            fontSize: 44,
            textAlign: 'center',
            transform: `scale(${subtitleScale})`,
            lineHeight: 1.4,
            maxWidth: 800,
          }}
        >
          of healthcare workers report burnout
        </div>
      </div>

      {/* Bottom block */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 32 }}>
        <div style={{ display: 'flex', flexDirection: 'row', gap: 20, justifyContent: 'center' }}>
          {pillLabels.map((label, i) => (
            <StagePill
              key={label}
              label={label}
              color={pillColors[i]}
              scale={sp(frame, fps, pillDelays[i])}
            />
          ))}
        </div>
        <div
          style={{
            color: WHITE,
            fontSize: 46,
            fontWeight: 600,
            textAlign: 'center',
            transform: `scale(${taglineScale})`,
          }}
        >
          But burnout has stages. And a map.
        </div>
      </div>
    </div>
  );
};

// ─── Scene 2: "START — The Awareness Walk" ────────────────────────────────────
const Scene2: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  const titleScale = sp(frame, fps, 5);
  const subtitleScale = sp(frame, fps, 15);

  // Crosswalk rail draw animation
  const railOffset = interpolate(frame, [20, 80], [680, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  // Stripe draw animation
  const stripeOffset = interpolate(frame, [25, 85], [80, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  // Footstep scale
  const footScale = sp(frame, fps, 40);
  // Glowing pulse
  const glowR = 30 + Math.sin(frame * 0.1) * 5;

  const line1Scale = sp(frame, fps, 60);
  const line2Scale = sp(frame, fps, 72);
  const line3Scale = sp(frame, fps, 88);

  const stripeYPositions = [130, 210, 290, 370, 450, 530, 610, 690];

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
      {/* Top block */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
        <div
          style={{
            color: GREEN,
            fontSize: 100,
            fontWeight: 800,
            textAlign: 'center',
            transform: `scale(${titleScale})`,
            lineHeight: 1,
          }}
        >
          START
        </div>
        <div
          style={{
            color: WHITE,
            fontSize: 56,
            fontWeight: 600,
            textAlign: 'center',
            transform: `scale(${subtitleScale})`,
          }}
        >
          The Awareness Walk
        </div>
      </div>

      {/* Middle block — Crosswalk SVG */}
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <svg width={400} height={780} viewBox="0 0 400 780">
          {/* Left rail */}
          <line
            x1={160} y1={50} x2={160} y2={730}
            stroke={WHITE}
            strokeWidth={6}
            strokeDasharray={680}
            strokeDashoffset={railOffset}
          />
          {/* Right rail */}
          <line
            x1={240} y1={50} x2={240} y2={730}
            stroke={WHITE}
            strokeWidth={6}
            strokeDasharray={680}
            strokeDashoffset={railOffset}
          />
          {/* Horizontal stripes */}
          {stripeYPositions.map((y, i) => (
            <line
              key={i}
              x1={160} y1={y} x2={240} y2={y}
              stroke={WHITE}
              strokeWidth={20}
              strokeDasharray={80}
              strokeDashoffset={stripeOffset}
              opacity={0.4}
            />
          ))}
          {/* Glowing pulse circle */}
          <circle
            cx={200}
            cy={730}
            r={glowR}
            fill="rgba(34,197,94,0.2)"
            stroke={GREEN}
            strokeWidth={2}
          />
          {/* Footstep left */}
          <ellipse
            cx={185}
            cy={730}
            rx={20}
            ry={28}
            fill={GREEN}
            transform={`scale(${footScale}) translate(${(1 - footScale) * -185 / footScale}, ${(1 - footScale) * -730 / footScale})`}
            style={{ transformOrigin: '185px 730px' }}
          />
          {/* Footstep right */}
          <ellipse
            cx={215}
            cy={718}
            rx={18}
            ry={26}
            fill={GREEN}
            style={{ transformOrigin: '215px 718px', transform: `scale(${footScale})` }}
          />
        </svg>
      </div>

      {/* Bottom block */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20 }}>
        <div
          style={{
            color: WHITE,
            fontSize: 48,
            fontWeight: 600,
            textAlign: 'center',
            transform: `scale(${line1Scale})`,
          }}
        >
          You notice the cracks.
        </div>
        <div
          style={{
            color: DIM,
            fontSize: 44,
            textAlign: 'center',
            lineHeight: 1.4,
            transform: `scale(${line2Scale})`,
            maxWidth: 860,
          }}
        >
          Awareness is the first step onto the crosswalk.
        </div>
        <div
          style={{
            color: INDIGO,
            fontSize: 42,
            textAlign: 'center',
            transform: `scale(${line3Scale})`,
          }}
        >
          This is where most people are.
        </div>
      </div>
    </div>
  );
};

// ─── Scene 3: "STOP → ELDER" ──────────────────────────────────────────────────
const Scene3: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  // STOP panel
  const stopTitleScale = sp(frame, fps, 5);
  const stopSubScale = sp(frame, fps, 15);
  const stopHandOpacity = sp(frame, fps, 20);
  const stopBodyScale = sp(frame, fps, 30);

  // Divider line
  const dividerWidth = interpolate(frame, [60, 90], [0, 960], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  // ELDER panel
  const elderTitleScale = sp(frame, fps, 80);
  const elderSubScale = sp(frame, fps, 90);
  const elderCompassOpacity = sp(frame, fps, 85);
  const elderBodyScale = sp(frame, fps, 100);

  // Arrow
  const arrowOpacity = clamp01(interpolate(frame, [75, 90], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  }));

  // Compass needle dash animation
  const compassDash = interpolate(frame, [85, 140], [400, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

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
      {/* Top: STOP panel */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 18 }}>
        <div
          style={{
            color: AMBER,
            fontSize: 88,
            fontWeight: 800,
            textAlign: 'center',
            transform: `scale(${stopTitleScale})`,
            lineHeight: 1,
          }}
        >
          STOP
        </div>
        <div
          style={{
            color: WHITE,
            fontSize: 52,
            fontWeight: 600,
            textAlign: 'center',
            transform: `scale(${stopSubScale})`,
          }}
        >
          The Pause
        </div>
        {/* Open palm SVG */}
        <div style={{ opacity: stopHandOpacity, transform: `scale(${stopHandOpacity})` }}>
          <svg width={100} height={120} viewBox="0 0 100 120">
            {/* Palm */}
            <rect x={30} y={65} width={40} height={50} rx={8} fill="none" stroke={AMBER} strokeWidth={3} />
            {/* Thumb */}
            <rect x={12} y={58} width={18} height={38} rx={9} fill="none" stroke={AMBER} strokeWidth={3} />
            {/* Index */}
            <rect x={30} y={20} width={14} height={48} rx={7} fill="none" stroke={AMBER} strokeWidth={3} />
            {/* Middle */}
            <rect x={46} y={12} width={14} height={56} rx={7} fill="none" stroke={AMBER} strokeWidth={3} />
            {/* Ring */}
            <rect x={62} y={20} width={13} height={50} rx={6.5} fill="none" stroke={AMBER} strokeWidth={3} />
            {/* Pinky */}
            <rect x={76} y={30} width={11} height={38} rx={5.5} fill="none" stroke={AMBER} strokeWidth={3} />
          </svg>
        </div>
        <div
          style={{
            color: DIM,
            fontSize: 42,
            textAlign: 'center',
            transform: `scale(${stopBodyScale})`,
            maxWidth: 860,
            lineHeight: 1.4,
          }}
        >
          The old coping mechanisms stop working.
        </div>
      </div>

      {/* Middle: divider + arrow */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
        <div
          style={{
            width: dividerWidth,
            height: 2,
            background: 'rgba(99,102,241,0.4)',
            borderRadius: 2,
          }}
        />
        <div style={{ opacity: arrowOpacity, fontSize: 60, color: INDIGO, lineHeight: 1 }}>
          ↓
        </div>
      </div>

      {/* Bottom: ELDER panel */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 18 }}>
        <div
          style={{
            color: TEAL,
            fontSize: 88,
            fontWeight: 800,
            textAlign: 'center',
            transform: `scale(${elderTitleScale})`,
            lineHeight: 1,
          }}
        >
          ELDER
        </div>
        <div
          style={{
            color: WHITE,
            fontSize: 52,
            fontWeight: 600,
            textAlign: 'center',
            transform: `scale(${elderSubScale})`,
          }}
        >
          The Seeking
        </div>
        {/* Compass SVG */}
        <div style={{ opacity: elderCompassOpacity }}>
          <svg width={120} height={120} viewBox="0 0 120 120">
            {/* Outer circle */}
            <circle
              cx={60} cy={60} r={55}
              fill="none"
              stroke={TEAL}
              strokeWidth={3}
              strokeDasharray={400}
              strokeDashoffset={compassDash}
            />
            {/* N marker */}
            <text x={60} y={16} textAnchor="middle" fill={TEAL} fontSize={14} fontWeight={700} fontFamily={FONT}>N</text>
            {/* S marker */}
            <text x={60} y={114} textAnchor="middle" fill={TEAL} fontSize={14} fontWeight={700} fontFamily={FONT}>S</text>
            {/* E marker */}
            <text x={112} y={65} textAnchor="middle" fill={TEAL} fontSize={14} fontWeight={700} fontFamily={FONT}>E</text>
            {/* W marker */}
            <text x={8} y={65} textAnchor="middle" fill={TEAL} fontSize={14} fontWeight={700} fontFamily={FONT}>W</text>
            {/* Needle — diamond pointing north */}
            <polygon
              points="60,22 67,60 60,72 53,60"
              fill={TEAL}
              opacity={elderCompassOpacity}
            />
            <polygon
              points="60,98 67,60 60,72 53,60"
              fill={TEAL}
              opacity={0.3 * elderCompassOpacity}
            />
            {/* Center dot */}
            <circle cx={60} cy={60} r={5} fill={TEAL} />
          </svg>
        </div>
        <div
          style={{
            color: DIM,
            fontSize: 42,
            textAlign: 'center',
            transform: `scale(${elderBodyScale})`,
            maxWidth: 860,
            lineHeight: 1.4,
          }}
        >
          You reach for books, mentors, coaches.
        </div>
      </div>
    </div>
  );
};

// ─── Scene 4: "HUMAN — The Reckoning" ────────────────────────────────────────
const Scene4: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  const titleScale = sp(frame, fps, 5);
  const subtitleScale = sp(frame, fps, 15);

  // Heart draw
  const heartDash = interpolate(frame, [15, 80], [600, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const heartPulse = 1 + Math.sin(frame * 0.1) * 0.04;

  const line1Scale = sp(frame, fps, 50);
  const line2Scale = sp(frame, fps, 62);
  const line3Scale = sp(frame, fps, 74);
  const tagline1Scale = sp(frame, fps, 90);
  const tagline2Scale = sp(frame, fps, 100);

  const pillDelays = [112, 120, 128, 136];
  const pillLabels = ['START', 'STOP', 'ELDER', 'HUMAN'];
  const pillColors = [GREEN, AMBER, TEAL, INDIGO];

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
      {/* Top block */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 16 }}>
        <div
          style={{
            color: INDIGO,
            fontSize: 100,
            fontWeight: 800,
            textAlign: 'center',
            transform: `scale(${titleScale})`,
            lineHeight: 1,
          }}
        >
          HUMAN
        </div>
        <div
          style={{
            color: WHITE,
            fontSize: 56,
            fontWeight: 600,
            textAlign: 'center',
            transform: `scale(${subtitleScale})`,
          }}
        >
          The Reckoning
        </div>
      </div>

      {/* Middle block */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 32 }}>
        {/* Heart SVG */}
        <svg
          width={280}
          height={260}
          viewBox="0 0 280 260"
          style={{ transform: `scale(${heartPulse})` }}
        >
          <path
            d="M140,220 C80,180 20,130 20,80 C20,40 50,15 80,15 C105,15 125,30 140,50 C155,30 175,15 200,15 C230,15 260,40 260,80 C260,130 200,180 140,220Z"
            stroke={INDIGO}
            strokeWidth={3}
            fill="none"
            strokeDasharray={600}
            strokeDashoffset={heartDash}
          />
        </svg>

        {/* Text below heart */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20 }}>
          <div
            style={{
              color: WHITE,
              fontSize: 52,
              fontWeight: 700,
              textAlign: 'center',
              transform: `scale(${line1Scale})`,
            }}
          >
            The armor comes off.
          </div>
          <div
            style={{
              color: DIM,
              fontSize: 46,
              textAlign: 'center',
              transform: `scale(${line2Scale})`,
            }}
          >
            You're not the job title anymore.
          </div>
          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              justifyContent: 'center',
              gap: 8,
              transform: `scale(${line3Scale})`,
            }}
          >
            <span style={{ color: WHITE, fontSize: 44 }}>You're a human who gave</span>
            <span style={{ color: INDIGO, fontSize: 44, fontWeight: 700 }}>more than they had.</span>
          </div>
        </div>
      </div>

      {/* Bottom block */}
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 24 }}>
        <div
          style={{
            color: GREEN,
            fontSize: 46,
            textAlign: 'center',
            transform: `scale(${tagline1Scale})`,
          }}
        >
          This isn't rock bottom.
        </div>
        <div
          style={{
            color: GREEN,
            fontSize: 56,
            fontWeight: 800,
            textAlign: 'center',
            transform: `scale(${tagline2Scale})`,
          }}
        >
          It's the beginning.
        </div>
        <div style={{ display: 'flex', flexDirection: 'row', gap: 20, justifyContent: 'center' }}>
          {pillLabels.map((label, i) => (
            <StagePill
              key={label}
              label={label}
              color={pillColors[i]}
              scale={sp(frame, fps, pillDelays[i])}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

// ─── Scene 5: CTA + Particles ─────────────────────────────────────────────────
const Scene5: React.FC<{ frame: number; fps: number }> = ({ frame, fps }) => {
  const opacity = fadeInOut(frame, SCENE_FRAMES);

  const particleXs = [90, 200, 310, 420, 530, 640, 750, 860, 150, 400, 650, 900];
  const particleSizes = [8, 5, 12, 6, 10, 7, 14, 5, 9, 11, 6, 8];
  const particleColors = [INDIGO, GREEN, AMBER, TEAL, INDIGO, GREEN, AMBER, TEAL, INDIGO, GREEN, AMBER, TEAL];

  const titleScale = sp(frame, fps, 10);
  const meterScale = sp(frame, fps, 30);
  const dotPulse = Math.sin(frame * 0.15) * 0.15 + 1;

  const cta1Scale = sp(frame, fps, 50);
  const cta2Scale = sp(frame, fps, 62);
  const cta3Scale = sp(frame, fps, 74);
  const urlScale = sp(frame, fps, 90);
  const brandScale = sp(frame, fps, 105);

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        opacity,
        fontFamily: FONT,
      }}
    >
      {/* Particle background */}
      <svg
        width={1080}
        height={1920}
        style={{ position: 'absolute', inset: 0 }}
      >
        {particleXs.map((x, i) => {
          const y = interpolate(frame, [0, 180], [1920 + i * 100, -200], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          return (
            <circle
              key={i}
              cx={x}
              cy={y}
              r={particleSizes[i]}
              fill={particleColors[i]}
              opacity={0.35}
            />
          );
        })}
      </svg>

      {/* Main content */}
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
        {/* Top */}
        <div
          style={{
            color: WHITE,
            fontSize: 84,
            fontWeight: 800,
            textAlign: 'center',
            transform: `scale(${titleScale})`,
            lineHeight: 1.1,
          }}
        >
          Which stage are you in?
        </div>

        {/* Middle: meter + CTA text */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 40 }}>
          {/* Stage progress meter */}
          <div style={{ transform: `scale(${meterScale})`, width: 960 }}>
            <div
              style={{
                width: 960,
                height: 24,
                display: 'flex',
                borderRadius: 12,
                overflow: 'hidden',
              }}
            >
              {/* START segment */}
              <div style={{ flex: 1, height: '100%', background: GREEN }} />
              {/* STOP segment */}
              <div style={{ flex: 1, height: '100%', background: AMBER }} />
              {/* ELDER segment — with glowing dot */}
              <div style={{ flex: 1, height: '100%', background: TEAL, position: 'relative' }}>
                <div
                  style={{
                    position: 'absolute',
                    right: 0,
                    top: -8,
                    width: 40,
                    height: 40,
                    borderRadius: '50%',
                    background: INDIGO,
                    boxShadow: '0 0 20px rgba(99,102,241,0.8)',
                    transform: `scale(${dotPulse})`,
                  }}
                />
              </div>
              {/* HUMAN segment */}
              <div style={{ flex: 1, height: '100%', background: INDIGO }} />
            </div>

            {/* Segment labels */}
            <div
              style={{
                width: 960,
                display: 'flex',
                flexDirection: 'row',
                marginTop: 16,
              }}
            >
              {[
                { label: 'START', color: GREEN },
                { label: 'STOP', color: AMBER },
                { label: 'ELDER', color: TEAL },
                { label: 'HUMAN', color: INDIGO },
              ].map(({ label, color }) => (
                <div
                  key={label}
                  style={{
                    flex: 1,
                    textAlign: 'center',
                    color,
                    fontSize: 36,
                    fontWeight: 700,
                    fontFamily: FONT,
                  }}
                >
                  {label}
                </div>
              ))}
            </div>
          </div>

          {/* CTA text lines */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 24 }}>
            <div
              style={{
                color: DIM,
                fontSize: 48,
                textAlign: 'center',
                transform: `scale(${cta1Scale})`,
              }}
            >
              Take the free assessment.
            </div>
            <div
              style={{
                color: WHITE,
                fontSize: 52,
                fontWeight: 600,
                textAlign: 'center',
                transform: `scale(${cta2Scale})`,
              }}
            >
              2 minutes. 12 questions.
            </div>
            <div
              style={{
                color: INDIGO,
                fontSize: 52,
                fontWeight: 700,
                textAlign: 'center',
                transform: `scale(${cta3Scale})`,
              }}
            >
              Your personalized healing map.
            </div>
          </div>
        </div>

        {/* Bottom */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20 }}>
          <div
            style={{
              color: WHITE,
              fontSize: 64,
              fontWeight: 800,
              textAlign: 'center',
              textShadow: '0 0 24px rgba(99,102,241,0.8)',
              transform: `scale(${urlScale})`,
            }}
          >
            crosswalkwisdom.com
          </div>
          <div
            style={{
              color: DIM,
              fontSize: 34,
              letterSpacing: 6,
              textAlign: 'center',
              transform: `scale(${brandScale})`,
            }}
          >
            CROSSWALK WISDOM
          </div>
        </div>
      </div>
    </div>
  );
};

// ─── Main Export ──────────────────────────────────────────────────────────────
export const CrosswalkMethodExplainer: React.FC = () => {
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
      <Audio src={staticFile('voiceover-crosswalk-method.wav')} volume={1.0} />
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
