/**
 * CareerPivotReel — 9:16 (1080x1920)
 * Retention-first structure: the lip-synced talking-head avatar (full 57s take)
 * reappears every ~15s between graphic beats, and each beat renders through one
 * of five distinct templates so no two consecutive beats look alike:
 *   statement — full-bleed kinetic type on the dark stage, no card
 *   avatar    — framed talking-head window over its own blurred backdrop
 *   card      — the white evidence card (also used for the quote payoff)
 *   number    — giant solid numeral takeover + bottom-third card, sides alternate
 *   cta       — statement variant with pulsing LINK IN BIO pill + bounce arrow
 * A blue spine motif tracks the "5 things I'd do again" list and pays off at
 * the thesis quote (card-10).
 */
import {
  AbsoluteFill,
  OffthreadVideo,
  Audio,
  useCurrentFrame,
  useVideoConfig,
  spring,
  interpolate,
  Easing,
  staticFile,
} from 'remotion';
import { theme } from '../theme';
import { Logo } from '../components/Logo';
import { PhotoBackground } from '../components/PhotoBackground';

const INK = '#0f172a';
const MUTED = '#64748b';
const ACCENT = '#2563eb';
const ACCENT_2 = '#38bdf8';
const CARD = '#f8fafc';
const STAGE_DARK = '#05070d';

const AVATAR_SRC = staticFile('avatar-career-pivot.mp4');
const VO_SRC = staticFile('voiceover-career-pivot.mp3');

const FPS = 30;
const TOTAL_SEC = 57.04;
const AVATAR_CUT_SEC = 2;
const sf = (sec: number) => Math.round(sec * FPS);

export const CAREER_PIVOT_TOTAL_FRAMES = sf(TOTAL_SEC);

type BeatTemplate = 'statement' | 'avatar' | 'card' | 'number' | 'quote' | 'cta';

interface Beat {
  id: string;
  template: BeatTemplate;
  startSec: number;
  endSec: number;
  kicker?: string;
  number?: string;
  anchor?: 'left' | 'right';
  punch?: boolean;
  title: string;
  detail?: string;
  accentWords?: string[];
  background: string;
  rotation: number;
}

const BEATS: Beat[] = [
  {
    id: 'card-01', template: 'statement', startSec: 0, endSec: 6.1,
    kicker: 'A CAREER PIVOT STORY',
    title: "What I'd do if my career suddenly had no room for me",
    accentWords: ['room'],
    background: 'assets/bg-gen-05-crosswalk-dawn.jpg',
    rotation: -0.6,
  },
  {
    id: 'card-02', template: 'avatar', startSec: 6.1, endSec: 13.3,
    kicker: 'THE LEAP',
    title: "I'm a doctor.",
    detail: 'I walked away from medicine three years ago — no plan, no savings.',
    accentWords: ['doctor'],
    background: 'assets/bg-gen-03-white-coat.jpg',
    rotation: 0.8,
  },
  {
    id: 'card-03', template: 'card', startSec: 13.3, endSec: 19.6,
    kicker: "5 THINGS I'D DO AGAIN",
    title: 'Even though no one around me understood them at the time',
    accentWords: ['understood'],
    background: 'assets/bg-gen-02-corridor.jpg',
    rotation: -0.4,
  },
  {
    id: 'card-04', template: 'number', startSec: 19.6, endSec: 23.9,
    number: '1', anchor: 'left',
    title: "I'd stop applying — and sit with the silence for 30 days.",
    accentWords: ['silence'],
    background: 'assets/bg-gen-16-snow-bench.jpg',
    rotation: 0.6,
  },
  {
    id: 'card-05', template: 'number', startSec: 23.9, endSec: 29.6,
    number: '2', anchor: 'right',
    title: "I'd write down every single thing my old career made me afraid to do.",
    accentWords: ['afraid'],
    background: 'assets/bg-gen-08-phone-night.jpg',
    rotation: -0.7,
  },
  {
    id: 'card-06', template: 'number', startSec: 29.6, endSec: 34.3,
    number: '3', anchor: 'left',
    title: "I'd calculate what my time was actually worth per hour.",
    accentWords: ['worth'],
    background: 'assets/bg-gen-04-textbooks.jpg',
    rotation: 0.5,
  },
  {
    id: 'card-07', template: 'avatar', startSec: 34.3, endSec: 37.4,
    punch: true,
    title: 'When I did, the number made me physically sick.',
    accentWords: ['sick'],
    background: 'assets/bg-gen-01-stop-sign.jpg',
    rotation: -0.3,
  },
  {
    id: 'card-08', template: 'number', startSec: 37.4, endSec: 41.7,
    number: '4', anchor: 'right',
    title: 'I’d tell one person the truth: “I don’t want this anymore.”',
    accentWords: ['truth'],
    background: 'assets/bg-gen-10-car-rain.jpg',
    rotation: 0.7,
  },
  {
    id: 'card-09', template: 'number', startSec: 41.7, endSec: 46.1,
    number: '5', anchor: 'left',
    title: "I'd build something of my own before anyone gave me permission.",
    accentWords: ['permission'],
    background: 'assets/bg-gen-12-work-boots.jpg',
    rotation: -0.5,
  },
  {
    id: 'card-10', template: 'quote', startSec: 46.1, endSec: 50.4,
    title: 'Nobody hands you a roadmap. You build one.',
    accentWords: ['build'],
    background: 'assets/bg-gen-15-open-road.jpg',
    rotation: 0.3,
  },
  {
    id: 'card-11', template: 'avatar', startSec: 50.4, endSec: 53.9,
    title: "If you're a doctor feeling this right now…",
    accentWords: ['doctor'],
    background: 'assets/bg-gen-13-id-badge.jpg',
    rotation: -0.6,
  },
  {
    id: 'card-12', template: 'cta', startSec: 53.9, endSec: TOTAL_SEC,
    kicker: 'LINK IN BIO',
    title: 'The number no one ever told you.',
    accentWords: ['number'],
    background: 'assets/bg-gen-11-window-skyline.jpg',
    rotation: 0.5,
  },
];

