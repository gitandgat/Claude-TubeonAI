import { footer } from "@/data/copy";

export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="bg-charcoal">
      <div className="mx-auto max-w-site px-6 py-16 sm:px-8">
        <span className="font-serif text-lg font-bold tracking-tight text-warm-white">
          Crosswalk Wisdom
        </span>
        <p className="mt-3 font-serif text-xl italic text-dim-white">
          {footer.tagline}
        </p>

        <div className="mt-10 flex flex-col gap-2 border-t border-warm-white/10 pt-6 text-sm text-dim-white sm:flex-row sm:items-center sm:justify-between">
          <p>
            © {year} Crosswalk Wisdom. All rights reserved.
          </p>
          <div className="flex flex-wrap gap-x-6 gap-y-2">
            <a
              href={`mailto:${footer.contactEmail}`}
              className="underline decoration-transparent underline-offset-4 transition-colors hover:decoration-current"
            >
              {footer.contactEmail}
            </a>
            <a
              href="https://crosswalkwisdom.com"
              className="underline decoration-transparent underline-offset-4 transition-colors hover:decoration-current"
            >
              {footer.siteLabel}
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
