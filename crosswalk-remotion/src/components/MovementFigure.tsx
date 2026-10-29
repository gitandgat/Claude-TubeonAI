import React from 'react';
import { useCurrentFrame } from 'remotion';

/**
 * MovementFigure — a rigged 2D clinical mannequin that actually *performs* each
 * self-test movement. Not a static picture: a joint-coordinate skeleton posed by
 * hand-authored keyframes, interpolated per-joint over the shot, with the "tell"
 * (the compensation) lighting up in terracotta as the fault appears.
 *
 * Coordinate space is a 400×440 stage (x centred on 200, head ≈ y40, floor ≈ y392).
 * Two skeleton templates — a front view (both limbs, frontal-plane faults like knee
 * valgus / pelvic drop / arch collapse) and a side profile (sagittal faults like
 * forward head, anterior pelvic tilt, wall reach, chair rise). Bones are drawn as
 * outlined ivory capsules for a sculpted, medical-atlas read on the beige surface.
 */

// ── Brand ────────────────────────────────────────────────────────────────────
const IVORY = '#e7ded0';
const SAGE_OUTLINE = '#57694f';
const SAGE_JOINT = '#6f8768';
const TERRA = '#c2503d';
const FLOOR = '#e3dccd';

type Pt = [number, number];
type JointMap = Record<string, Pt>;

// ── Skeleton templates (neutral stand) ───────────────────────────────────────
const FRONT_STAND: JointMap = {
  head: [200, 58],
  neck: [200, 92],
  chest: [200, 120],
  pelvis: [200, 214],
  shoulderL: [166, 124],
  shoulderR: [234, 124],
  elbowL: [150, 178],
  elbowR: [250, 178],
  handL: [146, 234],
  handR: [254, 234],
  hipL: [176, 220],
  hipR: [224, 220],
  kneeL: [172, 300],
  kneeR: [228, 300],
  ankleL: [170, 372],
  ankleR: [230, 372],
  footL: [156, 386],
  footR: [244, 386],
};

const SIDE_STAND: JointMap = {
  head: [212, 58],
  neck: [204, 92],
  chest: [198, 120],
  pelvis: [198, 214],
  shoulder: [202, 124],
  elbow: [206, 180],
  hand: [210, 236],
  hip: [198, 220],
  knee: [204, 300],
  ankle: [200, 372],
  toe: [236, 384],
  heel: [184, 384],
};

interface Bone {
  a: string;
  b: string;
  w: number;
}

const FRONT_BONES: Bone[] = [
  { a: 'neck', b: 'chest', w: 20 },
  { a: 'chest', b: 'pelvis', w: 40 },
  { a: 'shoulderL', b: 'shoulderR', w: 16 },
  { a: 'chest', b: 'shoulderL', w: 16 },
  { a: 'chest', b: 'shoulderR', w: 16 },
  { a: 'shoulderL', b: 'elbowL', w: 17 },
  { a: 'elbowL', b: 'handL', w: 14 },
  { a: 'shoulderR', b: 'elbowR', w: 17 },
  { a: 'elbowR', b: 'handR', w: 14 },
  { a: 'hipL', b: 'hipR', w: 18 },
  { a: 'hipL', b: 'kneeL', w: 26 },
  { a: 'kneeL', b: 'ankleL', w: 20 },
  { a: 'ankleL', b: 'footL', w: 13 },
  { a: 'hipR', b: 'kneeR', w: 26 },
  { a: 'kneeR', b: 'ankleR', w: 20 },
  { a: 'ankleR', b: 'footR', w: 13 },
];

const SIDE_BONES: Bone[] = [
  { a: 'neck', b: 'chest', w: 20 },
  { a: 'chest', b: 'pelvis', w: 40 },
  { a: 'chest', b: 'shoulder', w: 16 },
  { a: 'shoulder', b: 'elbow', w: 17 },
  { a: 'elbow', b: 'hand', w: 14 },
  { a: 'pelvis', b: 'hip', w: 22 },
  { a: 'hip', b: 'knee', w: 26 },
  { a: 'knee', b: 'ankle', w: 20 },
  { a: 'ankle', b: 'toe', w: 13 },
  { a: 'ankle', b: 'heel', w: 13 },
];

