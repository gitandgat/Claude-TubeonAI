import type { TranslationRow } from "@/data/copy";

interface TranslationTableProps {
  rows: TranslationRow[];
}

export function TranslationTable({ rows }: TranslationTableProps) {
  return (
    <div className="relative">
      <div
        aria-hidden="true"
        className="absolute inset-0 translate-x-2 translate-y-2 bg-charcoal/5"
      />
      <div className="relative border border-charcoal/15 bg-warm-white">
        <table className="hidden w-full border-collapse text-left sm:table">
          <caption className="sr-only">
            Clinical skills mapped to their tech and consulting equivalents
          </caption>
          <thead>
            <tr className="border-b border-charcoal/15">
              <th
                scope="col"
                className="w-1/2 px-6 py-4 text-xs font-semibold tracking-[0.15em] text-charcoal/60 uppercase"
              >
                On the Ward
              </th>
              <th
                scope="col"
                className="w-1/2 px-6 py-4 text-xs font-semibold tracking-[0.15em] text-charcoal/60 uppercase"
              >
                In the Field
              </th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr
                key={row.clinicalSkill}
                className="border-b border-charcoal/10 last:border-b-0"
              >
                <td className="px-6 py-5 align-top text-base text-charcoal">
                  {row.clinicalSkill}
                </td>
                <td className="px-6 py-5 align-top text-base text-charcoal">
                  {row.techEquivalent}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        <ul className="divide-y divide-charcoal/10 sm:hidden">
          {rows.map((row) => (
            <li key={row.clinicalSkill} className="px-5 py-5">
              <p className="text-xs font-semibold tracking-[0.15em] text-charcoal/50 uppercase">
                On the Ward
              </p>
              <p className="mt-1 text-base text-charcoal">{row.clinicalSkill}</p>
              <p className="mt-4 text-xs font-semibold tracking-[0.15em] text-charcoal/50 uppercase">
                In the Field
              </p>
              <p className="mt-1 text-base text-charcoal">{row.techEquivalent}</p>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
