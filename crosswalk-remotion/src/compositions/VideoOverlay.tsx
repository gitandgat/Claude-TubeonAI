/**
 * VideoOverlay — 1:1 (1080×1080), 15 seconds
 * Cinematic Freepik background + animated hook text + "Comment FEAR 👇" CTA
 * Used for all 17 social posts. Replaces firstComment link with DM automation.
 */
import React from 'react';
import { useCurrentFrame, interpolate, Easing, staticFile } from 'remotion';
import { theme } from '../theme';
import { Logo } from '../components/Logo';
import { PhotoBackground } from '../components/PhotoBackground';

// ─── Data ────────────────────────────────────────────────────────────────────

type OverlayData = {
  bg: string;
  label: string;       // small label above the hook (e.g. "THE SUNK COST TRAP")
  hook: string[];      // hook text — split into lines for layout
  cta: string;
};

const OVERLAYS: Record<string, OverlayData> = {
  '01-sunk-cost': {
    bg: staticFile('assets/vo-01-sunk-cost.jpg'),
    label: 'THE SUNK COST TRAP',
    hook: ['The cage gets', 'smaller every', 'year you stay.'],
    cta: 'Comment FEAR 👇',
  },
  '02-what-will-people-think': {
    bg: staticFile('assets/vo-02-what-will-people-think.jpg'),
    label: 'WHAT WILL PEOPLE THINK',
    hook: ['"What will people', 'think" lasts', '5 minutes.'],
    cta: 'Comment FEAR 👇',
  },
  '03-quitting': {
    bg: staticFile('assets/vo-03-quitting.jpg'),
    label: 'QUITTING IS NOT FAILURE',
    hook: ['Staying was', 'autopilot.', 'Leaving was a choice.'],
    cta: 'Comment FEAR 👇',
  },
  '04-fear-audit-intro': {
    bg: staticFile('assets/vo-04-fear-audit-intro.jpg'),
    label: 'INTRODUCING THE FEAR AUDIT',
    hook: ['Unnamed fears', 'have all', 'the power.'],
    cta: 'Comment FEAR 👇',
  },
  '05-named-fear': {
    bg: staticFile('assets/vo-05-named-fear.jpg'),
    label: 'I NAMED MY FEAR',
    hook: ['Fear named is', 'fear that can', 'be questioned.'],
    cta: 'Comment FEAR 👇',
  },
  '06-five-fears': {
    bg: staticFile('assets/vo-06-five-fears.jpg'),
    label: 'THE 5 FEARS',
    hook: ['There are 5 fears', 'inside', '"I can\'t leave."'],
    cta: 'Comment FEAR 👇',
  },
  '07-four-stages': {
    bg: staticFile('assets/vo-07-four-stages.jpg'),
    label: 'THE 4 STAGES OF STUCK',
    hook: ['Not everyone', 'who\'s stuck', 'looks the same.'],
    cta: 'Comment FEAR 👇',
  },
  '09-why-i-built-it': {
    bg: staticFile('assets/vo-09-why-i-built-it.jpg'),
    label: 'WHY I BUILT THE FEAR AUDIT',
    hook: ['I knew what', 'I wanted.', 'I didn\'t know what was stopping me.'],
    cta: 'Comment FEAR 👇',
  },
  '10-psychiatrist': {
    bg: staticFile('assets/vo-10-psychiatrist.jpg'),
    label: 'THE PSYCHIATRIST',
    hook: ['"You have no idea', 'what you\'re', 'throwing away."'],
    cta: 'Comment FEAR 👇',
  },
  '11-phone-call': {
    bg: staticFile('assets/vo-11-phone-call.jpg'),
    label: 'THE PHONE CALL',
    hook: ['"I wondered when', 'you were going', 'to figure that out."'],
    cta: 'Comment FEAR 👇',
  },
  '12-yellow-vest': {
    bg: staticFile('assets/vo-12-yellow-vest.jpg'),
    label: 'THE YELLOW VEST',
    hook: ['Take off the armor.', 'Find out what\'s', 'underneath.'],
    cta: 'Comment FEAR 👇',
  },
  '13-loneliest': {
    bg: staticFile('assets/vo-13-loneliest.jpg'),
    label: 'THE LONELIEST SIX MONTHS',
    hook: ['Nobody tells you', 'about the', 'identity hangover.'],
    cta: 'Comment FEAR 👇',
  },
  '14-3am': {
    bg: staticFile('assets/vo-14-3am.jpg'),
    label: 'THE 3AM QUESTIONS',
    hook: ['3am thinking', 'isn\'t thinking.', 'It\'s fear in costume.'],
    cta: 'Comment FEAR 👇',
  },
  '15-take-it-personally': {
    bg: staticFile('assets/vo-15-take-it-personally.jpg'),
    label: 'WHEN THEY TAKE IT PERSONALLY',
    hook: ['Your courage', 'reveals', 'their cage.'],
    cta: 'Comment FEAR 👇',
  },
  '16-first-step': {
    bg: staticFile('assets/vo-16-first-step.jpg'),
    label: 'YOU DON\'T NEED A PLAN',
    hook: ['You don\'t need', 'a plan.', 'You need a first step.'],
    cta: 'Comment FEAR 👇',
  },
  '17-what-do-you-do': {
    bg: staticFile('assets/vo-17-what-do-you-do.jpg'),
    label: 'WHAT DO YOU DO?',
    hook: ['I help', 'people', 'cross.'],
    cta: 'Comment FEAR 👇',
  },
  '18-courage': {
    bg: staticFile('assets/vo-18-courage.jpg'),
    label: 'THE COURAGE TO CHOOSE',
    hook: ['Transformation should', 'not require', 'a second mortgage.'],
    cta: 'Comment FEAR 👇',
  },
};

