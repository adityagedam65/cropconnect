import { createContext, useContext } from "react";

const DashboardContext = createContext(null);

export function DashboardProvider({ value, children }) {
  // Centralizes dashboard state so lazy page modules do not receive a huge prop object.
  return (
    <DashboardContext.Provider value={value}>
      {children}
    </DashboardContext.Provider>
  );
}

export function useDashboard() {
  const context = useContext(DashboardContext);
  if (!context) throw new Error("useDashboard must be used inside DashboardProvider");
  return context;
}
