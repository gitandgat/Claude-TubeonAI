interface EyebrowProps {
  children: string;
  tone?: "light" | "dark";
}

export function Eyebrow({ children, tone = "light" }: EyebrowProps) {
  const toneClass = tone === "light" ? "text-charcoal" : "text-dim-white";

  return (
    <p
      className={`flex items-center gap-3 text-xs font-semibold tracking-[0.2em] uppercase ${toneClass}`}
    >
      <span className="h-px w-8 bg-current opacity-50" aria-hidden="true" />
      {children}
    </p>
  );
}