const NUMBERED_IDS = ['card-04', 'card-05', 'card-06', 'card-08', 'card-09'];
const PAYOFF_ID = 'card-10';

// ─── Kinetic title: word-by-word spring reveal with single-word blue emphasis ──
interface KineticTitleProps {
  text: string;
  localFrame: number;
  fps: number;
  fontSize: number;
  accentWords?: string[];
  color?: string;
  accentColor?: string;
  align?: 'left' | 'center';
}

const KineticTitle = ({
  text,
  localFrame,
  fps,
  fontSize,
  accentWords = [],
  color = INK,
  accentColor = ACCENT,
  align = 'left',
}: KineticTitleProps) => {
  const accentSet = new Set(accentWords.map((w) => w.toLowerCase()));
  const words = text.split(' ');
  return (
    <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: align === 'center' ? 'center' : 'flex-start' }}>
      {words.map((word, i) => {
        const s = spring({
          frame: localFrame - i * 1.6,
          fps,
          config: { damping: 14, stiffness: 210, mass: 0.5 },
        });
        const ty = interpolate(s, [0, 1], [26, 0]);
        const clean = word.replace(/[.,;:!?"“”]/g, '').toLowerCase();
        const isAccent = accentSet.has(clean);
        const sweep = isAccent
          ? interpolate(localFrame - i * 1.6, [8, 20], [0, 100], {
              extrapolateLeft: 'clamp',
              extrapolateRight: 'clamp',
            })
          : 0;
        return (
          <span
            key={i}
            style={{
              position: 'relative',
              display: 'inline-block',
              opacity: s,
              transform: `translateY(${ty}px)`,
              marginRight: '0.28em',
              fontFamily: theme.fonts.sans,
              fontSize,
              fontWeight: 900,
              letterSpacing: '-0.02em',
              lineHeight: 1.14,
              color: isAccent ? accentColor : color,
            }}
          >
            {word}
            {isAccent && (
              <span
                style={{
                  position: 'absolute',
                  left: 0,
                  bottom: '-0.04em',
                  height: '0.09em',
                  width: `${sweep}%`,
                  borderRadius: 999,
                  background: `linear-gradient(90deg, ${accentColor}, ${ACCENT_2})`,
                }}
              />
            )}
          </span>
        );
      })}
    </div>
  );
};

// ─── Evidence card: white card pinned to the dark board, rises + fades in ────
interface EvidenceCardProps {
  beat: Beat;
  localFrame: number;
  fps: number;
}

