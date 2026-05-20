/**
 * StoryReel — "The Morning Nobody Knew My Name"
 * 5-scene cinematic story reel — 1080×1920 · 30fps · 30s (900 frames)
 * Each scene: 6 seconds (180 frames), distinct background, spring text reveals.
 */
import React from 'react';
import {
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Easing,
  Sequence,
  Audio,
  staticFile,
} from 'remotion';
import { theme } from '../theme';
import { Logo } from '../components/Logo';
import { PhotoBackground } from '../components/PhotoBackground';

const SCENE_FRAMES = 180; // 6s per scene at 30fps

// ─── Scene background images ──────────────────────────────────────────────────
const BG = {
  winterCrosswalk: staticFile('assets/bg-story-winter-crosswalk.jpg'),
  yellowVest: staticFile('assets/bg-carousel-not-your-job-title.jpg'),
  childHand: staticFile('assets/bg-story-child-hand.jpg'),
  thailand: staticFile('assets/bg-story-thailand-return.jpg'),
};

// ─── Amber particles for scene 5 ──────────────────────────────────────────────
const PARTICLES = Array.from({ length: 14 }, (_, i) => ({
  id: i,
  x: 8 + (i * 73) % 84,   // spread across width %
  size: 6 + (i * 17) % 14,
  speed: 0.18 + (i * 0.07) % 0.22,
  delay: (i * 11) % 60,
  opacity: 0.25 + (i * 0.04) % 0.35,
}));

// ─── Spring text reveal helper ────────────────────────────────────────────────
function useReveal(localFrame: number, delay: number = 0, damping = 200) {
  return spring({
    frame: localFrame - delay,
    fps: 30,
    config: { damping, stiffness: 120, mass: 0.8 },
  });
}

// ─── Fade transition overlay ───────────────────────────────────────────────────
const SceneFade: React.FC<{ localFrame: number; totalFrames: number }> = ({
  localFrame,
  totalFrames,
}) => {
  // Fade in: first 8 frames
  const fadeIn = interpolate(localFrame, [0, 8], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  // Fade out: last 10 frames
  const fadeOut = interpolate(localFrame, [totalFrames - 10, totalFrames], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const opacity = Math.max(fadeIn, fadeOut);

  if (opacity <= 0) return null;
  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        backgroundColor: '#000',
        opacity,
        zIndex: 10,
        pointerEvents: 'none',
      }}
    />
  );
};

