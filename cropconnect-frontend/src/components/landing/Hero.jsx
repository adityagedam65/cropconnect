import { ArrowRight, Sparkles, Globe2 } from "lucide-react";
import { Button } from "../ui/button";
import LiveSensorCard from "./LiveSensorCard";
import { useLandingLanguage } from "../../contexts/AppLanguageContext";

const FIELD_ARCS = Array.from({ length: 16 }, (_, index) => (
  `<path d="M${18 + index * 34} 344 c10 -18 22 -18 32 0" fill="none" stroke="#EDF6F0" stroke-width="3" stroke-linecap="round" />`
)).join("");

export default function Hero() {
  const { t } = useLandingLanguage();
  const scrollTo = (id) => {
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <section
      id="top"
      data-testid="hero-section"
      className="relative pt-28 lg:pt-36 pb-16 lg:pb-24 overflow-hidden bg-gradient-to-br from-[#FDFBF7] via-[#F4F1EA] to-[#EDF6F0] animate-bg-shift"
    >
      {/* Decorative dashed ring */}
      <div className="absolute -top-24 -right-24 w-[480px] h-[480px] rounded-full dashed-ring opacity-60 pointer-events-none" />
      <div className="absolute -bottom-40 -left-20 w-[360px] h-[360px] rounded-full bg-[#E07A5F]/10 blur-3xl pointer-events-none" />

      <div className="mx-auto max-w-7xl px-5 sm:px-8 grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
        <div className="lg:col-span-7 reveal" style={{ animationDelay: "0.05s" }}>
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#F4F1EA] border border-[#D5D1C5] text-[#1B4332]">
            <Sparkles className="w-3.5 h-3.5" />
            <span className="eyebrow">{t("heroBadge")}</span>
          </div>

          <h1
            data-testid="hero-headline"
            className="font-display mt-6 text-[clamp(2rem,6.5vw,4.8rem)] leading-[0.98] tracking-tight text-[#1A201C]"
          >
            {t("heroTitle1")}
            {" "}
            <span className="italic text-[#1B4332]">{t("heroTitle2")}</span>
            <br />
            {t("heroTitle3")}
          </h1>

          <p className="mt-6 max-w-xl text-base sm:text-lg text-[#1A201C]/70 leading-relaxed">
            {t("heroBody")}
          </p>

          <div className="mt-8 flex flex-wrap items-center gap-3">
            <Button
              data-testid="hero-cta-primary"
              onClick={() => scrollTo("features")}
              className="bg-[#1B4332] hover:bg-[#0F2A1F] text-[#FDFBF7] h-12 px-6 rounded-full group"
            >
              {t("explore")}
              <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
            </Button>
            <Button
              data-testid="hero-cta-secondary"
              variant="outline"
              onClick={() => scrollTo("contact")}
              className="h-12 px-6 rounded-full border-[#1B4332]/20 text-[#1B4332] hover:bg-[#1B4332] hover:text-[#FDFBF7]"
            >
              {t("talkTeam")}
            </Button>
          </div>

          <div className="mt-10 flex flex-wrap gap-6 text-sm text-[#1A201C]/70">
            <div className="flex items-center gap-2">
              <Globe2 className="w-4 h-4 text-[#1B4332]" />
              <span>{t("heroFacts")[0]}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-[#E07A5F]" />
              <span>{t("heroFacts")[1]}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-[#1B4332]" />
              <span>{t("heroFacts")[2]}</span>
            </div>
          </div>
        </div>

        <div
          className="lg:col-span-5 relative reveal"
          style={{ animationDelay: "0.25s" }}
        >
          <div className="relative aspect-[4/5] w-full rounded-[28px] overflow-hidden border border-[#D5D1C5] bg-[#F4F1EA]">
            <svg viewBox="0 0 520 650" className="h-full w-full" role="img" aria-label="Smart agriculture field with ESP32 telemetry">
              <defs>
                <linearGradient id="fieldSky" x1="0" x2="1" y1="0" y2="1">
                  <stop offset="0%" stopColor="#EDF6F0" />
                  <stop offset="55%" stopColor="#F4F1EA" />
                  <stop offset="100%" stopColor="#E3C77B" />
                </linearGradient>
                <linearGradient id="fieldRows" x1="0" x2="0" y1="0" y2="1">
                  <stop offset="0%" stopColor="#52796F" />
                  <stop offset="100%" stopColor="#1B4332" />
                </linearGradient>
                <radialGradient id="sunGlow" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stopColor="#F7D87A" stopOpacity="0.95" />
                  <stop offset="100%" stopColor="#F7D87A" stopOpacity="0" />
                </radialGradient>
              </defs>
              <rect width="520" height="650" fill="url(#fieldSky)" />
              <circle cx="410" cy="105" r="88" fill="url(#sunGlow)" />
              <circle cx="410" cy="105" r="34" fill="#E3C77B" opacity="0.9" />
              <path d="M0 245 C70 224 126 238 190 219 C278 193 348 214 520 178 L520 650 L0 650 Z" fill="#A7C8A1" opacity="0.75" />
              <path d="M0 285 C72 261 138 278 206 254 C304 220 384 250 520 212 L520 650 L0 650 Z" fill="#52796F" opacity="0.5" />
              <path d="M-20 650 L98 302 L157 302 L75 650 Z" fill="#1B4332" opacity="0.92" />
              <path d="M72 650 L180 302 L234 302 L167 650 Z" fill="#2D6A4F" opacity="0.92" />
              <path d="M178 650 L274 302 L328 302 L284 650 Z" fill="#1B4332" opacity="0.9" />
              <path d="M292 650 L370 302 L425 302 L405 650 Z" fill="#2D6A4F" opacity="0.9" />
              <path d="M414 650 L464 302 L520 302 L540 650 Z" fill="#1B4332" opacity="0.92" />
              <path d="M28 650 L132 304" stroke="#E3C77B" strokeWidth="5" opacity="0.45" />
              <path d="M124 650 L207 304" stroke="#E3C77B" strokeWidth="5" opacity="0.45" />
              <path d="M234 650 L301 304" stroke="#E3C77B" strokeWidth="5" opacity="0.45" />
              <path d="M354 650 L398 304" stroke="#E3C77B" strokeWidth="5" opacity="0.45" />
              <g opacity="0.7" dangerouslySetInnerHTML={{ __html: FIELD_ARCS }} />
              <g transform="translate(190 230)">
                <rect x="0" y="0" width="142" height="96" rx="18" fill="#0F2A1F" />
                <rect x="12" y="12" width="118" height="72" rx="12" fill="#1B4332" stroke="#E3C77B" strokeWidth="2" />
                <rect x="32" y="31" width="42" height="26" rx="5" fill="#E07A5F" />
                <rect x="84" y="29" width="26" height="30" rx="4" fill="#EDF6F0" opacity="0.9" />
                <circle cx="24" cy="24" r="4" fill="#22C55E" />
                <circle cx="24" cy="72" r="4" fill="#22C55E" />
                <circle cx="118" cy="24" r="4" fill="#F4F1EA" />
                <circle cx="118" cy="72" r="4" fill="#F4F1EA" />
                <path d="M71 0 V-38" stroke="#0F2A1F" strokeWidth="8" strokeLinecap="round" />
                <path d="M71 -39 C45 -58 40 -86 53 -108" fill="none" stroke="#1B4332" strokeWidth="7" strokeLinecap="round" />
                <path d="M71 -39 C97 -58 102 -86 89 -108" fill="none" stroke="#1B4332" strokeWidth="7" strokeLinecap="round" />
                <path d="M36 96 V138" stroke="#0F2A1F" strokeWidth="6" />
                <path d="M106 96 V138" stroke="#0F2A1F" strokeWidth="6" />
                <path d="M158 18 c26 10 45 32 50 60" fill="none" stroke="#E07A5F" strokeWidth="5" strokeLinecap="round" />
                <path d="M174 0 c42 18 72 54 80 100" fill="none" stroke="#E07A5F" strokeWidth="4" strokeLinecap="round" opacity="0.65" />
                <path d="M-16 18 c-26 10 -45 32 -50 60" fill="none" stroke="#E07A5F" strokeWidth="5" strokeLinecap="round" />
                <path d="M-32 0 c-42 18 -72 54 -80 100" fill="none" stroke="#E07A5F" strokeWidth="4" strokeLinecap="round" opacity="0.65" />
              </g>
              <g transform="translate(72 414)" fill="#F4F1EA" opacity="0.9">
                <rect x="0" y="0" width="58" height="18" rx="9" />
                <rect x="80" y="42" width="42" height="14" rx="7" />
                <rect x="310" y="20" width="66" height="16" rx="8" />
              </g>
              <rect x="0" y="0" width="520" height="650" fill="url(#fieldRows)" opacity="0.08" />
            </svg>
            <div className="absolute inset-0 bg-gradient-to-t from-[#0F2A1F]/30 via-transparent to-transparent" />
            <div className="absolute top-5 left-5 flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/30 backdrop-blur-md border border-white/20 text-white">
              <span className="text-xs tracking-[0.2em] uppercase font-semibold">
                ESP32 field telemetry
              </span>
            </div>
          </div>

          {/* Floating live sensor card */}
          <div
            className="absolute left-2 sm:left-0 lg:-left-16 bottom-6 sm:bottom-10 w-[88%] sm:w-[92%] max-w-[calc(100%-1rem)] sm:max-w-[420px] float-soft"
          >
            <LiveSensorCard />
          </div>
        </div>
      </div>
    </section>
  );
}