const EvidenceCard = ({ beat, localFrame, fps }: EvidenceCardProps) => {
  const rise = spring({ frame: localFrame, fps, config: { damping: 16, stiffness: 120, mass: 0.8 } });
  const ty = interpolate(rise, [0, 1], [46, 0]);
  const opacity = interpolate(rise, [0, 1], [0, 1]);
  const barWidth = interpolate(rise, [0, 1], [0, 120]);

  const titleSize = beat.template === 'quote' ? 52 : 46;

  return (
    <div
      style={{
        opacity,
        transform: `translateY(${ty}px) rotate(${beat.rotation}deg)`,
        background: CARD,
        borderRadius: 20,
        padding: '38px 44px',
        boxShadow: '0 30px 70px -20px rgba(0,0,0,0.65), 0 4px 14px rgba(0,0,0,0.35)',
        width: 900,
        display: 'flex',
        flexDirection: 'column',
        gap: 16,
      }}
    >
      {beat.kicker && (
        <span
          style={{
            alignSelf: 'flex-start',
            padding: '8px 16px',
            borderRadius: 6,
            background: ACCENT,
            color: '#fff',
            fontFamily: theme.fonts.sans,
            fontWeight: 800,
            fontSize: 18,
            letterSpacing: '0.14em',
          }}
        >
          {beat.kicker}
        </span>
      )}

      {beat.template === 'quote' && (
        <div style={{ fontFamily: theme.fonts.sans, fontSize: 88, fontWeight: 900, color: ACCENT_2, lineHeight: 0.5, marginBottom: 4 }}>
          {'“'}
        </div>
      )}

      <KineticTitle text={beat.title} localFrame={localFrame} fps={fps} fontSize={titleSize} accentWords={beat.accentWords} />

      {beat.detail && (
        <p style={{ margin: 0, fontFamily: theme.fonts.sans, fontSize: 24, fontWeight: 500, color: MUTED, lineHeight: 1.4 }}>
          {beat.detail}
        </p>
      )}

      <div style={{ height: 5, borderRadius: 3, background: `linear-gradient(90deg, ${ACCENT}, ${ACCENT_2})`, width: barWidth }} />
    </div>
  );
};

// ─── Full-bleed statement: big kinetic type straight on the dark stage ───────
interface FullBleedStatementProps {
  beat: Beat;
  localFrame: number;
  fps: number;
  isCta?: boolean;
}

const FullBleedStatement = ({ beat, localFrame, fps, isCta = false }: FullBleedStatementProps) => {
  const kickerOpacity = interpolate(localFrame, [0, 8], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const kickerPulse = isCta ? 1 + 0.07 * Math.sin(localFrame / 3) : 1;
  const arrowBounce = 14 * Math.sin(localFrame / 4);
  const arrowOpacity = interpolate(localFrame, [14, 26], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '0 90px',
        gap: 40,
        zIndex: 8,
      }}
    >
      {beat.kicker && (
        <span
          style={{
            padding: '12px 26px',
            borderRadius: 8,
            background: ACCENT,
            color: '#fff',
            fontFamily: theme.fonts.sans,
            fontWeight: 800,
            fontSize: 22,
            letterSpacing: '0.12em',
            opacity: kickerOpacity,
            transform: `scale(${kickerPulse})`,
          }}
        >
          {beat.kicker}
        </span>
      )}

      <KineticTitle
        text={beat.title}
        localFrame={localFrame}
        fps={fps}
        fontSize={68}
        accentWords={beat.accentWords}
        color="#fff"
        accentColor={ACCENT_2}
        align="center"
      />

      {isCta && (
        <div
          style={{
            fontFamily: theme.fonts.sans,
            fontSize: 76,
            fontWeight: 900,
            color: ACCENT_2,
            opacity: arrowOpacity,
            transform: `translateY(${arrowBounce}px)`,
            textShadow: '0 0 30px rgba(56,189,248,0.6)',
          }}
        >
          ↓
        </div>
      )}
    </AbsoluteFill>
  );
};

// ─── Giant solid numeral takeover + bottom-third card, anchor side alternates ─
interface NumberTakeoverProps {
  beat: Beat;
  localFrame: number;
  fps: number;
}

