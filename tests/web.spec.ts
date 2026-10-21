/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * variables: errors@L23; download@L74; locations@L98; unreachable@L100; locations@L119; locations@L140
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

test("real static review lists auxiliary-file locations and unused code", async ({ page }) => {
  /** Real API, inert upload; this is not a mocked worker/coverage acceptance test. */
  await page.locator('input[type="file"]').setInputFiles([
    { name: "helper.py", mimeType: "text/plain", buffer: Buffer.from("import math\ndef unused():\n    leftover = 1\n    return 7\n    print('never')\n") },
  ]);
  await page.getByRole("button", { name: "Static review · no execution", exact: true }).click();
  const locations = page.getByRole("region", { name: "Located diagnostics" });
  await expect(locations.getByRole("row").filter({ hasText: "PY-UNUSED-IMPORT" })).toContainText("helper.py");
  const unreachable = locations.getByRole("row").filter({ hasText: "PY-UNREACHABLE" });
  await expect(unreachable.getByRole("cell").nth(0)).toHaveText("helper.py");
  await expect(unreachable.getByRole("cell").nth(1)).toHaveText("5");
  await expect(locations).toContainText("Not measured");
});

test("coverage and unknown failures render accurately from report contract", async ({ page }) => {
  /** UI-only fixture; genuine coverage/runtime acceptance is separately verified by isolated workers. */
  await page.route("**/api/review", async (route) => route.fulfill({
    json: {
      static: { findings: [{ file: "helper.py", line: 2, message: "<script>inert</script>", code: "FIXTURE" }] },
      unlocated_failures: [{ stage: "case:wrong-answer", reason: "No root-cause line inferred." }],
      coverage: { status: "measured", files: {
        "helper.py": { status: "measured", missing_lines: [3, 7], missing_branches: [[2, 3], [7, -1]] },
        "unknown.py": { status: "not-measured", reason: "No coverage record" },
      } },
    },
  }));
  await page.getByRole("button", { name: "Static review · no execution", exact: true }).click();
  const locations = page.getByRole("region", { name: "Located diagnostics" });
  await expect(locations).toContainText("Uncovered lines: 3, 7");
  await expect(locations).toContainText("2 → 3, 7 → exit(-1)");
  await expect(locations).toContainText("No coverage record");
  await expect(locations).toContainText("No root-cause line inferred");
  await expect(locations).toContainText("<script>inert</script>");
  await expect(locations.locator("script")).toHaveCount(0);
  await page.setViewportSize({ width: 390, height: 844 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});

test("native coverage semantics and blocked unused tools stay visible", async ({ page }) => {
  /** UI fixture only; native collector accuracy is asserted independently by real worker scenarios. */
  await page.route("**/api/review", async route => route.fulfill({ json: {
    diagnostics: [{ file: "Main.java", line: 6, column: 9, code: "UnusedLocalVariable", stage: "unused-code", message: "Review leftover" }],
    unused: { status: "blocked", tool: "Fixture unavailable tool", reason: "Timeout is not a pass" },
    coverage: { status: "partial", tool: "JaCoCo", metric: "jacoco-instruction-backed-line", files: {
      "Main.java": { status: "measured", metric: "jacoco-instruction-backed-line", missing_lines: [3], branch_points: [{ line: 7, missing: 1, covered: 1, kind: "jacoco-branch-count" }] },
    } },
  } }));
  await page.getByRole("button", { name: "Static review · no execution", exact: true }).click();
  const locations = page.getByRole("region", { name: "Located diagnostics" });
  await expect(locations.getByRole("row").filter({hasText: "UnusedLocalVariable"}).getByRole("cell").nth(1)).toHaveText("6");
  await expect(locations).toContainText("Timeout is not a pass");
  await expect(locations).toContainText("partial");
  await expect(locations).toContainText("Uncovered lines: 3");
  await expect(locations).toContainText("jacoco-branch-count");
  await expect(locations).toContainText("not destination lines");
});
