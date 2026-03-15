import { defineConfig, devices } from '@playwright/test'

const baseURL = process.env.BASE_URL ?? process.env.E2E_BASE_URL ?? 'http://localhost:3000'

export default defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1,
  reporter: 'html',
  use: {
    baseURL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'on-first-retry',
  },
  timeout: 30_000,
  expect: {
    timeout: 15_000,
  },
  projects: [
    {
      name: 'e2e',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})
