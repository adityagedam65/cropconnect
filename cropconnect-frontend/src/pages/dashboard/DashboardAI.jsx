import DashboardPageContent from "../../components/dashboard/DashboardPageContent";

export default function DashboardAI() {
  // Lazy wrapper keeps AI and planner routes code-split without changing dashboard behavior.
  return <DashboardPageContent />;
}
