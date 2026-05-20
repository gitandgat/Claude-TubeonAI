import React from 'react';
import { useCurrentFrame, useVideoConfig, interpolate, Easing } from 'remotion';

interface Props {
  lines: string[];
  startFrame?: number;
  staggerFrames?: number;
  fontSize?: number;
  color?: string;
  fontFamily?: string;
  fontWeight?: number | string;
  lineHeight?: number;
  textAlign?: 'left' | 'center' | 'right';
}

export const AnimatedLines: React.FC<Props> = ({
  lines,
  startFrame = 0,
  staggerFrames = 8,
  fontSize = 48,
  color = '#FAF7F2',
  fontFamily = '"Inter", sans-serif',
  fontWeight = 400,
  lineHeight = 1.4,
  textAlign = 'left',
}) => {
  const frame = useCurrentFrame();

  return (
    <div style={{ textAlign }}>
      {lines.map((line, i) => {
        const lineStart = startFrame + i * staggerFrames;
        const opacity = interpolate(frame, [lineStart, lineStart + 10], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
          easing: Easing.out(Easing.quad),
        });
        const translateY = interpolate(frame, [lineStart, lineStart + 12], [16, 0], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
          easing: Easing.out(Easing.quad),
        });

        return (
          <div
            key={i}
            style={{
              opacity,
              transform: `translateY(${translateY}px)`,
              fontSize,
              color,
              fontFamily,
              fontWeight,
              lineHeight,
              marginBottom: fontSize * 0.3,
            }}
          >
            {line}
          </div>
        );
      })}
    </div>
  );
};
