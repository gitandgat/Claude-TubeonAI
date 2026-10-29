import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Sequence,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  interpolate,
} from 'remotion';
import captionPages from '../data/glute-captions.json';
import { PhotoBackground } from '../components/PhotoBackground';

type CaptionToken = { text: string; fromMs: number; toMs: number };
type CaptionPage = { text: string; startMs: number; tokens: CaptionToken[] };

// Glute Longevity palette (from the landing page) — NOT the Crosswalk theme.
const DARK = '#0d0d1a';
const TEAL = '#00A699';
const WHITE = '#ffffff';
const GRAY = '#9ca3af';
const SANS = 'Inter, "Helvetica Neue", Arial, system-ui, sans-serif';

// Narration: VoiSpark (onyx) TTS, 99.75s @ 30fps. Small tail buffer so the last word isn't clipped.
export const GLUTE_TITLE_FRAMES = 45; // 1.5s
export const GLUTE_FOOTAGE_FRAMES = 3008; // ~100s
export const GLUTE_ENDCARD_FRAMES = 120; // 4s
export const GLUTE_TOTAL_FRAMES =
  GLUTE_TITLE_FRAMES + GLUTE_FOOTAGE_FRAMES + GLUTE_ENDCARD_FRAMES;

// B-roll scenes timed to the script's 5 beats (thank -> problem -> mechanism -> offer -> next step),
// derived from the caption timestamps where each beat's opening line starts.
type BrollMotion = 'zoom-in' | 'zoom-out' | 'pan-left' | 'pan-right';
const BROLL_SCENES: { src: string; from: number; durationInFrames: number; motion: BrollMotion }[] = [
  { src: 'assets/glute-broll/scene-1-hello.jpg', from: 0, durationInFrames: 427, motion: 'zoom-in' },
  { src: 'assets/glute-broll/scene-2-problem.png', from: 427, durationInFrames: 810, motion: 'pan-right' },
  { src: 'assets/glute-broll/scene-3-mechanism.png', from: 1237, durationInFrames: 831, motion: 'zoom-out' },
  { src: 'assets/glute-broll/scene-4-offer.png', from: 2068, durationInFrames: 403, motion: 'pan-left' },
  { src: 'assets/glute-broll/scene-5-cta.png', from: 2471, durationInFrames: 537, motion: 'zoom-in' },
];

const Wordmark: React.FC<{ size: number }> = ({ size }) => (
  <div
    style={{
      fontFamily: SANS,
      fontWeight: 800,
      fontSize: size,
      letterSpacing: size * 0.08,
      color: WHITE,
    }}
  >
    GLUTE <span style={{ color: TEAL }}>LONGEVITY</span>
  </div>
);

const TitleCard: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(
    frame,
    [0, 10, GLUTE_TITLE_FRAMES - 12, GLUTE_TITLE_FRAMES],
    [0, 1, 1, 0],
    { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' }
  );
  return (
    <AbsoluteFill
      style={{ backgroundColor: DARK, justifyContent: 'center', alignItems: 'center', opacity }}
    >
      <Wordmark size={64} />
      <div style={{ width: 80, height: 3, backgroundColor: TEAL, margin: '24px 0' }} />
      <div style={{ fontFamily: SANS, fontSize: 24, color: GRAY, letterSpacing: 1 }}>
        A 2-minute introduction
      </div>
    </AbsoluteFill>
  );
};