// ── Motion definitions ───────────────────────────────────────────────────────
interface Keyframe {
  at: number; // 0..1 progress
  joints: Partial<Record<string, Pt>>;
}

interface Motion {
  view: 'front' | 'side';
  zoom?: number; // scale about stage centre-bottom (for close-ups)
  panY?: number;
  frames: Keyframe[];
  tellStart: number; // progress at which the highlight ramps in
  highlightBones: [string, string][]; // bones (by joint pair) that light up
  highlightJoints?: string[];
  overlay?: string; // named prop rig: 'wall' | 'chair' | 'wallLow'
  tellLabel: string;
}

// Base standing keyframe merged implicitly at progress 0 (per-joint carry-forward).
const MOTIONS: Record<string, Motion> = {
  // Frontal-plane: stand on one leg → the lifted-side hip drops, torso lists.
  'single-leg': {
    view: 'front',
    tellStart: 0.55,
    highlightBones: [['hipL', 'hipR']],
    highlightJoints: ['hipR'],
    tellLabel: 'hip drops',
    frames: [
      {
        at: 0.4,
        joints: { kneeR: [220, 282], ankleR: [238, 324], footR: [254, 334] },
      },
      {
        at: 0.82,
        joints: {
          // pelvis drops hard on the lifted (right) side; trunk lurches left
          hipL: [180, 202],
          hipR: [224, 242],
          chest: [186, 122],
          neck: [184, 94],
          head: [176, 60],
          shoulderL: [150, 122],
          shoulderR: [224, 128],
          kneeL: [166, 300],
          ankleL: [158, 372],
          footL: [144, 386],
          kneeR: [216, 296],
          ankleR: [240, 334],
          footR: [256, 344],
        },
      },
    ],
  },

  // Overhead squat: arms up → squat → knees cave inside the toes.
  'knee-cave': {
    view: 'front',
    tellStart: 0.66,
    highlightBones: [
      ['hipL', 'kneeL'],
      ['kneeL', 'ankleL'],
      ['hipR', 'kneeR'],
      ['kneeR', 'ankleR'],
    ],
    highlightJoints: ['kneeL', 'kneeR'],
    tellLabel: 'knees cave in',
    frames: [
      {
        at: 0.26,
        joints: {
          elbowL: [156, 84],
          elbowR: [244, 84],
          handL: [166, 40],
          handR: [234, 40],
        },
      },
      {
        at: 0.62,
        joints: {
          pelvis: [200, 262],
          chest: [200, 168],
          neck: [200, 140],
          head: [200, 106],
          hipL: [176, 268],
          hipR: [224, 268],
          kneeL: [158, 322],
          kneeR: [242, 322],
          shoulderL: [166, 172],
          shoulderR: [234, 172],
          elbowL: [156, 120],
          elbowR: [244, 120],
          handL: [168, 74],
          handR: [232, 74],
        },
      },
      {
        at: 1,
        joints: {
          kneeL: [192, 324],
          kneeR: [208, 324],
        },
      },
    ],
  },

  // Feet under hips → arches sink, ankles roll inward. Modest zoom on the base.
  arch: {
    view: 'front',
    zoom: 1.28,
    panY: -34,
    tellStart: 0.45,
    highlightBones: [
      ['ankleL', 'footL'],
      ['ankleR', 'footR'],
    ],
    highlightJoints: ['ankleL', 'ankleR'],
    tellLabel: 'arches collapse',
    frames: [
      { at: 0, joints: { kneeL: [184, 300], kneeR: [216, 300], ankleL: [184, 372], ankleR: [216, 372], footL: [168, 388], footR: [232, 388] } },
      {
        at: 1,
        joints: {
          kneeL: [188, 300],
          kneeR: [212, 300],
          ankleL: [194, 378],
          ankleR: [206, 378],
          footL: [176, 390],
          footR: [224, 390],
        },
      },
    ],
  },

  // Back to wall → head drifts forward, chin cranes up to reach.
  'forward-head': {
    view: 'side',
    overlay: 'wall',
    tellStart: 0.5,
    highlightBones: [['neck', 'chest']],
    highlightJoints: ['head', 'neck'],
    tellLabel: 'head sits forward',
    frames: [
      { at: 0, joints: { head: [206, 58], neck: [200, 92] } },
      { at: 0.5, joints: { head: [224, 60], neck: [210, 92] } },
      { at: 1, joints: { head: [230, 52], neck: [212, 92] } },
    ],
  },

  // Sit → rise. The tell: needs a forward rock + a hand pushing off the thigh.
  'chair-rise': {
    view: 'side',
    overlay: 'chair',
    tellStart: 0.5,
    highlightBones: [
      ['shoulder', 'elbow'],
      ['elbow', 'hand'],
    ],
    highlightJoints: ['hand'],
    tellLabel: 'needs a push',
    frames: [
      {
        at: 0,
        joints: {
          pelvis: [190, 300],
          hip: [190, 300],
          knee: [246, 300],
          ankle: [246, 372],
          toe: [280, 384],
          heel: [230, 384],
          chest: [188, 206],
          neck: [192, 178],
          head: [204, 150],
          shoulder: [192, 210],
          elbow: [204, 262],
          hand: [214, 312],
        },
      },
      {
        at: 0.55,
        joints: {
          pelvis: [196, 262],
          hip: [196, 262],
          knee: [238, 306],
          chest: [214, 196],
          neck: [214, 168],
          head: [226, 142],
          shoulder: [216, 200],
          elbow: [232, 250],
          hand: [244, 300],
        },
      },
      {
        at: 1,
        joints: {
          pelvis: [200, 236],
          hip: [200, 236],
          knee: [214, 306],
          ankle: [202, 372],
          toe: [238, 384],
          heel: [186, 384],
          chest: [214, 150],
          neck: [212, 120],
          head: [222, 92],
          shoulder: [214, 152],
          elbow: [230, 206],
          hand: [242, 262],
        },
      },
    ],
  },

  // Stand side-on → pelvis tips anteriorly, low back arches (belt-line tell).
  hamstrings: {
    view: 'side',
    tellStart: 0.45,
    highlightBones: [['chest', 'pelvis']],
    highlightJoints: ['pelvis'],
    tellLabel: 'pelvis tips forward',
    frames: [
      { at: 0 },
      {
        at: 1,
        joints: {
          chest: [190, 120],
          pelvis: [206, 214],
          hip: [206, 220],
          neck: [198, 92],
          head: [208, 58],
          knee: [206, 300],
        },
      },
    ] as Keyframe[],
  },

  // Back to wall, arms up → low back peels off the wall to finish the reach.
  'wall-reach': {
    view: 'side',
    overlay: 'wallLow',
    tellStart: 0.55,
    highlightBones: [['chest', 'pelvis']],
    highlightJoints: ['pelvis'],
    tellLabel: 'back peels off',
    frames: [
      { at: 0, joints: { head: [204, 58], neck: [198, 92], chest: [196, 120], hand: [206, 236], elbow: [204, 180] } },
      {
        at: 0.5,
        joints: {
          shoulder: [206, 120],
          elbow: [216, 74],
          hand: [222, 34],
        },
      },
      {
        at: 1,
        joints: {
          pelvis: [210, 214],
          hip: [210, 220],
          chest: [188, 122],
          neck: [196, 92],
          head: [206, 58],
          shoulder: [206, 120],
          elbow: [218, 66],
          hand: [224, 26],
        },
      },
    ],
  },
};

