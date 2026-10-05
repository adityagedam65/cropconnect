// Thin dashboard page entrypoint; dashboard state and rendering live in extracted modules.
import { useEffect } from "react";
import DashboardExperience from "./DashboardExperience";

export default function Dashboard() {
  useEffect(() => {
    document.title = "Dashboard - CropConnect";
    return () => {
      document.title = "CropConnect - Smart Farming Dashboard";
    };
  }, []);

  return <DashboardExperience />;
}
