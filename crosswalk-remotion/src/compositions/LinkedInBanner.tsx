/**
 * LinkedIn Banner — 1584×396 (static, render as PNG)
 * Text overlay on the right side of the crosswalk sunrise image.
 */
import React from 'react';
import { Img, staticFile } from 'remotion';
import { theme } from '../theme';
import { Logo } from '../components/Logo';

export const LinkedInBanner: React.FC = () => {
  return (
    <div
      style={{
        width: 1584,
        height: 396,
        position: 'relative',
        overflow: 'hidden',
        backgroundColor: theme.colors.black,
      }}
    >
      {/* Background photo — full bleed, no uniform overlay */}
      <Img
        src={staticFile('assets/bg-linkedin-banner.jpg')}
        style={{
          position: 'absolute',
          inset: 0,
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          objectPosition: 'center',
        }}
      />

      {/* Right-side gradient — darkens text zone over bright street lights */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background:
            'linear-gradient(to right, transparent 25%, rgba(12,10,8,0.55) 50%, rgba(12,10,8,0.78) 68%, rgba(12,10,8,0.88) 100%)',
        }}
      />

      {/* Subtle amber glow at bottom-right */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          right: 0,
          width: '50%',
          height: '60%',
          background:
            'radial-gradient(ellipse at 100% 100%, rgba(212,168,67,0.14) 0%, transparent 65%)',
        }}
      />

      {/* Text block — right-aligned */}
      <div
        style={{
          position: 'absolute',
          right: 72,
          top: 0,
          bottom: 0,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'flex-end',
          justifyContent: 'center',
          gap: 0,
        }}
      >
        {/* Brand label */}
        <div
          style={{
            fontFamily: theme.fonts.sans,
            fontSize: 15,
            fontWeight: 600,
            letterSpacing: '0.22em',
            textTransform: 'uppercase',
            color: theme.colors.amber,
            marginBottom: 10,
          }}
        >
          Crosswalk Wisdom
        </div>

        {/* Main headline line 1 */}
        <div
          style={{
            fontFamily: theme.fonts.serif,
            fontSize: 52,
            fontWeight: 700,
            lineHeight: 1.1,
            color: theme.colors.warmWhite,
            textAlign: 'right',
          }}
        >
          Your second act
        </div>

        {/* Main headline line 2 */}
        <div
          style={{
            fontFamily: theme.fonts.serif,
            fontSize: 52,
            fontWeight: 700,
            lineHeight: 1.1,
            color: theme.colors.amber,
            textAlign: 'right',
            marginBottom: 14,
          }}
        >
          starts here.
        </div>

        {/* URL */}
        <div
          style={{
            fontFamily: theme.fonts.sans,
            fontSize: 15,
            fontWeight: 400,
            color: 'rgba(250,247,242,0.55)',
            letterSpacing: '0.04em',
          }}
        >
          crosswalkwisdom.com
        </div>
      </div>

      {/* Logo — bottom left */}
      <div
        style={{
          position: 'absolute',
          bottom: 28,
          left: 36,
        }}
      >
        <Logo size={18} color={`rgba(212,168,67,0.5)`} />
      </div>
    </div>
  );
};
