import { useState } from "react";
import { Card } from "../components/Card";
import { Button } from "../components/Button";

type Sensitivity = "low" | "medium" | "high";

const OPTIONS: { value: Sensitivity; label: string; description: string }[] = [
  { value: "low", label: "Low", description: "Redacts only obvious credentials and identifiers." },
  { value: "medium", label: "Medium", description: "Masks names, emails, and financial markers." },
  {
    value: "high",
    label: "High",
    description: "Aggressive masking of all proper nouns and dates.",
  },
];

export function Settings() {
  const [sensitivity, setSensitivity] = useState<Sensitivity>("medium");

  return (
    <div className="flex max-w-xl flex-col gap-6">
      <h1 className="text-xl font-semibold">Settings</h1>

      <Card>
        <h2 className="mb-3 font-medium">Masking sensitivity</h2>
        <div className="flex flex-col gap-2">
          {OPTIONS.map((option) => (
            <label
              key={option.value}
              className="flex cursor-pointer items-start gap-3 rounded-md border border-surface-border p-3 has-[:checked]:border-accent"
            >
              <input
                type="radio"
                name="sensitivity"
                value={option.value}
                checked={sensitivity === option.value}
                onChange={() => setSensitivity(option.value)}
                className="mt-1"
              />
              <span>
                <span className="block font-medium">{option.label}</span>
                <span className="block text-sm text-on-surface-muted">{option.description}</span>
              </span>
            </label>
          ))}
        </div>
        <Button className="mt-4">Save changes</Button>
      </Card>
    </div>
  );
}