// ── Per-joint keyframe interpolation (carry-forward hold) ─────────────────────
const smooth = (t: number): number => t * t * (3 - 2 * t);
const lerp = (a: number, b: number, e: number): number => a + (b - a) * e;

function poseAt(motion: Motion, p: number): JointMap {
  const base = motion.view === 'front' ? FRONT_STAND : SIDE_STAND;
  const out: JointMap = {};
  for (const j of Object.keys(base)) {
    // Timeline for this joint: its base at 0, then every keyframe that names it.
    const stops: { at: number; pt: Pt }[] = [{ at: 0, pt: base[j] }];
    for (const kf of motion.frames) {
      const pt = kf.joints?.[j];
      if (pt) stops.push({ at: kf.at, pt });
    }
    if (stops.length === 1) {
      out[j] = base[j];
      continue;
    }
    // clamp + find bracket
    if (p <= stops[0].at) {
      out[j] = stops[0].pt;
    } else if (p >= stops[stops.length - 1].at) {
      out[j] = stops[stops.length - 1].pt;
    } else {
      let i = 0;
      while (i < stops.length - 1 && p > stops[i + 1].at) i++;
      const a = stops[i];
      const b = stops[i + 1];
      const e = smooth((p - a.at) / (b.at - a.at));
      out[j] = [lerp(a.pt[0], b.pt[0], e), lerp(a.pt[1], b.pt[1], e)];
    }
  }
  return out;
}

