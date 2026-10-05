import { describe, expect, it } from "vitest";
import { SENSOR_THRESHOLDS, evaluateAllReadings, evaluateSensorReading } from "./sensorThresholds";

describe("evaluateSensorReading", () => {
  it("returns null for readings within safe range", () => {
    expect(evaluateSensorReading("soilMoisture", 55)).toBeNull();
    expect(evaluateSensorReading("soilPh", 6.8)).toBeNull();
    expect(evaluateSensorReading("temperature", 28)).toBeNull();
  });

  it("returns a warning alert for borderline readings", () => {
    const alert = evaluateSensorReading("soilMoisture", 25);
    expect(alert).not.toBeNull();
    expect(alert.tone).toBe("warning");
    expect(alert.key).toBe("soilMoisture");
  });

  it("returns a critical alert for severely out-of-range readings", () => {
    const alert = evaluateSensorReading("temperature", 50);
    expect(alert).not.toBeNull();
    expect(alert.tone).toBe("critical");
  });

  it("returns null for null or undefined values", () => {
    expect(evaluateSensorReading("soilMoisture", null)).toBeNull();
    expect(evaluateSensorReading("soilMoisture", undefined)).toBeNull();
  });

  it("covers every sensor type at threshold boundaries", () => {
    Object.entries(SENSOR_THRESHOLDS).forEach(([key, spec]) => {
      // Boundary values are inclusive-safe; one step outside should alert.
      expect(evaluateSensorReading(key, spec.warning.low)).toBeNull();
      expect(evaluateSensorReading(key, spec.warning.high)).toBeNull();
      expect(evaluateSensorReading(key, spec.warning.low - 1)).not.toBeNull();
      expect(evaluateSensorReading(key, spec.warning.high + 1)).not.toBeNull();
    });
  });

  it("does not throw for absent values on every sensor type", () => {
    Object.keys(SENSOR_THRESHOLDS).forEach((key) => {
      expect(() => evaluateSensorReading(key, null)).not.toThrow();
      expect(() => evaluateSensorReading(key, undefined)).not.toThrow();
      expect(evaluateSensorReading(key, null)).toBeNull();
      expect(evaluateSensorReading(key, undefined)).toBeNull();
    });
  });
});

describe("evaluateAllReadings", () => {
  it("returns empty array when all readings are safe", () => {
    const alerts = evaluateAllReadings({
      soilMoisture: 55,
      temperature: 28,
      humidity: 65,
      soilPh: 6.8,
      nitrogen: 40,
      phosphorus: 25,
      potassium: 30,
    });
    expect(alerts).toHaveLength(0);
  });

  it("returns alerts for out-of-range readings", () => {
    const alerts = evaluateAllReadings({
      soilMoisture: 10,
      temperature: 28,
      humidity: 65,
      soilPh: 9.0,
      nitrogen: 40,
      phosphorus: 25,
      potassium: 30,
    });
    expect(alerts.length).toBeGreaterThanOrEqual(2);
    const keys = alerts.map((alert) => alert.key);
    expect(keys).toContain("soilMoisture");
    expect(keys).toContain("soilPh");
  });

  it("returns empty array for null sensorData", () => {
    expect(evaluateAllReadings(null)).toHaveLength(0);
  });
});
