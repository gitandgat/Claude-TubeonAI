interface OfferCardProps {
  index: string;
  title: string;
  body: string;
}

export function OfferCard({ index, title, body }: OfferCardProps) {
  return (
    <article className="relative overflow-hidden border border-charcoal/15 bg-warm-white p-8">
      <span
        aria-hidden="true"
        className="pointer-events-none absolute -right-2 -top-6 select-none font-serif text-8xl font-black text-charcoal/5"
      >
        {index}
      </span>
      <p className="relative text-xs font-semibold tracking-[0.2em] text-charcoal/70 uppercase">
        {index}
      </p>
      <h3 className="relative mt-4 font-serif text-2xl font-bold text-charcoal">
        {title}
      </h3>
      <p className="relative mt-4 text-base leading-relaxed text-charcoal/75">
        {body}
      </p>
    </article>
  );
}