// ── Rendering ────────────────────────────────────────────────────────────────
const boneKey = (a: string, b: string) => `${a}|${b}`;

const Capsule: React.FC<{ a: Pt; b: Pt; w: number; color: string; opacity?: number }> = ({ a, b, w, color, opacity = 1 }) => (
  <line
    x1={a[0]}
    y1={a[1]}
    x2={b[0]}
    y2={b[1]}
    stroke={color}
    strokeWidth={w}
    strokeLinecap="round"
    opacity={opacity}
  />
);

interface FigureProps {
  slug: string;
  /** Length (frames) the movement plays over — used when progress is time-driven. */
  shotFrames?: number;
  /** Pin the figure at a fixed progress (0..1), e.g. the tell pose for hub thumbnails. */
  fixedProgress?: number;
  /** Show the top-centre tell label (hidden in the hub where each item has its own text). */
  showLabel?: boolean;
}

/**
 * Renders the posed, animated figure for a shot. Reads shot-relative frame via
 * useCurrentFrame (inside the SHOT Sequence) so progress runs 0→1 across the shot,
 * unless `fixedProgress` pins it to a single pose.
 */
export const MovementFigure: React.FC<FigureProps> = ({ slug, shotFrames = 252, fixedProgress, showLabel = true }) => {
  const frame = useCurrentFrame();
  const motion = MOTIONS[slug];
  if (!motion) return null;

  const p = fixedProgress ?? Math.min(1, Math.max(0, frame / shotFrames));
  const J = poseAt(motion, p);
  const bones = motion.view === 'front' ? FRONT_BONES : SIDE_BONES;

  // Highlight ramps in at tellStart, then gently pulses for emphasis.
  const ramp = Math.min(1, Math.max(0, (p - motion.tellStart) / 0.12));
  const pulse = ramp > 0 ? 0.72 + 0.28 * (0.5 + 0.5 * Math.sin(frame * 0.35)) : 0;
  const hi = ramp * pulse;

  const hiSet = new Set(motion.highlightBones.map(([a, b]) => boneKey(a, b)));
  const hiJoints = new Set(motion.highlightJoints ?? []);

  const cx = 200;
  const cy = 392;
  const zoom = motion.zoom ?? 1;
  const panY = motion.panY ?? 0;
  const headR = 26;

  return (
    <svg
      viewBox="0 0 400 440"
      style={{ position: 'absolute', inset: 0, width: '100%', height: '100%' }}
      preserveAspectRatio="xMidYMid meet"
    >
      <defs>
        <filter id="tellGlow" x="-40%" y="-40%" width="180%" height="180%">
          <feDropShadow dx="0" dy="0" stdDeviation="6" floodColor={TERRA} floodOpacity="0.7" />
        </filter>
      </defs>

      <g transform={`translate(${cx} ${cy}) scale(${zoom}) translate(${-cx} ${-cy + panY})`}>
        {/* grounding shadow */}
        <ellipse cx={200} cy={398} rx={96} ry={12} fill={FLOOR} opacity={0.7} />

        {/* prop rig behind the body */}
        <PropRig overlay={motion.overlay} J={J} hi={hi} />

        {/* pass 1 — sage outline (draw all bones slightly wider) */}
        {bones.map((bn) => (
          <Capsule key={`o-${bn.a}-${bn.b}`} a={J[bn.a]} b={J[bn.b]} w={bn.w + 7} color={SAGE_OUTLINE} />
        ))}
        <circle cx={J.head[0]} cy={J.head[1]} r={headR + 3.5} fill={SAGE_OUTLINE} />

        {/* pass 2 — ivory fill; highlighted bones go terracotta */}
        {bones.map((bn) => {
          const on = hiSet.has(boneKey(bn.a, bn.b)) || hiSet.has(boneKey(bn.b, bn.a));
          return (
            <g key={`f-${bn.a}-${bn.b}`} filter={on && hi > 0.05 ? 'url(#tellGlow)' : undefined}>
              <Capsule a={J[bn.a]} b={J[bn.b]} w={bn.w} color={IVORY} />
              {on && <Capsule a={J[bn.a]} b={J[bn.b]} w={bn.w} color={TERRA} opacity={hi} />}
            </g>
          );
        })}
        <circle cx={J.head[0]} cy={J.head[1]} r={headR} fill={IVORY} />

        {/* joint pips */}
        {bones.map((bn) => (
          <circle key={`j-${bn.a}-${bn.b}`} cx={J[bn.b][0]} cy={J[bn.b][1]} r={3.4} fill={SAGE_JOINT} opacity={0.65} />
        ))}
        {[...hiJoints].map((j) =>
          J[j] ? (
            <circle key={`hj-${j}`} cx={J[j][0]} cy={J[j][1]} r={9} fill="none" stroke={TERRA} strokeWidth={3} opacity={hi} />
          ) : null,
        )}

        {/* fault markers / arrows in front (track joints, so inside the zoom) */}
        <FaultMarks slug={slug} J={J} hi={hi} />
      </g>

      {/* tell label — fixed top-centre, outside the zoom so it never drifts */}
      {showLabel && hi > 0.05 && (
        <text
          x={200}
          y={26}
          textAnchor="middle"
          fill={TERRA}
          fontFamily='"IBM Plex Sans", system-ui, sans-serif'
          fontSize={18}
          fontWeight={700}
          letterSpacing={2}
          opacity={hi}
          style={{ textTransform: 'uppercase' }}
        >
          {motion.tellLabel}
        </text>
      )}
    </svg>
  );
};

