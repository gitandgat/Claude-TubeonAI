import { useState } from "react";
import { Reveal } from "@/components/ui/Reveal";
import { SectionHeading } from "@/components/ui/SectionHeading";
import { triageCall } from "@/data/copy";
import { TRIAGE_CALL_SECTION_ID } from "@/lib/constants";
import { CalendlyEmbed } from "./CalendlyEmbed";
import { TriageForm } from "./TriageForm";

type SubmissionState =
  | { status: "idle" }
  | { status: "success"; firstName: string; email: string };

export function TriageCallSection() {
  const [submission, setSubmission] = useState<SubmissionState>({
    status: "idle",
  });

  return (
    <section
      id={TRIAGE_CALL_SECTION_ID}
      aria-labelledby="triage-call-heading"
      className="border-t border-charcoal/10 bg-warm-white py-24 sm:py-32"
    >
      <div className="mx-auto max-w-site px-6 sm:px-8">
        <Reveal>
          <SectionHeading
            headingId="triage-call-heading"
            eyebrow={triageCall.eyebrow}
            headline={triageCall.headline}
            subhead={triageCall.subhead}
          />
        </Reveal>

        <Reveal delayMs={80} className="mt-6 max-w-prose">
          <p className="border-l-2 border-teal pl-4 text-sm font-medium text-charcoal/70">
            {triageCall.immigrationLine}
          </p>
        </Reveal>

        <Reveal delayMs={120} className="mt-12">
          {submission.status === "idle" ? (
            <TriageForm
              onSuccess={(firstName, email) =>
                setSubmission({ status: "success", firstName, email })
              }
            />
          ) : (
            <div className="max-w-2xl">
              <h3 className="font-serif text-2xl font-bold text-charcoal">
                {triageCall.successHeading(submission.firstName)}
              </h3>
              <div className="mt-6">
                <CalendlyEmbed
                  prefillName={submission.firstName}
                  prefillEmail={submission.email}
                />
              </div>
            </div>
          )}
        </Reveal>
      </div>
    </section>
  );
}
