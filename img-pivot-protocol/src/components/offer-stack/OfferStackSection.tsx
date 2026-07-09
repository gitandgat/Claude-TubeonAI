import { Button } from "@/components/ui/Button";
import { Reveal } from "@/components/ui/Reveal";
import { SectionHeading } from "@/components/ui/SectionHeading";
import { offerStack } from "@/data/copy";
import { TRIAGE_CALL_SECTION_ID } from "@/lib/constants";
import { scrollToId } from "@/lib/scrollTo";
import { OfferCard } from "./OfferCard";

export function OfferStackSection() {
  return (
    <section
      aria-labelledby="offer-stack-heading"
      className="border-t border-charcoal/10 bg-warm-white py-24 sm:py-32"
    >
      <div className="mx-auto max-w-site px-6 sm:px-8">
        <Reveal>
          <SectionHeading
            headingId="offer-stack-heading"
            eyebrow={offerStack.eyebrow}
            headline={offerStack.headline}
            subhead={offerStack.subhead}
          />
        </Reveal>

        <div className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {offerStack.items.map((item, i) => (
            <Reveal key={item.index} delayMs={i * 80}>
              <OfferCard
                index={item.index}
                title={item.title}
                body={item.body}
              />
            </Reveal>
          ))}
        </div>

        <Reveal delayMs={240} className="mt-14 flex justify-center">
          <Button
            variant="primary"
            onClick={() => scrollToId(TRIAGE_CALL_SECTION_ID)}
          >
            {offerStack.ctaLabel}
          </Button>
        </Reveal>
      </div>
    </section>
  );
}
