/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * types: docs@L3
 * </code-map> */

/** Three-engine web smoke and interaction tests. Symbols: docs/code-index.md. */
import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "tests",
  testMatch: "web.spec.ts",
  fullyParallel: false,
  workers: 1,
  use: { baseURL: "http://127.0.0.1:8013", trace: "retain-on-failure" },
  projects: [
    { name: "chromium", use: { browserName: "chromium" } },
    { name: "firefox", use: { browserName: "firefox" } },
    { name: "webkit", use: { browserName: "webkit" } },
  ],
  webServer: {
    command:
      "python -m studio.cli serve --port 8013 --data runtime/browser-tests",
    url: "http://127.0.0.1:8013/health",
    env: { STUDIO_TOKEN: "browser-test-token-not-production-000000000000" },
    timeout: 30000,
    reuseExistingServer: process.env.STUDIO_TEST_REUSE_SERVER === "1",
  },
});
