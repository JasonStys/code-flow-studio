/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * types: Orphan@L34
 * functions: orphan()@L27
 * variables: assert@L14; path@L15; toolRequire@L16; { Linter }@L19; parser@L20; plugin@L21; fixtures@L22; fixture@L51; rule@L52; config@L55; findings@L74
 * </code-map> */

/**
 * Jason Stys: exercise the separately locked worker analyzer graph against independent source oracles.
 * Target text stays inert: no require/import/config from the fixtures is ever evaluated.
 * Functions and fixture variable locations are generated in docs/code-index.md.
 */
const assert = require("node:assert/strict");
const path = require("node:path");
const toolRequire = require("node:module").createRequire(
  path.resolve(__dirname, "../runner/tools/package.json"),
);
const { Linter } = toolRequire("eslint");
const parser = toolRequire("@typescript-eslint/parser");
const plugin = toolRequire("@typescript-eslint/eslint-plugin");
const fixtures = [
  {
    name: "main.js",
    typed: false,
    source:
      "function orphan(){ return 1; }\nconst used = 3;\nconsole.log(used);\n",
    line: 1,
  },
  {
    name: "main.ts",
    typed: true,
    source:
      "type Orphan = number;\nconst used: number = 3;\nconsole.log(used);\n",
    line: 1,
  },
  {
    name: "helper.js",
    typed: false,
    source: "/* eslint-disable no-unused-vars */\nconst abandoned = 1;\n",
    line: 2,
  },
  {
    name: "helper.ts",
    typed: true,
    source:
      "throw new Error('source-must-stay-inert');\nconst abandoned: number = 1;\n",
    line: 2,
  },
];
for (const fixture of fixtures) {
  const rule = fixture.typed
    ? "@typescript-eslint/no-unused-vars"
    : "no-unused-vars";
  const config = {
    files: ["**/*.{js,ts}"],
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: fixture.typed ? "module" : "commonjs",
      ...(fixture.typed ? { parser } : {}),
    },
    ...(fixture.typed ? { plugins: { "@typescript-eslint": plugin } } : {}),
    rules: {
      [rule]: [
        "warn",
        {
          args: "none",
          varsIgnorePattern: "^_",
          caughtErrorsIgnorePattern: "^_",
        },
      ],
    },
  };
  const findings = new Linter().verify(fixture.source, config, {
    filename: fixture.name,
    allowInlineConfig: false,
  });
  assert.deepEqual(
    findings.map((item) => ({ rule: item.ruleId, line: item.line })),
    [{ rule, line: fixture.line }],
    fixture.name,
  );
}
console.log(
  JSON.stringify({
    worker_analyzer_fixtures: fixtures.length,
    js_ts_exact_lines: true,
    inline_disable_ignored: true,
    target_text_inert: true,
  }),
);
