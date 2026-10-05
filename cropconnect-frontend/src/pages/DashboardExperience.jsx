import DashboardExperienceCore from "./DashboardExperienceCore";

export default function DashboardExperience() {
  // Thin entry keeps routing stable while the heavy dashboard state lives in the core module.
  return <DashboardExperienceCore />;
}