const NumberTakeover = ({ beat, localFrame, fps }: NumberTakeoverProps) => {
  const anchorLeft = beat.anchor !== 'right';

  const pop = spring({ frame: localFrame - 2, fps, config: { damping: 13, stiffness: 90, mass: 0.9 } });
  const numScale = interpolate(pop, [0, 1], [1.5, 1]);
  const numOpacity = interpolate(pop, [0, 1], [0, 0.92]);
  const drift = interpolate(localFrame, [0, 150], [0, -24]);

  const rise = spring({ frame: localFrame - 3, fps, config: { damping: 16, stiffness: 120, mass: 0.8 } });
  const cardTx = interpolate(rise, [0, 1], [anchorLeft ? -70 : 70, 0]);
  const cardOpacity = interpolate(rise, [0, 1], [0, 1]);
  const barWidth = interpolate(rise, [0, 1], [0, 120]);

  return (
    <>
      <svg
        width={800}
        height={800}
        viewBox="0 0 800 800"
        style={{
          position: 'absolute',
          top: 150,
          ...(anchorLeft ? { left: -50 } : { right: -50 }),
          opacity: numOpacity,
          transform: `scale(${numScale}) translateY(${drift}px) rotate(${anchorLeft ? -5 : 5}deg)`,
          zIndex: 7,
          overflow: 'visible',
        }}
      >
        <defs>
          <linearGradient id="bigNumGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={ACCENT_2} />
            <stop offset="100%" stopColor={ACCENT} />
          </linearGradient>
        </defs>
        <text
          x="50%"
          y="50%"
          textAnchor="middle"
          dominantBaseline="central"
          fontFamily={theme.fonts.sans}
          fontWeight={900}
          fontSize={680}
          fill="url(#bigNumGrad)"
          style={{ filter: 'drop-shadow(0 0 60px rgba(37,99,235,0.5))' }}
        >
          {beat.number}
        </text>
      </svg>

      <div
        style={{
          position: 'absolute',
          left: 90,
          right: 90,
          top: 1150,
          zIndex: 8,
          opacity: cardOpacity,
          transform: `translateX(${cardTx}px) rotate(${beat.rotation}deg)`,
        }}
      >
        <div
          style={{
            background: CARD,
            borderRadius: 20,
            padding: '34px 40px',
            boxShadow: '0 30px 70px -20px rgba(0,0,0,0.65), 0 4px 14px rgba(0,0,0,0.35)',
            display: 'flex',
            flexDirection: 'column',
            gap: 14,
          }}
        >
          <KineticTitle text={beat.title} localFrame={localFrame} fps={fps} fontSize={44} accentWords={beat.accentWords} />
          <div style={{ height: 5, borderRadius: 3, background: `linear-gradient(90deg, ${ACCENT}, ${ACCENT_2})`, width: barWidth }} />
        </div>
      </div>
    </>
  );
};

// ─── Recurring spine motif: tracks the "5 things" list, pays off at card-10 ──
interface SpineProps {
  sec: number;
  frame: number;
}

const Spine = ({ sec, frame }: SpineProps) => {
  const first = BEATS.find((b) => b.id === NUMBERED_IDS[0])!;
  const last = BEATS.find((b) => b.id === NUMBERED_IDS[NUMBERED_IDS.length - 1])!;
  const payoff = BEATS.find((b) => b.id === PAYOFF_ID)!;
  const isPayoff = sec >= payoff.startSec && sec < payoff.endSec;

  if (sec < first.startSec - 0.5 || sec >= payoff.endSec) return null;

  const railOpacity = interpolate(sec, [first.startSec - 0.5, first.startSec], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const fillPct = isPayoff
    ? 100
    : interpolate(sec, [first.startSec, last.endSec], [0, 100], {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      });
  const glow = isPayoff
    ? interpolate(frame - sf(payoff.startSec), [0, 20], [0, 1], { extrapolateRight: 'clamp' })
    : 0;

  return (
    <div style={{ position: 'absolute', left: 44, top: 260, bottom: 260, width: 4, opacity: railOpacity, zIndex: 6 }}>
      <div style={{ position: 'absolute', inset: 0, background: 'rgba(255,255,255,0.12)', borderRadius: 2 }} />
      <div
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          width: '100%',
          height: `${fillPct}%`,
          background: `linear-gradient(180deg, ${ACCENT_2}, ${ACCENT})`,
          borderRadius: 2,
          boxShadow: glow > 0 ? `0 0 ${20 * glow}px ${6 * glow}px rgba(56,189,248,${0.7 * glow})` : 'none',
        }}
      />
      {NUMBERED_IDS.map((id, i) => {
        const beat = BEATS.find((b) => b.id === id)!;
        const reached = sec >= beat.startSec;
        const posPct = (i / (NUMBERED_IDS.length - 1)) * 100;
        return (
          <div
            key={id}
            style={{
              position: 'absolute',
              left: -5,
              top: `${posPct}%`,
              width: 14,
              height: 14,
              borderRadius: '50%',
              background: reached ? ACCENT_2 : 'rgba(255,255,255,0.25)',
              transform: 'translateY(-50%)',
              boxShadow: reached ? '0 0 10px 2px rgba(56,189,248,0.6)' : 'none',
            }}
          />
        );
      })}
    </div>
  );
};

