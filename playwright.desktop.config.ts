/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * types: docs@L3
 * </code-map> */

/** Electron bundled-service launch smoke. Symbols: docs/code-index.md. */
import { defineConfig } from "@playwright/test";
export default defineConfig({
  testDir: "tests",
  testMatch: "desktop.spec.ts",
  workers: 1,
  timeout: 60000,
});
