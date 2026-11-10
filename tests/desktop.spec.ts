/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * variables: { verifyElectron }@L17; executable@L23; app@L26; resources@L45; file@L46; page@L70; browserErrors@L73; health@L77; state@L85; directory@L100; serviceLog@L103; statuses@L104
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
  console.info("NATIVE_JOURNEY_STAGE", "launch:start");
  const app = await electron.launch({
    executablePath: executable,
    args: process.env.STUDIO_INSTALLED_APP ? [] : ["."],
    env: {
      ...process.env,
      STUDIO_DESKTOP_TEST: "1",
      CFS_ACCOUNT_DATA: mkdtempSync(join(tmpdir(), "code-flow-native-test-")),
    },
  });
  console.info("NATIVE_JOURNEY_STAGE", "launch:complete");
  app.process().once("exit", (code, signal) => {
    console.info("NATIVE_PROCESS_EXIT", JSON.stringify({ code, signal }));
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
    page.once("crash", () => console.error("NATIVE_RENDERER_EVENT", "crashed"));
    page.once("close", () => console.info("NATIVE_RENDERER_EVENT", "closed"));
    const browserErrors: string[] = [];
    page.on("pageerror", (error) => {
      if (browserErrors.length < 8) browserErrors.push(error.name);
    });
    const health = await page.request.get(new URL("/health", page.url()).href);
    expect((await health.json()).version).toBe("0.4.0");
    try {
      console.info("NATIVE_JOURNEY_STAGE", "account:start");
      await createSession(page, "native_fictional");
      console.info("NATIVE_JOURNEY_STAGE", "account:complete");
    } catch (error) {
      // Only synthetic test-window state and fixed-route status codes; no keys, request bodies or cookies.
      const state = await page
        .evaluate(() => ({
          heading: document.querySelector("h2")?.textContent?.slice(0, 160),
          notice: document
            .getElementById("account-notice")
            ?.textContent?.slice(0, 250),
          unlockDisabled: (
            document.querySelector(
              'button[type="submit"]',
            ) as HTMLButtonElement | null
          )?.disabled,
        }))
        .catch(() => ({
          unavailable: "native renderer did not provide account state",
        }));
      const directory = await app.evaluate(({ app }) =>
        app.getPath("userData"),
      );
      const serviceLog = join(directory, "service.log");
      const statuses = existsSync(serviceLog)
        ? [
            ...readFileSync(serviceLog, "utf8").matchAll(
              /"(POST|GET) \/(private\/(?:unlock|account|register)|health) HTTP\/1\.1" (\d{3})/g,
            ),
          ]
            .slice(-12)
            .map((match) => ({
              method: match[1],
              route: match[2],
              status: Number(match[3]),
            }))
        : [];
      console.error(
        "NATIVE_ACCOUNT_FAILURE",
        JSON.stringify({ state, browserErrors, statuses }),
      );
      throw error;
    }
    console.info("NATIVE_JOURNEY_STAGE", "editor:start");
    await editorJourney(page);
    console.info("NATIVE_JOURNEY_STAGE", "editor:complete");
    console.info("NATIVE_JOURNEY_STAGE", "source-inspection:start");
    await inspectHelper(page);
    console.info("NATIVE_JOURNEY_STAGE", "source-inspection:complete");
    console.info("NATIVE_JOURNEY_STAGE", "workspace-security:start");
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
    console.info("NATIVE_JOURNEY_STAGE", "workspace-security:complete");
    console.info("NATIVE_JOURNEY_STAGE", "screenshot:start");
    await page.screenshot({
      path: "artifacts/desktop-workspace.png",
      fullPage: true,
    });
    console.info("NATIVE_JOURNEY_STAGE", "screenshot:complete");
    console.info("NATIVE_JOURNEY_STAGE", "lock:start");
    await page
      .getByRole("button", { name: "Lock workspace", exact: true })
      .click();
    await expect(
      page.getByRole("heading", { name: "Unlock your private code workspace" }),
    ).toBeVisible();
    console.info("NATIVE_JOURNEY_STAGE", "lock:complete");
    expect(
      browserErrors,
      "native renderer must not emit JavaScript errors",
    ).toEqual([]);
  } finally {
    console.info("NATIVE_JOURNEY_STAGE", "owned-close:start");
    await app.close();
    console.info("NATIVE_JOURNEY_STAGE", "owned-close:complete");
  }
});
