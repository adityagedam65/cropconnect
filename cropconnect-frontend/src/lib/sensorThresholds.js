// Sensor alert thresholds for general Indian summer crops.
// Each entry defines critical (immediate action) and warning (watch closely) levels.

export const SENSOR_THRESHOLDS = {
  soilMoisture: {
    label: "Soil Moisture",
    unit: "%",
    critical: { low: 20, high: 90 },
    warning: { low: 30, high: 80 },
  },
  temperature: {
    label: "Temperature",
    unit: "\u00b0C",
    critical: { low: 5, high: 45 },
    warning: { low: 10, high: 42 },
  },
  humidity: {
    label: "Humidity",
    unit: "%",
    critical: { low: 20, high: 95 },
    warning: { low: 30, high: 90 },
  },
  soilPh: {
    label: "Soil pH",
    unit: "",
    critical: { low: 5.0, high: 8.5 },
    warning: { low: 5.5, high: 8.0 },
  },
  nitrogen: {
    label: "Nitrogen",
    unit: " mg/kg",
    critical: { low: 5, high: 90 },
    warning: { low: 10, high: 80 },
  },
  phosphorus: {
    label: "Phosphorus",
    unit: " mg/kg",
    critical: { low: 3, high: 65 },
    warning: { low: 5, high: 60 },
  },
  potassium: {
    label: "Potassium",
    unit: " mg/kg",
    critical: { low: 5, high: 85 },
    warning: { low: 10, high: 80 },
  },
};

export function evaluateSensorReading(key, value) {
  const spec = SENSOR_THRESHOLDS[key];
  if (!spec || value === null || value === undefined || Number.isNaN(Number(value))) return null;

  const v = Number(value);
  const { label, unit, critical, warning } = spec;

  if (v < critical.low || v > critical.high) {
    const direction = v < critical.low ? "critically low" : "critically high";
    return {
      key,
      tone: "critical",
      title: `${label} ${direction}`,
      body: `Reading is ${v}${unit} - immediate attention needed. Safe range is ${warning.low}-${warning.high}${unit}.`,
      value: v,
    };
  }

  if (v < warning.low || v > warning.high) {
    const direction = v < warning.low ? "low" : "high";
    return {
      key,
      tone: "warning",
      title: `${label} is ${direction}`,
      body: `Reading is ${v}${unit} - monitor closely. Safe range is ${warning.low}-${warning.high}${unit}.`,
      value: v,
    };
  }

  return null;
}

export function evaluateAllReadings(sensorData) {
  if (!sensorData) return [];
  return Object.entries(SENSOR_THRESHOLDS)
    .map(([key]) => evaluateSensorReading(key, sensorData[key]))
    .filter(Boolean);
}
