import DashboardPageContent from "../../components/dashboard/DashboardPageContent";

export default function DashboardHome() {
  // Lazy wrapper keeps the overview route code-split without changing dashboard behavior.
  return <DashboardPageContent />;
}
