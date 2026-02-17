import { defineConfig, devices } from '@playwright/test';
import { BASE_URL } from './helpers/env';

export default defineConfig({
  globalSetup: './global-setup.ts',
  globalTeardown: './global-teardown.ts',
  testDir: './specs',
  fullyParallel: true,
  workers: process.env.CI ? 2 : 4,
  retries: process.env.CI ? 2 : 0,

  globalTimeout: 5 * 60 * 1000,
  timeout: 30_000,
  expect: {
    timeout: 5_000,
  },

  reporter: [
    ['html', { open: 'never' }],
    ['list'],
  ],

  use: {
    baseURL: BASE_URL,
    trace: 'off',
    screenshot: 'only-on-failure',
    video: 'off',
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