// Wall / chair props drawn behind the figure.
const PropRig: React.FC<{ overlay?: string; J: JointMap; hi: number }> = ({ overlay, J }) => {
  if (overlay === 'wall' || overlay === 'wallLow') {
    const x = 168;
    return (
      <g>
        <line x1={x} y1={54} x2={x} y2={398} stroke={SAGE_OUTLINE} strokeWidth={5} opacity={0.55} strokeLinecap="round" />
        <line x1={x} y1={398} x2={250} y2={398} stroke={SAGE_OUTLINE} strokeWidth={5} opacity={0.35} strokeLinecap="round" />
      </g>
    );
  }
  if (overlay === 'chair') {
    // seat under the pelvis at its lowest (seated) position
    return (
      <g opacity={0.6}>
        <rect x={176} y={306} width={92} height={12} rx={4} fill={SAGE_OUTLINE} />
        <line x1={182} y1={318} x2={182} y2={398} stroke={SAGE_OUTLINE} strokeWidth={7} strokeLinecap="round" />
        <line x1={262} y1={318} x2={262} y2={398} stroke={SAGE_OUTLINE} strokeWidth={7} strokeLinecap="round" />
        <line x1={262} y1={306} x2={262} y2={214} stroke={SAGE_OUTLINE} strokeWidth={7} strokeLinecap="round" />
      </g>
    );
  }
  return null;
};

