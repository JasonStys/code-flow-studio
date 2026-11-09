/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * variables: port@L10
 * </code-map> */

/** Three-engine web smoke and interaction tests. Symbols: docs/code-index.md. */
import { defineConfig } from "@playwright/test";

const port = Number(process.env.CFS_WEB_TEST_PORT ?? 8013);
if (!Number.isSafeInteger(port) || port < 1024 || port > 65535)
  throw new Error("Invalid CFS_WEB_TEST_PORT");

export default defineConfig({
  testDir: "tests",
  outputDir: "test-results/web",
  testMatch: ["web.spec.ts", "source-navigation.spec.ts"],
  fullyParallel: false,
  workers: 1,
  use: { baseURL: `http://127.0.0.1:${port}`, trace: "retain-on-failure" },
  projects: [
    { name: "chromium", use: { browserName: "chromium" } },
    { name: "firefox", use: { browserName: "firefox" } },
    { name: "webkit", use: { browserName: "webkit" } },
  ],
  webServer: {
    command: `python -m studio.cli serve --port ${port} --data runtime/browser-tests-${port}`,
    url: `http://127.0.0.1:${port}/health`,
    env: { STUDIO_TOKEN: "browser-test-token-not-production-000000000000" },
    timeout: 30000,
    reuseExistingServer: false,
  },
});
