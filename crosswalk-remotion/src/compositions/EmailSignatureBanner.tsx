/**
 * Email Signature Banner — 600×150 (static, render as PNG)
 * Fear Audit CTA over cinematic crosswalk background.
 */
import React from 'react';
import { Img, staticFile } from 'remotion';
import { theme } from '../theme';
import { Logo } from '../components/Logo';

export const EmailSignatureBanner: React.FC = () => {
  return (
    <div
      style={{
        width: 600,
        height: 150,
        position: 'relative',
        overflow: 'hidden',
        backgroundColor: theme.colors.black,
      }}
    >
      {/* Background photo — full bleed, focus on woman left-center */}
      <Img
        src={staticFile('assets/bg-email-signature-banner.jpg')}
        style={{
          position: 'absolute',
          inset: 0,
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          objectPosition: '35% center',
        }}
      />

      {/* Right-side gradient — darkens text zone */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          background:
            'linear-gradient(to right, transparent 30%, rgba(12,10,8,0.6) 50%, rgba(12,10,8,0.85) 65%, rgba(12,10,8,0.92) 100%)',
        }}
      />

      {/* Subtle amber glow bottom-right */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          right: 0,
          width: '50%',
          height: '70%',
          background:
            'radial-gradient(ellipse at 100% 100%, rgba(212,168,67,0.12) 0%, transparent 65%)',
        }}
      />

      {/* Text block — right side */}
      <div
        style={{
          position: 'absolute',
          right: 24,
          top: 0,
          bottom: 0,
          width: 280,
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
            fontSize: 8,
            fontWeight: 600,
            letterSpacing: '0.2em',
            textTransform: 'uppercase',
            color: theme.colors.amber,
            marginBottom: 6,
          }}
        >
          Crosswalk Wisdom
        </div>

        {/* Headline */}
        <div
          style={{
            fontFamily: theme.fonts.serif,
            fontSize: 18,
            fontWeight: 700,
            lineHeight: 1.2,
            color: theme.colors.warmWhite,
            textAlign: 'right',
            marginBottom: 8,
          }}
        >
          Are you stuck —{'\n'}or just scared?
        </div>

        {/* CTA */}
        <div
          style={{
            fontFamily: theme.fonts.sans,
            fontSize: 12,
            fontWeight: 600,
            color: theme.colors.amber,
            textAlign: 'right',
            marginBottom: 6,
          }}
        >
          Take the free Fear Audit →
        </div>

      </div>

      {/* Logo — bottom left */}
      <div
        style={{
          position: 'absolute',
          bottom: 12,
          left: 14,
        }}
      >
        <Logo size={12} color={`rgba(212,168,67,0.5)`} />
      </div>
    </div>
  );
};
