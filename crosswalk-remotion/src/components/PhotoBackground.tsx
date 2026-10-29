/**
 * PhotoBackground — renders a Freepik photo with a dark overlay.
 * Use this in compositions instead of CrosswalkBackground when a real photo is available.
 */
import React from 'react';
import { Img, useCurrentFrame, interpolate, Easing } from 'remotion';
import { theme } from '../theme';

type Motion = 'zoom-in' | 'zoom-out' | 'pan-left' | 'pan-right';

interface Props {
  src: string;           // e.g. staticFile('assets/bg-carousel-md-to-crossing-guard.jpg')
  overlayOpacity?: number; // 0–1, default 0.55
  overlayColor?: string;   // default charcoal
  parallax?: boolean;      // subtle Ken Burns motion, default true
  motion?: Motion;         // motion style, default 'zoom-in' (matches legacy behavior)
  durationInFrames?: number; // easing window for the motion, default 600 (legacy default)
}

export const PhotoBackground: React.FC<Props> = ({
  src,
  overlayOpacity = 0.55,
  overlayColor = theme.colors.charcoal,
  parallax = true,
  motion = 'zoom-in',
  durationInFrames = 600,
}) => {
  const frame = useCurrentFrame();
  const easing = Easing.out(Easing.quad);

  let scale = 1;
  let panPercent = 0;

  if (parallax) {
    switch (motion) {
      case 'zoom-out':
        scale = interpolate(frame, [0, durationInFrames], [1.08, 1.0], {
          extrapolateRight: 'clamp',
          easing,
        });
        break;
      case 'pan-left':
        scale = 1.1;
        panPercent = interpolate(frame, [0, durationInFrames], [2, -2], {
          extrapolateRight: 'clamp',
          easing,
        });
        break;
      case 'pan-right':
        scale = 1.1;
        panPercent = interpolate(frame, [0, durationInFrames], [-2, 2], {
          extrapolateRight: 'clamp',
          easing,
        });
        break;
      case 'zoom-in':
      default:
        scale = interpolate(frame, [0, durationInFrames], [1.0, 1.06], {
          extrapolateRight: 'clamp',
          easing,
        });
        break;
    }
  }

  return (
    <div style={{ position: 'absolute', inset: 0, overflow: 'hidden' }}>
      {/* Photo layer */}
      <Img
        src={src}
        style={{
          position: 'absolute',
          inset: 0,
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          objectPosition: 'center',
          transform: `translateX(${panPercent}%) scale(${scale})`,
          transformOrigin: 'center center',
        }}
      />
      {/* Dark overlay for text legibility */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundColor: overlayColor,
          opacity: overlayOpacity,
        }}
      />
      {/* Amber vignette glow at bottom */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: '40%',
          background: `radial-gradient(ellipse at 50% 100%, rgba(212,168,67,0.20) 0%, transparent 70%)`,
        }}
      />
    </div>
  );
};
