import DashboardPageContent from "../../components/dashboard/DashboardPageContent";

export default function DashboardWeather() {
  // Lazy wrapper keeps the weather route code-split without changing dashboard behavior.
  return <DashboardPageContent />;
}
