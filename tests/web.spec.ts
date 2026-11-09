/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * types: Page@L11
 * variables: browserEvidence@L16; evidence@L22; evidence@L40; timer@L43; state@L44; errors@L88; download@L139; locations@L173; unreachable@L177; locations@L231; locations@L294; inspector@L312; sourceInput@L313; editor@L341; invalid@L369; digest@L370; locations@L398; inspector@L403; legacy@L443; project@L445; locations@L468; inspector@L475; source@L515; generated@L516; project@L518; inspector@L547; cycle@L550; artifact@L551; view@L561
 * </code-map> */

/** Real browser flows; controller success does not substitute for isolated worker evidence.
 * Symbols/variables: docs/code-index.md.
 */
import { test, expect, type Page } from "@playwright/test";
import { createHash } from "node:crypto";
import { inspectHelper, inertHelper } from "./source-journey";

/** Keep bounded synthetic-journey failures readable even when optional CI artifact uploads are off. */
const browserEvidence = new WeakMap<
  Page,
  { errors: string[]; events: string[] }
>();

test.beforeEach(async ({ page }) => {
  const evidence = { errors: [] as string[], events: [] as string[] };
  browserEvidence.set(page, evidence);
  page.on("pageerror", (error) => {
    if (evidence.errors.length < 8)
      evidence.errors.push(error.message.slice(0, 512));
  });
  page.on("crash", () => evidence.events.push("renderer crashed"));
  page.on("framenavigated", (frame) => {
    if (frame === page.mainFrame() && evidence.events.length < 12)
      evidence.events.push(`main frame: ${new URL(frame.url()).pathname}`);
  });
  await page.goto("/#token=browser-test-token-not-production-000000000000");
  await expect(
    page.getByRole("heading", { name: "Make your next iteration count." }),
  ).toBeVisible();
});

