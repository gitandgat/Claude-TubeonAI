import { Eyebrow } from "@/components/ui/Eyebrow";
import { Reveal } from "@/components/ui/Reveal";
import { guarantee } from "@/data/copy";

export function GuaranteeSection() {
  return (
    <section
      aria-labelledby="guarantee-heading"
      className="bg-charcoal py-24 sm:py-32"
    >
      <div className="mx-auto max-w-site px-6 sm:px-8">
        <Reveal className="relative mx-auto max-w-3xl border border-warm-white/15 bg-charcoal p-10 sm:p-14">
          <span
            aria-hidden="true"
            className="absolute -right-4 -top-6 rotate-6 border-2 border-amber px-4 py-2 text-xs font-bold tracking-[0.15em] text-amber uppercase sm:right-6 sm:top-8"
          >
            {guarantee.badge}
          </span>

          <Eyebrow tone="dark">{guarantee.eyebrow}</Eyebrow>

          <h2
            id="guarantee-heading"
            className="mt-4 font-serif text-3xl font-bold text-warm-white sm:text-4xl"
          >
            {guarantee.headline}
          </h2>

          <p className="mt-6 text-lg leading-relaxed text-dim-white">
            {guarantee.body}
          </p>

          <p className="mt-6 border-t border-warm-white/15 pt-6 text-sm font-medium text-teal">
            {guarantee.closingLine}
          </p>
        </Reveal>
      </div>
    </section>
  );
}