// ─── Avatar scene: sharp framed talking-head window over its own blurred take.
// The full-length avatar video is mounted at composition root time, so the
// window is lip-synced no matter which beat it appears in. ──────────────────
interface AvatarSceneProps {
  localFrame: number;
  fps: number;
  zoomSpanFrames: number;
  title: string;
  titleSize: number;
  accentWords?: string[];
  kicker?: string;
  detail?: string;
}

const AvatarScene = ({
  localFrame,
  fps,
  zoomSpanFrames,
  title,
  titleSize,
  accentWords,
  kicker,
  detail,
}: AvatarSceneProps) => {
  const enter = spring({ frame: localFrame, fps, config: { damping: 15, stiffness: 140 } });
  const scale = interpolate(enter, [0, 1], [1.18, 1]);
  const idleZoom = interpolate(localFrame, [0, zoomSpanFrames || 1], [1, 1.04]);
  const opacity = interpolate(enter, [0, 1], [0, 1]);
  const pillOpacity = interpolate(localFrame, [2, 12], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const detailOpacity = interpolate(localFrame, [12, 26], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });

  const FRAME_SIZE = 460;

  return (
    <AbsoluteFill>
      <div style={{ position: 'absolute', inset: 0, overflow: 'hidden' }}>
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            width: '135%',
            height: '135%',
            transform: 'translate(-50%, -50%) scale(1.06)',
            filter: 'blur(52px) brightness(0.4) saturate(1.1)',
          }}
        >
          <OffthreadVideo src={AVATAR_SRC} muted style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        </div>
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background:
              'radial-gradient(ellipse at 50% 40%, rgba(37,99,235,0.28) 0%, rgba(5,7,13,0.55) 55%, rgba(5,7,13,0.92) 100%)',
          }}
        />
      </div>

      <div
        style={{
          position: 'absolute',
          left: '50%',
          top: 420,
          width: FRAME_SIZE,
          height: FRAME_SIZE,
          transform: `translateX(-50%) scale(${scale * idleZoom})`,
          opacity,
          borderRadius: 28,
          overflow: 'hidden',
          border: `4px solid ${ACCENT_2}`,
          boxShadow: '0 30px 80px -16px rgba(0,0,0,0.75), 0 0 60px -10px rgba(37,99,235,0.5)',
        }}
      >
        <OffthreadVideo src={AVATAR_SRC} muted style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
      </div>

      {kicker && (
        <div
          style={{
            position: 'absolute',
            left: 0,
            right: 0,
            top: 316,
            display: 'flex',
            justifyContent: 'center',
            opacity: pillOpacity,
          }}
        >
          <span
            style={{
              padding: '12px 26px',
              borderRadius: 8,
              background: ACCENT,
              color: '#fff',
              fontFamily: theme.fonts.sans,
              fontWeight: 800,
              fontSize: 22,
              letterSpacing: '0.12em',
            }}
          >
            {kicker}
          </span>
        </div>
      )}

      <div style={{ position: 'absolute', left: 90, right: 90, top: 960 }}>
        <KineticTitle
          text={title}
          localFrame={localFrame}
          fps={fps}
          fontSize={titleSize}
          accentWords={accentWords}
          color="#fff"
          accentColor={ACCENT_2}
          align="center"
        />
        {detail && (
          <p
            style={{
              margin: '22px 0 0',
              fontFamily: theme.fonts.sans,
              fontSize: 30,
              fontWeight: 500,
              color: 'rgba(255,255,255,0.75)',
              lineHeight: 1.45,
              textAlign: 'center',
              opacity: detailOpacity,
            }}
          >
            {detail}
          </p>
        )}
      </div>
    </AbsoluteFill>
  );
};

