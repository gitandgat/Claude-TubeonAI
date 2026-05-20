/**
 * Quiz Result Share Video — 1:1 (1080x1080) or 9:16 (1080x1920)
 * Shareable video generated after completing the Burnout Crosswalk Assessment.
 * stage prop: 'START' | 'STOP' | 'ELDER' | 'HUMAN'
 * format prop: 'square' | 'vertical'
 */
import React from 'react';
import { useCurrentFrame, interpolate, Easing, spring, useVideoConfig, staticFile } from 'remotion';
import { theme } from '../theme';
import { Logo } from '../components/Logo';
import { PhotoBackground } from '../components/PhotoBackground';
import { AnimatedLines } from '../components/AnimatedLines';

// ─── Stage data ─────────────────────────────────────────────────────────────────

const stages = {
  START: {
    label: 'START',
    subtitle: 'The Awareness Walk',
    color: theme.colors.teal,
    icon: '→',
    tagline: 'You\'re still standing.',
    message: [
      'The cracks haven\'t become canyons yet.',
      'But you\'re noticing them.',
      '',
      'This is the most powerful place to be.',
      'Awareness is where healing begins.',
      '',
      'The crosswalk is ahead of you.',
    ],
    score: '1.0 – 1.7',
  },
  STOP: {
    label: 'STOP',
    subtitle: 'The Pause',
    color: theme.colors.amber,
    icon: '◼',
    tagline: 'You\'ve hit the yellow light.',
    message: [
      'Something in you is saying "wait."',
      'And you\'re listening.',
      '',
      'The old coping mechanisms aren\'t working.',
      'But you haven\'t found new ones yet.',
      '',
      'This is not a failure.',
      'This is the pause before the turn.',
    ],
    score: '1.8 – 2.5',
  },
  ELDER: {
    label: 'ELDER',
    subtitle: 'The Seeking',
    color: theme.colors.orange,
    icon: '◎',
    tagline: 'You\'re looking for answers.',
    message: [
      'The answers inside feel depleted.',
      'So you\'re looking outside.',
      '',
      'You\'re not weak for seeking.',
      'You\'re wise.',
      '',
      'The crosswalk is right in front of you.',
      'You don\'t have to cross it alone.',
    ],
    score: '2.6 – 3.3',
  },
  HUMAN: {
    label: 'HUMAN',
    subtitle: 'The Reckoning',
    color: '#C0505A',
    icon: '♡',
    tagline: 'The armor comes off.',
    message: [
      'You\'re no longer the job title.',
      'The caregiver. The one who holds it together.',
      '',
      'You\'re a human being who has given',
      'more than they had to give.',
      '',
      'This isn\'t the end.',
      'It\'s the beginning.',
    ],
    score: '3.4 – 4.0',
  },
};

// ─── Animated score meter ───────────────────────────────────────────────────────

const ScoreMeter: React.FC<{ stage: keyof typeof stages; width: number }> = ({ stage, width }) => {
  const frame = useCurrentFrame();
  const stages_order: (keyof typeof stages)[] = ['START', 'STOP', 'ELDER', 'HUMAN'];
  const idx = stages_order.indexOf(stage);
  const targetProgress = (idx + 0.5) / 4;

  const progress = spring({
    frame: frame - 40,
    fps: 30,
    config: { damping: 18, stiffness: 60 },
    durationInFrames: 60,
  });
  const animatedProgress = progress * targetProgress;

  return (
    <div style={{ width, paddingTop: 24 }}>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginBottom: 10,
        }}
      >
        {stages_order.map((s) => (
          <div
            key={s}
            style={{
              fontFamily: theme.fonts.sans,
              fontSize: 18,
              color: s === stage ? stages[s].color : 'rgba(250,247,242,0.35)',
              fontWeight: s === stage ? 700 : 400,
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
            }}
          >
            {s}
          </div>
        ))}
      </div>
      {/* Track */}
      <div
        style={{
          position: 'relative',
          height: 8,
          backgroundColor: 'rgba(250,247,242,0.1)',
          borderRadius: 4,
        }}
      >
        {/* Fill */}
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            height: '100%',
            width: `${animatedProgress * 100}%`,
            backgroundColor: stages[stage].color,
            borderRadius: 4,
          }}
        />
        {/* Marker */}
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: `${animatedProgress * 100}%`,
            transform: 'translate(-50%, -50%)',
            width: 20,
            height: 20,
            borderRadius: '50%',
            backgroundColor: stages[stage].color,
            border: `3px solid ${theme.colors.warmWhite}`,
            boxShadow: `0 0 12px ${stages[stage].color}`,
          }}
        />
      </div>
    </div>
  );
};

// ─── Main composition ───────────────────────────────────────────────────────────

