/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * types: docs@L3
 * functions: port()@L23; launch()@L34
 * variables: { app, BrowserWindow, dialog, Menu, session }@L12; { spawn }@L13; { randomBytes }@L14; { join }@L15; net@L16; fs@L17; service@L18; serviceOrigin@L19; serviceToken@L20; closing@L21; server@L25; selected@L29; selected@L36; token@L37; resources@L39; executable@L42; ui@L49; config@L52; log@L54; exited@L79; origin@L86; ready@L88; attempt@L89; response@L91; window@L108; stopped@L157
 * </code-map> */

/** Bundled native launcher. Symbols/variables: docs/code-index.md.
 * No node integration, remote navigation, privileged preload, or uploaded-code execution.
 */
const { app, BrowserWindow, dialog, Menu, session } = require("electron");
const { spawn } = require("node:child_process");
const { randomBytes } = require("node:crypto");
const { join } = require("node:path");
const net = require("node:net");
const fs = require("node:fs");
let service;
let serviceOrigin;
let serviceToken;
let closing = false;

async function port() {
  /** Ask the OS for an available loopback port; the Python listener verifies bind success. */
  const server = net.createServer();
  await new Promise((resolve, reject) =>
    server.once("error", reject).listen(0, "127.0.0.1", resolve),
  );
  const selected = server.address().port;
  await new Promise((resolve) => server.close(resolve));
  return selected;
}

async function launch() {
  /** Start the bundled service and open only its authenticated local renderer. */
  const selected = await port();
  const token = randomBytes(32).toString("hex");
  serviceToken = token;
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
  const config = join(app.getPath("userData"), "providers.json");
  fs.mkdirSync(app.getPath("userData"), { recursive: true });
  const log = fs.openSync(
    join(app.getPath("userData"), "service.log"),
    "a",
    0o600,
  );
  service = spawn(
    executable,
    [
      "serve",
      "--port",
      String(selected),
      "--data",
      app.getPath("userData"),
      "--ui",
      ui,
      "--config",
      config,
    ],
    {
      env: { ...process.env, STUDIO_TOKEN: token },
      windowsHide: true,
      stdio: ["ignore", log, log],
    },
  );
  fs.closeSync(log);
  let exited = false;
  service.once("error", () => {
    exited = true;
  });
  service.once("exit", () => {
    exited = true;
  });
  const origin = `http://127.0.0.1:${selected}`;
  serviceOrigin = origin;
  let ready = false;
  for (let attempt = 0; attempt < 120 && !exited; attempt++) {
    try {
      const response = await fetch(`${origin}/health`, {
        signal: AbortSignal.timeout(1000),
      });
      ready = response.ok;
    } catch {
      /* Service is still unpacking/starting. */
    }
    if (ready) break;
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  if (!ready)
    throw new Error(
      "The bundled app service could not start. No code was executed.",
    );
  session.defaultSession.setPermissionRequestHandler(
    (_contents, _permission, callback) => callback(false),
  );
  const window = new BrowserWindow({
    width: 1440,
    height: 1000,
    minWidth: 420,
    minHeight: 600,
    show: false,
    backgroundColor: "#122338",
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      webSecurity: true,
    },
  });
  window.webContents.setWindowOpenHandler(() => ({ action: "deny" }));
  window.webContents.on("will-navigate", (event, url) => {
    if (new URL(url).origin !== origin) event.preventDefault();
  });
  window.once("ready-to-show", () => window.show());
  Menu.setApplicationMenu(
    Menu.buildFromTemplate([
      {
        label: "Code Flow",
        submenu: [
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
    ]),
  );
  await window.loadURL(`${origin}/#token=${token}`);
}

app.on("before-quit", (event) => {
  if (closing || !service || service.exitCode !== null) return;
  event.preventDefault();
  closing = true;
  const stopped = new Promise(resolve => service.once("exit", resolve));
  (async () => {
    try {
      await fetch(`${serviceOrigin}/api/shutdown`, {method: "POST", headers: {Authorization: `Bearer ${serviceToken}`}, signal: AbortSignal.timeout(2000)});
      await Promise.race([stopped, new Promise(resolve => setTimeout(resolve, 12000))]);
    } catch { /* Startup errors still close only this owned child. */ }
    if (service.exitCode === null) service.kill();
    app.exit(0);
  })();
});
app.on("window-all-closed", () => app.quit());
app
  .whenReady()
  .then(launch)
  .catch((error) => {
    if (process.env.STUDIO_DESKTOP_TEST) console.error(error);
    else dialog.showErrorBox("Code Flow startup", error.message);
    app.quit();
  });
