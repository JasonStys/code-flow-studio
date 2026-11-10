/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * functions: nativeStage(stage, details = {})@L27; port()@L42; launch()@L53
 * variables: { spawn }@L17; { randomBytes }@L18; { join }@L19; net@L20; fs@L21; { shutdownProof }@L22; service@L23; closing@L24; record@L29; server@L43; selected@L47; selected@L54; nonce@L56; resources@L57; executable@L60; ui@L67; log@L71; env@L76; exited@L93; origin@L102; ready@L104; attempt@L105; response@L107; health@L110; isolated@L124; allowed@L132; window@L140; stopped@L220; response@L226; stopping@L237; outcome@L239; window@L266
 * </code-map> */

/** Jason Stys: native private-account launcher. No renderer secrets, privileged preload or host code execution. */
const {
  app,
  BrowserWindow,
  dialog,
  Menu,
  session,
  shell,
} = require("electron");
const { spawn } = require("node:child_process");
const { randomBytes } = require("node:crypto");
const { join } = require("node:path");
const net = require("node:net");
const fs = require("node:fs");
const { shutdownProof } = require("./shutdown-proof.cjs");
let service, serviceOrigin, serviceToken;
let closing = false;

/** Emit only owned process/status milestones during disposable native acceptance; never token or response content. */
function nativeStage(stage, details = {}) {
  if (process.env.STUDIO_DESKTOP_TEST === "1") {
    const record = JSON.stringify({ stage, ...details });
    console.info("NATIVE_LAUNCHER_STAGE", record);
    // The debugger may disconnect before asynchronous before-quit finishes.
    // Preserve only the same value-free milestone in the disposable profile.
    fs.appendFileSync(
      join(app.getPath("userData"), "native-lifecycle.log"),
      record + "\n",
      { mode: 0o600 },
    );
  }
}

/** Reserve a local port; the owned Python service verifies binding and a random launch nonce. */
async function port() {
  const server = net.createServer();
  await new Promise((resolve, reject) =>
    server.once("error", reject).listen(0, "127.0.0.1", resolve),
  );
  const selected = server.address().port;
  await new Promise((resolve) => server.close(resolve));
  return selected;
}

