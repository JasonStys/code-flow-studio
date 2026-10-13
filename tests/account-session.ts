/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * types: Page@L9
 * functions: createSession(page: Page, alias: string)@L12; editorJourney(page: Page)@L40
 * </code-map> */

/** Jason Stys: reusable actual browser/native account journey; credentials and code are disposable fixtures. */
import { expect, type Page } from "@playwright/test";

/** Create an empty account and prove its vault phrase through WebCrypto and the real service. */
export async function createSession(page: Page, alias: string) {
  await page
    .getByRole("button", { name: "Create account", exact: true })
    .click();
  await page.getByLabel("Account alias").fill(alias);
  await page
    .getByLabel("Login password", { exact: true })
    .fill("fictional-browser-password-2026");
  await page
    .getByRole("button", { name: "Register account", exact: true })
    .click();
  await expect(page.locator("#recovery-code")).toBeVisible();
  await page
    .getByRole("button", { name: "I saved it privately", exact: true })
    .click();
  await page
    .getByLabel("Vault phrase")
    .fill("fictional six word vault phrase example 2026");
  await page
    .getByRole("button", { name: "Unlock or create workspace", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Make your next iteration count." }),
  ).toBeVisible();
  await expect(page.locator(".monaco-editor")).toBeVisible();
}

/** Validate real non-executing source/history/export controls; never represent static metrics as compiler evidence. */
export async function editorJourney(page: Page) {
  await page
    .getByLabel("Project", { exact: true })
    .fill("Fictional private project");
  await page
    .getByRole("button", { name: "Save revision only", exact: true })
    .click();
  await expect(page.locator(".rail-history button").first()).toContainText(
    "Fictional private project",
  );
  await page
    .getByRole("button", { name: "Static review · no execution", exact: true })
    .click();
  await expect(
    page.getByRole("heading", {
      name: "Static review — code was not executed",
    }),
  ).toBeVisible();
  await expect(page.locator(".evidence").first()).toContainText(
    '"executed": false',
  );
  await page.getByRole("button", { name: "Test catalog", exact: true }).click();
  await expect(page.locator(".catalog-grid article")).toHaveCount(48);
  await page.getByRole("button", { name: "Workspace", exact: true }).click();
}
