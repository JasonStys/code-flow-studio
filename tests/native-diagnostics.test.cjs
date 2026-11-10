/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * variables: { test }@L8; assert@L9; fs@L10; { tmpdir }@L11; { join }@L12; { readDiagnosticLog }@L13; directory@L16; file@L18; directory@L34; file@L35; original@L37; descriptor@L39
 * </code-map> */

/** Jason Stys: actual filesystem regressions for bounded native diagnostic reading. Symbols: docs/code-index.md. */
const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const { tmpdir } = require("node:os");
const { join } = require("node:path");
const { readDiagnosticLog } = require("./native-diagnostics.cjs");

test("absent logs are unavailable; actual ordinary and oversized files are bounded", () => {
  const directory = fs.mkdtempSync(join(tmpdir(), "cfs-diagnostic-reader-"));
  try {
    const file = join(directory, "service.log");
    assert.equal(readDiagnosticLog(file), "");
    fs.writeFileSync(file, "fixed milestone");
    assert.equal(readDiagnosticLog(file), "fixed milestone");
    fs.writeFileSync(file, "a".repeat(70000));
    assert.equal(readDiagnosticLog(file), "a".repeat(65536));
    assert.throws(
      () => readDiagnosticLog(directory),
      /regular file|EISDIR|EACCES|EPERM/,
    );
  } finally {
    fs.rmSync(directory, { recursive: true });
  }
});

test("actual pathname replacement after open cannot redirect the descriptor", () => {
  const directory = fs.mkdtempSync(join(tmpdir(), "cfs-diagnostic-swap-"));
  const file = join(directory, "service.log");
  fs.writeFileSync(file, "opened owned bytes");
  const original = fs.openSync;
  fs.openSync = (...args) => {
    const descriptor = original(...args);
    if (args[0] === file) {
      fs.renameSync(file, join(directory, "original.log"));
      fs.writeFileSync(file, "replacement bytes");
    }
    return descriptor;
  };
  try {
    assert.equal(readDiagnosticLog(file), "opened owned bytes");
  } finally {
    fs.openSync = original;
    fs.rmSync(directory, { recursive: true });
  }
});