// ─── Component ───────────────────────────────────────────────────────────────

export const VideoOverlay: React.FC<{ overlayId: string }> = ({ overlayId }) => {
  const frame = useCurrentFrame();
  const data = OVERLAYS[overlayId];

  if (!data) return null;

  const fps = 30;
  const totalFrames = 15 * fps; // 450

  // Label fades in 0→20
  const labelOpacity = interpolate(frame, [0, 20, totalFrames - 20, totalFrames], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.out(Easing.quad),
  });

  // Hook lines stagger in: line 0 at frame 15, line 1 at frame 25, line 2 at frame 35
  const hookLines = data.hook.map((line, i) => {
    const start = 15 + i * 12;
    const opacity = interpolate(frame, [start, start + 18, totalFrames - 20, totalFrames], [0, 1, 1, 0], {
      extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
      easing: Easing.out(Easing.cubic),
    });
    const translateY = interpolate(frame, [start, start + 18], [24, 0], {
      extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
      easing: Easing.out(Easing.cubic),
    });
    return { line, opacity, translateY };
  });

  // CTA fades + pulses in after hook
  const ctaStart = 15 + data.hook.length * 12 + 20;
  const ctaOpacity = interpolate(frame, [ctaStart, ctaStart + 20, totalFrames - 20, totalFrames], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  // Gentle pulse on CTA
  const ctaScale = 1 + 0.02 * Math.sin((frame - ctaStart) * 0.15);

  // Amber accent line slides in
  const accentWidth = interpolate(frame, [5, 35], [0, 120], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });

  return (
    <div style={{ width: 1080, height: 1080, position: 'relative', overflow: 'hidden', fontFamily: theme.fonts.sans }}>
      {/* Background */}
      <PhotoBackground src={data.bg} overlayOpacity={0.62} parallax />

      {/* Amber glow top-left accent */}
      <div style={{
        position: 'absolute', top: 0, left: 0, width: 320, height: 320,
        background: 'radial-gradient(ellipse at 0% 0%, rgba(212,168,67,0.18) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />

      {/* Logo — top left */}
      <div style={{ position: 'absolute', top: 48, left: 48 }}>
        <Logo size={52} />
      </div>

      {/* Label — small caps above hook */}
      <div style={{
        position: 'absolute', top: 48, right: 48,
        opacity: labelOpacity,
        color: theme.colors.amber,
        fontSize: 20,
        fontWeight: 700,
        letterSpacing: '0.12em',
        textTransform: 'uppercase',
        textAlign: 'right',
        maxWidth: 340,
        lineHeight: 1.3,
        textShadow: '0 1px 8px rgba(0,0,0,0.6)',
      }}>
        {data.label}
      </div>

      {/* Amber accent bar */}
      <div style={{
        position: 'absolute', left: 64, bottom: 290,
        width: accentWidth, height: 3,
        backgroundColor: theme.colors.amber,
        borderRadius: 2,
      }} />

      {/* Hook text block */}
      <div style={{
        position: 'absolute', left: 64, right: 64, bottom: 200,
        display: 'flex', flexDirection: 'column', gap: 2,
      }}>
        {hookLines.map(({ line, opacity, translateY }, i) => (
          <div key={i} style={{
            opacity,
            transform: `translateY(${translateY}px)`,
            color: theme.colors.warmWhite,
            fontSize: line.length > 20 ? 52 : 66,
            fontWeight: 800,
            lineHeight: 1.1,
            fontFamily: theme.fonts.serif,
            textShadow: '0 2px 16px rgba(0,0,0,0.7)',
            letterSpacing: '-0.01em',
          }}>
            {line}
          </div>
        ))}
      </div>

      {/* CTA pill */}
      <div style={{
        position: 'absolute', left: 64, bottom: 80,
        opacity: ctaOpacity,
        transform: `scale(${ctaScale})`,
        transformOrigin: 'left center',
      }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: 12,
          backgroundColor: theme.colors.amber,
          color: theme.colors.charcoal,
          paddingTop: 16, paddingBottom: 16,
          paddingLeft: 32, paddingRight: 32,
          borderRadius: 60,
          fontSize: 30,
          fontWeight: 800,
          letterSpacing: '0.02em',
          boxShadow: '0 4px 24px rgba(212,168,67,0.4)',
        }}>
          {data.cta}
        </div>
      </div>

      {/* Bottom brand line */}
      <div style={{
        position: 'absolute', bottom: 32, right: 48,
        color: 'rgba(250,247,242,0.55)',
        fontSize: 18,
        fontWeight: 500,
        letterSpacing: '0.06em',
        textTransform: 'uppercase',
      }}>
        crosswalkwisdom.com
      </div>
    </div>
  );
};
