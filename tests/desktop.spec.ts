/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * variables: app@L18; page@L28
 * </code-map> */

/** Verify the actual Electron shell and bundled Python service, without faking readiness.
 * Symbol locations: docs/code-index.md.
 */
import { test, expect, _electron as electron } from "@playwright/test";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { createSession, editorJourney } from "./account-session";

test("bundled desktop authenticates, seals history and provides a sandboxed editor", async () => {
  /** Native renderer and bundled service both start without a separately installed Python runtime. */
  const app = await electron.launch({
    executablePath: process.env.STUDIO_INSTALLED_APP,
    args: process.env.STUDIO_INSTALLED_APP ? [] : ["."],
    env: {
      ...process.env,
      STUDIO_DESKTOP_TEST: "1",
      CFS_ACCOUNT_DATA: mkdtempSync(join(tmpdir(), "code-flow-native-test-")),
    },
  });
  try {
    const page = await app.firstWindow();
    await createSession(page, "native_fictional");
    await editorJourney(page);
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
