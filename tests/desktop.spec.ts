/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * variables: { verifyElectron }@L17; executable@L23; app@L25; resources@L40; file@L41; page@L65; health@L66
 * </code-map> */

/** Verify the actual Electron shell and bundled Python service, without faking readiness.
 * Symbol locations: docs/code-index.md.
 */
import { test, expect, _electron as electron } from "@playwright/test";
import { mkdtempSync, existsSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { createRequire } from "node:module";
import { createSession, editorJourney } from "./account-session";
import { inspectHelper } from "./source-journey";
const { verifyElectron } = createRequire(import.meta.url)(
  "../scripts/verify_electron.cjs",
);

test("bundled desktop authenticates, seals history and provides a sandboxed editor", async () => {
  /** Native renderer and bundled service both start without a separately installed Python runtime. */
  const executable =
    process.env.STUDIO_INSTALLED_APP ?? verifyElectron().executable;
  const app = await electron.launch({
    executablePath: executable,
    args: process.env.STUDIO_INSTALLED_APP ? [] : ["."],
    env: {
      ...process.env,
      STUDIO_DESKTOP_TEST: "1",
      CFS_ACCOUNT_DATA: mkdtempSync(join(tmpdir(), "code-flow-native-test-")),
    },
  });
  try {
    expect(await app.evaluate(({ app }) => app.getPath("userData"))).toContain(
      "code-flow-launcher-test-",
    );
    if (process.env.STUDIO_INSTALLED_APP) {
      // Inspect the actual packaged resources, not the repository or mocked build configuration.
      const resources = await app.evaluate(() => process.resourcesPath);
      for (const file of [
        "Dockerfile",
        "worker.py",
        "language_checks.py",
        "node_checks.cjs",
        "sql_runtime.py",
        "php_coverage.php",
        "bash_coverage.sh",
        "java-unused.xml",
        "tools/package.json",
        "tools/package-lock.json",
      ]) {
        expect(
          existsSync(join(resources, "runner", file)),
          `Bundled worker resource: ${file}`,
        ).toBe(true);
      }
      expect(
        readFileSync(join(resources, "runner", "bash_coverage.sh"), "utf8"),
      ).not.toContain("\r");
      expect(
        existsSync(join(resources, "runner", "tools", "node_modules")),
      ).toBe(false);
    }
    const page = await app.firstWindow();
    const health = await page.request.get(new URL("/health", page.url()).href);
    expect((await health.json()).version).toBe("0.4.0");
    await createSession(page, "native_fictional");
    await editorJourney(page);
    await inspectHelper(page);
    await page.getByRole("button", { name: "Workspace", exact: true }).click();
    await expect(
      page.getByRole("heading", { name: "Make your next iteration count." }),
    ).toBeVisible();
    await expect(page.locator(".monaco-editor")).toBeVisible();
    expect(await page.evaluate(() => typeof (window as any).require)).toBe(
      "undefined",
    );
    expect(await page.evaluate(() => typeof (window as any).process)).toBe(
      "undefined",
    );
    await page.getByRole("button", { name: "Test catalog" }).click();
    await expect(page.locator(".catalog-grid article")).toHaveCount(48);
    await page.getByRole("button", { name: "Workspace", exact: true }).click();
    expect(new URL(page.url()).hash).toBe("");
    expect(
      await page.evaluate(() => localStorage.length + sessionStorage.length),
    ).toBe(0);
    await page.screenshot({
      path: "artifacts/desktop-workspace.png",
      fullPage: true,
    });
    await page
      .getByRole("button", { name: "Lock workspace", exact: true })
      .click();
    await expect(
      page.getByRole("heading", { name: "Unlock your private code workspace" }),
    ).toBeVisible();
  } finally {
    await app.close();
  }
});
