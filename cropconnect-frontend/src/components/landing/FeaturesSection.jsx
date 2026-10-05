import {
  Languages,
  Activity,
  BellRing,
  WifiOff,
  CloudSun,
  Brain,
  Sprout,
  Tractor,
  ShieldCheck,
} from "lucide-react";
import { useLandingLanguage } from "../../contexts/AppLanguageContext";

const features = [
  {
    icon: Languages,
    title: "Talk to your farm in any language",
    desc: "English, Hindi, Marathi and more - switch languages from any screen.",
    span: "lg:col-span-5 lg:row-span-2",
    tone: "primary",
  },
  {
    icon: Activity,
    title: "Live sensor readings",
    desc: "Soil moisture, temperature, humidity, pH and NPK - streamed directly from your field node.",
    span: "lg:col-span-4",
    tone: "accent",
  },
  {
    icon: BellRing,
    title: "Smart alerts",
    desc: "Get notified the moment a reading crosses safe crop thresholds.",
    span: "lg:col-span-3",
    tone: "default",
  },
  {
    icon: Brain,
    title: "AI crop advice",
    desc: "Ask anything about your crop. The AI sees your live soil data and local weather before answering.",
    span: "lg:col-span-4",
    tone: "default",
  },
  {
    icon: WifiOff,
    title: "Works over SIM card",
    desc: "No farm Wi-Fi needed. The ESP32 sends data over a SIM800L cellular module.",
    span: "lg:col-span-3",
    tone: "accent",
  },
  {
    icon: CloudSun,
    title: "Live weather",
    desc: "Local forecast shown alongside your sensor data for complete picture.",
    span: "lg:col-span-4",
    tone: "default",
  },
  {
    icon: Sprout,
    title: "Crop planner",
    desc: "Tell the AI your land size and season - get a planting schedule built around your actual soil.",
    span: "lg:col-span-4",
    tone: "default",
  },
  {
    icon: Tractor,
    title: "Full farm profile",
    desc: "One place for your land size, location, device ID and setup status.",
    span: "lg:col-span-4",
    tone: "default",
  },
  {
    icon: ShieldCheck,
    title: "Your data stays yours",
    desc: "Each ESP32 device gets its own API key. Nobody else can read or write your sensor data.",
    span: "lg:col-span-4",
    tone: "primary",
  },
];

const toneStyles = {
  primary: "bg-[#1B4332] text-[#FDFBF7] border-[#1B4332]",
  accent: "bg-[#E07A5F] text-white border-[#E07A5F]",
  default: "bg-white text-[#1A201C] border-[#D5D1C5]",
};

export default function FeaturesSection() {
  const { t } = useLandingLanguage();
  return (
    <section
      id="features"
      data-testid="features-section"
      className="relative py-20 sm:py-28 bg-[#FDFBF7]"
    >
      <div className="mx-auto max-w-7xl px-5 sm:px-8">
        <div className="max-w-2xl">
          <span className="eyebrow">{t("featuresEyebrow")}</span>
          <h2 className="font-display mt-3 text-4xl sm:text-5xl leading-tight text-[#1A201C]">
            {t("featuresTitle")}
            <span className="italic text-[#1B4332]">{t("featuresItalic")}</span>
          </h2>
          <p className="mt-5 text-base text-[#1A201C]/70">
            {t("featuresBody")}
          </p>
        </div>

        <div className="mt-12 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-12 gap-5 auto-rows-[minmax(180px,auto)]">
          {features.map((f, i) => (
            <div
              key={i}
              data-testid={`feature-${i}`}
              className={`group cursor-pointer rounded-2xl border p-6 hover-lift sm:col-span-1 ${f.span} ${toneStyles[f.tone]}`}
              style={f.tone === "default" ? undefined : {
                backgroundImage: "radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px)",
                backgroundSize: "20px 20px",
              }}
            >
              <f.icon
                className="w-6 h-6 transition-transform duration-200 group-hover:-translate-y-1"
                strokeWidth={1.8}
              />
              <h3 className="font-display mt-4 text-xl sm:text-2xl leading-snug">
                {f.title}
              </h3>
              <p className={`mt-3 text-sm leading-relaxed ${f.tone === "default" ? "text-[#1A201C]/70" : "text-white/85"}`}>
                {f.desc}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
