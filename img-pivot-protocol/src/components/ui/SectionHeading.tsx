import type { ReactNode } from "react";
import { Eyebrow } from "./Eyebrow";

interface SectionHeadingProps {
  headingId: string;
  eyebrow: string;
  headline: string;
  subhead?: string;
  tone?: "light" | "dark";
  children?: ReactNode;
}

export function SectionHeading({
  headingId,
  eyebrow,
  headline,
  subhead,
  tone = "light",
  children,
}: SectionHeadingProps) {
  const headlineTone = tone === "light" ? "text-charcoal" : "text-warm-white";
  const subheadTone = tone === "light" ? "text-charcoal/70" : "text-dim-white";

  return (
    <div className="max-w-prose">
      <Eyebrow tone={tone}>{eyebrow}</Eyebrow>
      <h2
        id={headingId}
        className={`mt-4 text-3xl font-bold leading-tight sm:text-4xl ${headlineTone}`}
      >
        {headline}
      </h2>
      {subhead && (
        <p className={`mt-4 text-lg leading-relaxed ${subheadTone}`}>
          {subhead}
        </p>
      )}
      {children}
    </div>
  );
}