const LowerThird: React.FC = () => {
  const frame = useCurrentFrame();
  const dur = 150;
  const opacity = interpolate(frame, [0, 12, dur - 14, dur], [0, 1, 1, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const ty = interpolate(frame, [0, 14], [24, 0], { extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ justifyContent: 'flex-end', alignItems: 'flex-start' }}>
      <div
        style={{
          opacity,
          transform: `translateY(${ty}px)`,
          margin: '0 0 56px 56px',
          display: 'flex',
          alignItems: 'stretch',
          backgroundColor: 'rgba(13,13,26,0.82)',
          borderRadius: 10,
          overflow: 'hidden',
        }}
      >
        <div style={{ width: 6, backgroundColor: TEAL }} />
        <div style={{ padding: '14px 22px' }}>
          <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 34, color: WHITE, lineHeight: 1.1 }}>
            Sahawat
          </div>
          <div style={{ fontFamily: SANS, fontSize: 20, color: TEAL, marginTop: 4 }}>
            Former Physician · Founder, Glute Longevity
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

const EndCard: React.FC = () => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, 14], [0, 1], { extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill
      style={{ backgroundColor: DARK, justifyContent: 'center', alignItems: 'center', opacity }}
    >
      <Wordmark size={30} />
      <div style={{ height: 40 }} />
      <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 64, color: WHITE }}>
        Reply <span style={{ color: TEAL }}>&ldquo;I&rsquo;m in&rdquo;</span>
      </div>
      <div style={{ fontFamily: SANS, fontSize: 26, color: GRAY, marginTop: 18 }}>
        Founding spots are limited.
      </div>
    </AbsoluteFill>
  );
};

const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const ms = (frame / fps) * 1000;
  const pages = captionPages as CaptionPage[];
  if (pages.length === 0) return null;

  let active: CaptionPage | null = null;
  for (let i = 0; i < pages.length; i++) {
    const page = pages[i];
    const next = pages[i + 1];
    const lastTok = page.tokens[page.tokens.length - 1];
    const endMs = Math.min(
      next ? next.startMs : Number.MAX_SAFE_INTEGER,
      lastTok ? lastTok.toMs + 400 : page.startMs + 1500
    );
    if (ms >= page.startMs && ms < endMs) {
      active = page;
      break;
    }
  }
  if (!active) return null;

  return (
    <AbsoluteFill style={{ justifyContent: 'flex-end', alignItems: 'center' }}>
      <div
        style={{
          maxWidth: '82%',
          margin: '0 0 72px',
          padding: '12px 22px',
          backgroundColor: 'rgba(13,13,26,0.74)',
          borderRadius: 12,
          textAlign: 'center',
          fontFamily: SANS,
          fontWeight: 800,
          fontSize: 40,
          lineHeight: 1.2,
          color: WHITE,
          textShadow: '0 2px 8px rgba(0,0,0,0.5)',
        }}
      >
        {active.tokens.map((tok, i) => {
          const on = ms >= tok.fromMs && ms <= tok.toMs;
          return (
            <span key={i} style={{ color: on ? TEAL : WHITE }}>
              {tok.text}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

export const GluteIntro: React.FC = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: DARK }}>
      <Sequence durationInFrames={GLUTE_TITLE_FRAMES}>
        <TitleCard />
      </Sequence>

      <Sequence from={GLUTE_TITLE_FRAMES} durationInFrames={GLUTE_FOOTAGE_FRAMES}>
        <Audio src={staticFile('voiceover-glute-intro.wav')} volume={1.0} />
        {BROLL_SCENES.map((scene) => (
          <Sequence key={scene.src} from={scene.from} durationInFrames={scene.durationInFrames}>
            <PhotoBackground
              src={staticFile(scene.src)}
              overlayColor={DARK}
              overlayOpacity={0.32}
              motion={scene.motion}
              durationInFrames={scene.durationInFrames}
            />
          </Sequence>
        ))}
        <Captions />
      </Sequence>

      <Sequence from={GLUTE_TITLE_FRAMES + 45} durationInFrames={150}>
        <LowerThird />
      </Sequence>

      <Sequence
        from={GLUTE_TITLE_FRAMES + GLUTE_FOOTAGE_FRAMES}
        durationInFrames={GLUTE_ENDCARD_FRAMES}
      >
        <EndCard />
      </Sequence>
    </AbsoluteFill>
  );
};
