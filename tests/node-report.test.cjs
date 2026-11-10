/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * functions: fixture(run)@L21
 * variables: assert@L12; fs@L13; path@L14; os@L15; { test }@L16; { reportJson }@L17; LIMIT@L18; directory@L22; content@L39; content@L49; original@L66; read@L85; descriptor@L86; original@L104; status@L106
 * </code-map> */

/** Jason Stys: real worker JSON reader oracles for bounded bytes, descriptor identity and failure cleanup.
 * Only disposable local fixtures are read; requiring the bridge never starts analyzers or executes target code.
 * Exact definitions and variables: docs/code-index.md.
 */
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");
const { test } = require("node:test");
const { reportJson } = require("../runner/node_checks.cjs");
const LIMIT = 8 * 1024 * 1024;

/** Own and verify one fresh temporary directory before recursively removing its synthetic files. */
function fixture(run) {
  const directory = fs.mkdtempSync(
    path.join(os.tmpdir(), "cfs-report-oracle-"),
  );
  try {
    run(path.join(directory, "report.json"));
  } finally {
    assert.equal(
      path.dirname(path.resolve(directory)),
      path.resolve(os.tmpdir()),
    );
    assert.ok(path.basename(directory).startsWith("cfs-report-oracle-"));
    fs.rmSync(directory, { recursive: true, force: true });
  }
}

test("actual reader accepts Unicode JSON and exactly the byte limit", () =>
  fixture((file) => {
    const content = Buffer.from('{"value":"α 😀"}');
    fs.writeFileSync(
      file,
      Buffer.concat([content, Buffer.alloc(LIMIT - content.length, 32)]),
    );
    assert.deepEqual(reportJson(file), { value: "α 😀" });
  }));

test("actual reader rejects empty/malformed JSON and closes its descriptor", () =>
  fixture((file) => {
    for (const content of ["", "{", "not JSON"]) {
      fs.writeFileSync(file, content);
      assert.throws(() => reportJson(file), SyntaxError);
      fs.renameSync(file, file + ".old");
      fs.unlinkSync(file + ".old");
    }
  }));

test("actual reader rejects oversized files", () =>
  fixture((file) => {
    fs.writeFileSync(file, Buffer.alloc(LIMIT + 1, 32));
    assert.throws(() => reportJson(file), /exceeds eight MiB/);
  }));

test("actual read cap rejects growth or a stale small size observation", () =>
  fixture((file) => {
    fs.writeFileSync(file, Buffer.alloc(LIMIT + 1, 32));
    const original = fs.fstatSync;
    fs.fstatSync = (descriptor) =>
      Object.assign(original(descriptor), { size: 1 });
    try {
      assert.throws(() => reportJson(file), /exceeds eight MiB/);
    } finally {
      fs.fstatSync = original;
    }
  }));

test("actual reader refuses a directory", () =>
  fixture((file) => {
    fs.mkdirSync(file);
    assert.throws(() => reportJson(file));
  }));

test("read errors propagate and close exactly the owned descriptor", () =>
  fixture((file) => {
    fs.writeFileSync(file, "{}");
    const read = fs.readSync;
    let descriptor;
    fs.readSync = (value) => {
      descriptor = value;
      throw Object.assign(new Error("Synthetic read I/O failure"), {
        code: "EIO",
      });
    };
    try {
      assert.throws(() => reportJson(file), /Synthetic read I\/O failure/);
    } finally {
      fs.readSync = read;
    }
    assert.throws(() => fs.fstatSync(descriptor), { code: "EBADF" });
  }));

test("replacing the path after opening cannot replace descriptor contents", () =>
  fixture((file) => {
    fs.writeFileSync(file, '{"original":true}');
    const original = fs.fstatSync;
    fs.fstatSync = (descriptor) => {
      const status = original(descriptor);
      fs.renameSync(file, file + ".original");
      fs.writeFileSync(file, '{"replacement":true}');
      return status;
    };
    try {
      assert.deepEqual(reportJson(file), { original: true });
    } finally {
      fs.fstatSync = original;
    }
    assert.deepEqual(JSON.parse(fs.readFileSync(file, "utf8")), {
      replacement: true,
    });
  }));
