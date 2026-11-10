/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * functions: reportJson(file)@L17; main()@L40
 * variables: fs@L12; path@L13; { fileURLToPath }@L14; MAX_REPORT_BYTES@L15; descriptor@L19; status@L21; chunks@L24; size@L25; content@L27; count@L28; toolRequire@L42; { Linter }@L43; tsParser@L44; tsPlugin@L45; v8toIstanbul@L46; [mode, input, output, directory]@L47; project@L48; typed@L49; files@L50; linter@L52; findings@L53; file@L54; config@L55; item@L61; collected@L71; name@L72; report@L74; script@L75; scriptPath@L77; base@L78; original@L79; expectedPath@L80; source@L82; sources@L83; map@L85; converter@L94; coverage@L97; lines@L98; [id, statement]@L99; line@L100
 * </code-map> */

/** Jason Stys: fixed ESLint and V8-to-Istanbul bridge; never import a target module/config/plugin.
 * Inputs: mode, original job, result path, V8 report directory. Output is bounded by the worker tmpfs.
 * Declaration/variable locations: docs/code-index.md. All target text stays inert in this process.
 */
const fs = require("node:fs");
const path = require("node:path");
const { fileURLToPath } = require("node:url");
const MAX_REPORT_BYTES = 8 * 1024 * 1024;

function reportJson(file) {
  /** Open once, reject non-regular files and cap actual descriptor bytes even if a writer grows/replaces its path. */
  const descriptor = fs.openSync(file, fs.constants.O_RDONLY | (fs.constants.O_NONBLOCK || 0) | (fs.constants.O_NOFOLLOW || 0));
  try {
    const status = fs.fstatSync(descriptor);
    if (!status.isFile()) throw Error("Native JSON report must be a regular file");
    if (status.size > MAX_REPORT_BYTES) throw Error("Native JSON report exceeds eight MiB");
    const chunks = [];
    let size = 0;
    while (size <= MAX_REPORT_BYTES) {
      const content = Buffer.alloc(Math.min(64 * 1024, MAX_REPORT_BYTES + 1 - size));
      const count = fs.readSync(descriptor, content, 0, content.length, null);
      if (count === 0) break;
      size += count;
      if (size > MAX_REPORT_BYTES) throw Error("Native JSON report exceeds eight MiB");
      chunks.push(content.subarray(0, count));
    }
    return JSON.parse(Buffer.concat(chunks, size).toString("utf8"));
  } finally {
    fs.closeSync(descriptor);
  }
}

async function main() {
  /** Inspect original source or translate native V8 ranges; only supplied paths may enter reports. */
  const toolRequire = require("node:module").createRequire("/opt/tools/package.json");
  const { Linter } = toolRequire("eslint");
  const tsParser = toolRequire("@typescript-eslint/parser");
  const tsPlugin = toolRequire("@typescript-eslint/eslint-plugin");
  const v8toIstanbul = toolRequire("v8-to-istanbul");
  const [mode, input, output, directory] = process.argv.slice(2);
  const project = reportJson(input);
  const typed = project.language === "typescript";
  const files = project.files.filter(file => file.encoding === "text" && (file.name.endsWith(typed ? ".ts" : ".js") || file.name === project.entry));
  if (mode === "lint") {
    const linter = new Linter();
    const findings = [];
    for (const file of files) {
      const config = { files: ["**/*.{js,ts}"], languageOptions: {
        ecmaVersion: "latest", sourceType: typed ? "module" : "commonjs",
        ...(typed ? { parser: tsParser } : {}),
      }, ...(typed ? { plugins: { "@typescript-eslint": tsPlugin } } : {}),
      rules: { [typed ? "@typescript-eslint/no-unused-vars" : "no-unused-vars"]:
        ["warn", { args: "none", varsIgnorePattern: "^_", caughtErrorsIgnorePattern: "^_" }] } };
      for (const item of linter.verify(file.content, config, { filename: file.name, allowInlineConfig: false })) {
        if (findings.length >= 1001) break;
        if (!item.line) continue;
        findings.push({ file: file.name, line: item.line, column: item.column,
          code: item.ruleId || "parse-error", message: item.message, severity: item.fatal ? "error" : "review" });
      }
    }
    fs.writeFileSync(output, JSON.stringify({ findings }));
    return;
  }
  const collected = new Map();
  for (const name of fs.readdirSync(directory)) {
    if (!name.endsWith(".json")) continue;
    const report = reportJson(path.join(directory, name));
    for (const script of report.result || []) {
      if (!script.url.startsWith("file:")) continue;
      const scriptPath = fileURLToPath(script.url);
      const base = path.basename(scriptPath, ".js");
      const original = files.find(file => typed ? file.name === `${base}.ts` : file.name === path.basename(scriptPath));
      const expectedPath = typed ? path.join("/tmp/project/compiled", `${base}.js`) : path.join("/tmp/project", original?.name || "");
      if (!original || scriptPath !== expectedPath) continue;
      let source = fs.readFileSync(scriptPath, "utf8");
      let sources;
      if (typed) {
        const map = reportJson(scriptPath + ".map");
        if (map.sources.length !== 1 || path.basename(map.sources[0]) !== original.name) throw Error("Unexpected source map");
        map.sourcesContent = [original.content];
        sources = { source, originalSource: original.content, sourceMap: { sourcemap: map } };
      } else {
        // Never follow uploaded sourceMappingURL paths, URLs or inline maps. Preserve UTF-16 offsets.
        source = source.replace(/\/\/[#@]\s*sourceMappingURL=[^\r\n]*|\/\*[#@]\s*sourceMappingURL=[\s\S]*?\*\//g, value => value.replace(/[^\r\n]/g, " "));
        sources = { source };
      }
      const converter = v8toIstanbul(scriptPath, undefined, sources);
      await converter.load();
      converter.applyCoverage(script.functions);
      for (const coverage of Object.values(converter.toIstanbul())) {
        const lines = collected.get(original.name) || {};
        for (const [id, statement] of Object.entries(coverage.statementMap)) {
          const line = statement.start.line;
          lines[line] = Math.max(lines[line] || 0, coverage.s[id] || 0);
        }
        collected.set(original.name, lines);
      }
    }
  }
  fs.writeFileSync(output, JSON.stringify(Object.fromEntries(collected)));
}
module.exports = { reportJson };
if (require.main === module) main().catch(error => { console.error(error.message); process.exitCode = 2; });
