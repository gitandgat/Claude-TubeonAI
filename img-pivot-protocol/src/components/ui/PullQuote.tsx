interface PullQuoteProps {
  children: string;
}

export function PullQuote({ children }: PullQuoteProps) {
  return (
    <blockquote className="border-l-2 border-amber pl-6 text-xl italic leading-relaxed text-charcoal sm:text-2xl">
      {children}
    </blockquote>
  );
}
