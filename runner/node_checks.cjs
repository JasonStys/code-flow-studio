/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * functions: main()@L21
 * variables: fs@L12; path@L13; { fileURLToPath }@L14; toolRequire@L15; { Linter }@L16; tsParser@L17; tsPlugin@L18; v8toIstanbul@L19; [mode, input, output, directory]@L23; project@L24; typed@L25; files@L26; linter@L28; findings@L29; file@L30; config@L31; item@L37; collected@L47; name@L48; report@L50; script@L51; scriptPath@L53; base@L54; original@L55; expectedPath@L56; source@L58; sources@L59; map@L61; converter@L70; coverage@L73; lines@L74; [id, statement]@L75; line@L76
 * </code-map> */

/** Jason Stys: fixed ESLint and V8-to-Istanbul bridge; never import a target module/config/plugin.
 * Inputs: mode, original job, result path, V8 report directory. Output is bounded by the worker tmpfs.
 * Declaration/variable locations: docs/code-index.md. All target text stays inert in this process.
 */
const fs = require("node:fs");
const path = require("node:path");
const { fileURLToPath } = require("node:url");
const toolRequire = require("node:module").createRequire("/opt/tools/package.json");
const { Linter } = toolRequire("eslint");
const tsParser = toolRequire("@typescript-eslint/parser");
const tsPlugin = toolRequire("@typescript-eslint/eslint-plugin");
const v8toIstanbul = toolRequire("v8-to-istanbul");

async function main() {
  /** Inspect original source or translate native V8 ranges; only supplied paths may enter reports. */
  const [mode, input, output, directory] = process.argv.slice(2);
  const project = JSON.parse(fs.readFileSync(input, "utf8"));
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
    const report = JSON.parse(fs.readFileSync(path.join(directory, name), "utf8"));
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
        const map = JSON.parse(fs.readFileSync(scriptPath + ".map", "utf8"));
        if (map.sources.length !== 1 || path.basename(map.sources[0]) !== original.name) throw Error("Unexpected source map");
        map.sourcesContent = [original.content];
        sources = { source, originalSource: original.content, sourceMap: { sourcemap: map } };
      } else {
        // Never follow uploaded sourceMappingURL paths, URLs or inline maps. Preserve UTF-16 offsets.
        source = source.replace(/\/\/[#@]\s*sourceMappingURL=[^\r\n]*/g, value => " ".repeat(value.length));
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
main().catch(error => { console.error(error.message); process.exitCode = 2; });
