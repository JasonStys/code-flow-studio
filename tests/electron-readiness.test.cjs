/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * variables: test@L12; assert@L13; fs@L14; os@L15; path@L16; { verifyElectron }@L17; directory@L20
 * </code-map> */

/**
 * Jason Stys: a missing SDK must fail before Electron's lazy downloader can enter a UI test.
 * Only disposable metadata is created; the real SDK/runtime and user profiles are untouched.
 * Exact fixture and function positions are generated in docs/code-index.md.
 */
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { verifyElectron } = require("../scripts/verify_electron.cjs");

test("missing SDK fails locally without downloading or modifying the fixture", () => {
  const directory = fs.mkdtempSync(
    path.join(os.tmpdir(), "cfs-electron-preflight-"),
  );
  fs.writeFileSync(
    path.join(directory, "package.json"),
    JSON.stringify({ devDependencies: { electron: "44.10.2" } }),
  );
  assert.throws(() => verifyElectron(directory), /SDK is not ready/);
  assert.deepEqual(fs.readdirSync(directory), ["package.json"]);
});
