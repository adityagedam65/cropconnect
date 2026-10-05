import { Languages, Mail, MessageCircle, Moon, Phone, Sun } from "lucide-react";
import { toast } from "sonner";
import LanguageSelect, { languages } from "../LanguageSelect";

export default function SettingsSection({ ctx }) {
  const {
    colors,
    language,
    setLanguage,
    setTheme,
    t,
    theme,
  } = ctx;

  return (
    <div className="space-y-6">
      <div className="p-5 rounded-xl bg-white border border-[#e8e3d8] shadow-sm">
        <h3 className="font-semibold mb-4" style={{ color: colors.textDark }}>{t("language")}</h3>
        <div className="mb-4 inline-flex rounded-lg border border-gray-200 bg-gray-50 px-3 py-2">
          <LanguageSelect value={language} onChange={setLanguage} />
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {languages.map((lang) => (
            <button
              key={lang.code}
              onClick={() => {
                localStorage.setItem("cropconnect-language", lang.code);
                setLanguage(lang.code);
                toast.success(`Language changed to ${lang.name}`);
              }}
              className={`p-3 rounded-lg border-2 transition-colors flex flex-col items-center gap-1 ${
                language === lang.code
                  ? "border-green-500 bg-green-50"
                  : "border-gray-200 hover:border-gray-300"
              }`}
            >
              <Languages className="w-4 h-4" style={{ color: colors.greenDark }} />
              <span className="text-lg font-medium" style={{ color: colors.textDark }}>{lang.name}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="p-5 rounded-xl bg-white border border-[#e8e3d8] shadow-sm">
        <h3 className="font-semibold mb-4" style={{ color: colors.textDark }}>{t("appearance")}</h3>
        <div className="flex gap-4">
          <button
            onClick={() => {
              setTheme("light");
              toast.success("Light mode enabled");
            }}
            className={`flex-1 p-4 rounded-lg border-2 flex flex-col items-center gap-2 ${theme === "light" ? "border-green-500 bg-green-50" : "border-gray-300 hover:border-gray-400"}`}
          >
            <Sun className="w-8 h-8 text-amber-500" />
            <span className="font-medium" style={{ color: colors.textDark }}>{t("lightMode")}</span>
          </button>
          <button
            onClick={() => {
              setTheme("dark");
              toast.success("Dark mode enabled");
            }}
            className={`flex-1 p-4 rounded-lg border-2 flex flex-col items-center gap-2 transition-colors ${theme === "dark" ? "border-green-500 bg-green-50" : "border-gray-300 hover:border-gray-400"}`}
          >
            <Moon className="w-8 h-8 text-gray-600" />
            <span className="font-medium" style={{ color: colors.textDark }}>{t("darkMode")}</span>
          </button>
        </div>
      </div>

      <div className="p-5 rounded-xl bg-white border border-[#e8e3d8] shadow-sm">
        <h3 className="font-semibold mb-4" style={{ color: colors.textDark }}>Contact Us</h3>
        <div className="space-y-4">
          <div className="flex items-center gap-3 p-3 rounded-lg" style={{ background: colors.cream }}>
            <Mail className="w-5 h-5" style={{ color: colors.greenDark }} />
            <div>
              <p className="font-medium" style={{ color: colors.textDark }}>Email</p>
              <p className="text-sm" style={{ color: colors.textMid }}>cropconnectco@gmail.com</p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 rounded-lg" style={{ background: colors.cream }}>
            <Phone className="w-5 h-5" style={{ color: colors.greenDark }} />
            <div>
              <p className="font-medium" style={{ color: colors.textDark }}>Phone</p>
              <p className="text-sm" style={{ color: colors.textMid }}>+91 94791 87552</p>
            </div>
          </div>
          <div className="flex items-center gap-3 p-3 rounded-lg" style={{ background: colors.cream }}>
            <MessageCircle className="w-5 h-5" style={{ color: colors.greenDark }} />
            <div>
              <p className="font-medium" style={{ color: colors.textDark }}>WhatsApp</p>
              <p className="text-sm" style={{ color: colors.textMid }}>+91 94791 87552</p>
            </div>
          </div>
        </div>
      </div>

      <div className="p-5 rounded-xl bg-white border border-[#e8e3d8] shadow-sm">
        <h3 className="font-semibold mb-4" style={{ color: colors.textDark }}>About</h3>
        <p className="text-sm" style={{ color: colors.textMid }}>
          CropConnect v1.0.0 - Smart Farming Dashboard<br />
          Empowering farmers with IoT and AI technology
        </p>
      </div>
    </div>
  );
}
