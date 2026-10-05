import { Droplets, TrendingUp, HeartHandshake, Leaf, Timer, Wallet } from "lucide-react";
import { useLandingLanguage } from "../../contexts/AppLanguageContext";

const benefits = [
  {
    icon: Droplets,
    title: "Water use visibility",
    desc: "Irrigation decisions can use live soil moisture instead of guesswork.",
    featured: true,
  },
  {
    icon: TrendingUp,
    title: "Better crop decisions",
    desc: "Sensor context helps farmers choose the next field action with less uncertainty.",
  },
  {
    icon: Wallet,
    title: "Lower input cost",
    desc: "Fertiliser and pesticide decisions can be checked against live farm readings.",
  },
  {
    icon: Timer,
    title: "Less time in the field",
    desc: "Farmers can check connected farm readings from the dashboard before making a field trip.",
  },
  {
    icon: Leaf,
    title: "Sustainable practice",
    desc: "Data-backed practice supports careful irrigation and input planning.",
  },
  {
    icon: HeartHandshake,
    title: "Farm context in one place",
    desc: "Profile, sensor readings, AI advice and pump status stay tied to one farm account.",
  },
];

export default function BenefitsSection() {
  const { t } = useLandingLanguage();
  return (
    <section
      id="benefits"
      data-testid="benefits-section"
      className="relative py-20 sm:py-28 bg-[#FDFBF7]"
    >
      <div className="mx-auto max-w-7xl px-5 sm:px-8">
        <div className="max-w-2xl">
          <span className="eyebrow">{t("benefitsEyebrow")}</span>
          <h2 className="font-display mt-3 text-4xl sm:text-5xl leading-tight text-[#1A201C]">
            {t("benefitsTitle")}
            <span className="italic text-[#1B4332]">{t("benefitsItalic")}</span>
          </h2>
        </div>

        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-5">
          {benefits.map((b, i) => (
            <div
              key={i}
              data-testid={`benefit-${i}`}
              className={`rounded-2xl border p-6 hover-lift ${
                b.featured
                  ? "md:col-span-3 lg:col-span-1 bg-[#1B4332] text-[#FDFBF7] border-[#1B4332]"
                  : "bg-white text-[#1A201C] border-[#D5D1C5]"
              }`}
              style={b.featured ? {
                backgroundImage: "radial-gradient(circle, rgba(255,255,255,0.08) 1px, transparent 1px)",
                backgroundSize: "18px 18px",
              } : undefined}
            >
              <span className={`w-10 h-10 rounded-xl flex items-center justify-center ${b.featured ? "bg-[#FDFBF7]/15 text-[#FDFBF7]" : "bg-[#1B4332]/5 text-[#1B4332]"}`}>
                <b.icon className="w-5 h-5" />
              </span>
              <h3 className={`font-display mt-5 text-xl ${b.featured ? "text-[#FDFBF7]" : "text-[#1A201C]"}`}>{b.title}</h3>
              <p className={`mt-2 text-sm leading-relaxed ${b.featured ? "text-[#FDFBF7]/80" : "text-[#1A201C]/70"}`}>{b.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
