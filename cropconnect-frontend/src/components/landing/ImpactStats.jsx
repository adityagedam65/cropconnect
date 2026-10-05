import { useEffect, useRef, useState } from "react";
import { useLandingLanguage } from "../../contexts/AppLanguageContext";

const stats = [
  { value: "7", suffix: "", label: "Soil readings tracked live" },
  { value: "8", suffix: "+", label: "Indian languages supported" },
  { value: "ESP32", suffix: "", label: "Low-cost field node foundation" },
  { value: "100%", suffix: "", label: "Open hardware, local data" },
];

const easeOutCubic = (value) => 1 - Math.pow(1 - value, 3);

export default function ImpactStats() {
  const { t } = useLandingLanguage();
  const sectionRef = useRef(null);
  const [visible, setVisible] = useState(false);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const node = sectionRef.current;
    if (!node) return undefined;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.35 }
    );
    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!visible) return undefined;
    const duration = 1200;
    const startedAt = performance.now();
    let frameId;
    const tick = (now) => {
      const next = Math.min(1, (now - startedAt) / duration);
      setProgress(easeOutCubic(next));
      if (next < 1) frameId = requestAnimationFrame(tick);
    };
    frameId = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frameId);
  }, [visible]);

  const renderValue = (stat) => {
    const numeric = Number(stat.value);
    if (!Number.isFinite(numeric) || stat.value.includes("%")) return stat.value;
    return `${Math.round(numeric * progress)}${stat.suffix}`;
  };

  return (
    <section
      ref={sectionRef}
      data-testid="impact-stats"
      className="relative bg-[#1B4332]"
    >
      <div className="mx-auto max-w-7xl px-5 sm:px-8 grid grid-cols-2 lg:grid-cols-4 divide-x divide-[#FDFBF7]/20">
        {stats.map((s, i) => (
          <div key={i} className="py-8 px-4 sm:px-8">
            <div className="font-display text-4xl sm:text-5xl text-[#FDFBF7]">{renderValue(s)}</div>
            <div className="mt-2 text-sm text-[#FDFBF7]/70 max-w-[180px]">{s.label || t("impact")[i]}</div>
          </div>
        ))}
      </div>
    </section>
  );
}
