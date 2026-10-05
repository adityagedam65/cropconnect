import DashboardPageContent from "../../components/dashboard/DashboardPageContent";

export default function DashboardSettings() {
  // Lazy wrapper keeps settings/profile routes code-split without changing dashboard behavior.
  return <DashboardPageContent />;
}
