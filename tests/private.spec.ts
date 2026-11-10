/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * variables: external@L15; origin@L16; url@L20; downloaded@L37; external@L109; origin@L110; release@L143; held@L144; ready@L147; received@L148; response@L152; creating@L157
 * </code-map> */

/** Jason Stys: private website journeys, owner isolation, downloads and no unsolicited external requests. */
import { test, expect } from "@playwright/test";
import { createSession, editorJourney } from "./account-session";
import { inspectHelper } from "./source-journey";

test("real account editor locks, reopens history and downloads encrypted bytes", async ({
  page,
}) => {
  const external: string[] = [];
  const origin = new URL(
    test.info().project.use.baseURL ?? "http://127.0.0.1:8077",
  ).origin;
  page.on("request", (request) => {
    const url = request.url();
    if (/^https?:/.test(url) && new URL(url).origin !== origin)
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

test("private exact-source inspection sends no external requests and disappears on lock", async ({
  page,
}) => {
  const external: string[] = [];
  const origin = new URL(
    test.info().project.use.baseURL ?? "http://127.0.0.1:8077",
  ).origin;
  page.on("request", (request) => {
    if (
      /^https?:/.test(request.url()) &&
      new URL(request.url()).origin !== origin
    )
      external.push(request.url());
  });
  await page.goto("/");
  await createSession(
    page,
    "navigate_" + test.info().project.name.replace(/-/g, "_"),
  );
  await inspectHelper(page);
  await page
    .getByRole("button", { name: "Lock workspace", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Unlock your private code workspace" }),
  ).toBeVisible();
  await expect(
    page.getByRole("region", { name: "Evidence source inspector" }),
  ).toHaveCount(0);
  expect(external).toEqual([]);
});

test("account helper observes genuine unlock completion before checking the rendered workspace", async ({
  page,
}) => {
  /** Hold a real accepted response, prove the UI is still busy/locked, then release without sleeps or retries. */
  await page.goto("/");
  let release!: () => void;
  const held = new Promise<void>((resolve) => {
    release = resolve;
  });
  let ready!: () => void;
  const received = new Promise<void>((resolve) => {
    ready = resolve;
  });
  await page.route("**/private/unlock", async (route) => {
    const response = await route.fetch();
    ready();
    await held;
    await route.fulfill({ response });
  });
  const creating = createSession(page, "staged_" + test.info().project.name);
  try {
    await received;
    await expect(
      page.getByRole("heading", { name: "Unlock your private code workspace" }),
    ).toBeVisible();
    await expect(
      page.getByRole("button", {
        name: "Unlock or create workspace",
        exact: true,
      }),
    ).toBeDisabled();
    await expect(
      page.getByRole("heading", { name: "Make your next iteration count." }),
    ).toHaveCount(0);
  } finally {
    release();
  }
  await creating;
  await page
    .getByRole("button", { name: "Lock workspace", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Unlock your private code workspace" }),
  ).toBeVisible();
});
