/**
 * AprilPost — animated Instagram post reel (1080×1920, 30fps, 8s / 240 frames)
 *
 * Layers:
 *   1. PhotoBackground with Ken Burns zoom (or CrosswalkBackground if no image)
 *   2. Top gradient fade for logo safety
 *   3. Bottom gradient fade for handle safety
 *   4. Logo — top-left, springs in at frame 5
 *   5. Date pill — top-right, fades in at frame 10
 *   6. Hook text — center-high, Playfair Display, springs up at frame 18
 *   7. Sub text — below hook, Inter, fades in at frame 55
 *   8. @crosswalkwisdom handle — bottom center, fades in at frame 22
 */
import React from 'react';
import { useCurrentFrame, useVideoConfig, spring, interpolate } from 'remotion';
import { theme } from '../theme';
import { Logo } from '../components/Logo';
import { PhotoBackground } from '../components/PhotoBackground';
import { CrosswalkBackground } from '../components/CrosswalkBackground';
import { APRIL_POSTS } from '../data/april-posts';
import { MARCH_POSTS } from '../data/march-posts';

export interface AprilPostProps {
  postId: string;
}

export const AprilPost: React.FC<AprilPostProps> = ({ postId }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const post = APRIL_POSTS.find((p) => p.slug === postId) ?? MARCH_POSTS.find((p) => p.slug === postId);
  if (!post) return null;

  // ── Spring helpers ────────────────────────────────────────────────────────
  const logoSpring = spring({ frame: frame - 5, fps, config: { damping: 200 } });
  const hookSpring = spring({ frame: frame - 18, fps, config: { damping: 160, stiffness: 80 } });
  const subFade = interpolate(frame, [55, 80], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const handleFade = interpolate(frame, [22, 45], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const dateFade = interpolate(frame, [10, 30], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const pillFade = interpolate(frame, [8, 28], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  // Hook rises up as it springs in
  const hookTranslateY = interpolate(hookSpring, [0, 1], [60, 0]);

  // Safe zones
  const SAFE_TOP = 150;
  const SAFE_BOTTOM = 170;
  const SAFE_SIDE = 60;

  return (
    <div style={{ width: 1080, height: 1920, position: 'relative', overflow: 'hidden', fontFamily: theme.fonts.sans }}>

      {/* ── Background ─────────────────────────────────────────────────────── */}
      {post.image ? (
        <PhotoBackground src={post.image} overlayOpacity={0.52} parallax />
      ) : (
        <CrosswalkBackground variant="warm" animate />
      )}

      {/* ── Top gradient (darkens the top third for logo legibility) ─────── */}
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0, height: 400,
        background: 'linear-gradient(to bottom, rgba(0,0,0,0.55) 0%, transparent 100%)',
      }} />

      {/* ── Bottom gradient (darkens bottom third for handle legibility) ─── */}
      <div style={{
        position: 'absolute', bottom: 0, left: 0, right: 0, height: 380,
        background: 'linear-gradient(to top, rgba(0,0,0,0.65) 0%, transparent 100%)',
      }} />

      {/* ── Logo — top left ───────────────────────────────────────────────── */}
      <div style={{
        position: 'absolute',
        top: SAFE_TOP,
        left: SAFE_SIDE,
        opacity: logoSpring,
        transform: `scale(${interpolate(logoSpring, [0, 1], [0.85, 1])})`,
        transformOrigin: 'top left',
      }}>
        <Logo size={28} color={theme.colors.amber} />
      </div>

      {/* ── Date pill — top right ─────────────────────────────────────────── */}
      <div style={{
        position: 'absolute',
        top: SAFE_TOP,
        right: SAFE_SIDE,
        opacity: dateFade,
        backgroundColor: 'rgba(212,168,67,0.18)',
        border: `1.5px solid rgba(212,168,67,0.45)`,
        borderRadius: 100,
        paddingTop: 8,
        paddingBottom: 8,
        paddingLeft: 20,
        paddingRight: 20,
        display: 'flex',
        alignItems: 'center',
        gap: 0,
      }}>
        <span style={{
          fontFamily: theme.fonts.sans,
          fontWeight: 600,
          fontSize: 26,
          color: theme.colors.amber,
          letterSpacing: '0.02em',
        }}>
          {post.label}
        </span>
      </div>

      {/* ── Amber accent bar ──────────────────────────────────────────────── */}
      <div style={{
        position: 'absolute',
        top: 760,
        left: SAFE_SIDE,
        width: 52,
        height: 5,
        borderRadius: 3,
        backgroundColor: theme.colors.amber,
        opacity: hookSpring,
      }} />

      {/* ── Hook text ─────────────────────────────────────────────────────── */}
      <div style={{
        position: 'absolute',
        top: 790,
        left: SAFE_SIDE,
        right: SAFE_SIDE,
        opacity: hookSpring,
        transform: `translateY(${hookTranslateY}px)`,
      }}>
        <p style={{
          fontFamily: theme.fonts.serif,
          fontWeight: 700,
          fontSize: 68,
          lineHeight: 1.18,
          color: theme.colors.warmWhite,
          margin: 0,
          whiteSpace: 'pre-line',
        }}>
          {post.hook}
        </p>
      </div>

      {/* ── Sub text ──────────────────────────────────────────────────────── */}
      <div style={{
        position: 'absolute',
        top: 1060,
        left: SAFE_SIDE,
        right: SAFE_SIDE,
        opacity: subFade,
      }}>
        <p style={{
          fontFamily: theme.fonts.sans,
          fontWeight: 400,
          fontSize: 36,
          lineHeight: 1.55,
          color: 'rgba(250,247,242,0.80)',
          margin: 0,
          whiteSpace: 'pre-line',
        }}>
          {post.sub}
        </p>
      </div>

      {/* ── @crosswalkwisdom handle — bottom ─────────────────────────────── */}
      <div style={{
        position: 'absolute',
        bottom: SAFE_BOTTOM,
        left: 0,
        right: 0,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: 8,
        opacity: handleFade,
      }}>
        {/* Thin amber separator */}
        <div style={{
          width: 40,
          height: 2,
          borderRadius: 1,
          backgroundColor: 'rgba(212,168,67,0.6)',
          marginBottom: 4,
        }} />
        <span style={{
          fontFamily: theme.fonts.sans,
          fontWeight: 600,
          fontSize: 30,
          letterSpacing: '0.04em',
          color: theme.colors.amber,
        }}>
          @crosswalkwisdom
        </span>
        <span style={{
          fontFamily: theme.fonts.sans,
          fontWeight: 400,
          fontSize: 24,
          color: 'rgba(250,247,242,0.55)',
          letterSpacing: '0.02em',
        }}>
          crosswalkwisdom.com
        </span>
      </div>
    </div>
  );
};