export const QuizResultVideo: React.FC<{
  stage?: keyof typeof stages;
  format?: 'square' | 'vertical';
}> = ({ stage = 'STOP', format = 'square' }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = stages[stage];

  const isVertical = format === 'vertical';
  const W = 1080;
  const H = isVertical ? 1920 : 1080;

  // Phase timings
  const badgeStart = 20;
  const messageStart = 60;
  const meterStart = 40;
  const ctaStart = messageStart + s.message.length * 8 + 20;

  // Badge scale spring
  const badgeScale = spring({
    frame: frame - badgeStart,
    fps,
    config: { damping: 14, stiffness: 80 },
    durationInFrames: 40,
  });

  const badgeOpacity = interpolate(frame, [badgeStart, badgeStart + 15], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const ctaOpacity = interpolate(frame, [ctaStart, ctaStart + 20], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const contentPadding = isVertical ? 80 : 70;
  const badgeFontSize = isVertical ? 36 : 28;
  const stageFontSize = isVertical ? 110 : 96;
  const subtitleFontSize = isVertical ? 44 : 36;
  const messageFontSize = isVertical ? 44 : 40;
  const meterWidth = isVertical ? W - contentPadding * 2 : W - contentPadding * 2;

  return (
    <div
      style={{
        width: W,
        height: H,
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <PhotoBackground
        src={staticFile('assets/bg-quiz-result-neutral.jpg')}
        overlayOpacity={0.60}
        parallax
      />

      {/* Colored glow from stage color */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '40%',
          background: `radial-gradient(ellipse at 50% 0%, ${s.color}22 0%, transparent 70%)`,
        }}
      />

      {/* Logo */}
      <div style={{ position: 'absolute', top: 60, left: contentPadding, zIndex: 10 }}>
        <Logo size={24} color={theme.colors.amber} />
      </div>

      {/* "Assessment Result" label */}
      <div
        style={{
          position: 'absolute',
          top: 68,
          right: contentPadding,
          fontFamily: theme.fonts.sans,
          fontSize: 20,
          color: 'rgba(250,247,242,0.35)',
          letterSpacing: '0.12em',
          textTransform: 'uppercase',
        }}
      >
        Burnout Assessment
      </div>

      {/* Main content */}
      <div
        style={{
          position: 'absolute',
          top: isVertical ? 180 : 140,
          left: contentPadding,
          right: contentPadding,
        }}
      >
        {/* Stage badge */}
        <div
          style={{
            opacity: badgeOpacity,
            transform: `scale(${badgeScale})`,
            marginBottom: isVertical ? 40 : 30,
          }}
        >
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: 12,
              backgroundColor: `${s.color}22`,
              border: `2px solid ${s.color}`,
              borderRadius: 100,
              padding: `${badgeFontSize * 0.4}px ${badgeFontSize * 0.9}px`,
            }}
          >
            <span style={{ fontSize: badgeFontSize * 1.2, color: s.color }}>{s.icon}</span>
            <span
              style={{
                fontFamily: theme.fonts.sans,
                fontSize: badgeFontSize,
                fontWeight: 700,
                color: s.color,
                letterSpacing: '0.12em',
                textTransform: 'uppercase',
              }}
            >
              You are at: {s.label}
            </span>
          </div>
        </div>

        {/* Stage name */}
        <div
          style={{
            fontFamily: theme.fonts.serif,
            fontSize: stageFontSize,
            fontWeight: 700,
            color: theme.colors.warmWhite,
            lineHeight: 1,
            marginBottom: 12,
            opacity: badgeOpacity,
          }}
        >
          {s.subtitle}
        </div>

        {/* Tagline */}
        <div
          style={{
            fontFamily: theme.fonts.sans,
            fontSize: subtitleFontSize,
            color: s.color,
            marginBottom: isVertical ? 48 : 36,
            opacity: badgeOpacity,
          }}
        >
          {s.tagline}
        </div>

        {/* Message lines */}
        <AnimatedLines
          lines={s.message}
          startFrame={messageStart}
          staggerFrames={7}
          fontSize={messageFontSize}
          color={theme.colors.warmWhite}
          fontFamily={theme.fonts.sans}
          fontWeight={400}
          lineHeight={1.4}
        />

        {/* Score meter */}
        <div style={{ marginTop: isVertical ? 60 : 40, opacity: badgeOpacity }}>
          <ScoreMeter stage={stage} width={meterWidth} />
        </div>

        {/* CTA */}
        <div style={{ opacity: ctaOpacity, marginTop: isVertical ? 60 : 40 }}>
          <div
            style={{
              backgroundColor: s.color,
              borderRadius: 12,
              padding: isVertical ? '24px 40px' : '18px 32px',
              display: 'inline-flex',
              alignItems: 'center',
              gap: 16,
            }}
          >
            <span
              style={{
                fontFamily: theme.fonts.sans,
                fontSize: isVertical ? 36 : 30,
                fontWeight: 700,
                color: theme.colors.charcoal,
              }}
            >
              Take the free assessment →
            </span>
          </div>
          <div
            style={{
              marginTop: 16,
              fontFamily: theme.fonts.sans,
              fontSize: isVertical ? 30 : 24,
              color: 'rgba(250,247,242,0.5)',
            }}
          >
            crosswalkwisdom.com
          </div>
        </div>
      </div>
    </div>
  );
};
