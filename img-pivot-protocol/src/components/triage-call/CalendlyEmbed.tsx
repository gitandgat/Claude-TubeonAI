import { CALENDLY_URL } from "@/lib/constants";

interface CalendlyEmbedProps {
  prefillName: string;
  prefillEmail: string;
}

export function CalendlyEmbed({ prefillName, prefillEmail }: CalendlyEmbedProps) {
  const src = `${CALENDLY_URL}?name=${encodeURIComponent(
    prefillName
  )}&email=${encodeURIComponent(prefillEmail)}&hide_gdpr_banner=1`;

  return (
    <div className="h-[700px] w-full overflow-hidden border border-charcoal/15 bg-white">
      <iframe
        title="Book your Triage Call"
        src={src}
        loading="lazy"
        className="h-full w-full"
      />
    </div>
  );
}
