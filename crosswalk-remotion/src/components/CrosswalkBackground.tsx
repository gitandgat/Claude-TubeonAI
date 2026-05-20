import React from 'react';
import { useCurrentFrame, interpolate, Easing } from 'remotion';
import { theme } from '../theme';

interface Props {
  variant?: 'dark' | 'warm' | 'amber';
  animate?: boolean;
}

export const CrosswalkBackground: React.FC<Props> = ({
  variant = 'dark',
  animate = true,
}) => {
  const frame = useCurrentFrame();

  const bg = {
    dark: theme.colors.charcoal,
    warm: '#1E1810',
    amber: '#2A1F0A',
  }[variant];

  const stripeColor = {
    dark: 'rgba(212,168,67,0.07)',
    warm: 'rgba(232,131,74,0.06)',
    amber: 'rgba(212,168,67,0.10)',
  }[variant];

  const parallax = animate
    ? interpolate(frame, [0, 300], [0, 60], {
        extrapolateRight: 'clamp',
        easing: Easing.linear,
      })
    : 0;

  return (
    <div
      style={{
        position: 'absolute',
        inset: 0,
        backgroundColor: bg,
        overflow: 'hidden',
      }}
    >
      {/* Crosswalk stripes — vertical bands */}
      {Array.from({ length: 8 }).map((_, i) => (
        <div
          key={i}
          style={{
            position: 'absolute',
            top: 0,
            bottom: 0,
            left: `${i * 12.5}%`,
            width: '6%',
            backgroundColor: stripeColor,
            transform: `translateY(${parallax * (i % 2 === 0 ? 1 : -1)}px)`,
          }}
        />
      ))}
      {/* Warm amber vignette glow from bottom */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          height: '50%',
          background: `radial-gradient(ellipse at 50% 100%, rgba(212,168,67,0.15) 0%, transparent 70%)`,
        }}
      />
    </div>
  );
};
