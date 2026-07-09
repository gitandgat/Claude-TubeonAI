import { Button } from "@/components/ui/Button";
import { TRIAGE_CALL_SECTION_ID } from "@/lib/constants";
import { scrollToId } from "@/lib/scrollTo";

export function Header() {
  return (
    <header className="border-b border-charcoal/10 bg-warm-white">
      <div className="mx-auto flex max-w-site items-center justify-between px-6 py-5 sm:px-8">
        <span className="font-serif text-lg font-bold tracking-tight text-charcoal">
          Crosswalk Wisdom
        </span>
        <Button
          variant="primary"
          className="px-5 py-3 text-xs"
          onClick={() => scrollToId(TRIAGE_CALL_SECTION_ID)}
        >
          Book a Triage Call
        </Button>
      </div>
    </header>
  );
}
