export const CROP_SCAN_STATES = Object.freeze({
  IDLE: "idle",
  IMAGE_SELECTED: "image-selected",
  VALIDATING: "validating",
  PLANT_CONFIRMED: "plant-confirmed",
  NOT_A_PLANT: "not-a-plant",
  ANALYZING: "analyzing",
  RESULT: "result",
  LOW_CONFIDENCE: "low-confidence",
  ERROR: "error",
});

export const CROP_SCAN_LIMITS = Object.freeze({
  maxFileSize: 10 * 1024 * 1024,
  acceptedTypes: ["image/jpeg", "image/png", "image/webp"],
  acceptedExtensions: ["jpg", "jpeg", "png", "webp"],
});

export function validateCropImage(file) {
  if (!file) return { valid: false, code: "no-image", message: "Choose a crop photo before continuing." };

  const extension = file.name?.split(".").pop()?.toLowerCase();
  if (!CROP_SCAN_LIMITS.acceptedTypes.includes(file.type) || !CROP_SCAN_LIMITS.acceptedExtensions.includes(extension)) {
    return { valid: false, code: "invalid-type", message: "Please choose a JPG, PNG, or WebP image." };
  }
  if (file.size > CROP_SCAN_LIMITS.maxFileSize) {
    return { valid: false, code: "file-too-large", message: "That image is larger than 10 MB. Choose a smaller photo." };
  }
  return { valid: true };
}

export async function analyzeCropImage(file) {
  const validation = validateCropImage(file);
  if (!validation.valid) throw new Error(validation.message);

  const { API, authHeaders } = await import("../lib/api");
  const response = await fetch(`${API}/vision/analyze`, {
    method: "POST",
    body: file,
    credentials: "include",
    headers: { "Content-Type": file.type, ...authHeaders() },
  });
  const result = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(result.detail || "The scan service is unavailable. Please try again.");
  if (!result.valid_image) throw new Error(result.message || "Please upload a proper crop or leaf photo.");
  if (!result.result_found) throw new Error(result.message || "No reliable crop result was found. Please try a clearer crop or leaf photo.");
  return {
    crop: result.crop,
    disease: result.condition,
    confidence: Math.round(Number(result.confidence || 0) * 100),
    severity: result.severity || "Not available",
    symptoms: result.symptoms || "No symptoms were provided.",
    recommendations: result.recommendation ? [result.recommendation] : ["Consult an agricultural expert for the next steps."],
    modelVersion: result.source || "CropConnect vision model",
    timestamp: new Date().toISOString(),
  };
}
