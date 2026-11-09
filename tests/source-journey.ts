/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * types: Page@L14
 * functions: inspectHelper(page: Page)@L20
 * variables: inertHelper@L16; locations@L31; inspector@L52; source@L57
 * </code-map> */

/**
 * Synthetic source-inspection journeys by Jason Stys, shared by legacy and private account UI tests.
 * Inputs are inert Python text; real static analysis produces content-bound references without execution.
 * Exact fixture and function declarations are generated in docs/code-index.md.
 */
import { expect, type Page } from "@playwright/test";

export const inertHelper =
  "import math\n\ndef unused_helper():\n    leftover = 1\n    return 7\n    print('never')\n";

/** Upload an auxiliary source and inspect a real independently located unreachable statement. */
export async function inspectHelper(page: Page) {
  await page.locator('input[type="file"]').setInputFiles([
    {
      name: "helper.py",
      mimeType: "text/plain",
      buffer: Buffer.from(inertHelper),
    },
  ]);
  await page
    .getByRole("button", { name: "Static review · no execution", exact: true })
    .click();
  const locations = page.getByRole("region", { name: "Located diagnostics" });
  await locations
    .getByLabel("Evidence file", { exact: true })
    .selectOption("helper.py");
  await locations
    .getByLabel("Finding category", { exact: true })
    .selectOption("unused");
  await expect(
    locations.getByRole("row").filter({ hasText: "PY-UNUSED-IMPORT" }),
  ).toContainText("helper.py");
  await expect(
    locations.getByRole("row").filter({ hasText: "PY-UNREACHABLE" }),
  ).toHaveCount(0);
  await locations
    .getByLabel("Finding category", { exact: true })
    .selectOption("all");
  await locations
    .getByRole("row")
    .filter({ hasText: "PY-UNREACHABLE" })
    .getByRole("button", { name: "Inspect source helper.py:6", exact: true })
    .click();
  const inspector = page.getByRole("region", {
    name: "Evidence source inspector",
  });
  await expect(inspector).toContainText("helper.py:6");
  await expect(inspector).toContainText("Current draft matches");
  const source = inspector.getByRole("textbox", {
    name: "Verified evidence source",
    exact: true,
  });
  await expect(source).toBeVisible();
  await expect(source).toHaveValue(inertHelper);
  await expect
    .poll(() =>
      source.evaluate((target: HTMLTextAreaElement) =>
        target.value.slice(target.selectionStart, target.selectionEnd),
      ),
    )
    .toBe("    print('never')");
  await expect(inspector.locator(".monaco-editor")).toHaveCount(0);
  return inspector;
}
