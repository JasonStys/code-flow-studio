/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * functions: verifyElectron(root = path.resolve(__dirname, "..")@L18
 * variables: fs@L13; path@L14; { execFileSync }@L15; expected@L19; sdk@L28; installed@L30; selected@L33; directory@L34; executable@L35; relative@L36; environment@L51; key@L52; actual@L54
 * </code-map> */

/**
 * Jason Stys: fail-fast pinned Electron SDK readiness, without invoking its lazy-download module.
 * Reads fixed package metadata, constrains the executable path, and probes only its embedded version.
 * Exact function/variable positions are generated in docs/code-index.md.
 */
const fs = require("node:fs");
const path = require("node:path");
const { execFileSync } = require("node:child_process");

/** Verify the actual pinned SDK before a timed UI journey; never download or launch a GUI here. */
function verifyElectron(root = path.resolve(__dirname, "..")) {
  const expected = JSON.parse(
    fs.readFileSync(path.join(root, "package.json"), "utf8"),
  ).devDependencies.electron;
  if (!/^\d+\.\d+\.\d+$/.test(expected))
    throw Error("Electron must be an exact pinned version.");
  if (process.env.ELECTRON_OVERRIDE_DIST_PATH)
    throw Error(
      "Unpinned Electron distribution overrides cannot validate this build.",
    );
  const sdk = path.join(root, "node_modules", "electron");
  try {
    const installed = JSON.parse(
      fs.readFileSync(path.join(sdk, "package.json"), "utf8"),
    ).version;
    const selected = fs.readFileSync(path.join(sdk, "path.txt"), "utf8").trim();
    const directory = fs.realpathSync(path.join(sdk, "dist"));
    const executable = fs.realpathSync(path.join(directory, selected));
    const relative = path.relative(directory, executable);
    if (
      relative === ".." ||
      relative.startsWith(".." + path.sep) ||
      path.isAbsolute(relative)
    )
      throw Error("Electron executable escapes the pinned SDK distribution.");
    if (
      installed !== expected ||
      fs.readFileSync(path.join(directory, "version"), "utf8").trim() !==
        expected
    )
      throw Error("Electron SDK metadata differs from the pinned version.");
    if (!fs.statSync(executable).isFile())
      throw Error("Electron executable is not a regular file.");
    const environment = { ELECTRON_RUN_AS_NODE: "1" };
    for (const key of ["PATH", "SYSTEMROOT", "TEMP", "TMP"])
      if (process.env[key] !== undefined) environment[key] = process.env[key];
    const actual = execFileSync(
      executable,
      ["-p", "process.versions.electron"],
      {
        env: environment,
        encoding: "utf8",
        windowsHide: true,
        timeout: 10000,
      },
    ).trim();
    if (actual !== expected)
      throw Error("Electron executable version differs from the pinned SDK.");
    return { version: actual, executable };
  } catch (error) {
    throw Error(
      "Pinned Electron SDK is not ready. Run npm run setup:electron before native tests. " +
        error.message,
    );
  }
}
module.exports = { verifyElectron };
if (require.main === module) console.log(JSON.stringify(verifyElectron()));