/** Launch a private backend and an ephemeral sandboxed renderer, never forwarding global provider credentials. */
async function launch() {
  const selected = await port();
  serviceToken = randomBytes(32).toString("hex");
  const nonce = randomBytes(32).toString("hex");
  const resources = app.isPackaged
    ? process.resourcesPath
    : join(__dirname, "..", "release");
  const executable = join(
    resources,
    "service",
    process.platform === "win32"
      ? "code-flow-service.exe"
      : "code-flow-service",
  );
  const ui = app.isPackaged
    ? join(resources, "ui")
    : join(__dirname, "..", "dist", "ui");
  fs.mkdirSync(app.getPath("userData"), { recursive: true });
  const log = fs.openSync(
    join(app.getPath("userData"), "service.log"),
    "a",
    0o600,
  );
  const env = {
    ...process.env,
    CFS_LAUNCH_TOKEN: serviceToken,
    CFS_LAUNCH_NONCE: nonce,
    CFS_PARENT_PID: String(process.pid),
  };
  delete env.STUDIO_TOKEN;
  delete env.STUDIO_OPENAI_KEY;
  delete env.STUDIO_ANTHROPIC_KEY;
  delete env.STUDIO_AI_CONFIG;
  service = spawn(
    executable,
    ["--port", String(selected), "--ui", ui, "--no-browser"],
    { env, windowsHide: true, stdio: ["ignore", log, log] },
  );
  fs.closeSync(log);
  nativeStage("service-spawned", { pid: service.pid });
  let exited = false;
  service.once("error", () => {
    exited = true;
  });
  service.once("exit", (code, signal) => {
    exited = true;
    nativeStage("service-exited", { pid: service.pid, code, signal });
    if (!closing) app.quit();
  });
  const origin = `http://127.0.0.1:${selected}`;
  serviceOrigin = origin;
  let ready = false;
  for (let attempt = 0; attempt < 180 && !exited; attempt++) {
    try {
      const response = await fetch(origin + "/health", {
        signal: AbortSignal.timeout(1000),
      });
      const health = response.ok ? await response.json() : {};
      ready =
        health.mode === "private-local-accounts" &&
        health.launcher_nonce === nonce;
    } catch {
      /* Unpacking/startup is bounded; no connection to an unrelated listener is accepted. */
    }
    if (ready) break;
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  if (!ready)
    throw new Error(
      "The private local service could not start. Preserve account recovery data; no submitted code was executed.",
    );
  const isolated = session.fromPartition("code-flow-ephemeral-" + nonce, {
    cache: false,
  });
  isolated.setPermissionRequestHandler((_webContents, _permission, callback) =>
    callback(false),
  );
  isolated.setPermissionCheckHandler(() => false);
  isolated.webRequest.onBeforeRequest((details, callback) => {
    let allowed = false;
    try {
      allowed =
        new URL(details.url).origin === origin ||
        details.url.startsWith("blob:" + origin + "/");
    } catch {}
    callback({ cancel: !allowed });
  });
  const window = new BrowserWindow({
    width: 1440,
    height: 1000,
    minWidth: 420,
    minHeight: 600,
    show: false,
    backgroundColor: "#122338",
    webPreferences: {
      session: isolated,
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      webSecurity: true,
    },
  });
  window.webContents.setWindowOpenHandler(() => ({ action: "deny" }));
  window.webContents.on("will-navigate", (event, url) => {
    try {
      if (new URL(url).origin !== origin) event.preventDefault();
    } catch {
      event.preventDefault();
    }
  });
  window.once("ready-to-show", () => window.show());
  Menu.setApplicationMenu(
    Menu.buildFromTemplate([
      {
        label: "Code Flow",
        submenu: [
          {
            label: "Open local website",
            click: () => {
              void shell.openExternal(origin + "/");
            },
          },
          { label: "Reload", role: "reload" },
          { label: "Quit", role: "quit" },
        ],
      },
      {
        label: "Edit",
        submenu: [
          { role: "undo" },
          { role: "redo" },
          { type: "separator" },
          { role: "cut" },
          { role: "copy" },
          { role: "paste" },
          { role: "selectAll" },
        ],
      },
      {
        label: "Help",
        submenu: [
          {
            label: "Jason Stys · GitHub",
            click: () => {
              void shell.openExternal("https://github.com/JasonStys");
            },
          },
          {
            label: "Contact Jason Stys · LinkedIn",
            click: () => {
              void shell.openExternal(
                "https://www.linkedin.com/in/jason-stys-31b30b351/",
              );
            },
          },
        ],
      },
    ]),
  );
  await window.loadURL(origin + "/");
}

/** Ask only the owned backend to cancel jobs and seal. Never force-delete recovery files on timeout. */
app.on("before-quit", (event) => {
  if (closing || !service || service.exitCode !== null) return;
  event.preventDefault();
  closing = true;
  const stopped = new Promise((resolve) =>
    service.once("exit", () => resolve("service-exited")),
  );
  void (async () => {
    try {
      nativeStage("shutdown-requested", { pid: service.pid });
      const response = await fetch(serviceOrigin + "/launcher/shutdown", {
        method: "POST",
        headers: {
          Authorization: "Bearer " + serviceToken,
          "X-CFS-Request": "v1",
          "Content-Type": "application/json",
        },
        body: "{}",
        signal: AbortSignal.timeout(2000),
      });
      nativeStage("shutdown-http-response", { status: response.status });
      const stopping = await shutdownProof(response);
      nativeStage("shutdown-response", { status: response.status, stopping });
      const outcome = await Promise.race([
        stopped,
        new Promise((resolve) =>
          setTimeout(() => resolve("existing-deadline"), 30000),
        ),
      ]);
      nativeStage("shutdown-wait-complete", { outcome });
    } catch (error) {
      nativeStage("shutdown-transport-failed", { errorType: error.name });
      /* Parent monitor still requests graceful sealing if this launcher exits. */
    }
    app.exit(0);
  })();
});
app.on("window-all-closed", () => app.quit());
// Native regression runs own a disposable launcher profile as well as a disposable account store.
app.setPath(
  "userData",
  process.env.STUDIO_DESKTOP_TEST === "1"
    ? fs.mkdtempSync(
        join(require("node:os").tmpdir(), "code-flow-launcher-test-"),
      )
    : join(app.getPath("appData"), "CodeFlowStudioLauncher"),
);
if (!app.requestSingleInstanceLock()) app.quit();
else {
  app.on("second-instance", () => {
    const window = BrowserWindow.getAllWindows()[0];
    if (window) {
      window.restore();
      window.focus();
    }
  });
  app
    .whenReady()
    .then(launch)
    .catch((error) => {
      if (process.env.STUDIO_DESKTOP_TEST) console.error(error.message);
      else dialog.showErrorBox("Code Flow startup", error.message);
      app.quit();
    });
}
