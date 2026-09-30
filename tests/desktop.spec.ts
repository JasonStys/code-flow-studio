/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * variables: app@L14; page@L19
 * </code-map> */

/** Verify the actual Electron shell and bundled Python service, without faking readiness.
 * Symbol locations: docs/code-index.md.
 */
import { test, expect, _electron as electron } from "@playwright/test";

test("bundled desktop launches a sandboxed working editor", async () => {
  /** Native renderer and bundled service both start without a separately installed Python runtime. */
  const app = await electron.launch({
    args: ["."],
    env: { ...process.env, STUDIO_DESKTOP_TEST: "1" },
  });
  try {
    const page = await app.firstWindow();
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
  } finally {
    await app.close();
  }
});
