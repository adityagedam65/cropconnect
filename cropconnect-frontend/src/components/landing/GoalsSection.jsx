import { Tabs, TabsList, TabsTrigger, TabsContent } from "../ui/tabs";
import { CheckCircle2 } from "lucide-react";
import { useLandingLanguage } from "../../contexts/AppLanguageContext";

const shortTerm = [
  "Connect one ESP32 field node and see live soil readings on your dashboard.",
  "Check soil moisture, temperature, humidity and pH from your phone.",
  "Ask the AI farming assistant questions in your own language.",
  "Control your irrigation pump remotely from the dashboard.",
];

const longTerm = [
  "Manage multiple farm plots and irrigation zones from one account.",
  "Track crop history across seasons and compare yield results.",
  "Multilingual voice guidance for farmers who prefer to speak, not type.",
  "Partner network for FPOs, cooperatives and agricultural research stations.",
];

export default function GoalsSection() {
  const { t } = useLandingLanguage();
  return (
    <section
      id="goals"
      data-testid="goals-section"
      className="relative py-20 sm:py-28"
    >
      <div className="mx-auto max-w-7xl px-5 sm:px-8">
        <div className="max-w-2xl">
          <span className="eyebrow">{t("goalsEyebrow")}</span>
          <h2 className="font-display mt-3 text-4xl sm:text-5xl leading-tight text-[#1A201C]">
            {t("goalsTitle")}
            <br />
            <span className="italic text-[#1B4332]">{t("goalsItalic")}</span>
          </h2>
          <p className="mt-5 text-base text-[#1A201C]/70">
            {t("goalsBody")}
          </p>
        </div>

        <div className="mt-12">
          <Tabs defaultValue="short" className="w-full">
            <TabsList
              data-testid="goals-tabs"
              className="bg-[#F4F1EA] border border-[#D5D1C5] rounded-full p-1 h-12"
            >
              <TabsTrigger
                value="short"
                data-testid="tab-short-term"
                className="rounded-full data-[state=active]:bg-[#1B4332] data-[state=active]:text-[#FDFBF7] px-6 h-10 text-sm"
              >
                What works today
              </TabsTrigger>
              <TabsTrigger
                value="long"
                data-testid="tab-long-term"
                className="rounded-full data-[state=active]:bg-[#1B4332] data-[state=active]:text-[#FDFBF7] px-6 h-10 text-sm"
              >
                What's coming next
              </TabsTrigger>
            </TabsList>

            <TabsContent value="short" className="mt-8">
              <GoalList items={shortTerm} accent="#1B4332" />
            </TabsContent>
            <TabsContent value="long" className="mt-8">
              <GoalList items={longTerm} accent="#E07A5F" />
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </section>
  );
}

function GoalList({ items, accent }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {items.map((g, i) => (
        <div
          key={i}
          data-testid={`goal-item-${i}`}
          className="flex gap-4 p-5 rounded-2xl border border-[#D5D1C5] bg-white hover-lift"
        >
          <CheckCircle2 className="w-5 h-5 flex-shrink-0 mt-0.5" style={{ color: accent }} />
          <p className="text-[15px] leading-relaxed text-[#1A201C]">{g}</p>
        </div>
      ))}
    </div>
  );
}
