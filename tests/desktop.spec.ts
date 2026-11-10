/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * variables: { verifyElectron }@L24; { readDiagnosticLog }@L27; executable@L33; app@L36; launcherDirectory@L54; acceptedPackage@L57; resources@L64; file@L65; file@L91; metadata@L103; page@L123; accountStartedAt@L126; accountRoutes@L127; route@L129; route@L141; browserErrors@L153; health@L157; state@L165; directory@L196; serviceLog@L199; statuses@L200; lifecycle@L265; records@L266; launcher@L273; line@L276; service@L281; line@L282; diagnostic@L289; records@L293; stage@L294; record@L306; pid@L319
 * </code-map> */

/** Verify the actual Electron shell and bundled Python service, without faking readiness.
 * Symbol locations: docs/code-index.md.
 */
import { test, expect, _electron as electron } from "@playwright/test";
import {
  mkdtempSync,
  existsSync,
  readFileSync,
  mkdirSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { createRequire } from "node:module";
import { createHash } from "node:crypto";
import { createSession, editorJourney } from "./account-session";
import { inspectHelper } from "./source-journey";
const { verifyElectron } = createRequire(import.meta.url)(
  "../scripts/verify_electron.cjs",
);
const { readDiagnosticLog } = createRequire(import.meta.url)(
  "./native-diagnostics.cjs",
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
  app.on("console", (message) => {
    // Main-process instrumentation contains fixed milestones/statuses only; never forward arbitrary console content.
    if (message.text().startsWith("NATIVE_LAUNCHER_STAGE "))
      console.info(message.text());
  });
  const launcherDirectory = await app.evaluate(({ app }) =>
    app.getPath("userData"),
  );
  let acceptedPackage: { source: string; worker_sha256: string } | undefined;
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
        "csharp_coverage_bridge.py",
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
      // Bind the actual packaged analyzers and C# bridge to this reviewed source.
      // Metadata schema 1 retains its legacy Node-only worker_sha256 field.
      for (const file of ["node_checks.cjs", "csharp_coverage_bridge.py"]) {
        expect(
          createHash("sha256")
            .update(readFileSync(join(resources, "runner", file)))
            .digest("hex"),
          `Bundled worker digest: ${file}`,
        ).toBe(
          createHash("sha256")
            .update(readFileSync(join("runner", file)))
            .digest("hex"),
        );
      }
      const metadata = JSON.parse(
        readFileSync(
          join(resources, "metadata", "source-release.json"),
          "utf8",
        ),
      );
      expect(metadata.schema).toBe(1);
      expect(metadata.product).toBe("code-flow-studio");
      expect(metadata.version).toBe("0.4.3");
      expect(metadata.source).toMatch(/^[a-f0-9]{40}$/);
      expect(typeof metadata.source_dirty).toBe("boolean");
      expect(metadata.worker_sha256).toBe(
        createHash("sha256")
          .update(readFileSync(join(resources, "runner", "node_checks.cjs")))
          .digest("hex"),
      );
      if (process.env.GITHUB_SHA)
        expect(metadata.source).toBe(process.env.GITHUB_SHA);
      acceptedPackage = metadata;
    }
    const page = await app.firstWindow();
    page.once("crash", () => console.error("NATIVE_RENDERER_EVENT", "crashed"));
    page.once("close", () => console.info("NATIVE_RENDERER_EVENT", "closed"));
    const accountStartedAt = Date.now();
    const accountRoutes = new Set(["/private/register", "/private/unlock"]);
    page.on("request", (request) => {
      const route = new URL(request.url()).pathname;
      if (request.method() === "POST" && accountRoutes.has(route))
        console.info(
          "NATIVE_ACCOUNT_REQUEST",
          JSON.stringify({
            route,
            stage: "started",
            elapsedMs: Date.now() - accountStartedAt,
          }),
        );
    });
    page.on("response", (response) => {
      const route = new URL(response.url()).pathname;
      if (response.request().method() === "POST" && accountRoutes.has(route))
        console.info(
          "NATIVE_ACCOUNT_REQUEST",
          JSON.stringify({
            route,
            stage: "response",
            status: response.status(),
            elapsedMs: Date.now() - accountStartedAt,
          }),
        );
    });
    const browserErrors: string[] = [];
    page.on("pageerror", (error) => {
      if (browserErrors.length < 8) browserErrors.push(error.name);
    });
    const health = await page.request.get(new URL("/health", page.url()).href);
    expect((await health.json()).version).toBe("0.4.3");
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
          documentReady: document.readyState,
          inputs: Array.from(
            document.querySelectorAll<HTMLInputElement>(
              "input[name=alias], input[name=password], input[name=phrase]",
            ),
          ).map((input) => ({
            name: input.name,
            valid: input.validity.valid,
            valueMissing: input.validity.valueMissing,
            patternMismatch: input.validity.patternMismatch,
            tooShort: input.validity.tooShort,
            tooLong: input.validity.tooLong,
          })),
          submitDisabled: (
            document
              .querySelector<HTMLInputElement>(
                "input[name=alias], input[name=phrase]",
              )
              ?.closest("form")
              ?.querySelector("button") as HTMLButtonElement | null
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
    const lifecycle = () => {
      const records: {
        stage: string;
        pid: number;
        parent_pid: number;
        connections?: number;
        tasks?: number;
      }[] = [];
      const launcher = readDiagnosticLog(
        join(launcherDirectory, "native-lifecycle.log"),
      );
      for (const line of launcher.split(/\r?\n/).filter(Boolean))
        console.info(
          "NATIVE_LAUNCHER_RECEIPT",
          JSON.stringify(JSON.parse(line)),
        );
      const service = readDiagnosticLog(join(launcherDirectory, "service.log"));
      for (const line of service.split(/\r?\n/))
        if (line.startsWith("NATIVE_SERVICE_STAGE ")) {
          console.info(line);
          records.push(JSON.parse(line.slice("NATIVE_SERVICE_STAGE ".length)));
        }
      return records;
    };
    const diagnostic = setTimeout(lifecycle, 10000);
    try {
      await app.close();
      console.info("NATIVE_JOURNEY_STAGE", "owned-close:complete");
      const records = lifecycle();
      for (const stage of [
        "http-drain-started",
        "http-drain-complete",
        "workspace-close-complete",
        "lifespan-close-complete",
        "server-thread-stopped",
        "main-complete",
      ])
        expect(
          records.some((record) => record.stage === stage),
          `Actual frozen service milestone: ${stage}`,
        ).toBe(true);
      for (const record of records.filter((record) =>
        ["http-drain-started", "http-drain-complete"].includes(record.stage),
      )) {
        expect(
          Number.isSafeInteger(record.connections) && record.connections! >= 0,
        ).toBe(true);
        expect(Number.isSafeInteger(record.tasks) && record.tasks! >= 0).toBe(
          true,
        );
        if (record.stage === "http-drain-complete")
          expect(record.tasks).toBe(0);
      }
      // Signal zero observes identity existence without sending a termination signal or touching unrelated processes.
      for (const pid of new Set(
        records.flatMap((record) => [record.pid, record.parent_pid]),
      )) {
        expect(Number.isSafeInteger(pid) && pid > 0).toBe(true);
        expect(
          () => process.kill(pid, 0),
          `Owned service/bootloader PID ${pid} must have exited`,
        ).toThrow(/ESRCH/);
      }
    } finally {
      clearTimeout(diagnostic);
      lifecycle();
    }
  }
  if (acceptedPackage) {
    // Generated proof contains source/package identity only; no profile, alias, source text or account key.
    mkdirSync("artifacts", { recursive: true });
    writeFileSync(
      "artifacts/native-resource-acceptance.json",
      JSON.stringify({
        schema: 1,
        version: "0.4.3",
        source: acceptedPackage.source,
        worker_sha256: acceptedPackage.worker_sha256,
        compiled_app: true,
        journey: "passed",
      }),
    );
  }
});
