/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * variables: errors@L23; download@L74
 * </code-map> */

/** Real browser flows; controller success does not substitute for isolated worker evidence.
 * Symbols/variables: docs/code-index.md.
 */
import { test, expect } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  await page.goto("/#token=browser-test-token-not-production-000000000000");
  await expect(
    page.getByRole("heading", { name: "Make your next iteration count." }),
  ).toBeVisible();
});

test("editor, catalog, priorities and source-consent boundaries", async ({
  page,
}, testInfo) => {
  /** Verify the usable interface and explicit no-provider behavior in each engine. */
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(error.message));
  await expect(page.locator(".monaco-editor")).toBeVisible();
  await page.screenshot({
    path: `artifacts/workspace-${testInfo.project.name}.png`,
    fullPage: true,
  });
  await expect(
    page.getByRole("button", { name: "Generate code", exact: true }),
  ).toBeDisabled();
  await page.getByRole("button", { name: "Test catalog" }).click();
  await expect(page.locator(".catalog-grid article")).toHaveCount(48);
  await expect(
    page.getByRole("heading", {
      name: "44 · Hardware-in-the-loop",
      exact: true,
    }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Priorities & AI" }).click();
  await expect(
    page.getByRole("heading", { name: "Optimization priorities" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Workspace", exact: true }).click();
  await page
    .getByLabel(
      "I approve sending this project's text to the configured model.",
    )
    .check();
  await page
    .getByRole("button", { name: "Generate code", exact: true })
    .click();
  await expect(page.getByRole("alert", {name: "Workspace error"})).toContainText(
    "No AI provider configured",
  );
  expect(errors).toEqual([]);
});

test("revision and retained run evidence", async ({ page }) => {
  /** Exercise a real saved run; unavailable Docker must be explicitly blocked, not passed. */
  await page
    .getByRole("button", { name: "Save revision & run checks" })
    .click();
  await expect(page.locator(".metric").first()).not.toContainText("queued", {
    timeout: 30000,
  });
  await expect(page.locator(".evidence")).toContainText("tool_status", {
    timeout: 30000,
  });
  await expect(page.locator(".rail-history button").first()).toContainText(
    "CSV sensor normalizer",
  );
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "ZIP", exact: true }).click();
  expect((await download).suggestedFilename()).toBe("code-flow-evidence.zip");
});

test("mobile layout fits without page overflow", async ({ page }) => {
  /** The web view works on a narrow viewport; this is not native mobile installation proof. */
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(
    page.getByRole("button", { name: "Save revision & run checks" }),
  ).toBeVisible();
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
});
