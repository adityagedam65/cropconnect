import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import SensorPanel from "./SensorPanel";

const colors = {
  textDark: "#111",
  textMid: "#444",
  textLight: "#666",
  greenLight: "#4ade80",
  greenMid: "#286",
  creamDark: "#eee",
  cream: "#fff",
  terracotta: "#b65",
  blue: "#38f",
  gold: "#ca8",
};

const sensorData = {
  soilMoisture: 55,
  temperature: 28,
  humidity: 65,
  soilPh: 6.8,
  nitrogen: 40,
  phosphorus: 25,
  potassium: 30,
};

describe("SensorPanel", () => {
  it("renders live sensor values", () => {
    render(
      <SensorPanel
        colors={colors}
        sensorConnection={{ status: "connected", source: "backend", deviceId: "dev1" }}
        sensorData={sensorData}
        userData={{ state: "Maharashtra" }}
      />
    );
    expect(screen.getByText("55")).toBeInTheDocument();
    expect(screen.getByText("28")).toBeInTheDocument();
  });

  it("renders the crop alert ranges table", () => {
    render(
      <SensorPanel
        colors={colors}
        sensorConnection={{ status: "connected", source: "backend", deviceId: "dev1" }}
        sensorData={sensorData}
        userData={{ state: "Maharashtra" }}
      />
    );
    expect(screen.getAllByText("Soil Moisture").length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Soil pH/i).length).toBeGreaterThan(0);
  });
});
