/**
 * LinkedIn Post — 1920×1080 (static, render as PNG)
 * Stat-contrast visual for IMG pivot content.
 * postId selects the content variant.
 */
import React from 'react';
import { Img, staticFile } from 'remotion';
import { theme } from '../theme';
import { Logo } from '../components/Logo';

const BACKGROUNDS: Record<string, string> = {
  'sunk-cost-trap': staticFile('assets/post-sunk-cost.jpg'),
};

type PostData = {
  label: string;
  stat1: { value: string; sub: string };
  stat2: { value: string; sub: string; color: string };
  quote: string;
};

const posts: Record<string, PostData> = {
  'sunk-cost-trap': {
    label: 'Match Rate · Canada',
    stat1: {
      value: '97%',
      sub: 'Canadian medical graduates',
    },
    stat2: {
      value: '10–22%',
      sub: 'International Medical Graduates',
      color: theme.colors.amber,
    },
    quote: '"This is not a skill gap.\nIt is a structural failure."',
  },
};

export const LinkedInPost: React.FC<{ postId?: string }> = ({
  postId = 'sunk-cost-trap',
}) => {
  const post = posts[postId] ?? posts['sunk-cost-trap'];
  const bg = BACKGROUNDS[postId] ?? BACKGROUNDS['sunk-cost-trap'];

  return (
    <div
      style={{
        width: 1920,
        height: 1080,
        position: 'relative',
        overflow: 'hidden',
        backgroundColor: theme.colors.black,
      }}
    >
      {/* Background */}
      <Img
        src={bg}
        style={{
          position: 'absolute',
          inset: 0,
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          objectPosition: 'center',
        }}
      />

      {/* Dark overlay */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          backgroundColor: 'rgba(20,16,12,0.68)',
        }}
      />

      {/* Amber glow — bottom left */}
      <div
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          width: '55%',
          height: '55%',
          background:
            'radial-gradient(ellipse at 0% 100%, rgba(212,168,67,0.12) 0%, transparent 65%)',
        }}
      />

      {/* Top accent rule */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: 5,
          backgroundColor: theme.colors.amber,
        }}
      />

      {/* Logo — top left */}
      <div style={{ position: 'absolute', top: 56, left: 80 }}>
        <Logo size={28} color={theme.colors.amber} />
      </div>

      {/* Brand label — top right */}
      <div
        style={{
          position: 'absolute',
          top: 62,
          right: 80,
          fontFamily: theme.fonts.sans,
          fontSize: 20,
          fontWeight: 600,
          letterSpacing: '0.18em',
          textTransform: 'uppercase' as const,
          color: `rgba(212,168,67,0.7)`,
        }}
      >
        Crosswalk Wisdom · IMG
      </div>

      {/* ── Center content ── */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {/* Category label */}
        <div
          style={{
            fontFamily: theme.fonts.sans,
            fontSize: 22,
            fontWeight: 600,
            letterSpacing: '0.2em',
            textTransform: 'uppercase' as const,
            color: theme.colors.amber,
            marginBottom: 40,
          }}
        >
          {post.label}
        </div>

        {/* Stat 1 */}
        <div style={{ textAlign: 'center', marginBottom: 8 }}>
          <div
            style={{
              fontFamily: theme.fonts.serif,
              fontSize: 190,
              fontWeight: 700,
              lineHeight: 1,
              color: theme.colors.warmWhite,
              letterSpacing: '-0.02em',
            }}
          >
            {post.stat1.value}
          </div>
          <div
            style={{
              fontFamily: theme.fonts.sans,
              fontSize: 28,
              fontWeight: 400,
              color: 'rgba(250,247,242,0.55)',
              letterSpacing: '0.05em',
              marginTop: 12,
            }}
          >
            {post.stat1.sub}
          </div>
        </div>

        {/* Amber divider */}
        <div
          style={{
            width: 260,
            height: 3,
            backgroundColor: theme.colors.amber,
            borderRadius: 2,
            marginTop: 28,
            marginBottom: 28,
          }}
        />

        {/* Stat 2 */}
        <div style={{ textAlign: 'center', marginBottom: 64 }}>
          <div
            style={{
              fontFamily: theme.fonts.serif,
              fontSize: 190,
              fontWeight: 700,
              lineHeight: 1,
              color: post.stat2.color,
              letterSpacing: '-0.02em',
            }}
          >
            {post.stat2.value}
          </div>
          <div
            style={{
              fontFamily: theme.fonts.sans,
              fontSize: 28,
              fontWeight: 400,
              color: 'rgba(250,247,242,0.55)',
              letterSpacing: '0.05em',
              marginTop: 12,
            }}
          >
            {post.stat2.sub}
          </div>
        </div>

        {/* Quote */}
        <div
          style={{
            textAlign: 'center',
            maxWidth: 1300,
            padding: '0 80px',
          }}
        >
          {post.quote.split('\n').map((line, i) => (
            <div
              key={i}
              style={{
                fontFamily: theme.fonts.serif,
                fontSize: 52,
                fontWeight: 400,
                fontStyle: 'italic',
                lineHeight: 1.35,
                color: theme.colors.warmWhite,
                textShadow: '0 2px 12px rgba(0,0,0,0.5)',
              }}
            >
              {line}
            </div>
          ))}
        </div>

        {/* Attribution */}
        <div
          style={{
            marginTop: 32,
            fontFamily: theme.fonts.sans,
            fontSize: 26,
            fontWeight: 500,
            color: theme.colors.amber,
            letterSpacing: '0.06em',
          }}
        >
          — Crosswalk Wisdom
        </div>
      </div>

      {/* Bottom URL */}
      <div
        style={{
          position: 'absolute',
          bottom: 26,
          left: 0,
          right: 0,
          textAlign: 'center',
          fontFamily: theme.fonts.sans,
          fontSize: 18,
          fontWeight: 400,
          color: 'rgba(250,247,242,0.25)',
          letterSpacing: '0.1em',
        }}
      >
        crosswalkwisdom.com
      </div>
    </div>
  );
};
