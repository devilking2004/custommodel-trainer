import { CheckCircle2 } from "lucide-react";

import { LandingHero } from "@/components/landing-hero";

const features = [
  "Text-to-Text and Text-to-Image model setup",
  "Data validation and readiness scoring",
  "Owner-reviewed feedback before retraining",
  "Versioning with future rollback support",
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-50">
      <LandingHero />
      <section className="mx-auto grid max-w-6xl gap-4 px-6 pb-20 md:grid-cols-4">
        {features.map((feature) => (
          <div key={feature} className="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
            <CheckCircle2 className="h-5 w-5 text-slate-800" />
            <p className="mt-4 text-sm font-medium leading-6 text-slate-700">{feature}</p>
          </div>
        ))}
      </section>
    </main>
  );
}
