import { describe, expect, it } from "vitest";
import { getReadableError } from "./errors";

describe("getReadableError", () => {
  it("handles session expiration status codes", () => {
    expect(getReadableError(null, 401)).toBe("Session expired. Please log in again.");
    expect(getReadableError(null, 403)).toBe("Session expired. Please log in again.");
  });

  it("handles rate limits", () => {
    expect(getReadableError(null, 429)).toBe("Too many requests — please wait a moment.");
  });

  it("handles server errors", () => {
    expect(getReadableError(null, 500)).toBe("Server error. We're looking into it.");
    expect(getReadableError(null, 503)).toBe("Server error. We're looking into it.");
  });

  it("handles network errors", () => {
    expect(getReadableError(new TypeError("Failed to fetch"))).toBe("Couldn't load data. Check your connection.");
  });

  it("falls back gracefully for unknown errors", () => {
    expect(getReadableError(new Error("Something surprising"))).toBe("Something went wrong. Please try again.");
  });
});
