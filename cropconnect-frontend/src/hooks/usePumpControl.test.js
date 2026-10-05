import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { API } from "../lib/api";
import { usePumpControl } from "./usePumpControl";

vi.mock("sonner", () => ({
  toast: {
    error: vi.fn(),
    info: vi.fn(),
    success: vi.fn(),
  },
}));

const hookOptions = (protectedFetch) => ({
  protectedFetch,
  userLoaded: false,
  sensorConnection: { deviceId: "ccdev_test" },
  sensorDeviceId: "ccdev_test",
  pollIntervalMs: 100000,
});

describe("usePumpControl", () => {
  beforeEach(() => {
    const store = { "cropconnect-pump-control-mode": "sim800l" };
    vi.stubGlobal("localStorage", {
      getItem: vi.fn((key) => store[key] || null),
      setItem: vi.fn((key, value) => {
        store[key] = String(value);
      }),
      clear: vi.fn(() => {
        Object.keys(store).forEach((key) => delete store[key]);
      }),
    });
    vi.clearAllMocks();
  });

  it("togglePump calls the backend pump state endpoint", async () => {
    const protectedFetch = vi.fn(async () => ({
      ok: true,
      json: async () => ({ is_on: true, message: "queued" }),
    }));
    const { result } = renderHook(() => usePumpControl(hookOptions(protectedFetch)));

    await act(async () => {
      await result.current.togglePump("pump1");
    });

    expect(protectedFetch).toHaveBeenCalledWith(`${API}/pump/state`, expect.objectContaining({
      method: "POST",
    }));
    expect(JSON.parse(protectedFetch.mock.calls[0][1].body)).toMatchObject({
      pump_id: "pump1",
      on: true,
      device_id: "ccdev_test",
    });
  });

  it("updates optimistically then rolls back on error", async () => {
    let rejectFetch;
    const protectedFetch = vi.fn(() => new Promise((_resolve, reject) => {
      rejectFetch = reject;
    }));
    const { result } = renderHook(() => usePumpControl(hookOptions(protectedFetch)));

    let togglePromise;
    act(() => {
      togglePromise = result.current.togglePump("pump1");
    });

    expect(result.current.pumps.pump1.on).toBe(true);

    await act(async () => {
      rejectFetch(new Error("network failed"));
      await togglePromise;
    });

    // Failed pump commands restore the previous UI state immediately.
    expect(result.current.pumps.pump1.on).toBe(false);
  });
});
