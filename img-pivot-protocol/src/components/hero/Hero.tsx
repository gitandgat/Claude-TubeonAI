import { Button } from "@/components/ui/Button";
import { Eyebrow } from "@/components/ui/Eyebrow";
import { hero } from "@/data/copy";
import { TRIAGE_CALL_SECTION_ID } from "@/lib/constants";
import { scrollToId } from "@/lib/scrollTo";

export function Hero() {
  return (
    <section
      aria-labelledby="hero-heading"
      className="relative overflow-hidden border-b border-charcoal/10 bg-warm-white"
    >
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -right-24 -top-24 h-96 w-96 rounded-full bg-amber/10 blur-3xl"
      />
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -bottom-32 -left-24 h-80 w-80 rounded-full bg-teal/10 blur-3xl"
      />

      <div className="relative mx-auto max-w-site px-6 py-24 sm:px-8 sm:py-32">
        <div className="max-w-3xl">
          <Eyebrow>{hero.eyebrow}</Eyebrow>

          <h1
            id="hero-heading"
            className="mt-6 text-4xl font-bold leading-[1.1] tracking-tight text-charcoal sm:text-5xl lg:text-6xl"
          >
            {hero.headline}
          </h1>

          <p className="mt-8 max-w-prose text-lg leading-relaxed text-charcoal/80 sm:text-xl">
            {hero.subhead}
          </p>

          <p className="mt-6 border-l-2 border-teal pl-4 text-sm font-medium text-charcoal/70">
            {hero.stat}
          </p>

          <div className="mt-10">
            <Button
              variant="primary"
              onClick={() => scrollToId(TRIAGE_CALL_SECTION_ID)}
            >
              {hero.ctaLabel}
            </Button>
            <p className="mt-3 text-sm text-charcoal/60">{hero.ctaMicrocopy}</p>
          </div>
        </div>
      </div>
    </section>
  );
}
