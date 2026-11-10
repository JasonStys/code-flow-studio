/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * functions: readDiagnosticLog(file)@L12
 * variables: fs@L9; descriptor@L13; metadata@L26; bytes@L29; used@L30
 * </code-map> */

/** Jason Stys: bounded single-descriptor reads of disposable native diagnostic logs. Symbols: docs/code-index.md. */
const fs = require("node:fs");

/** Observe one regular-file descriptor without a pathname precheck; absence is diagnostic unavailability. */
function readDiagnosticLog(file) {
  let descriptor;
  try {
    descriptor = fs.openSync(
      file,
      fs.constants.O_RDONLY |
        (fs.constants.O_NONBLOCK ?? 0) |
        (fs.constants.O_NOFOLLOW ?? 0),
    );
  } catch (error) {
    if (error.code === "ENOENT") return "";
    throw error;
  }
  try {
    const metadata = fs.fstatSync(descriptor);
    if (!metadata.isFile())
      throw new Error("Native diagnostic is not a regular file");
    const bytes = Buffer.alloc(Math.min(metadata.size, 65536));
    const used = fs.readSync(
      descriptor,
      bytes,
      0,
      bytes.length,
      Math.max(0, metadata.size - bytes.length),
    );
    return bytes.subarray(0, used).toString("utf8");
  } finally {
    fs.closeSync(descriptor);
  }
}
module.exports = { readDiagnosticLog };