// Terracotta directional cues that track the joints (drawn inside the zoom group).
const FaultMarks: React.FC<{ slug: string; J: JointMap; hi: number }> = ({ slug, J, hi }) => {
  if (hi <= 0.05) return null;
  const arrows: React.ReactNode[] = [];
  const A = (x1: number, y1: number, x2: number, y2: number, key: string) => (
    <g key={key} opacity={hi}>
      <line x1={x1} y1={y1} x2={x2} y2={y2} stroke={TERRA} strokeWidth={4} strokeLinecap="round" />
      <path d={`M ${x2} ${y2} l -7 -3 M ${x2} ${y2} l -3 -7`} stroke={TERRA} strokeWidth={4} strokeLinecap="round" fill="none" transform={`rotate(${Math.atan2(y2 - y1, x2 - x1) * (180 / Math.PI) - 45} ${x2} ${y2})`} />
    </g>
  );

  if (slug === 'single-leg') arrows.push(A(J.hipR[0] + 30, J.hipR[1] - 14, J.hipR[0] + 30, J.hipR[1] + 22, 'a1'));
  if (slug === 'knee-cave') {
    arrows.push(A(J.kneeL[0] - 26, J.kneeL[1], J.kneeL[0] - 6, J.kneeL[1], 'a1'));
    arrows.push(A(J.kneeR[0] + 26, J.kneeR[1], J.kneeR[0] + 6, J.kneeR[1], 'a2'));
  }
  if (slug === 'arch') {
    arrows.push(A(J.ankleL[0] - 24, J.ankleL[1] - 8, J.ankleL[0] - 6, J.ankleL[1] + 6, 'a1'));
    arrows.push(A(J.ankleR[0] + 24, J.ankleR[1] - 8, J.ankleR[0] + 6, J.ankleR[1] + 6, 'a2'));
  }
  if (slug === 'forward-head') arrows.push(<GapBracket key="g" x1={170} x2={J.head[0] - 26} y={J.head[1]} hi={hi} />);
  if (slug === 'wall-reach') arrows.push(<GapBracket key="g" x1={170} x2={J.pelvis[0] - 22} y={J.pelvis[1]} hi={hi} />);
  if (slug === 'hamstrings') {
    // belt-line: a short bar across the pelvis, tipped down in front
    arrows.push(
      <line key="belt" x1={J.pelvis[0] - 26} y1={J.pelvis[1] - 4} x2={J.pelvis[0] + 26} y2={J.pelvis[1] + 12} stroke={TERRA} strokeWidth={5} strokeLinecap="round" opacity={hi} />,
    );
  }
  if (slug === 'chair-rise') arrows.push(A(J.hand[0] + 4, J.hand[1] - 22, J.hand[0] + 4, J.hand[1] - 4, 'a1'));

  return <g>{arrows}</g>;
};

const GapBracket: React.FC<{ x1: number; x2: number; y: number; hi: number }> = ({ x1, x2, y, hi }) => (
  <g opacity={hi}>
    <line x1={x1} y1={y - 14} x2={x1} y2={y + 14} stroke={TERRA} strokeWidth={3} strokeLinecap="round" />
    <line x1={x2} y1={y - 14} x2={x2} y2={y + 14} stroke={TERRA} strokeWidth={3} strokeLinecap="round" />
    <line x1={x1} y1={y} x2={x2} y2={y} stroke={TERRA} strokeWidth={3} strokeDasharray="4 5" />
  </g>
);
