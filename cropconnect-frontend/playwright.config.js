import { defineConfig } from "@playwright/test";

// Install browsers once with: npx playwright install chromium

export default defineConfig({
  testDir: "./e2e",
  workers: process.env.CI ? 1 : undefined,
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || "http://localhost:3000",
    headless: true,
    screenshot: "only-on-failure",
  },
});