test.afterEach(async ({ page }, testInfo) => {
  const evidence = browserEvidence.get(page);
  if (testInfo.status !== testInfo.expectedStatus) {
    // Log only bounded state from these synthetic fixtures, never account tokens or source contents.
    let timer: ReturnType<typeof setTimeout> | undefined;
    const state = await Promise.race([
      page
        .evaluate(() => ({
          title: document.title,
          heading: document
            .querySelector("main h2")
            ?.textContent?.slice(0, 160),
          locatedRegions: document.querySelectorAll(
            '[aria-label="Located diagnostics"]',
          ).length,
          locatedText: document
            .querySelector('[aria-label="Located diagnostics"]')
            ?.textContent?.slice(0, 2000),
          rootChildren: document.getElementById("root")?.childElementCount,
        }))
        .catch((error: Error) => ({
          unavailable: error.message.slice(0, 160),
        })),
      new Promise((resolve) => {
        timer = setTimeout(
          () =>
            resolve({
              unavailable: "renderer did not answer bounded diagnostic probe",
            }),
          1000,
        );
      }),
    ]);
    clearTimeout(timer);
    console.error(
      "BROWSER_FAILURE_STATE",
      JSON.stringify({ ...evidence, state }),
    );
  }
  expect(
    evidence?.errors ?? [],
    "The complete user journey must not raise unhandled browser errors",
  ).toEqual([]);
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
  await expect(
    page.getByRole("alert", { name: "Workspace error" }),
  ).toContainText("No AI provider configured");
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

test("real static review lists auxiliary-file locations and unused code", async ({
  page,
}) => {
  /** Real API, inert upload; this is not a mocked worker/coverage acceptance test. */
  await page.locator('input[type="file"]').setInputFiles([
    {
      name: "helper.py",
      mimeType: "text/plain",
      buffer: Buffer.from(
        "import math\ndef unused():\n    leftover = 1\n    return 7\n    print('never')\n",
      ),
    },
  ]);
  await page
    .getByRole("button", { name: "Static review · no execution", exact: true })
    .click();
  const locations = page.getByRole("region", { name: "Located diagnostics" });
  await expect(
    locations.getByRole("row").filter({ hasText: "PY-UNUSED-IMPORT" }),
  ).toContainText("helper.py");
  const unreachable = locations
    .getByRole("row")
    .filter({ hasText: "PY-UNREACHABLE" });
  await expect(unreachable.getByRole("cell").nth(0)).toHaveText("helper.py");
  await expect(unreachable.getByRole("cell").nth(1)).toHaveText("5");
  await expect(locations).toContainText("Not measured");
});

test("coverage and unknown failures render accurately from report contract", async ({
  page,
}) => {
  /** UI-only fixture; genuine coverage/runtime acceptance is separately verified by isolated workers. */
  await page.route("**/api/review", async (route) =>
    route.fulfill({
      json: {
        static: {
          findings: [
            {
              file: "helper.py",
              line: 2,
              message: "<script>inert</script>",
              code: "FIXTURE",
            },
          ],
        },
        unlocated_failures: [
          {
            stage: "case:wrong-answer",
            reason: "No root-cause line inferred.",
          },
        ],
        coverage: {
          status: "measured",
          files: {
            "helper.py": {
              status: "measured",
              missing_lines: [3, 7],
              missing_branches: [
                [2, 3],
                [7, -1],
              ],
            },
            "unknown.py": {
              status: "not-measured",
              reason: "No coverage record",
            },
          },
        },
      },
    }),
  );
  await page
    .getByRole("button", { name: "Static review · no execution", exact: true })
    .click();
  const locations = page.getByRole("region", { name: "Located diagnostics" });
  await expect(locations).toContainText("Uncovered lines: 3, 7");
  await expect(locations).toContainText("2 → 3, 7 → exit(-1)");
  await expect(locations).toContainText("No coverage record");
  await expect(locations).toContainText("No root-cause line inferred");
  await expect(locations).toContainText("<script>inert</script>");
  await expect(locations.locator("script")).toHaveCount(0);
  await page.setViewportSize({ width: 390, height: 844 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
});

test("native coverage semantics and blocked unused tools stay visible", async ({
  page,
}) => {
  /** UI fixture only; native collector accuracy is asserted independently by real worker scenarios. */
  await page.route("**/api/review", async (route) =>
    route.fulfill({
      json: {
        diagnostics: [
          {
            file: "Main.java",
            line: 6,
            column: 9,
            code: "UnusedLocalVariable",
            stage: "unused-code",
            message: "Review leftover",
          },
        ],
        unused: {
          status: "blocked",
          tool: "Fixture unavailable tool",
          reason: "Timeout is not a pass",
        },
        coverage: {
          status: "partial",
          tool: "JaCoCo",
          metric: "jacoco-instruction-backed-line",
          files: {
            "Main.java": {
              status: "measured",
              metric: "jacoco-instruction-backed-line",
              missing_lines: [3],
              branch_points: [
                {
                  line: 7,
                  missing: 1,
                  covered: 1,
                  kind: "jacoco-branch-count",
                },
              ],
            },
          },
        },
      },
    }),
  );
  await page
    .getByRole("button", { name: "Static review · no execution", exact: true })
    .click();
  const locations = page.getByRole("region", { name: "Located diagnostics" });
  await expect(
    locations
      .getByRole("row")
      .filter({ hasText: "UnusedLocalVariable" })
      .getByRole("cell")
      .nth(1),
  ).toHaveText("6");
  await expect(locations).toContainText("Timeout is not a pass");
  await expect(locations).toContainText("partial");
  await expect(locations).toContainText("Uncovered lines: 3");
  await expect(locations).toContainText("jacoco-branch-count");
  await expect(locations).toContainText("not destination lines");
});

test("developer inspects exact source, edits only a matching draft and retains the historical snapshot", async ({
  page,
}) => {
  const inspector = await inspectHelper(page);
  const sourceInput = inspector.getByRole("textbox", {
    name: "Verified evidence source",
    exact: true,
  });
  await sourceInput.focus();
  await sourceInput.press("ControlOrMeta+Home");
  await page.keyboard.type("SHOULD_NOT_APPEAR");
  await expect(sourceInput).toHaveValue(inertHelper);
  expect(
    await sourceInput.evaluate(
      (target: HTMLTextAreaElement) => target.readOnly,
    ),
  ).toBe(true);
  await inspector
    .getByLabel("Browse snapshot line", { exact: true })
    .fill("999");
  await inspector
    .getByRole("button", { name: "Go to snapshot line", exact: true })
    .click();
  await expect(inspector.getByRole("alert")).toContainText("physical line");
  await inspector.getByLabel("Browse snapshot line", { exact: true }).fill("6");
  await inspector
    .getByRole("button", { name: "Go to snapshot line", exact: true })
    .click();
  await expect(inspector.getByRole("alert")).toHaveCount(0);
  await inspector
    .getByRole("button", { name: "Edit matching draft at line 6", exact: true })
    .click();
  const editor = page.getByRole("textbox", {
    name: "Project source editor",
    exact: true,
  });
  await expect(editor).toBeFocused();
  await expect(
    page.getByRole("button", { name: "helper.py", exact: true }),
  ).toHaveClass("selected");
  await editor.press("ControlOrMeta+Home");
  await page.keyboard.type("# newer draft\n");
  await expect(page.locator(".monaco-editor")).toContainText("newer draft");
  await page.getByRole("button", { name: "Run evidence", exact: true }).click();
  await expect(inspector).toContainText("Current draft differs");
  await expect(
    inspector.getByRole("button", {
      name: "Edit matching draft at line 6",
      exact: true,
    }),
  ).toBeDisabled();
  await expect(sourceInput).toHaveValue(inertHelper);
  await page.getByRole("button", { name: "Workspace", exact: true }).click();
  await expect(page.locator(".monaco-editor")).toContainText("newer draft");
});

test("coverage links verify bytes while mismatched and out-of-range references fail closed", async ({
  page,
}) => {
  /** UI-contract fixture only; real collector/toolchain accuracy remains in isolated-worker acceptance. */
  let invalid: "none" | "hash" | "line" = "none";
  const digest = createHash("sha256").update(inertHelper).digest("hex");
  await page.locator('input[type="file"]').setInputFiles([
    {
      name: "helper.py",
      mimeType: "text/plain",
      buffer: Buffer.from(inertHelper),
    },
  ]);
  await page.route("**/api/review", async (route) =>
    route.fulfill({
      json: {
        coverage: {
          status: "measured",
          tool: "UI fixture",
          files: {
            "helper.py": {
              status: "measured",
              source_sha256: invalid === "hash" ? "0".repeat(64) : digest,
              missing_lines: [invalid === "line" ? 999 : 4],
            },
          },
        },
      },
    }),
  );
  await page
    .getByRole("button", { name: "Static review · no execution", exact: true })
    .click();
  const locations = page.getByRole("region", { name: "Located diagnostics" });
  await locations
    .locator(".coverage-file")
    .getByRole("button", { name: "Inspect source helper.py:4", exact: true })
    .click();
  const inspector = page.getByRole("region", {
    name: "Evidence source inspector",
  });
  await expect(inspector).toContainText("helper.py:4");
  await expect(inspector).toContainText("Current draft matches");
  await inspector
    .getByRole("button", { name: "Close source inspector", exact: true })
    .click();
  await page.getByRole("button", { name: "Workspace", exact: true }).click();
  invalid = "hash";
  await page
    .getByRole("button", { name: "Static review · no execution", exact: true })
    .click();
  await locations
    .locator(".coverage-file")
    .getByRole("button", { name: "Inspect source helper.py:4", exact: true })
    .click();
  await expect(inspector.getByRole("alert")).toContainText(
    "fingerprint mismatch",
  );
  await expect(inspector.locator(".monaco-editor")).toHaveCount(0);
  await inspector
    .getByRole("button", { name: "Close source inspector", exact: true })
    .click();
  await page.getByRole("button", { name: "Workspace", exact: true }).click();
  invalid = "line";
  await page
    .getByRole("button", { name: "Static review · no execution", exact: true })
    .click();
  await locations
    .locator(".coverage-file")
    .getByRole("button", { name: "Inspect source helper.py:999", exact: true })
    .click();
  await expect(inspector.getByRole("alert")).toContainText("outside");
});

test("generated artifacts remain distinct and legacy locations never gain guessed links", async ({
  page,
}) => {
  /** Generated text comes only from the reviewed manifest; no arbitrary artifact path is fetched. */
  let legacy = false;
  await page.route("**/api/review", async (route) => {
    const project = route.request().postDataJSON();
    await route.fulfill({
      json: {
        diagnostics: legacy
          ? [{ file: "main.py", line: 1, message: "Legacy reference" }]
          : [
              {
                file: "test_generated.py",
                line: 2,
                source_sha256: createHash("sha256")
                  .update(project.tests)
                  .digest("hex"),
                artifact: "generated",
                stage: "generated-tests",
                message: "Generated test fixture",
              },
            ],
      },
    });
  });
  await page
    .getByRole("button", { name: "Static review · no execution", exact: true })
    .click();
  const locations = page.getByRole("region", { name: "Located diagnostics" });
  await locations
    .getByRole("button", {
      name: "Inspect generated test_generated.py:2",
      exact: true,
    })
    .click();
  const inspector = page.getByRole("region", {
    name: "Evidence source inspector",
  });
  await expect(inspector).toContainText("Generated harness/test artifact");
  await expect(
    inspector.getByRole("button", {
      name: "Edit matching draft at line 2",
      exact: true,
    }),
  ).toBeDisabled();
  await inspector
    .getByRole("button", { name: "Close source inspector", exact: true })
    .click();
  await page.getByRole("button", { name: "Workspace", exact: true }).click();
  legacy = true;
  await page
    .getByRole("button", { name: "Static review · no execution", exact: true })
    .click();
  await expect(
    locations
      .getByRole("row")
      .filter({ hasText: "Legacy reference" })
      .getByRole("cell")
      .nth(1),
  ).toHaveText("1");
  await expect(
    locations.getByRole("button", { name: /Inspect source/ }),
  ).toHaveCount(0);
  await page.setViewportSize({ width: 390, height: 844 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
});

test("repeated generated and source inspection releases the read-only view without editor models", async ({
  page,
}) => {
  /** Exercise 32 real mount/close cycles; no retries or browser-process restart hides a lifecycle failure. */
  let source = "";
  let generated = "";
  await page.route("**/api/review", async (route) => {
    const project = route.request().postDataJSON();
    source = project.files.find(
      (file: { name: string }) => file.name === project.entry,
    ).content;
    generated = project.tests;
    await route.fulfill({
      json: {
        diagnostics: [
          {
            file: project.entry,
            line: 1,
            source_sha256: createHash("sha256").update(source).digest("hex"),
            artifact: "source",
            message: "Original source fixture",
          },
          {
            file: "test_generated.py",
            line: 2,
            source_sha256: createHash("sha256").update(generated).digest("hex"),
            artifact: "generated",
            message: "Generated fixture",
          },
        ],
      },
    });
  });
  await page
    .getByRole("button", { name: "Static review · no execution", exact: true })
    .click();
  const inspector = page.getByRole("region", {
    name: "Evidence source inspector",
  });
  for (let cycle = 0; cycle < 16; cycle += 1) {
    for (const artifact of ["source", "generated"]) {
      await page
        .getByRole("button", {
          name:
            artifact === "source"
              ? "Inspect source main.py:1"
              : "Inspect generated test_generated.py:2",
          exact: true,
        })
        .click();
      const view = inspector.getByRole("textbox", {
        name: "Verified evidence source",
        exact: true,
      });
      await expect(view).toHaveValue(
        artifact === "source" ? source : generated,
      );
      await expect
        .poll(() =>
          view.evaluate((input: HTMLTextAreaElement) =>
            input.value.slice(input.selectionStart, input.selectionEnd),
          ),
        )
        .toBe(
          (artifact === "source" ? source : generated).split("\n")[
            artifact === "source" ? 0 : 1
          ],
        );
      await expect(page.locator(".monaco-editor")).toHaveCount(0);
      await expect(view).toHaveCount(1);
      await inspector
        .getByRole("button", { name: "Close source inspector", exact: true })
        .click();
      await expect(inspector).toHaveCount(0);
      await expect(
        page.getByRole("textbox", {
          name: "Verified evidence source",
          exact: true,
        }),
      ).toHaveCount(0);
    }
  }
});