// ─── Main composition ────────────────────────────────────────────────────────
export const CareerPivotReel = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const sec = frame / fps;

  const showHook = sec < AVATAR_CUT_SEC;
  const currentBeat = BEATS.find((b) => sec >= b.startSec && sec < b.endSec) ?? BEATS[BEATS.length - 1];
  const beatStartFrame = sf(currentBeat.startSec);
  const localFrame = frame - beatStartFrame;
  const beatDurationFrames = sf(currentBeat.endSec) - sf(currentBeat.startSec);
  const template = currentBeat.template;

  const bgPunch = interpolate(localFrame, [0, 12], [1.12, 1.0], {
    extrapolateRight: 'clamp',
    easing: Easing.out(Easing.cubic),
  });
  const bgDrift = interpolate(localFrame, [0, beatDurationFrames || 1], [1.0, 1.07]);
  const bgScale = bgPunch * bgDrift;

  const isPunch = !!currentBeat.punch;
  const flash = interpolate(localFrame, [0, isPunch ? 6 : 4], [isPunch ? 0.85 : 0.5, 0], {
    extrapolateRight: 'clamp',
  });
  const shakeAmp = isPunch
    ? interpolate(localFrame, [0, 16], [15, 0], { extrapolateRight: 'clamp', easing: Easing.out(Easing.quad) })
    : 0;
  const shakeX = Math.sin(localFrame * 2.7) * shakeAmp;
  const shakeY = Math.cos(localFrame * 3.4) * shakeAmp * 0.7;

  const avatarTitleSize = currentBeat.title.length < 20 ? 72 : 54;

  return (
    <AbsoluteFill style={{ backgroundColor: STAGE_DARK }}>
      <Audio src={VO_SRC} />

      <AbsoluteFill style={{ transform: `translate(${shakeX}px, ${shakeY}px)` }}>
        {showHook ? (
          <AvatarScene
            localFrame={frame}
            fps={fps}
            zoomSpanFrames={sf(AVATAR_CUT_SEC)}
            kicker={BEATS[0].kicker}
            title={BEATS[0].title}
            titleSize={62}
            accentWords={BEATS[0].accentWords}
          />
        ) : template === 'avatar' ? (
          <AvatarScene
            localFrame={localFrame}
            fps={fps}
            zoomSpanFrames={beatDurationFrames}
            kicker={currentBeat.kicker}
            title={currentBeat.title}
            titleSize={avatarTitleSize}
            accentWords={currentBeat.accentWords}
            detail={currentBeat.detail}
          />
        ) : (
          <>
            <div style={{ position: 'absolute', inset: 0, transform: `scale(${bgScale})`, transformOrigin: 'center' }}>
              <PhotoBackground
                src={staticFile(currentBeat.background)}
                overlayOpacity={0.72}
                overlayColor={STAGE_DARK}
                parallax={false}
              />
            </div>
            <div
              style={{
                position: 'absolute',
                inset: 0,
                background:
                  'radial-gradient(ellipse at 50% 30%, rgba(37,99,235,0.22) 0%, transparent 60%), radial-gradient(ellipse at 50% 100%, rgba(5,7,13,0.75) 0%, transparent 55%)',
              }}
            />

            {template === 'number' && <NumberTakeover beat={currentBeat} localFrame={localFrame} fps={fps} />}

            {(template === 'statement' || template === 'cta') && (
              <FullBleedStatement beat={currentBeat} localFrame={localFrame} fps={fps} isCta={template === 'cta'} />
            )}

            {(template === 'card' || template === 'quote') && (
              <div
                style={{
                  position: 'absolute',
                  inset: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  zIndex: 8,
                }}
              >
                <EvidenceCard beat={currentBeat} localFrame={localFrame} fps={fps} />
              </div>
            )}
          </>
        )}

        <Spine sec={sec} frame={frame} />

        {!showHook && flash > 0.01 && (
          <div
            style={{
              position: 'absolute',
              inset: 0,
              backgroundColor: isPunch ? '#ffffff' : ACCENT_2,
              opacity: flash,
              zIndex: 20,
              pointerEvents: 'none',
            }}
          />
        )}
      </AbsoluteFill>

      <div style={{ position: 'absolute', top: 80, left: 60, zIndex: 10 }}>
        <Logo size={24} color={ACCENT_2} />
      </div>
      <div
        style={{
          position: 'absolute',
          top: 88,
          right: 60,
          zIndex: 10,
          fontFamily: theme.fonts.sans,
          fontSize: 22,
          color: 'rgba(255,255,255,0.45)',
          letterSpacing: '0.08em',
          textTransform: 'uppercase',
        }}
      >
        @crosswalkwisdom
      </div>

      <div
        style={{
          position: 'absolute',
          bottom: 140,
          left: 60,
          right: 60,
          height: 3,
          backgroundColor: 'rgba(255,255,255,0.15)',
          borderRadius: 2,
          zIndex: 10,
        }}
      >
        <div
          style={{
            height: '100%',
            width: `${(sec / TOTAL_SEC) * 100}%`,
            background: `linear-gradient(90deg, ${ACCENT}, ${ACCENT_2})`,
            borderRadius: 2,
          }}
        />
      </div>
    </AbsoluteFill>
  );
};
