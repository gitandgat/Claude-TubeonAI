import { useState } from "react";
import type { FormEvent } from "react";
import { Button } from "@/components/ui/Button";
import { triageCall } from "@/data/copy";
import { isValidEmail } from "@/lib/validateEmail";

interface TriageFormProps {
  onSuccess: (firstName: string, email: string) => void;
}

type Status = "idle" | "loading" | "error";

export function TriageForm({ onSuccess }: TriageFormProps) {
  const [firstName, setFirstName] = useState("");
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [errorMessage, setErrorMessage] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedName = firstName.trim();
    const trimmedEmail = email.trim();

    if (!trimmedName) {
      setStatus("error");
      setErrorMessage("First name is required.");
      return;
    }

    if (!isValidEmail(trimmedEmail)) {
      setStatus("error");
      setErrorMessage("Please enter a valid email address.");
      return;
    }

    setStatus("loading");
    setErrorMessage("");

    try {
      const response = await fetch("/api/triage-call-lead", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ firstName: trimmedName, email: trimmedEmail }),
      });

      const data: unknown = await response.json();

      if (!response.ok) {
        const message =
          typeof data === "object" && data !== null && "error" in data
            ? String((data as { error: unknown }).error)
            : "Something went wrong. Please try again.";
        setStatus("error");
        setErrorMessage(message);
        return;
      }

      onSuccess(trimmedName, trimmedEmail);
    } catch {
      setStatus("error");
      setErrorMessage("Something went wrong. Please try again.");
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate className="max-w-md">
      <div>
        <label
          htmlFor="firstName"
          className="block text-sm font-medium text-charcoal"
        >
          {triageCall.formLabels.firstName}
        </label>
        <input
          id="firstName"
          name="firstName"
          type="text"
          autoComplete="given-name"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          className="mt-2 block w-full min-h-[44px] border border-charcoal/25 bg-white px-4 py-3 text-base text-charcoal focus-visible:ring-2 focus-visible:ring-charcoal focus-visible:ring-offset-2"
        />
      </div>

      <div className="mt-5">
        <label
          htmlFor="email"
          className="block text-sm font-medium text-charcoal"
        >
          {triageCall.formLabels.email}
        </label>
        <input
          id="email"
          name="email"
          type="email"
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="mt-2 block w-full min-h-[44px] border border-charcoal/25 bg-white px-4 py-3 text-base text-charcoal focus-visible:ring-2 focus-visible:ring-charcoal focus-visible:ring-offset-2"
        />
      </div>

      {status === "error" && (
        <p
          role="alert"
          className="mt-4 border-l-2 border-orange pl-3 text-sm font-medium text-charcoal"
        >
          {errorMessage}
        </p>
      )}

      <div className="mt-6">
        <Button type="submit" variant="primary" disabled={status === "loading"}>
          {status === "loading" ? "Sending…" : triageCall.formLabels.submit}
        </Button>
      </div>

      <p className="mt-4 text-xs text-charcoal/60">{triageCall.trustLine}</p>
    </form>
  );
}
