import { CircuitBoard, Cpu, Radio, Ruler } from "lucide-react";
import { useLandingLanguage } from "../../contexts/AppLanguageContext";

const SENSOR_LABELS = ["Soil", "DHT22", "pH", "NPK"].map((label, index) => (
  `<g transform="translate(88 ${106 + index * 80})">`
  + `<rect width="98" height="48" rx="10" fill="#0F2A1F" stroke="#E3C77B" stroke-opacity="0.55"/>`
  + `<text x="49" y="30" text-anchor="middle" fill="#FDFBF7" font-size="16" font-family="DM Sans">${label}</text>`
  + `<circle cx="112" cy="24" r="5" fill="#22C55E" stroke="none"/>`
  + `</g>`
)).join("");

const ESP32_PINS = Array.from({ length: 9 }, (_, i) => (
  `<rect x="-12" y="${20 + i * 18}" width="12" height="5" fill="#E3C77B" opacity="0.7" />`
  + `<rect x="130" y="${20 + i * 18}" width="12" height="5" fill="#E3C77B" opacity="0.7" />`
)).join("");

const specs = [
  { icon: Cpu, label: "MCU", value: "ESP32 field node" },
  { icon: Radio, label: "Connectivity", value: "SIM800L cellular" },
  { icon: CircuitBoard, label: "Sensors", value: "Soil, DHT22, pH, NPK" },
  { icon: Ruler, label: "Field scale", value: "1-2 acre pilot plot" },
];

export default function PrototypeSection() {
  const { t } = useLandingLanguage();
  const specCards = specs.map((s, i) => (
    <div
      key={i}
      data-testid={`prototype-spec-${i}`}
      className="rounded-xl border border-[#D5D1C5] bg-white p-4 hover-lift"
    >
      <s.icon className="w-4 h-4 text-[#E07A5F]" />
      <div className="mt-3 eyebrow text-[10px]">{s.label}</div>
      <div className="mt-1 text-sm font-medium text-[#1A201C]">{s.value}</div>
    </div>
  ));

  return (
    <section
      id="prototype"
      data-testid="prototype-section"
      className="relative py-20 sm:py-28"
    >
      <div className="mx-auto max-w-7xl px-5 sm:px-8 grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
        <div className="lg:col-span-5 order-2 lg:order-1">
          <span className="eyebrow">{t("prototypeEyebrow")}</span>
          <h2 className="font-display mt-3 text-4xl sm:text-5xl leading-tight text-[#1A201C]">
            {t("prototypeTitle")} <span className="italic text-[#1B4332]">{t("prototypeTitleItalic")}</span>
          </h2>
          <p className="mt-5 text-base text-[#1A201C]/70 max-w-md">
            {t("prototypeBody")}
          </p>

          <div className="mt-8 grid grid-cols-2 gap-4">
            {specCards}
          </div>
        </div>

        <div className="lg:col-span-7 order-1 lg:order-2">
          <div className="relative">
            <div className="absolute -inset-3 rounded-[28px] bg-[#1B4332]/5 -z-0" />
            <div className="relative rounded-[22px] border-[10px] border-[#1B4332] bg-[#0F2A1F] overflow-hidden shadow-[0_40px_80px_-40px_rgba(15,42,31,0.6)]">
              <svg
                viewBox="0 0 760 520"
                data-testid="prototype-image"
                className="w-full h-[420px] sm:h-[520px]"
                role="img"
                aria-label="CropConnect ESP32 prototype circuit schematic"
              >
                <rect width="760" height="520" fill="#0F2A1F" />
                <rect x="42" y="42" width="676" height="436" rx="34" fill="#1B4332" stroke="#52796F" strokeWidth="3" />
                <g stroke="#E3C77B" strokeOpacity="0.4" strokeWidth="3" fill="none">
                  <path d="M185 130 H315" />
                  <path d="M185 210 H315" />
                  <path d="M185 290 H315" />
                  <path d="M185 370 H315" />
                  <path d="M445 180 H575" />
                  <path d="M445 260 H575" />
                  <path d="M445 340 H575" />
                  <path d="M380 170 V92 H610" />
                  <path d="M380 350 V430 H150" />
                  <path d="M314 260 H240 V430" />
                  <path d="M445 260 H520 V92" />
                </g>
                <g dangerouslySetInnerHTML={{ __html: SENSOR_LABELS }} />
                <g transform="translate(315 160)">
                  <rect width="130" height="200" rx="16" fill="#0F2A1F" stroke="#E3C77B" strokeOpacity="0.8" strokeWidth="2" />
                  <rect x="24" y="48" width="82" height="92" rx="10" fill="#E07A5F" opacity="0.9" />
                  <text x="65" y="100" textAnchor="middle" fill="#0F2A1F" fontSize="22" fontWeight="700" fontFamily="JetBrains Mono">ESP32</text>
                  <g dangerouslySetInnerHTML={{ __html: ESP32_PINS }} />
                  <circle cx="24" cy="24" r="5" fill="#22C55E" />
                  <circle cx="106" cy="176" r="5" fill="#22C55E" />
                </g>
                <g transform="translate(575 190)">
                  <rect width="116" height="138" rx="14" fill="#0F2A1F" stroke="#E3C77B" strokeOpacity="0.65" strokeWidth="2" />
                  <rect x="18" y="18" width="80" height="52" rx="8" fill="#52796F" />
                  <text x="58" y="50" textAnchor="middle" fill="#FDFBF7" fontSize="16" fontWeight="700" fontFamily="JetBrains Mono">SIM800L</text>
                  <path d="M26 96 H90 M26 112 H74" stroke="#E3C77B" strokeOpacity="0.6" strokeWidth="4" strokeLinecap="round" />
                  <circle cx="94" cy="112" r="6" fill="#22C55E" />
                </g>
                <g fill="#22C55E">
                  <circle cx="628" cy="92" r="6" />
                  <circle cx="150" cy="430" r="6" />
                  <circle cx="240" cy="430" r="6" />
                </g>
              </svg>
              <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between px-4 py-2 rounded-lg bg-black/40 backdrop-blur-md border border-white/10">
                <span className="font-mono text-xs text-white/80">prototype_v1 &middot; field node</span>
                <span className="flex items-center gap-2 text-white/80 text-xs">
                  <span className="live-dot" /> field node
                </span>
              </div>
            </div>
            <p className="mt-3 text-xs text-[#1A201C]/50 font-mono">
              Prototype circuit schematic.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
