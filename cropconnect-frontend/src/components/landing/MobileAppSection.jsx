import { Languages, Smartphone, Droplets, Thermometer, Bell } from "lucide-react";
import { useLandingLanguage } from "../../contexts/AppLanguageContext";

const langs = [
  "English",
  "Hindi",
  "Marathi",
  "Telugu",
  "Tamil",
  "Bengali",
  "Kannada",
];

export default function MobileAppSection() {
  const { t } = useLandingLanguage();
  return (
    <section
      id="app"
      data-testid="mobile-app-section"
      className="relative py-20 sm:py-28 overflow-hidden bg-[#FDFBF7] border-t border-[#D5D1C5]"
    >
      <div className="mx-auto max-w-7xl px-5 sm:px-8 grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
        <div className="lg:col-span-6 order-2 lg:order-1 relative">
          <div className="relative aspect-[4/3] rounded-3xl overflow-hidden border border-[#D5D1C5]">
            <svg viewBox="0 0 640 480" className="h-full w-full" role="img" aria-label="Mobile farm dashboard illustration">
              <rect width="640" height="480" fill="#EDF6F0" />
              <path d="M0 310 C120 260 200 304 320 252 C445 198 535 234 640 190 L640 480 L0 480 Z" fill="#52796F" opacity="0.5" />
              <path d="M0 480 L105 292 L160 292 L85 480 Z" fill="#1B4332" />
              <path d="M112 480 L210 292 L266 292 L198 480 Z" fill="#2D6A4F" />
              <path d="M232 480 L326 292 L383 292 L326 480 Z" fill="#1B4332" />
              <path d="M365 480 L445 292 L502 292 L472 480 Z" fill="#2D6A4F" />
              <g transform="translate(366 54)">
                <rect width="168" height="318" rx="28" fill="#0F2A1F" />
                <rect x="14" y="24" width="140" height="270" rx="18" fill="#FDFBF7" />
                <text x="34" y="62" fill="#1A201C" fontSize="15" fontWeight="700" fontFamily="DM Sans">Field live</text>
                <circle cx="132" cy="56" r="6" fill="#22C55E" />
                <rect x="30" y="86" width="108" height="62" rx="12" fill="#1B4332" />
                <text x="44" y="116" fill="#FDFBF7" fontSize="12" fontFamily="DM Sans">Soil moisture</text>
                <text x="44" y="138" fill="#E3C77B" fontSize="23" fontFamily="Fraunces">42%</text>
                <rect x="30" y="164" width="48" height="58" rx="10" fill="#F4F1EA" />
                <rect x="90" y="164" width="48" height="58" rx="10" fill="#F4F1EA" />
                <rect x="30" y="236" width="108" height="34" rx="10" fill="#E07A5F" opacity="0.92" />
              </g>
              <g transform="translate(92 114)" fill="#FDFBF7" opacity="0.9">
                <circle cx="42" cy="42" r="42" fill="#E3C77B" opacity="0.8" />
                <path d="M18 160 c30 -38 78 -38 108 0" stroke="#1B4332" strokeWidth="9" strokeLinecap="round" fill="none" />
                <path d="M72 86 v72" stroke="#1B4332" strokeWidth="10" strokeLinecap="round" />
              </g>
            </svg>
            <div className="absolute inset-0 bg-gradient-to-tr from-[#0F2A1F]/50 via-transparent to-transparent" />
          </div>

          <div className="absolute -right-4 sm:-right-10 -bottom-6 w-[240px] rounded-[32px] bg-[#1B4332] p-2 shadow-2xl hidden sm:block">
            <div className="rounded-[24px] bg-[#FDFBF7] p-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="eyebrow text-[10px]">Account</div>
                  <div className="font-display text-lg text-[#1A201C]">Field</div>
                </div>
                <span className="live-dot" />
              </div>
              <div className="mt-4 space-y-2">
                <Row icon={Droplets} label="Soil moisture" value="42%" tone="#1B4332" />
                <Row icon={Thermometer} label="Temperature" value="28C" tone="#E07A5F" />
                <Row icon={Bell} label="Alert" value="Irrigate soon" tone="#52796F" />
              </div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-6 order-1 lg:order-2">
          <span className="eyebrow">{t("appEyebrow")}</span>
          <h2 className="font-display mt-3 text-4xl sm:text-5xl leading-tight text-[#1A201C]">
            {t("appTitle")}
            <span className="italic text-[#1B4332]">{t("appItalic")}</span>
          </h2>
          <p className="mt-5 text-base text-[#1A201C]/70 max-w-lg">
            {t("appBody")}
          </p>

          <div className="mt-8 flex flex-wrap gap-2" data-testid="language-chips">
            {langs.map((label) => (
              <span
                key={label}
                className="px-4 py-2 rounded-full border border-[#D5D1C5] bg-white text-sm text-[#1A201C]"
              >
                {label}
              </span>
            ))}
          </div>

          <div className="mt-8 grid grid-cols-2 gap-4 max-w-lg">
            <div className="p-4 rounded-xl bg-[#F4F1EA] border border-[#D5D1C5]">
              <Languages className="w-5 h-5 text-[#1B4332]" />
              <div className="mt-2 font-display text-xl text-[#1A201C]">AI translation</div>
              <div className="text-xs text-[#1A201C]/60">Hindi, Marathi, Tamil and more</div>
            </div>
            <div className="p-4 rounded-xl bg-[#F4F1EA] border border-[#D5D1C5]">
              <Smartphone className="w-5 h-5 text-[#E07A5F]" />
              <div className="mt-2 font-display text-xl text-[#1A201C]">Live backend</div>
              <div className="text-xs text-[#1A201C]/60">streamed from your ESP32 node</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Row({ icon: Icon, label, value, tone }) {
  return (
    <div className="flex items-center justify-between px-3 py-2 rounded-lg border border-[#E8E4D7] bg-white">
      <div className="flex items-center gap-2">
        <span
          className="w-6 h-6 rounded-md flex items-center justify-center text-white"
          style={{ backgroundColor: tone }}
        >
          <Icon className="w-3 h-3" />
        </span>
        <span className="text-xs text-[#1A201C]/70">{label}</span>
      </div>
      <span className="font-display text-sm text-[#1A201C]">{value}</span>
    </div>
  );
}
