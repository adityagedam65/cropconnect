import { Leaf } from "lucide-react";
import { useLandingLanguage } from "../../contexts/AppLanguageContext";

export default function Footer() {
  const { t } = useLandingLanguage();
  const year = new Date().getFullYear();
  return (
    <footer
      data-testid="site-footer"
      className="relative bg-[#1B4332] text-[#FDFBF7] overflow-hidden"
    >
      <div className="mx-auto max-w-7xl px-5 sm:px-8 pt-20 pb-10">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-10">
          <div className="md:col-span-5">
            <div className="flex items-center gap-2">
              <span className="w-9 h-9 rounded-full bg-[#FDFBF7] text-[#1B4332] flex items-center justify-center">
                <Leaf className="w-4 h-4" strokeWidth={2.5} />
              </span>
              <span className="font-display text-2xl">CropConnect</span>
            </div>
            <p className="mt-4 text-sm text-white/70 max-w-sm leading-relaxed">
              {t("footerBody")}
            </p>
          </div>

          <div className="md:col-span-2">
            <h5 className="eyebrow text-[#E3C77B] text-[10px]">Product</h5>
            <ul className="mt-4 space-y-2 text-sm text-white/75">
              <li><a href="#features" className="link-u">Features</a></li>
              <li><a href="#how-it-works" className="link-u">How it works</a></li>
              <li><a href="#app" className="link-u">Mobile app</a></li>
              <li><a href="#prototype" className="link-u">Prototype</a></li>
            </ul>
          </div>

          <div className="md:col-span-2">
            <h5 className="eyebrow text-[#E3C77B] text-[10px]">Company</h5>
            <ul className="mt-4 space-y-2 text-sm text-white/75">
              <li><a href="#goals" className="link-u">Roadmap</a></li>
              <li><a href="#ecosystem" className="link-u">Ecosystem</a></li>
              <li><a href="#benefits" className="link-u">Benefits</a></li>
              <li><a href="#contact" className="link-u">Contact</a></li>
            </ul>
          </div>

          <div className="md:col-span-3">
            <h5 className="eyebrow text-[#E3C77B] text-[10px]">Get pilot access</h5>
            <p className="mt-4 text-sm text-white/70 mb-4">
              Join the early farmer pilot. We'll send setup instructions.
            </p>
            <button
              onClick={() => {
                const el = document.getElementById("contact");
                if (el) el.scrollIntoView({ behavior: "smooth" });
              }}
              className="w-full rounded-full border border-white/20 bg-white/10 hover:bg-white/20 transition-colors px-4 py-2.5 text-sm text-white/90 text-left flex items-center justify-between group"
            >
              <span>Request pilot access -&gt;</span>
            </button>
            <p className="mt-3 text-xs text-white/40">Maharashtra - Karnataka - Punjab pilots open</p>
          </div>
        </div>

        <div className="mt-16 pt-8 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-white/50 font-mono">
          <span>&copy; {year} CropConnect &middot; Crafted with soil, sun & silicon.</span>
          <span>v1.0 &middot; prototype ready</span>
        </div>
      </div>

      {/* Massive wordmark */}
      <div
        aria-hidden
        className="select-none pointer-events-none px-5 sm:px-8 pb-6"
      >
        <div className="font-display leading-none tracking-tighter text-[#FDFBF7]/10 text-[18vw] sm:text-[14vw]">
          CropConnect
        </div>
      </div>
    </footer>
  );
}

