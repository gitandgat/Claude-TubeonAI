import { PullQuote } from "@/components/ui/PullQuote";
import { Reveal } from "@/components/ui/Reveal";
import { SectionHeading } from "@/components/ui/SectionHeading";
import { moat } from "@/data/copy";
import { TranslationTable } from "./TranslationTable";

export function MoatSection() {
  return (
    <section
      aria-labelledby="moat-heading"
      className="bg-warm-white py-24 sm:py-32"
    >
      <div className="mx-auto max-w-site px-6 sm:px-8">
        <Reveal>
          <SectionHeading
            headingId="moat-heading"
            eyebrow={moat.eyebrow}
            headline={moat.headline}
            subhead={moat.intro}
          />
        </Reveal>

        <Reveal delayMs={80} className="mt-14">
          <TranslationTable rows={moat.rows} />
        </Reveal>

        <Reveal delayMs={120} className="mt-16 max-w-3xl">
          <PullQuote>{moat.pullQuote}</PullQuote>
        </Reveal>
      </div>
    </section>
  );
}
