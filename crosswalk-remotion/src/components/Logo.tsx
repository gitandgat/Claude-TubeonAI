import React from 'react';
import { theme } from '../theme';

export const Logo: React.FC<{ size?: number; color?: string }> = ({
  size = 32,
  color = theme.colors.amber,
}) => (
  <div
    style={{
      display: 'flex',
      alignItems: 'center',
      gap: 10,
    }}
  >
    {/* Crosswalk stripes icon */}
    <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      {[0, 1, 2, 3].map((i) => (
        <div
          key={i}
          style={{
            width: size,
            height: size * 0.18,
            backgroundColor: color,
            borderRadius: 2,
            opacity: i % 2 === 0 ? 1 : 0.6,
          }}
        />
      ))}
    </div>
    <span
      style={{
        fontFamily: theme.fonts.serif,
        fontSize: size * 0.75,
        color,
        fontWeight: 700,
        letterSpacing: '-0.02em',
        lineHeight: 1,
      }}
    >
      Crosswalk Wisdom
    </span>
  </div>
);
