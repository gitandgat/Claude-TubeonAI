import {
  AbsoluteFill,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

const CHARCOAL = "#2E2B28";
const AMBER = "#D4A843";

function Particles({ frame }: { frame: number }) {
  const particles = Array.from({ length: 18 }, (_, i) => {
    const seed = i * 137.508;
    const x = (seed * 61) % 1920;
    const y = (seed * 83) % 1080;
    const size = 2 + (seed % 6);
    const speed = 0.15 + (seed % 10) * 0.04;
    const drift = Math.sin(frame * 0.008 + seed) * 30;
    const opacity = 0.06 + (Math.sin(frame * 0.015 + seed) + 1) * 0.05;
    const yPos = ((y - frame * speed) % 1080 + 1080) % 1080;
    return { x: x + drift, y: yPos, size, opacity };
  });

  return (
    <>
      {particles.map((p, i) => (
        <div
          key={i}
          style={{
            position: "absolute",
            left: p.x,
            top: p.y,
            width: p.size,
            height: p.size,
            borderRadius: "50%",
            backgroundColor: AMBER,
            opacity: p.opacity,
            filter: `blur(${p.size * 0.8}px)`,
          }}
        />
      ))}
    </>
  );
}

export function CrosswalkHero() {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  // Ken Burns: slow zoom
  const scale = interpolate(frame, [0, durationInFrames], [1.0, 1.06], {
    extrapolateRight: "clamp",
  });

  // Overlay: settles at 0.62 — dark enough for text contrast
  const overlayOpacity = interpolate(frame, [0, 60], [0.4, 0.62], {
    extrapolateRight: "clamp",
  });

  // Vignette pulse
  const vignette = 0.6 + Math.sin(frame * 0.012) * 0.03;

  // Crosswalk stripe sweep
  const stripeW = interpolate(frame, [20, 100], [0, 1920], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Amber bar fade in
  const amberOpacity = interpolate(frame, [40, 80], [0, 0.7], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: CHARCOAL, overflow: "hidden" }}>

      {/* ── Photo (Ken Burns) ── */}
      <AbsoluteFill style={{ transform: `scale(${scale})`, transformOrigin: "center center" }}>
        <Img
          src={staticFile("crosswalk-hero.jpg")}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      </AbsoluteFill>

      {/* ── Charcoal overlay ── */}
      <AbsoluteFill style={{ backgroundColor: CHARCOAL, opacity: overlayOpacity }} />

      {/* ── Vignette ── */}
      <AbsoluteFill
        style={{
          background: `radial-gradient(ellipse at center, transparent 35%, rgba(0,0,0,${vignette}) 100%)`,
        }}
      />

      {/* ── Particles ── */}
      <AbsoluteFill>
        <Particles frame={frame} />
      </AbsoluteFill>

      {/* ── Crosswalk stripes at bottom ── */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          width: stripeW,
          height: 14,
          backgroundImage:
            "repeating-linear-gradient(90deg, #F8F4EE 0px, #F8F4EE 36px, transparent 36px, transparent 52px)",
          opacity: 0.55,
        }}
      />

      {/* ── Amber left accent bar ── */}
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          bottom: 0,
          width: 4,
          backgroundColor: AMBER,
          opacity: amberOpacity,
        }}
      />
    </AbsoluteFill>
  );
}