// ─── Safe-zone text block ─────────────────────────────────────────────────────
const SafeText: React.FC<{
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({ children, style }) => (
  <div
    style={{
      position: 'absolute',
      left: 60,
      right: 60,
      ...style,
    }}
  >
    {children}
  </div>
);

// ─── Scene 1: The Hook ────────────────────────────────────────────────────────
const Scene1: React.FC<{ localFrame: number }> = ({ localFrame }) => {
  const r1 = useReveal(localFrame, 2);
  const r2 = useReveal(localFrame, 8);
  const r3 = useReveal(localFrame, 22);

  return (
    <>
      <PhotoBackground src={BG.winterCrosswalk} overlayOpacity={0.50} />
      <SceneFade localFrame={localFrame} totalFrames={SCENE_FRAMES} />

      {/* Line 1 */}
      <SafeText style={{ top: 260 }}>
        <div
          style={{
            fontFamily: theme.fonts.serif,
            fontSize: 96,
            fontWeight: 700,
            color: theme.colors.warmWhite,
            lineHeight: 1.05,
            letterSpacing: '-0.02em',
            opacity: r1,
            transform: `translateY(${interpolate(r1, [0, 1], [30, 0])}px)`,
          }}
        >
          I was a doctor.
        </div>
      </SafeText>

      {/* Amber rule */}
      <SafeText style={{ top: 390 }}>
        <div
          style={{
            width: `${interpolate(r2, [0, 1], [0, 60])}%`,
            height: 3,
            backgroundColor: theme.colors.amber,
            borderRadius: 2,
          }}
        />
      </SafeText>

      {/* Line 2 */}
      <SafeText style={{ top: 415 }}>
        <div
          style={{
            fontFamily: theme.fonts.sans,
            fontSize: 56,
            fontWeight: 400,
            color: theme.colors.dimWhite,
            lineHeight: 1.35,
            opacity: r2,
            transform: `translateY(${interpolate(r2, [0, 1], [20, 0])}px)`,
          }}
        >
          Then I became a crossing guard in Canada.
        </div>
      </SafeText>

      {/* Temperature detail */}
      <SafeText style={{ top: 610 }}>
        <div
          style={{
            fontFamily: theme.fonts.sans,
            fontSize: 34,
            fontWeight: 300,
            color: theme.colors.amber,
            letterSpacing: '0.04em',
            opacity: r3 * 0.8,
          }}
        >
          −8°C. 6:45am.
        </div>
      </SafeText>
    </>
  );
};

// ─── Scene 2: The Setup ───────────────────────────────────────────────────────
const Scene2: React.FC<{ localFrame: number }> = ({ localFrame }) => {
  const r1 = useReveal(localFrame, 4);
  const r2 = useReveal(localFrame, 28);
  const r3 = useReveal(localFrame, 65);

  return (
    <>
      <PhotoBackground src={BG.yellowVest} overlayOpacity={0.52} />
      <SceneFade localFrame={localFrame} totalFrames={SCENE_FRAMES} />

      <SafeText style={{ top: 280 }}>
        <div
          style={{
            fontFamily: theme.fonts.serif,
            fontSize: 88,
            fontWeight: 700,
            color: theme.colors.warmWhite,
            lineHeight: 1.1,
            letterSpacing: '-0.02em',
            opacity: r1,
            transform: `translateY(${interpolate(r1, [0, 1], [30, 0])}px)`,
          }}
        >
          12 years.{'\n'}One title.
        </div>
      </SafeText>

      <SafeText style={{ top: 500 }}>
        <div
          style={{
            fontFamily: theme.fonts.sans,
            fontSize: 52,
            fontWeight: 400,
            color: theme.colors.dimWhite,
            lineHeight: 1.4,
            opacity: r2,
            transform: `translateY(${interpolate(r2, [0, 1], [18, 0])}px)`,
          }}
        >
          Dr. Sahawat walked into every room before I did.
        </div>
      </SafeText>

      <SafeText style={{ top: 690 }}>
        <div
          style={{
            fontFamily: theme.fonts.serif,
            fontSize: 52,
            fontWeight: 600,
            fontStyle: 'italic',
            color: theme.colors.amber,
            opacity: r3,
            transform: `translateY(${interpolate(r3, [0, 1], [14, 0])}px)`,
          }}
        >
          Then I left.
        </div>
      </SafeText>
    </>
  );
};

// ─── Scene 3: The Tension ─────────────────────────────────────────────────────
const Scene3: React.FC<{ localFrame: number }> = ({ localFrame }) => {
  const r1 = useReveal(localFrame, 3);
  const r2 = useReveal(localFrame, 22);
  const r3 = useReveal(localFrame, 55);

  return (
    <>
      <PhotoBackground src={BG.winterCrosswalk} overlayOpacity={0.62} parallax={false} />
      <SceneFade localFrame={localFrame} totalFrames={SCENE_FRAMES} />

      <SafeText style={{ top: 300 }}>
        <div
          style={{
            fontFamily: theme.fonts.serif,
            fontSize: 92,
            fontWeight: 700,
            color: theme.colors.warmWhite,
            lineHeight: 1.05,
            letterSpacing: '-0.02em',
            opacity: r1,
            transform: `translateY(${interpolate(r1, [0, 1], [28, 0])}px)`,
          }}
        >
          My hands were shaking.
        </div>
      </SafeText>

      <SafeText style={{ top: 440 }}>
        <div
          style={{
            fontFamily: theme.fonts.sans,
            fontSize: 52,
            fontWeight: 600,
            color: theme.colors.amber,
            letterSpacing: '-0.01em',
            opacity: r2,
            transform: `translateY(${interpolate(r2, [0, 1], [16, 0])}px)`,
          }}
        >
          Not from the cold.
        </div>
      </SafeText>

      <SafeText style={{ top: 545 }}>
        <div
          style={{
            fontFamily: theme.fonts.sans,
            fontSize: 48,
            fontWeight: 400,
            color: theme.colors.dimWhite,
            lineHeight: 1.45,
            opacity: r3,
            transform: `translateY(${interpolate(r3, [0, 1], [14, 0])}px)`,
          }}
        >
          Nobody driving past had any idea who I used to be.
        </div>
      </SafeText>
    </>
  );
};

// ─── Scene 4: The Turn ────────────────────────────────────────────────────────
const Scene4: React.FC<{ localFrame: number }> = ({ localFrame }) => {
  const r1 = useReveal(localFrame, 4);
  const r2 = useReveal(localFrame, 30);
  const r3 = useReveal(localFrame, 72);

  return (
    <>
      <PhotoBackground src={BG.childHand} overlayOpacity={0.38} />
      <SceneFade localFrame={localFrame} totalFrames={SCENE_FRAMES} />

      <SafeText style={{ top: 220 }}>
        <div
          style={{
            fontFamily: theme.fonts.sans,
            fontSize: 52,
            fontWeight: 400,
            color: theme.colors.dimWhite,
            lineHeight: 1.4,
            opacity: r1,
            transform: `translateY(${interpolate(r1, [0, 1], [18, 0])}px)`,
          }}
        >
          She didn't ask my name.
        </div>
      </SafeText>

      <SafeText style={{ top: 325 }}>
        <div
          style={{
            fontFamily: theme.fonts.serif,
            fontSize: 78,
            fontWeight: 700,
            color: theme.colors.warmWhite,
            lineHeight: 1.1,
            letterSpacing: '-0.02em',
            opacity: r2,
            transform: `translateY(${interpolate(r2, [0, 1], [26, 0])}px)`,
          }}
        >
          She just reached up and took my hand.
        </div>
      </SafeText>

      <SafeText style={{ top: 560 }}>
        <div
          style={{
            fontFamily: theme.fonts.sans,
            fontSize: 46,
            fontWeight: 400,
            color: theme.colors.dimWhite,
            lineHeight: 1.55,
            opacity: r3,
            transform: `translateY(${interpolate(r3, [0, 1], [12, 0])}px)`,
          }}
        >
          We crossed.{'\n'}She said thank you.{'\n'}She ran to class.
        </div>
      </SafeText>
    </>
  );
};

// ─── Scene 5: The Lesson ──────────────────────────────────────────────────────
const Scene5: React.FC<{ localFrame: number }> = ({ localFrame }) => {
  const r1 = useReveal(localFrame, 5);
  const r2 = useReveal(localFrame, 35);
  const r3 = useReveal(localFrame, 75);
  const r4 = useReveal(localFrame, 110);

  return (
    <>
      <PhotoBackground src={BG.thailand} overlayOpacity={0.45} />
      <SceneFade localFrame={localFrame} totalFrames={SCENE_FRAMES} />

      {/* Amber particles */}
      {PARTICLES.map((p) => {
        const progress = ((localFrame - p.delay + 300) % 300) / 300;
        const y = interpolate(progress, [0, 1], [1920, -60]);
        return (
          <div
            key={p.id}
            style={{
              position: 'absolute',
              left: `${p.x}%`,
              top: y,
              width: p.size,
              height: p.size,
              borderRadius: '50%',
              backgroundColor: theme.colors.amber,
              opacity: p.opacity * r1,
            }}
          />
        );
      })}

      <SafeText style={{ top: 280 }}>
        <div
          style={{
            fontFamily: theme.fonts.serif,
            fontSize: 84,
            fontWeight: 700,
            color: theme.colors.warmWhite,
            lineHeight: 1.08,
            letterSpacing: '-0.02em',
            opacity: r1,
            transform: `translateY(${interpolate(r1, [0, 1], [28, 0])}px)`,
          }}
        >
          Worth was never in the title.
        </div>
      </SafeText>

      <SafeText style={{ top: 495 }}>
        <div
          style={{
            fontFamily: theme.fonts.serif,
            fontSize: 68,
            fontWeight: 600,
            fontStyle: 'italic',
            color: theme.colors.amber,
            lineHeight: 1.15,
            opacity: r2,
            transform: `translateY(${interpolate(r2, [0, 1], [20, 0])}px)`,
          }}
        >
          It was always in the crossing.
        </div>
      </SafeText>

      {/* Divider */}
      <SafeText style={{ top: 620 }}>
        <div
          style={{
            width: `${interpolate(r3, [0, 1], [0, 45])}%`,
            height: 2,
            backgroundColor: theme.colors.amber,
            opacity: 0.6,
          }}
        />
      </SafeText>

      {/* CTA handle */}
      <SafeText style={{ top: 645 }}>
        <div
          style={{
            fontFamily: theme.fonts.sans,
            fontSize: 42,
            fontWeight: 500,
            color: theme.colors.amber,
            letterSpacing: '0.03em',
            opacity: r4,
          }}
        >
          @crosswalkwisdom
        </div>
      </SafeText>

      <SafeText style={{ top: 700 }}>
        <div
          style={{
            fontFamily: theme.fonts.sans,
            fontSize: 34,
            fontWeight: 400,
            color: 'rgba(250,247,242,0.6)',
            letterSpacing: '0.01em',
            opacity: r4,
          }}
        >
          crosswalkwisdom.com
        </div>
      </SafeText>
    </>
  );
};

// ─── Progress bar ─────────────────────────────────────────────────────────────
const ProgressBar: React.FC<{ frame: number; totalFrames: number }> = ({
  frame,
  totalFrames,
}) => {
  const progress = frame / totalFrames;
  return (
    <div
      style={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        height: 4,
        backgroundColor: 'rgba(255,255,255,0.15)',
      }}
    >
      <div
        style={{
          height: '100%',
          width: `${progress * 100}%`,
          backgroundColor: theme.colors.amber,
          borderRadius: 2,
        }}
      />
    </div>
  );
};

