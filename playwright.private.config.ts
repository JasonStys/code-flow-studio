/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * </code-map> */

/** Jason Stys: isolated test-only account website; never reuse a real user's service/data. */
import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "tests",
  testMatch: "private.spec.ts",
  workers: 1,
  timeout: 60000,
  use: { baseURL: "http://127.0.0.1:8077", trace: "off" },
  projects: [
    { name: "chromium", use: { browserName: "chromium" } },
    { name: "firefox", use: { browserName: "firefox" } },
    { name: "webkit", use: { browserName: "webkit" } },
  ],
  webServer: {
    command: "python -m studio.private_cli --port 8077 --no-browser",
    url: "http://127.0.0.1:8077/health",
    timeout: 60000,
    reuseExistingServer: false,
    env: { CFS_ACCOUNT_DATA: "runtime/private-browser-" + Date.now() },
  },
});
