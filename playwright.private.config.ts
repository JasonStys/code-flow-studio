/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * variables: port@L9
 * </code-map> */

/** Jason Stys: isolated test-only account website; never reuse a real user's service/data. */
import { defineConfig } from "@playwright/test";
const port = Number(process.env.CFS_PRIVATE_TEST_PORT ?? 8077);
if (!Number.isSafeInteger(port) || port < 1024 || port > 65535)
  throw new Error("Invalid CFS_PRIVATE_TEST_PORT");
export default defineConfig({
  testDir: "tests",
  outputDir: "test-results/private",
  testMatch: "private.spec.ts",
  workers: 1,
  timeout: 60000,
  use: { baseURL: `http://127.0.0.1:${port}`, trace: "off" },
  projects: [
    { name: "chromium", use: { browserName: "chromium" } },
    { name: "firefox", use: { browserName: "firefox" } },
    { name: "webkit", use: { browserName: "webkit" } },
  ],
  webServer: {
    command: `python -m studio.private_cli --port ${port} --no-browser`,
    url: `http://127.0.0.1:${port}/health`,
    timeout: 60000,
    reuseExistingServer: false,
    env: { CFS_ACCOUNT_DATA: "runtime/private-browser-" + Date.now() },
  },
});