// ─── Main composition ─────────────────────────────────────────────────────────
export const StoryReel: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  return (
    <div style={{ position: 'absolute', inset: 0, backgroundColor: '#000', overflow: 'hidden' }}>
      {/* Background music */}
      <Audio src={staticFile('music.mp3')} volume={0.07} loop />

      {/* Scene 1 — 0–179 */}
      <Sequence from={0} durationInFrames={SCENE_FRAMES}>
        <Scene1 localFrame={frame} />
      </Sequence>

      {/* Scene 2 — 180–359 */}
      <Sequence from={SCENE_FRAMES} durationInFrames={SCENE_FRAMES}>
        <Scene2 localFrame={frame - SCENE_FRAMES} />
      </Sequence>

      {/* Scene 3 — 360–539 */}
      <Sequence from={SCENE_FRAMES * 2} durationInFrames={SCENE_FRAMES}>
        <Scene3 localFrame={frame - SCENE_FRAMES * 2} />
      </Sequence>

      {/* Scene 4 — 540–719 */}
      <Sequence from={SCENE_FRAMES * 3} durationInFrames={SCENE_FRAMES}>
        <Scene4 localFrame={frame - SCENE_FRAMES * 3} />
      </Sequence>

      {/* Scene 5 — 720–899 */}
      <Sequence from={SCENE_FRAMES * 4} durationInFrames={SCENE_FRAMES}>
        <Scene5 localFrame={frame - SCENE_FRAMES * 4} />
      </Sequence>

      {/* Logo — persistent, bottom-safe zone */}
      <div
        style={{
          position: 'absolute',
          bottom: 180,
          left: 60,
          opacity: interpolate(frame, [0, 20], [0, 1], { extrapolateRight: 'clamp' }),
        }}
      >
        <Logo size={22} />
      </div>

      {/* Progress bar */}
      <ProgressBar frame={frame} totalFrames={durationInFrames} />
    </div>
  );
};
