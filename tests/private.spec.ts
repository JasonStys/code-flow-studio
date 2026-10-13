/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * variables: external@L14; url@L16; downloaded@L33
 * </code-map> */

/** Jason Stys: private website journeys, owner isolation, downloads and no unsolicited external requests. */
import { test, expect } from "@playwright/test";
import { createSession, editorJourney } from "./account-session";

test("real account editor locks, reopens history and downloads encrypted bytes", async ({
  page,
}) => {
  const external: string[] = [];
  page.on("request", (request) => {
    const url = request.url();
    if (/^https?:/.test(url) && !url.startsWith("http://127.0.0.1:8077/"))
      external.push(url);
  });
  await page.goto("/");
  await createSession(
    page,
    "browser_" + test.info().project.name.replace(/-/g, "_"),
  );
  await editorJourney(page);
  expect(
    await page.evaluate(() => ({
      local: localStorage.length,
      session: sessionStorage.length,
      cookie: document.cookie,
    })),
  ).toEqual({ local: 0, session: 0, cookie: "" });
  const downloaded = page.waitForEvent("download");
  await page
    .getByRole("button", { name: "Download encrypted archive", exact: true })
    .click();
  expect((await downloaded).suggestedFilename()).toMatch(/cfsvault$/);
  await page
    .getByRole("button", { name: "Lock workspace", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Unlock your private code workspace" }),
  ).toBeVisible();
  await page
    .getByLabel("Vault phrase")
    .fill("incorrect but long enough vault phrase");
  await page
    .getByRole("button", { name: "Unlock or create workspace", exact: true })
    .click();
  await expect(page.locator("#account-notice")).toContainText("Cannot unlock");
  await page
    .getByLabel("Vault phrase")
    .fill("fictional six word vault phrase example 2026");
  await page
    .getByRole("button", { name: "Unlock or create workspace", exact: true })
    .click();
  await expect(page.locator(".rail-history button").first()).toContainText(
    "Fictional private project",
  );
  await page.locator(".rail-history button").first().click();
  await expect(page.getByLabel("Project", { exact: true })).toHaveValue(
    "Fictional private project",
  );
  await page
    .getByRole("button", { name: "Private AI settings", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Your private AI providers" }),
  ).toBeVisible();
  expect(external).toEqual([]);
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Sign in to your local studio" }),
  ).toBeVisible();
});

test("separate account starts empty and mobile help remains usable", async ({
  page,
}) => {
  await page.goto("/");
  await createSession(
    page,
    "empty_" + test.info().project.name.replace(/-/g, "_"),
  );
  await expect(page.locator(".rail-history button")).toHaveCount(0);
  await page.getByText("Help, privacy & installation", { exact: true }).click();
  await expect(
    page.getByText("Your development loop", { exact: true }),
  ).toBeVisible();
  await page.setViewportSize({ width: 390, height: 844 });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
  await page.getByRole("button", { name: "Sign out", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Sign in to your local studio" }),
  ).toBeVisible();
});
