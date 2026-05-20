/**
 * PhotoBackground — renders a Freepik photo with a dark overlay.
 * Use this in compositions instead of CrosswalkBackground when a real photo is available.
 */
import React from 'react';
import { Img, useCurrentFrame, interpolate, Easing } from 'remotion';
import { theme } from '../theme';

interface Props {
  src: string;           // e.g. staticFile('assets/bg-carousel-md-to-crossing-guard.jpg')
  overlayOpacity?: number; // 0–1, default 0.55
  overlayColor?: string;   // default charcoal
  parallax?: boolean;      // subtle Ken Burns pan, default true
}

export const PhotoBackground: React.FC<Props> = ({
  src,
  overlayOpacity = 0.55,
  overlayColor = theme.colors.charcoal,
  parallax = true,
}) => {
  const frame = useCurrentFrame();

  const scale = parallax
    ? interpolate(frame, [0, 600], [1.0, 1.06], {
        extrapolateRight: 'clamp',
        easing: Easing.out(Easing.quad),
      })
    : 1;

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
          transform: `scale(${scale})`,
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
