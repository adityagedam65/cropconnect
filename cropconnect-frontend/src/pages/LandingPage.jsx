import { useEffect } from "react";
import Header from "../components/landing/Header";
import Hero from "../components/landing/Hero";
import PrototypeSection from "../components/landing/PrototypeSection";
import FeaturesSection from "../components/landing/FeaturesSection";
import HowItWorks from "../components/landing/HowItWorks";
import GoalsSection from "../components/landing/GoalsSection";
import EcosystemSection from "../components/landing/EcosystemSection";
import MobileAppSection from "../components/landing/MobileAppSection";
import BenefitsSection from "../components/landing/BenefitsSection";
import ImpactStats from "../components/landing/ImpactStats";
import ContactSection from "../components/landing/ContactSection";
import Footer from "../components/landing/Footer";

export default function LandingPage() {
  useEffect(() => {
    document.title = "CropConnect - Smart Farming Dashboard";
  }, []);

  return (
    <div data-testid="landing-page" className="relative">
      <a
        href="#main-content"
        className="skip-link sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-[100] focus:bg-[#1B4332] focus:text-[#FDFBF7] focus:px-4 focus:py-2 focus:rounded-full focus:text-sm focus:font-medium"
      >
        Skip to main content
      </a>
      <Header />
      <main id="main-content" className="relative z-10">
        <Hero />
        <ImpactStats />
        <PrototypeSection />
        <FeaturesSection />
        <HowItWorks />
        <GoalsSection />
        <BenefitsSection />
        <EcosystemSection />
        <MobileAppSection />
        <ContactSection />
      </main>
      <Footer />
    </div>
  );
}
