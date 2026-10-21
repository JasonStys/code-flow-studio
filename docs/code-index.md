# Code symbol index

Generated declaration locations. Python uses AST; JS/TS uses declaration-line matching. Inline docstrings/comments describe behavior and variable use. Headers include exact positions and are checked mechanically in CI.

## desktop/main.cjs

| Kind | Declaration | Line |
|---|---|---|
| variable | `{ spawn }` | 17 |
| variable | `{ randomBytes }` | 18 |
| variable | `{ join }` | 19 |
| variable | `net` | 20 |
| variable | `fs` | 21 |
| variable | `service` | 22 |
| variable | `closing` | 23 |
| function | `port()` | 26 |
| variable | `server` | 27 |
| variable | `selected` | 31 |
| function | `launch()` | 37 |
| variable | `selected` | 38 |
| variable | `nonce` | 40 |
| variable | `resources` | 41 |
| variable | `executable` | 44 |
| variable | `ui` | 51 |
| variable | `log` | 55 |
| variable | `env` | 60 |
| variable | `exited` | 76 |
| variable | `origin` | 84 |
| variable | `ready` | 86 |
| variable | `attempt` | 87 |
| variable | `response` | 89 |
| variable | `health` | 92 |
| variable | `isolated` | 106 |
| variable | `allowed` | 114 |
| variable | `window` | 122 |
| variable | `stopped` | 202 |
| variable | `window` | 230 |

## examples/language_locations.py

| Kind | Declaration | Line |
|---|---|---|
| variable | `SAMPLES` | 18 |
| function | `location_fixture(language)` | 77 |
| parameter | `language` | 77 |
| variable | `data` | 79 |
| variable | `missing` | 80 |
| variable | `source` | 80 |
| variable | `unused` | 80 |
| variable | `lines` | 90 |
| variable | `i` | 93 |
| variable | `line` | 93 |
| variable | `i` | 94 |
| variable | `line` | 94 |
| function | `module_fixture(language)` | 98 |
| parameter | `language` | 98 |
| variable | `typed` | 100 |
| variable | `suffix` | 101 |
| variable | `data` | 102 |

## examples/projects.py

| Kind | Declaration | Line |
|---|---|---|
| variable | `PROGRAMS` | 17 |
| function | `fixture(language)` | 66 |
| parameter | `language` | 66 |
| variable | `code` | 68 |
| variable | `name` | 68 |
| variable | `stdin` | 69 |

## playwright.config.ts

| Kind | Declaration | Line |
|---|---|---|

## playwright.desktop.config.ts

| Kind | Declaration | Line |
|---|---|---|

## playwright.private.config.ts

| Kind | Declaration | Line |
|---|---|---|

## runner/language_checks.py

| Kind | Declaration | Line |
|---|---|---|
| variable | `MAX_REPORT` | 24 |
| variable | `SUFFIXES` | 25 |
| function | `read_text(path)` | 43 |
| parameter | `path` | 43 |
| function | `read_json(path)` | 50 |
| parameter | `path` | 50 |
| function | `read_xml(path)` | 55 |
| parameter | `path` | 55 |
| variable | `text` | 59 |
| variable | `text` | 62 |
| class | `Evidence` | 68 |
| function | `__init__(self, project)` | 71 |
| parameter | `project` | 71 |
| parameter | `self` | 71 |
| variable | `file` | 75 |
| variable | `name` | 82 |
| variable | `text` | 82 |
| variable | `name` | 84 |
| variable | `text` | 84 |
| function | `name(self, path)` | 90 |
| parameter | `path` | 90 |
| parameter | `self` | 90 |
| variable | `value` | 92 |
| function | `line(self, name, value)` | 95 |
| parameter | `name` | 95 |
| parameter | `self` | 95 |
| parameter | `value` | 95 |
| variable | `line` | 97 |
| function | `add_lines(self, path, counts)` | 100 |
| parameter | `counts` | 100 |
| parameter | `path` | 100 |
| parameter | `self` | 100 |
| variable | `name` | 102 |
| variable | `lines` | 105 |
| variable | `count` | 106 |
| variable | `value` | 106 |
| variable | `line` | 107 |
| function | `finding(self, path, line, column, code, message, severity)` | 111 |
| parameter | `code` | 111 |
| parameter | `column` | 111 |
| parameter | `line` | 111 |
| parameter | `message` | 111 |
| parameter | `path` | 111 |
| parameter | `self` | 111 |
| parameter | `severity` | 111 |
| variable | `name` | 113 |
| variable | `key` | 116 |
| function | `coverage(self, tool, metric, cases, expected)` | 136 |
| parameter | `cases` | 136 |
| parameter | `expected` | 136 |
| parameter | `metric` | 136 |
| parameter | `self` | 136 |
| parameter | `tool` | 136 |
| variable | `files` | 138 |
| variable | `name` | 139 |
| variable | `text` | 139 |
| variable | `counts` | 140 |
| variable | `covered` | 147 |
| variable | `value` | 147 |
| variable | `count` | 158 |
| variable | `line` | 158 |
| variable | `count` | 159 |
| variable | `line` | 159 |
| variable | `budget` | 165 |
| variable | `key` | 166 |
| variable | `record` | 167 |
| variable | `values` | 168 |
| variable | `budget` | 170 |
| variable | `file` | 172 |
| variable | `measured` | 172 |
| variable | `complete` | 173 |
| variable | `case` | 175 |
| variable | `file` | 185 |
| function | `cobertura(evidence, path, case_index)` | 190 |
| parameter | `case_index` | 190 |
| parameter | `evidence` | 190 |
| parameter | `path` | 190 |
| variable | `document` | 192 |
| variable | `roots` | 193 |
| variable | `source` | 193 |
| variable | `item` | 194 |
| variable | `reported` | 195 |
| variable | `paths` | 196 |
| variable | `root` | 196 |
| variable | `candidate` | 197 |
| variable | `name` | 197 |
| variable | `path` | 197 |
| variable | `line` | 201 |
| variable | `line` | 203 |
| variable | `condition` | 204 |
| function | `jacoco(evidence, path)` | 216 |
| parameter | `evidence` | 216 |
| parameter | `path` | 216 |
| variable | `file` | 218 |
| variable | `name` | 219 |
| variable | `line` | 222 |
| variable | `line` | 230 |
| function | `gcov(evidence, path)` | 235 |
| parameter | `evidence` | 235 |
| parameter | `path` | 235 |
| variable | `stream` | 237 |
| variable | `text` | 238 |
| variable | `file` | 241 |
| variable | `name` | 242 |
| variable | `line` | 245 |
| variable | `line` | 248 |
| variable | `branch` | 249 |
| variable | `index` | 249 |
| function | `lcov(evidence, text)` | 253 |
| parameter | `evidence` | 253 |
| parameter | `text` | 253 |
| variable | `name` | 255 |
| variable | `row` | 256 |
| variable | `name` | 258 |
| variable | `_` | 260 |
| variable | `count` | 260 |
| variable | `line` | 260 |
| variable | `block` | 263 |
| variable | `branch` | 263 |
| variable | `count` | 263 |
| variable | `line` | 263 |
| function | `shell_lines(node)` | 274 |
| parameter | `node` | 274 |
| variable | `output` | 276 |
| variable | `pending` | 277 |
| variable | `item` | 279 |
| variable | `position` | 282 |
| function | `assembly_symbols(evidence)` | 291 |
| parameter | `evidence` | 291 |
| variable | `name` | 293 |
| variable | `text` | 293 |
| variable | `definitions` | 294 |
| variable | `exported` | 295 |
| variable | `used` | 296 |
| variable | `line` | 297 |
| variable | `source` | 297 |
| variable | `source` | 298 |
| variable | `label` | 304 |
| variable | `source` | 307 |
| variable | `source` | 309 |
| variable | `column` | 311 |
| variable | `label` | 311 |
| variable | `line` | 311 |
| function | `native_checks(project, work, execute, command)` | 322 |
| parameter | `command` | 322 |
| parameter | `execute` | 322 |
| parameter | `project` | 322 |
| parameter | `work` | 322 |
| variable | `evidence` | 324 |
| variable | `root` | 325 |
| variable | `unused` | 327 |
| variable | `coverage` | 331 |
| variable | `coverage` | 333 |
| function | `unused_checks(evidence, root, execute)` | 340 |
| parameter | `evidence` | 340 |
| parameter | `execute` | 340 |
| parameter | `root` | 340 |
| variable | `project` | 342 |
| variable | `language` | 343 |
| variable | `entry` | 344 |
| variable | `output` | 345 |
| variable | `allowed` | 346 |
| variable | `result` | 347 |
| variable | `parse_failed` | 348 |
| variable | `result` | 351 |
| variable | `item` | 356 |
| variable | `parse_failed` | 357 |
| variable | `tool` | 366 |
| variable | `result` | 368 |
| variable | `item` | 384 |
| variable | `location` | 387 |
| variable | `tool` | 395 |
| variable | `result` | 397 |
| variable | `line` | 415 |
| variable | `item` | 416 |
| variable | `code` | 417 |
| variable | `span` | 419 |
| variable | `tool` | 428 |
| variable | `allowed` | 430 |
| variable | `result` | 431 |
| variable | `parsed` | 448 |
| variable | `parse_failed` | 449 |
| variable | `file` | 450 |
| variable | `item` | 451 |
| variable | `tool` | 459 |
| variable | `allowed` | 461 |
| variable | `result` | 462 |
| variable | `parsed` | 479 |
| variable | `parse_failed` | 480 |
| variable | `file` | 481 |
| variable | `item` | 482 |
| variable | `tool` | 484 |
| variable | `allowed` | 486 |
| variable | `result` | 487 |
| variable | `item` | 499 |
| variable | `parse_failed` | 500 |
| variable | `tool` | 504 |
| variable | `allowed` | 506 |
| variable | `result` | 507 |
| variable | `file` | 524 |
| variable | `item` | 525 |
| variable | `parse_failed` | 526 |
| variable | `tool` | 534 |
| variable | `result` | 536 |
| variable | `line` | 552 |
| variable | `match` | 553 |
| variable | `tool` | 558 |
| variable | `result` | 561 |
| variable | `tool` | 562 |
| function | `measure(evidence, root, execute, command)` | 585 |
| parameter | `command` | 585 |
| parameter | `evidence` | 585 |
| parameter | `execute` | 585 |
| parameter | `root` | 585 |
| variable | `project` | 587 |
| variable | `entry` | 588 |
| variable | `language` | 588 |
| variable | `work` | 589 |
| variable | `build` | 590 |
| variable | `metric` | 591 |
| variable | `tool` | 591 |
| variable | `run` | 592 |
| variable | `metric` | 594 |
| variable | `tool` | 594 |
| variable | `build` | 595 |
| variable | `run` | 605 |
| variable | `metric` | 607 |
| variable | `tool` | 607 |
| variable | `build` | 608 |
| variable | `run` | 623 |
| variable | `metric` | 625 |
| variable | `tool` | 625 |
| variable | `classes` | 626 |
| variable | `build` | 628 |
| variable | `run` | 629 |
| variable | `metric` | 638 |
| variable | `tool` | 638 |
| variable | `build` | 639 |
| variable | `metric` | 641 |
| variable | `tool` | 641 |
| variable | `metric` | 644 |
| variable | `tool` | 644 |
| variable | `run` | 645 |
| variable | `metric` | 647 |
| variable | `tool` | 647 |
| variable | `build` | 648 |
| variable | `metric` | 660 |
| variable | `tool` | 660 |
| variable | `name` | 661 |
| variable | `tree` | 662 |
| variable | `result` | 663 |
| variable | `line` | 670 |
| variable | `metric` | 672 |
| variable | `tool` | 672 |
| variable | `result` | 674 |
| variable | `cases` | 677 |
| variable | `case` | 678 |
| variable | `index` | 678 |
| variable | `output` | 679 |
| variable | `environment` | 680 |
| variable | `run` | 688 |
| variable | `run` | 690 |
| variable | `run` | 701 |
| variable | `result` | 716 |
| variable | `lines` | 730 |
| variable | `name` | 730 |
| variable | `count` | 731 |
| variable | `line` | 731 |
| variable | `trace` | 735 |
| variable | `match` | 736 |
| variable | `current` | 739 |
| variable | `row` | 740 |
| variable | `current` | 742 |
| variable | `_` | 744 |
| variable | `hits` | 744 |
| variable | `line` | 744 |
| variable | `output` | 747 |
| variable | `result` | 748 |
| variable | `lines` | 754 |
| variable | `name` | 754 |
| variable | `note` | 757 |
| variable | `result` | 758 |
| variable | `file` | 761 |
| variable | `profiles` | 764 |
| variable | `result` | 765 |
| variable | `output` | 778 |
| variable | `result` | 779 |
| variable | `output` | 794 |
| variable | `result` | 795 |
| variable | `result` | 816 |
| variable | `row` | 817 |
| variable | `match` | 818 |
| variable | `name` | 820 |
| variable | `existing` | 822 |

## runner/node_checks.cjs

| Kind | Declaration | Line |
|---|---|---|
| variable | `fs` | 12 |
| variable | `path` | 13 |
| variable | `{ fileURLToPath }` | 14 |
| variable | `toolRequire` | 15 |
| variable | `{ Linter }` | 16 |
| variable | `tsParser` | 17 |
| variable | `tsPlugin` | 18 |
| variable | `v8toIstanbul` | 19 |
| function | `reportJson(file)` | 21 |
| function | `main()` | 27 |
| variable | `[mode, input, output, directory]` | 29 |
| variable | `project` | 30 |
| variable | `typed` | 31 |
| variable | `files` | 32 |
| variable | `linter` | 34 |
| variable | `findings` | 35 |
| variable | `file` | 36 |
| variable | `config` | 37 |
| variable | `item` | 43 |
| variable | `collected` | 53 |
| variable | `name` | 54 |
| variable | `report` | 56 |
| variable | `script` | 57 |
| variable | `scriptPath` | 59 |
| variable | `base` | 60 |
| variable | `original` | 61 |
| variable | `expectedPath` | 62 |
| variable | `source` | 64 |
| variable | `sources` | 65 |
| variable | `map` | 67 |
| variable | `converter` | 76 |
| variable | `coverage` | 79 |
| variable | `lines` | 80 |
| variable | `[id, statement]` | 81 |
| variable | `line` | 82 |

## runner/sql_runtime.py

| Kind | Declaration | Line |
|---|---|---|
| variable | `SQL_SPACE` | 21 |
| function | `statements(text)` | 24 |
| parameter | `text` | 24 |
| variable | `output` | 26 |
| variable | `start` | 27 |
| variable | `char` | 28 |
| variable | `index` | 28 |
| variable | `start` | 32 |
| variable | `item` | 37 |
| variable | `index` | 39 |
| variable | `source` | 40 |
| variable | `index` | 43 |
| variable | `end` | 45 |
| variable | `index` | 46 |
| variable | `end` | 48 |
| variable | `index` | 49 |
| variable | `item` | 56 |
| function | `main(entry)` | 59 |
| parameter | `entry` | 59 |
| variable | `text` | 61 |
| variable | `chunks` | 62 |
| variable | `item` | 63 |
| variable | `lines` | 63 |
| variable | `output` | 64 |
| variable | `connection` | 66 |
| variable | `item` | 67 |
| variable | `row` | 77 |

## runner/worker.py

| Kind | Declaration | Line |
|---|---|---|
| variable | `DEADLINE` | 30 |
| variable | `WORK` | 31 |
| variable | `RUNTIME` | 32 |
| function | `prepare_runtime()` | 35 |
| function | `execute(argv, stdin, timeout, env, stdout_path, stderr_path)` | 41 |
| parameter | `argv` | 42 |
| parameter | `stdin` | 43 |
| parameter | `timeout` | 44 |
| parameter | `env` | 46 |
| parameter | `stdout_path` | 47 |
| parameter | `stderr_path` | 48 |
| variable | `remaining` | 51 |
| variable | `started` | 54 |
| variable | `output` | 56 |
| variable | `errors` | 57 |
| variable | `child` | 60 |
| variable | `expired` | 73 |
| variable | `expired` | 77 |
| variable | `code` | 78 |
| variable | `size` | 82 |
| function | `adapter(language, entry)` | 96 |
| parameter | `entry` | 96 |
| parameter | `language` | 96 |
| variable | `plans` | 98 |
| function | `seeds(project)` | 141 |
| parameter | `project` | 141 |
| variable | `rng` | 143 |
| variable | `case` | 144 |
| variable | `corpus` | 144 |
| variable | `boundaries` | 145 |
| variable | `dictionary` | 146 |
| variable | `enabled` | 147 |
| variable | `method` | 149 |
| variable | `rows` | 152 |
| variable | `index` | 153 |
| variable | `method` | 156 |
| variable | `value` | 158 |
| variable | `_` | 160 |
| variable | `value` | 160 |
| variable | `value` | 162 |
| variable | `value` | 169 |
| variable | `data` | 171 |
| variable | `position` | 172 |
| variable | `strategy` | 173 |
| variable | `value` | 184 |
| function | `coverage(command, project)` | 189 |
| parameter | `command` | 189 |
| parameter | `project` | 189 |
| variable | `case` | 196 |
| variable | `measured` | 213 |
| variable | `data` | 216 |
| variable | `files` | 217 |
| variable | `measured_files` | 218 |
| variable | `budget` | 219 |
| variable | `file` | 220 |
| variable | `name` | 221 |
| variable | `measured_file` | 224 |
| variable | `record` | 231 |
| variable | `key` | 240 |
| variable | `measured_file` | 241 |
| variable | `name` | 241 |
| variable | `values` | 242 |
| variable | `budget` | 244 |
| variable | `entry` | 246 |
| variable | `file` | 253 |
| function | `mutants(command, project)` | 258 |
| parameter | `command` | 258 |
| parameter | `project` | 258 |
| variable | `path` | 267 |
| variable | `original` | 268 |
| variable | `tree` | 269 |
| variable | `node` | 270 |
| variable | `sites` | 270 |
| variable | `outcomes` | 271 |
| variable | `index` | 273 |
| variable | `candidate` | 274 |
| variable | `node` | 275 |
| variable | `target` | 275 |
| variable | `compile_check` | 283 |
| variable | `killed` | 287 |
| variable | `inconclusive` | 288 |
| variable | `case` | 289 |
| variable | `result` | 290 |
| variable | `inconclusive` | 291 |
| variable | `killed` | 292 |
| variable | `result` | 297 |
| variable | `inconclusive` | 298 |
| variable | `killed` | 299 |
| variable | `item` | 308 |
| variable | `valid` | 308 |
| variable | `item` | 313 |
| function | `instrumented_fuzz(project)` | 318 |
| parameter | `project` | 318 |
| variable | `engine` | 320 |
| variable | `harness` | 321 |
| variable | `result` | 328 |
| variable | `build` | 332 |
| variable | `argv` | 345 |
| variable | `build` | 347 |
| variable | `argv` | 350 |
| variable | `result` | 353 |
| function | `main()` | 364 |
| variable | `project` | 366 |
| variable | `file` | 369 |
| variable | `build` | 386 |
| variable | `command` | 386 |
| variable | `compilation` | 387 |
| variable | `report` | 388 |
| variable | `times` | 413 |
| variable | `case` | 414 |
| variable | `result` | 415 |
| variable | `passed` | 416 |
| variable | `_` | 424 |
| variable | `benchmark` | 425 |
| variable | `findings` | 461 |
| variable | `corpus` | 462 |
| variable | `method` | 463 |
| variable | `value` | 463 |
| variable | `result` | 464 |
| variable | `method` | 490 |

## scripts/code_index.py

| Kind | Declaration | Line |
|---|---|---|
| variable | `ROOT` | 21 |
| variable | `DIRECTORIES` | 22 |
| function | `strip_map(text)` | 25 |
| parameter | `text` | 25 |
| function | `symbols(text, python)` | 32 |
| parameter | `python` | 32 |
| parameter | `text` | 32 |
| variable | `rows` | 34 |
| variable | `tree` | 36 |
| variable | `node` | 37 |
| variable | `kind` | 39 |
| variable | `name` | 40 |
| variable | `name` | 42 |
| variable | `argument` | 46 |
| variable | `line` | 56 |
| variable | `value` | 56 |
| variable | `match` | 59 |
| variable | `match` | 61 |
| variable | `match` | 63 |
| parameter | `row` | 65 |
| function | `header(rows, python)` | 68 |
| parameter | `python` | 68 |
| parameter | `rows` | 68 |
| variable | `grouped` | 70 |
| variable | `kind` | 70 |
| variable | `kind` | 71 |
| variable | `line` | 71 |
| variable | `name` | 71 |
| variable | `descriptions` | 73 |
| variable | `descriptions` | 77 |
| variable | `kind` | 79 |
| variable | `values` | 79 |
| variable | `value` | 83 |
| variable | `value` | 84 |
| function | `render(path)` | 87 |
| parameter | `path` | 87 |
| variable | `original` | 89 |
| variable | `python` | 90 |
| variable | `revised` | 91 |
| variable | `_` | 92 |
| variable | `rows` | 93 |
| variable | `candidate` | 94 |
| variable | `revised` | 97 |
| function | `main()` | 101 |
| variable | `parser` | 103 |
| variable | `args` | 105 |
| variable | `paths` | 106 |
| variable | `directory` | 109 |
| variable | `path` | 110 |
| parameter | `path` | 114 |
| variable | `index` | 116 |
| variable | `stale` | 122 |
| variable | `path` | 123 |
| variable | `rows` | 124 |
| variable | `updated` | 124 |
| variable | `index` | 129 |
| variable | `index` | 135 |
| variable | `kind` | 136 |
| variable | `line` | 136 |
| variable | `name` | 136 |
| variable | `expected` | 139 |
| variable | `output` | 140 |

## scripts/frozen_entry.py

| Kind | Declaration | Line |
|---|---|---|

## scripts/license_bundle.py

| Kind | Declaration | Line |
|---|---|---|
| function | `main()` | 17 |
| variable | `root` | 19 |
| variable | `output` | 20 |
| variable | `records` | 23 |
| variable | `distribution` | 24 |
| variable | `name` | 25 |
| variable | `file` | 34 |
| variable | `target` | 40 |
| variable | `python_license` | 43 |
| variable | `candidates` | 50 |
| variable | `candidate` | 51 |
| variable | `folder` | 59 |
| variable | `path` | 66 |
| variable | `target` | 68 |

## scripts/private_worker_checks.py

| Kind | Declaration | Line |
|---|---|---|
| function | `main()` | 22 |
| variable | `temporary` | 24 |
| variable | `app` | 25 |
| variable | `client` | 30 |
| variable | `key` | 38 |
| variable | `language` | 40 |
| variable | `revision` | 41 |
| variable | `job` | 44 |
| variable | `deadline` | 45 |
| variable | `report` | 47 |

## scripts/push_analysis.py

| Kind | Declaration | Line |
|---|---|---|
| function | `main()` | 26 |
| variable | `output` | 28 |
| variable | `manifest` | 30 |
| variable | `project` | 31 |
| variable | `evidence` | 32 |
| variable | `config` | 39 |
| variable | `config_json` | 40 |
| variable | `router` | 41 |
| variable | `directory` | 44 |
| variable | `path` | 45 |
| variable | `router` | 47 |
| variable | `router` | 49 |
| variable | `tests` | 51 |
| variable | `payload` | 52 |
| variable | `tested` | 54 |
| variable | `generated` | 55 |
| variable | `improved` | 56 |
| variable | `replacements` | 57 |
| variable | `item` | 59 |
| variable | `row` | 59 |
| variable | `candidate` | 61 |

## scripts/release_archive.py

| Kind | Declaration | Line |
|---|---|---|
| function | `write_release_checksum(path)` | 18 |
| parameter | `path` | 18 |
| variable | `stream` | 20 |
| variable | `digest` | 21 |
| function | `main()` | 27 |
| variable | `root` | 29 |
| variable | `platform` | 30 |
| variable | `folder` | 31 |
| variable | `version` | 40 |
| variable | `base` | 41 |
| variable | `path` | 43 |

## scripts/training_checks.py

| Kind | Declaration | Line |
|---|---|---|
| function | `main()` | 20 |
| variable | `key` | 22 |
| variable | `app` | 23 |
| variable | `client` | 24 |
| variable | `body` | 25 |
| variable | `response` | 30 |
| variable | `result` | 33 |

## scripts/worker_checks.py

| Kind | Declaration | Line |
|---|---|---|
| class | `Evidence` | 26 |
| function | `__setitem__(self, key, value)` | 29 |
| parameter | `key` | 29 |
| parameter | `self` | 29 |
| parameter | `value` | 29 |
| variable | `path` | 32 |
| variable | `temporary` | 34 |
| function | `main()` | 39 |
| variable | `reports` | 41 |
| variable | `baseline_errors` | 42 |
| variable | `language` | 43 |
| variable | `result` | 44 |
| variable | `key` | 55 |
| variable | `acceptance` | 58 |
| variable | `native_errors` | 59 |
| variable | `language` | 60 |
| variable | `missing_line` | 61 |
| variable | `project` | 61 |
| variable | `unused_line` | 61 |
| variable | `result` | 62 |
| variable | `key` | 69 |
| variable | `language` | 90 |
| variable | `project` | 91 |
| variable | `result` | 92 |
| variable | `suffix` | 94 |
| variable | `item` | 100 |
| function | `assert_native_locations(language, result, project, unused_line, missing_line)` | 111 |
| parameter | `language` | 111 |
| parameter | `missing_line` | 111 |
| parameter | `project` | 111 |
| parameter | `result` | 111 |
| parameter | `unused_line` | 111 |
| variable | `item` | 117 |
| variable | `measured_file` | 120 |
| function | `original_scenarios(reports)` | 125 |
| parameter | `reports` | 125 |
| variable | `python` | 127 |
| variable | `bad` | 141 |
| variable | `invalid` | 145 |
| variable | `item` | 150 |
| variable | `attack` | 152 |
| variable | `code` | 163 |
| variable | `name` | 163 |
| variable | `target` | 164 |
| variable | `cpp` | 168 |
| variable | `web_demo` | 207 |
| variable | `located` | 213 |
| variable | `measured` | 230 |
| variable | `item` | 237 |
| variable | `crashing` | 239 |
| variable | `item` | 256 |
| variable | `mapped` | 258 |
| variable | `item` | 275 |
| variable | `item` | 285 |

## studio/__init__.py

| Kind | Declaration | Line |
|---|---|---|

## studio/accounts.py

| Kind | Declaration | Line |
|---|---|---|
| variable | `SESSION_SECONDS` | 26 |
| variable | `IDLE_SECONDS` | 27 |
| variable | `HASH_SLOTS` | 28 |
| function | `digest(value)` | 31 |
| parameter | `value` | 31 |
| function | `password_hash(password, salt)` | 36 |
| parameter | `password` | 36 |
| parameter | `salt` | 36 |
| variable | `salt` | 38 |
| variable | `key` | 40 |
| function | `password_matches(password, stored)` | 46 |
| parameter | `password` | 46 |
| parameter | `stored` | 46 |
| variable | `_` | 49 |
| variable | `salt` | 49 |
| variable | `version` | 49 |
| class | `Accounts` | 55 |
| function | `__init__(self, path)` | 58 |
| parameter | `path` | 58 |
| parameter | `self` | 58 |
| variable | `db` | 64 |
| function | `connection(self)` | 80 |
| parameter | `self` | 80 |
| variable | `db` | 82 |
| function | `throttle(self, key, maximum, window)` | 91 |
| parameter | `key` | 91 |
| parameter | `maximum` | 91 |
| parameter | `self` | 91 |
| parameter | `window` | 91 |
| variable | `now` | 93 |
| variable | `db` | 94 |
| variable | `row` | 97 |
| variable | `count` | 98 |
| function | `register(self, username, password)` | 105 |
| parameter | `password` | 105 |
| parameter | `self` | 105 |
| parameter | `username` | 105 |
| variable | `owner` | 107 |
| variable | `recovery` | 107 |
| variable | `hashed` | 108 |
| variable | `db` | 109 |
| function | `login(self, username, password)` | 118 |
| parameter | `password` | 118 |
| parameter | `self` | 118 |
| parameter | `username` | 118 |
| variable | `db` | 120 |
| variable | `row` | 121 |
| variable | `valid` | 122 |
| function | `session(self, owner)` | 125 |
| parameter | `owner` | 125 |
| parameter | `self` | 125 |
| variable | `now` | 127 |
| variable | `token` | 127 |
| variable | `db` | 128 |
| function | `owner(self, token)` | 140 |
| parameter | `self` | 140 |
| parameter | `token` | 140 |
| variable | `now` | 142 |
| variable | `db` | 143 |
| variable | `row` | 144 |
| function | `revoke(self, token)` | 152 |
| parameter | `self` | 152 |
| parameter | `token` | 152 |
| variable | `db` | 154 |
| function | `vault(self, owner)` | 157 |
| parameter | `owner` | 157 |
| parameter | `self` | 157 |
| variable | `db` | 159 |
| variable | `row` | 160 |
| function | `save(self, owner, envelope, revision)` | 167 |
| parameter | `envelope` | 167 |
| parameter | `owner` | 167 |
| parameter | `revision` | 167 |
| parameter | `self` | 167 |
| variable | `db` | 169 |
| variable | `row` | 171 |
| function | `reset(self, username, recovery, password)` | 180 |
| parameter | `password` | 180 |
| parameter | `recovery` | 180 |
| parameter | `self` | 180 |
| parameter | `username` | 180 |
| variable | `db` | 182 |
| variable | `row` | 183 |
| variable | `fresh` | 186 |
| variable | `hashed` | 186 |
| variable | `db` | 187 |
| variable | `updated` | 188 |
| function | `delete(self, owner, password)` | 197 |
| parameter | `owner` | 197 |
| parameter | `password` | 197 |
| parameter | `self` | 197 |
| variable | `db` | 199 |
| variable | `row` | 200 |
| variable | `db` | 203 |
| function | `decode_field(value, minimum, maximum)` | 209 |
| parameter | `maximum` | 209 |
| parameter | `minimum` | 209 |
| parameter | `value` | 209 |
| variable | `result` | 212 |

## studio/analysis.py

| Kind | Declaration | Line |
|---|---|---|
| function | `inspect_source(project)` | 23 |
| parameter | `project` | 23 |
| variable | `file` | 25 |
| variable | `text` | 25 |
| variable | `lines` | 26 |
| variable | `findings` | 27 |
| variable | `truncated` | 28 |
| variable | `files` | 29 |
| variable | `patterns` | 30 |
| variable | `functions` | 36 |
| variable | `branches` | 37 |
| variable | `python_files` | 38 |
| variable | `file` | 40 |
| variable | `file` | 45 |
| variable | `used` | 45 |
| variable | `file` | 46 |
| variable | `digest` | 49 |
| variable | `located` | 52 |
| variable | `metadata` | 52 |
| variable | `functions` | 55 |
| variable | `branches` | 56 |
| variable | `content` | 58 |
| variable | `char` | 59 |
| variable | `index` | 59 |
| variable | `offsets` | 59 |
| variable | `message` | 60 |
| variable | `pattern` | 60 |
| variable | `match` | 61 |
| variable | `line` | 64 |
| variable | `previous` | 65 |
| variable | `truncated` | 78 |
| variable | `line` | 83 |
| function | `compare(baseline, candidate, priorities)` | 93 |
| parameter | `baseline` | 93 |
| parameter | `candidate` | 93 |
| parameter | `priorities` | 93 |
| variable | `reasons` | 95 |
| variable | `result` | 96 |
| variable | `dimensions` | 117 |
| variable | `area` | 118 |
| variable | `key` | 118 |
| variable | `metric` | 118 |
| variable | `after` | 124 |
| variable | `before` | 124 |
| variable | `metric` | 127 |
| variable | `total` | 127 |
| variable | `score` | 128 |
| variable | `metric` | 129 |
| variable | `value` | 129 |

## studio/api.py

| Kind | Declaration | Line |
|---|---|---|
| function | `create_app(data_directory, token, ui_directory, config, private_mode, owned_providers)` | 35 |
| parameter | `data_directory` | 36 |
| parameter | `token` | 37 |
| parameter | `ui_directory` | 38 |
| parameter | `config` | 39 |
| parameter | `private_mode` | 40 |
| parameter | `owned_providers` | 41 |
| variable | `store` | 46 |
| variable | `providers` | 47 |
| variable | `active` | 48 |
| variable | `semaphore` | 49 |
| variable | `ai_semaphore` | 50 |
| function | `lifespan(app)` | 53 |
| parameter | `app` | 53 |
| function | `probe()` | 56 |
| variable | `checking` | 62 |
| variable | `owned` | 66 |
| variable | `task` | 67 |
| variable | `app` | 71 |
| function | `private_invalid(request, error)` | 90 |
| parameter | `error` | 90 |
| parameter | `request` | 90 |
| function | `guard(request, call_next)` | 95 |
| parameter | `call_next` | 95 |
| parameter | `request` | 95 |
| variable | `host` | 97 |
| variable | `origin` | 98 |
| variable | `permitted` | 99 |
| variable | `body` | 108 |
| variable | `chunk` | 109 |
| variable | `response` | 114 |
| function | `health()` | 124 |
| function | `shutdown()` | 129 |
| variable | `callback` | 131 |
| function | `status()` | 138 |
| function | `capabilities()` | 147 |
| function | `review(project)` | 152 |
| parameter | `project` | 152 |
| function | `history()` | 157 |
| function | `save(project, parent)` | 162 |
| parameter | `parent` | 162 |
| parameter | `project` | 162 |
| function | `revision(identifier)` | 170 |
| parameter | `identifier` | 170 |
| function | `work(identifier, project)` | 177 |
| parameter | `identifier` | 177 |
| parameter | `project` | 177 |
| variable | `result` | 182 |
| function | `start(identifier)` | 197 |
| parameter | `identifier` | 197 |
| variable | `project` | 202 |
| variable | `job` | 205 |
| variable | `task` | 206 |
| function | `get_run(identifier)` | 212 |
| parameter | `identifier` | 212 |
| function | `report(identifier, format)` | 220 |
| parameter | `format` | 220 |
| parameter | `identifier` | 220 |
| variable | `result` | 223 |
| variable | `source` | 224 |
| function | `compare_runs(baseline, candidate)` | 241 |
| parameter | `baseline` | 241 |
| parameter | `candidate` | 241 |
| variable | `new` | 244 |
| variable | `old` | 244 |
| variable | `new_revision` | 245 |
| variable | `old_revision` | 245 |
| function | `ai(request)` | 256 |
| parameter | `request` | 256 |

## studio/catalog.py

| Kind | Declaration | Line |
|---|---|---|
| variable | `TEST_NAMES` | 14 |
| variable | `HUMAN` | 64 |
| variable | `EXTERNAL` | 65 |
| variable | `AUTOMATED` | 66 |
| function | `catalog()` | 69 |
| variable | `rows` | 71 |
| variable | `name` | 72 |
| variable | `number` | 72 |
| variable | `mode` | 73 |
| variable | `requirement` | 82 |

## studio/cli.py

| Kind | Declaration | Line |
|---|---|---|
| function | `main()` | 29 |
| variable | `parser` | 31 |
| variable | `args` | 39 |
| variable | `token` | 41 |
| variable | `application` | 44 |
| variable | `server` | 45 |
| variable | `project` | 51 |
| variable | `result` | 52 |
| variable | `failed` | 65 |
| variable | `failed` | 70 |

## studio/execution.py

| Kind | Declaration | Line |
|---|---|---|
| variable | `IMAGE` | 28 |
| variable | `DOCKER` | 29 |
| function | `command(argv, timeout, output_limit)` | 32 |
| parameter | `argv` | 32 |
| parameter | `output_limit` | 32 |
| parameter | `timeout` | 32 |
| variable | `environment` | 34 |
| variable | `environment` | 36 |
| variable | `selector` | 37 |
| variable | `process` | 45 |
| variable | `output` | 48 |
| function | `read()` | 50 |
| variable | `chunk` | 53 |
| function | `container_arguments(input_directory, name)` | 69 |
| parameter | `input_directory` | 69 |
| parameter | `name` | 69 |
| function | `diagnostics(local_only)` | 102 |
| parameter | `local_only` | 102 |
| variable | `endpoint` | 106 |
| variable | `context` | 108 |
| variable | `context_code` | 108 |
| variable | `endpoint` | 118 |
| variable | `config` | 125 |
| variable | `prefix` | 126 |
| variable | `code` | 127 |
| variable | `output` | 127 |
| variable | `_` | 130 |
| variable | `found` | 130 |
| variable | `code` | 136 |
| variable | `output` | 136 |
| variable | `_` | 139 |
| variable | `found` | 139 |
| function | `run(project, local_only, scratch)` | 160 |
| parameter | `local_only` | 160 |
| parameter | `project` | 160 |
| parameter | `scratch` | 160 |
| variable | `ready` | 162 |
| variable | `static` | 163 |
| variable | `name` | 166 |
| variable | `directory` | 169 |
| variable | `path` | 170 |
| variable | `config` | 173 |
| variable | `prefix` | 175 |
| variable | `prefix` | 177 |
| variable | `code` | 179 |
| variable | `output` | 179 |
| variable | `marker` | 180 |
| variable | `line` | 181 |
| variable | `lines` | 181 |
| variable | `result` | 189 |

## studio/locations.py

| Kind | Declaration | Line |
|---|---|---|
| variable | `LIMIT` | 20 |
| variable | `ANSI` | 21 |
| function | `tool_locations(result, project)` | 24 |
| parameter | `project` | 24 |
| parameter | `result` | 24 |
| variable | `file` | 26 |
| variable | `sources` | 26 |
| variable | `name` | 30 |
| variable | `text` | 30 |
| variable | `name` | 40 |
| variable | `names` | 40 |
| variable | `path` | 41 |
| variable | `patterns` | 42 |
| variable | `details` | 49 |
| variable | `artifact` | 55 |
| variable | `name` | 55 |
| variable | `text` | 55 |
| variable | `findings` | 57 |
| variable | `unlocated` | 58 |
| variable | `seen` | 59 |
| variable | `truncated` | 60 |
| function | `process(record, stage, failed)` | 62 |
| parameter | `failed` | 62 |
| parameter | `record` | 62 |
| parameter | `stage` | 62 |
| variable | `before` | 65 |
| variable | `stream` | 66 |
| variable | `output` | 67 |
| variable | `message` | 68 |
| variable | `pattern` | 69 |
| variable | `match` | 70 |
| variable | `name` | 71 |
| variable | `line` | 77 |
| variable | `column` | 80 |
| variable | `key` | 85 |
| variable | `truncated` | 90 |
| variable | `compilation` | 115 |
| variable | `case` | 117 |
| variable | `index` | 117 |
| variable | `generated` | 119 |
| variable | `fuzz` | 121 |
| variable | `finding` | 122 |
| variable | `index` | 122 |
| variable | `item` | 127 |
| variable | `line` | 128 |
| variable | `name` | 128 |
| variable | `truncated` | 134 |

## studio/models.py

| Kind | Declaration | Line |
|---|---|---|
| variable | `LANGUAGES` | 24 |
| variable | `Language` | 38 |
| variable | `FUZZ_METHODS` | 52 |
| class | `Contract` | 64 |
| variable | `model_config` | 67 |
| class | `SourceFile` | 70 |
| variable | `name` | 73 |
| variable | `content` | 74 |
| variable | `encoding` | 75 |
| function | `safe_name(cls, value)` | 79 |
| parameter | `cls` | 79 |
| parameter | `value` | 79 |
| variable | `stem` | 81 |
| variable | `i` | 89 |
| variable | `i` | 90 |
| function | `bytes(self)` | 95 |
| parameter | `self` | 95 |
| class | `TestCase` | 107 |
| variable | `name` | 110 |
| variable | `stdin` | 111 |
| variable | `stdout` | 112 |
| variable | `exit_code` | 113 |
| class | `Priorities` | 116 |
| variable | `runtime` | 119 |
| variable | `memory` | 120 |
| variable | `readability` | 121 |
| variable | `footprint` | 122 |
| variable | `scrutiny` | 123 |
| function | `nonzero(self)` | 126 |
| parameter | `self` | 126 |
| class | `Project` | 136 |
| variable | `title` | 139 |
| variable | `language` | 140 |
| variable | `entry` | 141 |
| variable | `files` | 142 |
| variable | `cases` | 143 |
| variable | `requirements` | 144 |
| variable | `tests` | 145 |
| variable | `fuzz_methods` | 146 |
| variable | `fuzz_cases` | 147 |
| variable | `seed` | 148 |
| variable | `benchmark_repeats` | 149 |
| variable | `mutation` | 150 |
| variable | `fuzz_engine` | 151 |
| variable | `fuzz_harness` | 152 |
| variable | `priorities` | 153 |
| function | `coherent(self)` | 156 |
| parameter | `self` | 156 |
| variable | `file` | 158 |
| variable | `names` | 158 |
| variable | `file` | 159 |
| variable | `reserved` | 161 |
| variable | `file` | 176 |
| variable | `file` | 178 |
| variable | `method` | 180 |
| class | `AIRequest` | 187 |
| variable | `task` | 190 |
| variable | `project` | 191 |
| variable | `prompt` | 192 |
| variable | `consent` | 193 |
| class | `Proposal` | 196 |
| variable | `explanation` | 199 |
| variable | `files` | 200 |
| variable | `tests` | 201 |
| variable | `suggestions` | 202 |

## studio/permissions.py

| Kind | Declaration | Line |
|---|---|---|
| function | `protect_directory(root)` | 18 |
| parameter | `root` | 18 |
| variable | `root` | 20 |
| variable | `system` | 26 |
| variable | `flags` | 27 |
| variable | `identity` | 28 |
| variable | `rows` | 35 |

## studio/private_api.py

| Kind | Declaration | Line |
|---|---|---|
| variable | `CSP` | 36 |
| variable | `HISTORY_STOP_BYTES` | 37 |
| class | `Boundary` | 40 |
| function | `__init__(self, app, manager, port)` | 43 |
| parameter | `app` | 43 |
| parameter | `manager` | 43 |
| parameter | `port` | 43 |
| parameter | `self` | 43 |
| function | `__call__(self, scope, receive, send)` | 49 |
| parameter | `receive` | 49 |
| parameter | `scope` | 49 |
| parameter | `self` | 49 |
| parameter | `send` | 49 |
| variable | `raw` | 53 |
| variable | `headers` | 54 |
| variable | `k` | 54 |
| variable | `v` | 54 |
| function | `guarded(message)` | 56 |
| parameter | `message` | 56 |
| variable | `k` | 61 |
| variable | `v` | 61 |
| function | `deny(status, detail)` | 77 |
| parameter | `detail` | 77 |
| parameter | `status` | 77 |
| variable | `_` | 83 |
| variable | `k` | 83 |
| variable | `cookies` | 101 |
| variable | `token` | 106 |
| variable | `account` | 107 |
| variable | `chunks` | 115 |
| variable | `length` | 115 |
| variable | `message` | 117 |
| variable | `data` | 120 |
| variable | `length` | 121 |
| variable | `delivered` | 127 |
| function | `replay()` | 129 |
| variable | `delivered` | 133 |
| class | `Closed` | 140 |
| variable | `model_config` | 143 |
| class | `Credentials` | 146 |
| variable | `alias` | 149 |
| variable | `password` | 150 |
| class | `Recovery` | 153 |
| variable | `recovery` | 156 |
| class | `Unlock` | 159 |
| variable | `key` | 162 |
| variable | `salt` | 163 |
| class | `Activity` | 166 |
| variable | `idle_seconds` | 169 |
| class | `Delete` | 172 |
| variable | `password` | 175 |
| variable | `confirm` | 176 |
| class | `Provider` | 179 |
| variable | `id` | 182 |
| variable | `kind` | 183 |
| variable | `url` | 184 |
| variable | `model` | 185 |
| variable | `key` | 186 |
| variable | `retain_key` | 187 |
| variable | `token_parameter` | 188 |
| variable | `temperature` | 189 |
| class | `Settings` | 192 |
| variable | `providers` | 195 |
| variable | `routes` | 196 |
| function | `coherent(self)` | 201 |
| parameter | `self` | 201 |
| variable | `ids` | 203 |
| variable | `p` | 203 |
| variable | `value` | 204 |
| variable | `p` | 207 |
| function | `public_settings(manager)` | 213 |
| parameter | `manager` | 213 |
| variable | `keys` | 215 |
| variable | `settings` | 215 |
| variable | `data` | 216 |
| variable | `p` | 218 |
| class | `Proxy` | 226 |
| function | `__init__(self, manager)` | 229 |
| parameter | `manager` | 229 |
| parameter | `self` | 229 |
| function | `__call__(self, scope, receive, send)` | 233 |
| parameter | `receive` | 233 |
| parameter | `scope` | 233 |
| parameter | `self` | 233 |
| parameter | `send` | 233 |
| variable | `manager` | 237 |
| variable | `app` | 240 |
| variable | `path` | 245 |
| variable | `db` | 251 |
| variable | `count` | 252 |
| variable | `headers` | 264 |
| variable | `forwarded` | 273 |
| variable | `k` | 274 |
| variable | `v` | 274 |
| function | `create_private_app(root, port, ui, launcher_token, nonce)` | 284 |
| parameter | `launcher_token` | 285 |
| parameter | `nonce` | 285 |
| parameter | `port` | 285 |
| parameter | `root` | 285 |
| parameter | `ui` | 285 |
| variable | `manager` | 288 |
| function | `lifespan(app)` | 292 |
| parameter | `app` | 292 |
| function | `idle()` | 295 |
| variable | `task` | 309 |
| variable | `app` | 319 |
| function | `invalid(request, error)` | 331 |
| parameter | `error` | 331 |
| parameter | `request` | 331 |
| function | `bad_value(request, error)` | 336 |
| parameter | `error` | 336 |
| parameter | `request` | 336 |
| function | `bad_disk(request, error)` | 341 |
| parameter | `error` | 341 |
| parameter | `request` | 341 |
| function | `identify(request)` | 347 |
| parameter | `request` | 347 |
| function | `signed(owner, data)` | 351 |
| parameter | `data` | 351 |
| parameter | `owner` | 351 |
| variable | `response` | 353 |
| function | `auth_limit(alias)` | 364 |
| parameter | `alias` | 364 |
| function | `health()` | 372 |
| function | `shutdown(request)` | 383 |
| parameter | `request` | 383 |
| variable | `callback` | 389 |
| function | `register(data)` | 396 |
| parameter | `data` | 396 |
| variable | `owner` | 400 |
| variable | `recovery` | 400 |
| function | `login(data)` | 406 |
| parameter | `data` | 406 |
| variable | `owner` | 409 |
| function | `reset(data)` | 415 |
| parameter | `data` | 415 |
| variable | `db` | 419 |
| variable | `row` | 420 |
| variable | `fresh` | 426 |
| function | `account(request)` | 432 |
| parameter | `request` | 432 |
| variable | `owner` | 434 |
| variable | `session` | 434 |
| function | `unlock(request, data)` | 442 |
| parameter | `data` | 442 |
| parameter | `request` | 442 |
| variable | `owner` | 444 |
| variable | `session` | 444 |
| function | `activity(request, data)` | 453 |
| parameter | `data` | 453 |
| parameter | `request` | 453 |
| function | `save(request)` | 461 |
| parameter | `request` | 461 |
| function | `lock(request)` | 468 |
| parameter | `request` | 468 |
| variable | `owner` | 471 |
| variable | `session` | 471 |
| function | `logout(request)` | 476 |
| parameter | `request` | 476 |
| variable | `owner` | 479 |
| variable | `session` | 479 |
| variable | `response` | 483 |
| function | `delete(request, data)` | 488 |
| parameter | `data` | 488 |
| parameter | `request` | 488 |
| variable | `_` | 491 |
| variable | `owner` | 491 |
| variable | `db` | 492 |
| variable | `row` | 493 |
| variable | `response` | 499 |
| function | `backup(request)` | 504 |
| parameter | `request` | 504 |
| variable | `_` | 506 |
| variable | `owner` | 506 |
| variable | `path` | 507 |
| function | `get_providers(request)` | 515 |
| parameter | `request` | 515 |
| function | `providers(request, data)` | 522 |
| parameter | `data` | 522 |
| parameter | `request` | 522 |
| variable | `keys` | 526 |
| variable | `old` | 526 |
| variable | `rows` | 527 |
| variable | `provider` | 528 |
| variable | `row` | 529 |
| variable | `p` | 531 |
| variable | `previous` | 531 |
| variable | `config` | 536 |
| variable | `router` | 537 |
| variable | `k` | 539 |
| variable | `p` | 539 |
| variable | `v` | 539 |
| variable | `p` | 542 |

## studio/private_cli.py

| Kind | Declaration | Line |
|---|---|---|
| function | `data_directory()` | 26 |
| variable | `base` | 31 |
| variable | `base` | 33 |
| variable | `base` | 35 |
| function | `parent_guard(server)` | 39 |
| parameter | `server` | 39 |
| variable | `pid` | 41 |
| variable | `started` | 42 |
| variable | `parent` | 46 |
| function | `main()` | 60 |
| variable | `parser` | 62 |
| variable | `args` | 67 |
| variable | `bundle` | 70 |
| variable | `ui` | 71 |
| variable | `listener` | 72 |
| variable | `port` | 75 |
| variable | `app` | 76 |
| variable | `server` | 83 |
| variable | `thread` | 96 |
| variable | `deadline` | 100 |
| variable | `url` | 105 |

## studio/private_workspace.py

| Kind | Declaration | Line |
|---|---|---|
| variable | `HISTORY_RECOVERY_BYTES` | 34 |
| function | `atomic_json(path, value)` | 37 |
| parameter | `path` | 37 |
| parameter | `value` | 37 |
| variable | `descriptor` | 39 |
| variable | `name` | 39 |
| variable | `stream` | 41 |
| class | `InstanceLock` | 50 |
| function | `__init__(self, path)` | 53 |
| parameter | `path` | 53 |
| parameter | `self` | 53 |
| function | `close(self)` | 73 |
| parameter | `self` | 73 |
| class | `Workspaces` | 78 |
| function | `__init__(self, root)` | 81 |
| parameter | `root` | 81 |
| parameter | `self` | 81 |
| variable | `allowed` | 87 |
| variable | `p` | 96 |
| function | `archive(self, owner)` | 116 |
| parameter | `owner` | 116 |
| parameter | `self` | 116 |
| variable | `c` | 119 |
| function | `status(self, owner, session)` | 124 |
| parameter | `owner` | 124 |
| parameter | `self` | 124 |
| parameter | `session` | 124 |
| variable | `config` | 126 |
| function | `providers(self)` | 136 |
| parameter | `self` | 136 |
| variable | `path` | 138 |
| variable | `data` | 139 |
| variable | `data` | 143 |
| variable | `k` | 145 |
| variable | `p` | 145 |
| variable | `v` | 145 |
| variable | `p` | 148 |
| function | `unlock(self, owner, session, encoded, salt)` | 150 |
| parameter | `encoded` | 150 |
| parameter | `owner` | 150 |
| parameter | `salt` | 150 |
| parameter | `self` | 150 |
| parameter | `session` | 150 |
| variable | `key` | 154 |
| variable | `current` | 155 |
| variable | `config` | 156 |
| variable | `proof` | 159 |
| variable | `nonce` | 170 |
| variable | `config` | 171 |
| variable | `keys` | 200 |
| variable | `settings` | 200 |
| function | `require(self, owner, session)` | 214 |
| parameter | `owner` | 214 |
| parameter | `self` | 214 |
| parameter | `session` | 214 |
| function | `save(self, force)` | 220 |
| parameter | `force` | 220 |
| parameter | `self` | 220 |
| variable | `current` | 228 |
| function | `remove_active(self, owner)` | 235 |
| parameter | `owner` | 235 |
| parameter | `self` | 235 |
| function | `lock(self, owner)` | 247 |
| parameter | `owner` | 247 |
| parameter | `self` | 247 |
| function | `delete(self, owner)` | 265 |
| parameter | `owner` | 265 |
| parameter | `self` | 265 |
| function | `close(self)` | 273 |
| parameter | `self` | 273 |

## studio/providers.py

| Kind | Declaration | Line |
|---|---|---|
| variable | `SYSTEM` | 25 |
| class | `Providers` | 37 |
| function | `__init__(self, path, settings, credentials)` | 40 |
| parameter | `credentials` | 41 |
| parameter | `path` | 41 |
| parameter | `self` | 41 |
| parameter | `settings` | 41 |
| variable | `provider` | 50 |
| variable | `url` | 51 |
| function | `public(self)` | 61 |
| parameter | `self` | 61 |
| variable | `row` | 71 |
| function | `request(self, request)` | 74 |
| parameter | `request` | 74 |
| parameter | `self` | 74 |
| variable | `identifier` | 78 |
| variable | `provider` | 79 |
| variable | `row` | 79 |
| variable | `key` | 82 |
| variable | `source` | 85 |
| variable | `row` | 87 |
| variable | `user` | 88 |
| variable | `headers` | 91 |
| variable | `kind` | 92 |
| variable | `headers` | 94 |
| variable | `body` | 95 |
| variable | `body` | 104 |
| variable | `temperature` | 112 |
| variable | `client` | 115 |
| variable | `response` | 116 |
| variable | `data` | 118 |
| variable | `chunk` | 119 |
| variable | `message` | 123 |
| variable | `text` | 125 |
| variable | `block` | 126 |
| variable | `text` | 129 |
| variable | `text` | 131 |
| variable | `text` | 135 |
| variable | `proposal` | 136 |
| function | `key(self, provider)` | 146 |
| parameter | `provider` | 146 |
| parameter | `self` | 146 |

## studio/reports.py

| Kind | Declaration | Line |
|---|---|---|
| function | `location_summary(run)` | 21 |
| parameter | `run` | 21 |
| variable | `result` | 23 |
| variable | `findings` | 24 |
| function | `escape(value)` | 26 |
| parameter | `value` | 26 |
| variable | `rows` | 30 |
| variable | `value` | 34 |
| variable | `item` | 43 |
| variable | `coverage` | 45 |
| variable | `data` | 67 |
| variable | `name` | 67 |
| variable | `unknown` | 69 |
| variable | `item` | 71 |
| variable | `unknown` | 73 |
| variable | `data` | 79 |
| variable | `name` | 79 |
| variable | `key` | 94 |
| variable | `key` | 97 |
| function | `html_report(run)` | 106 |
| parameter | `run` | 106 |
| variable | `evidence` | 108 |
| function | `bundle(run, revision)` | 118 |
| parameter | `revision` | 118 |
| parameter | `run` | 118 |
| variable | `buffer` | 120 |
| variable | `archive` | 121 |
| variable | `file` | 125 |

## studio/source_checks.py

| Kind | Declaration | Line |
|---|---|---|
| function | `source_location(name, lines, digest, node)` | 20 |
| parameter | `digest` | 20 |
| parameter | `lines` | 20 |
| parameter | `name` | 20 |
| parameter | `node` | 20 |
| variable | `line` | 22 |
| variable | `prefix` | 23 |
| function | `block_nodes(root)` | 27 |
| parameter | `root` | 27 |
| variable | `pending` | 29 |
| variable | `node` | 31 |
| function | `python_checks(name, text, project_references)` | 49 |
| parameter | `name` | 49 |
| parameter | `project_references` | 49 |
| parameter | `text` | 49 |
| variable | `findings` | 51 |
| variable | `digest` | 52 |
| variable | `lines` | 54 |
| function | `add(node, code, message, severity)` | 56 |
| parameter | `code` | 56 |
| parameter | `message` | 56 |
| parameter | `node` | 56 |
| parameter | `severity` | 56 |
| variable | `tree` | 70 |
| variable | `table` | 72 |
| variable | `line` | 74 |
| variable | `nodes` | 94 |
| variable | `exports` | 95 |
| variable | `dynamic_exports` | 96 |
| variable | `node` | 97 |
| variable | `t` | 99 |
| variable | `item` | 102 |
| variable | `item` | 104 |
| variable | `dynamic_exports` | 106 |
| variable | `keyword` | 116 |
| variable | `value` | 124 |
| variable | `targets` | 125 |
| variable | `word` | 131 |
| variable | `target` | 132 |
| function | `scope(root, symbols)` | 137 |
| parameter | `root` | 137 |
| parameter | `symbols` | 137 |
| variable | `children` | 139 |
| variable | `captures` | 140 |
| variable | `pending` | 141 |
| variable | `child` | 143 |
| variable | `symbol` | 146 |
| variable | `bindings` | 150 |
| variable | `definitions` | 151 |
| variable | `node` | 152 |
| variable | `alias` | 156 |
| variable | `symbol` | 165 |
| variable | `identifier` | 166 |
| variable | `kind` | 174 |
| variable | `node` | 174 |
| variable | `child` | 201 |
| variable | `node` | 202 |
| variable | `node` | 207 |
| variable | `_` | 208 |
| variable | `value` | 208 |
| variable | `item` | 212 |
| variable | `terminated` | 215 |
| variable | `statement` | 216 |
| variable | `terminated` | 223 |
| variable | `node` | 226 |
| variable | `node` | 228 |
| function | `references(texts)` | 233 |
| parameter | `texts` | 233 |
| variable | `result` | 235 |
| variable | `text` | 236 |
| variable | `node` | 238 |
| variable | `alias` | 242 |

## studio/store.py

| Kind | Declaration | Line |
|---|---|---|
| variable | `SCHEMA` | 23 |
| class | `Store` | 33 |
| function | `__init__(self, path)` | 36 |
| parameter | `path` | 36 |
| parameter | `self` | 36 |
| variable | `connection` | 40 |
| function | `connect(self)` | 45 |
| parameter | `self` | 45 |
| variable | `connection` | 47 |
| function | `create(self, payload, parent)` | 56 |
| parameter | `parent` | 56 |
| parameter | `payload` | 56 |
| parameter | `self` | 56 |
| variable | `revision` | 58 |
| variable | `connection` | 59 |
| variable | `previous` | 61 |
| variable | `old` | 66 |
| variable | `project` | 73 |
| variable | `project` | 75 |
| function | `revision(self, identifier)` | 83 |
| parameter | `identifier` | 83 |
| parameter | `self` | 83 |
| variable | `connection` | 85 |
| variable | `row` | 86 |
| function | `history(self)` | 96 |
| parameter | `self` | 96 |
| variable | `connection` | 98 |
| variable | `row` | 101 |
| function | `queue(self, revision)` | 106 |
| parameter | `revision` | 106 |
| parameter | `self` | 106 |
| variable | `identifier` | 108 |
| variable | `connection` | 109 |
| function | `finish(self, identifier, status, result)` | 115 |
| parameter | `identifier` | 115 |
| parameter | `result` | 115 |
| parameter | `self` | 115 |
| parameter | `status` | 115 |
| variable | `connection` | 117 |
| function | `run(self, identifier)` | 122 |
| parameter | `identifier` | 122 |
| parameter | `self` | 122 |
| variable | `connection` | 124 |
| variable | `row` | 125 |
| function | `runs(self, revision)` | 130 |
| parameter | `revision` | 130 |
| parameter | `self` | 130 |
| variable | `connection` | 132 |
| variable | `identifiers` | 133 |
| variable | `row` | 135 |
| variable | `identifier` | 139 |
| function | `timeline(self, revision)` | 141 |
| parameter | `revision` | 141 |
| parameter | `self` | 141 |
| variable | `project` | 143 |
| variable | `connection` | 144 |
| variable | `rows` | 145 |
| variable | `items` | 149 |
| variable | `row` | 150 |
| variable | `payload` | 151 |
| variable | `attempts` | 152 |
| variable | `summaries` | 156 |
| variable | `attempt` | 157 |
| variable | `result` | 158 |
| variable | `key` | 165 |

## studio/vault.py

| Kind | Declaration | Line |
|---|---|---|
| variable | `MAGIC` | 30 |
| variable | `AAD` | 31 |
| variable | `MAX_BYTES` | 32 |
| variable | `MAX_FILES` | 33 |
| variable | `CHUNK` | 34 |
| function | `safe_name(name)` | 37 |
| parameter | `name` | 37 |
| variable | `path` | 39 |
| variable | `devices` | 40 |
| variable | `i` | 45 |
| variable | `i` | 46 |
| variable | `c` | 53 |
| variable | `c` | 54 |
| variable | `p` | 57 |
| function | `members(root)` | 64 |
| parameter | `root` | 64 |
| variable | `found` | 66 |
| variable | `names` | 66 |
| variable | `total` | 66 |
| variable | `path` | 67 |
| variable | `name` | 72 |
| variable | `total` | 77 |
| function | `signature(root)` | 83 |
| parameter | `root` | 83 |
| variable | `p` | 86 |
| class | `EncryptedWriter` | 90 |
| function | `__init__(self, stream, encryptor)` | 93 |
| parameter | `encryptor` | 93 |
| parameter | `self` | 93 |
| parameter | `stream` | 93 |
| function | `writable(self)` | 97 |
| parameter | `self` | 97 |
| function | `write(self, data)` | 101 |
| parameter | `data` | 101 |
| parameter | `self` | 101 |
| function | `tell(self)` | 107 |
| parameter | `self` | 107 |
| function | `encrypt_workspace(root, destination, key)` | 112 |
| parameter | `destination` | 112 |
| parameter | `key` | 112 |
| parameter | `root` | 112 |
| variable | `paths` | 114 |
| variable | `p` | 115 |
| variable | `descriptor` | 117 |
| variable | `temporary` | 117 |
| variable | `scratch` | 118 |
| variable | `nonce` | 120 |
| variable | `encryptor` | 121 |
| variable | `stream` | 123 |
| variable | `writer` | 125 |
| variable | `archive` | 126 |
| variable | `path` | 128 |
| variable | `source` | 129 |
| variable | `source` | 131 |
| variable | `original` | 133 |
| variable | `copied` | 134 |
| variable | `content` | 138 |
| variable | `entry` | 139 |
| function | `decrypt_workspace(source, root, key)` | 153 |
| parameter | `key` | 153 |
| parameter | `root` | 153 |
| parameter | `source` | 153 |
| variable | `descriptor` | 157 |
| variable | `temporary` | 157 |
| variable | `plain` | 159 |
| variable | `stream` | 159 |
| variable | `nonce` | 162 |
| variable | `tag` | 164 |
| variable | `remaining` | 166 |
| variable | `decryptor` | 167 |
| variable | `chunk` | 170 |
| variable | `remaining` | 173 |
| variable | `archive` | 176 |
| variable | `entries` | 177 |
| variable | `names` | 178 |
| variable | `total` | 178 |
| variable | `entry` | 181 |
| variable | `name` | 182 |
| variable | `total` | 187 |
| variable | `metadata` | 190 |
| variable | `original` | 193 |
| variable | `entry` | 204 |
| variable | `target` | 207 |
| variable | `content` | 209 |
| variable | `output` | 209 |

## tests/account-session.ts

| Kind | Declaration | Line |
|---|---|---|
| type | `Page` | 9 |
| function | `createSession(page: Page, alias: string)` | 12 |
| function | `editorJourney(page: Page)` | 40 |

## tests/conftest.py

| Kind | Declaration | Line |
|---|---|---|
| function | `project()` | 17 |

## tests/desktop.spec.ts

| Kind | Declaration | Line |
|---|---|---|
| variable | `app` | 18 |
| variable | `resources` | 30 |
| variable | `file` | 31 |
| variable | `page` | 37 |

## tests/private.spec.ts

| Kind | Declaration | Line |
|---|---|---|
| variable | `external` | 14 |
| variable | `url` | 16 |
| variable | `downloaded` | 33 |

## tests/test_api.py

| Kind | Declaration | Line |
|---|---|---|
| variable | `TOKEN` | 17 |
| variable | `AUTH` | 18 |
| function | `client(tmp_path)` | 22 |
| parameter | `tmp_path` | 22 |
| variable | `value` | 24 |
| function | `test_auth_and_origin(client, project)` | 28 |
| parameter | `client` | 28 |
| parameter | `project` | 28 |
| variable | `response` | 36 |
| function | `test_revision_reports(client, project)` | 40 |
| parameter | `client` | 40 |
| parameter | `project` | 40 |
| variable | `saved` | 42 |
| variable | `store` | 49 |
| variable | `identifier` | 50 |
| variable | `format` | 52 |
| variable | `result` | 53 |
| function | `test_no_provider(client, project)` | 58 |
| parameter | `client` | 58 |
| parameter | `project` | 58 |
| variable | `body` | 60 |
| variable | `result` | 63 |
| function | `test_export_iteration_history(client, project)` | 67 |
| parameter | `client` | 67 |
| parameter | `project` | 67 |
| variable | `store` | 69 |
| variable | `original` | 70 |
| variable | `candidate` | 71 |
| variable | `unrelated` | 72 |
| variable | `revision` | 73 |
| variable | `identifier` | 74 |
| variable | `run` | 78 |
| variable | `exported` | 79 |
| variable | `timeline` | 80 |
| variable | `row` | 81 |
| function | `test_blocked_execution_retained(client, project, monkeypatch)` | 88 |
| parameter | `client` | 88 |
| parameter | `monkeypatch` | 88 |
| parameter | `project` | 88 |
| function | `blocked(_project)` | 91 |
| parameter | `_project` | 91 |
| variable | `saved` | 95 |
| variable | `job` | 96 |
| variable | `result` | 98 |
| function | `test_compare_unrelated(client, project)` | 103 |
| parameter | `client` | 103 |
| parameter | `project` | 103 |
| variable | `store` | 105 |
| variable | `runs` | 106 |
| variable | `_` | 107 |
| variable | `saved` | 108 |

## tests/test_contracts.py

| Kind | Declaration | Line |
|---|---|---|
| function | `test_unsafe_names(name)` | 47 |
| parameter | `name` | 47 |
| function | `test_safe_flat_names(suffix)` | 54 |
| parameter | `suffix` | 54 |
| function | `test_project_invalid(project, changes)` | 73 |
| parameter | `changes` | 73 |
| parameter | `project` | 73 |
| function | `test_invalid_binary(project)` | 79 |
| parameter | `project` | 79 |
| variable | `payload` | 81 |
| function | `test_zero_weights()` | 87 |
| function | `test_history_retains_oracles(tmp_path, project)` | 93 |
| parameter | `project` | 93 |
| parameter | `tmp_path` | 93 |
| variable | `store` | 95 |
| variable | `payload` | 96 |
| variable | `initial` | 98 |
| variable | `candidate` | 99 |
| variable | `change` | 104 |
| function | `test_history_restart(tmp_path, project)` | 112 |
| parameter | `project` | 112 |
| parameter | `tmp_path` | 112 |
| variable | `store` | 114 |
| variable | `revision` | 115 |
| variable | `run` | 116 |
| variable | `restarted` | 117 |
| function | `test_reports_escaped(project)` | 123 |
| parameter | `project` | 123 |
| variable | `run` | 125 |
| variable | `report` | 126 |
| variable | `archive` | 128 |
| function | `test_static_no_execution(project, tmp_path)` | 133 |
| parameter | `project` | 133 |
| parameter | `tmp_path` | 133 |
| variable | `sentinel` | 135 |
| variable | `payload` | 136 |
| variable | `result` | 138 |
| function | `test_comparison_gates()` | 142 |
| variable | `valid` | 144 |
| variable | `candidate` | 152 |
| variable | `changes` | 154 |
| function | `test_catalog_no_fake_passes()` | 167 |
| variable | `rows` | 169 |
| variable | `row` | 170 |
| variable | `row` | 173 |
| function | `test_training_split()` | 176 |
| variable | `result` | 178 |
| variable | `train` | 178 |
| variable | `validation` | 178 |
| variable | `row` | 179 |
| function | `test_web_demo_source_matches_ci()` | 183 |
| variable | `manifest` | 185 |
| variable | `matched` | 186 |
| function | `test_training_bad_data(tmp_path, rows)` | 203 |
| parameter | `rows` | 203 |
| parameter | `tmp_path` | 203 |
| variable | `path` | 205 |
| variable | `row` | 206 |

## tests/test_execution.py

| Kind | Declaration | Line |
|---|---|---|
| function | `test_fixed_container_flags(tmp_path)` | 19 |
| parameter | `tmp_path` | 19 |
| variable | `args` | 21 |
| variable | `value` | 24 |
| variable | `value` | 25 |
| function | `test_command_limit()` | 28 |
| function | `test_command_timeout()` | 34 |
| function | `test_no_host_fallback(project, monkeypatch)` | 40 |
| parameter | `monkeypatch` | 40 |
| parameter | `project` | 40 |
| function | `unavailable()` | 43 |
| variable | `result` | 47 |
| function | `test_private_remote_context_blocked(endpoint, monkeypatch)` | 54 |
| parameter | `endpoint` | 54 |
| parameter | `monkeypatch` | 54 |
| function | `forbidden()` | 59 |
| parameter | `args` | 59 |
| parameter | `kwargs` | 59 |
| function | `test_private_local_context_and_scoped_job(project, monkeypatch, tmp_path)` | 66 |
| parameter | `monkeypatch` | 66 |
| parameter | `project` | 66 |
| parameter | `tmp_path` | 66 |
| variable | `observed` | 69 |
| function | `fake_command(argv)` | 71 |
| parameter | `argv` | 71 |
| parameter | `kwargs` | 71 |
| variable | `argv` | 75 |
| variable | `mount` | 80 |
| variable | `x` | 80 |
| variable | `result` | 87 |
| variable | `argv` | 89 |
| function | `test_context_overrides_host_but_remote_source_stays_blocked(monkeypatch)` | 93 |
| parameter | `monkeypatch` | 93 |
| function | `context_only(argv)` | 98 |
| parameter | `argv` | 98 |
| parameter | `kwargs` | 98 |

## tests/test_locations.py

| Kind | Declaration | Line |
|---|---|---|
| function | `manifest(files, entry, language)` | 33 |
| parameter | `entry` | 33 |
| parameter | `files` | 33 |
| parameter | `language` | 33 |
| variable | `name` | 39 |
| variable | `text` | 39 |
| function | `test_multifile_unicode_syntax_and_no_source_execution(tmp_path)` | 44 |
| parameter | `tmp_path` | 44 |
| variable | `sentinel` | 46 |
| variable | `project` | 47 |
| variable | `result` | 54 |
| variable | `dynamic` | 55 |
| variable | `item` | 55 |
| variable | `item` | 57 |
| variable | `syntax` | 57 |
| function | `test_unused_and_unreachable_locations()` | 63 |
| variable | `text` | 65 |
| variable | `result` | 66 |
| variable | `item` | 67 |
| variable | `located` | 67 |
| variable | `item` | 74 |
| function | `test_physical_newlines_not_unicode_string_separators(separator)` | 78 |
| parameter | `separator` | 78 |
| variable | `text` | 80 |
| variable | `finding` | 81 |
| variable | `item` | 83 |
| function | `test_unused_false_positive_boundaries(text)` | 101 |
| parameter | `text` | 101 |
| function | `test_cross_file_references_and_empty_or_unparseable_source()` | 106 |
| variable | `project` | 108 |
| variable | `empty` | 112 |
| variable | `invalid` | 114 |
| function | `test_unrelated_module_names_do_not_hide_unused_imports_or_locals()` | 119 |
| variable | `result` | 121 |
| variable | `item` | 129 |
| variable | `located` | 129 |
| variable | `item` | 132 |
| function | `test_structural_python_errors_and_other_language_offsets()` | 135 |
| variable | `result` | 137 |
| variable | `other` | 139 |
| variable | `result` | 144 |
| function | `test_toolchain_formats(entry, language, output)` | 165 |
| parameter | `entry` | 165 |
| parameter | `language` | 165 |
| parameter | `output` | 165 |
| variable | `project` | 167 |
| variable | `result` | 168 |
| function | `test_unmapped_failure_bounds_duplicates_ansi_and_generated_artifacts()` | 177 |
| variable | `project` | 179 |
| variable | `evidence` | 181 |
| variable | `result` | 190 |
| function | `test_tool_location_limit_and_fuzz_paths()` | 196 |
| variable | `project` | 198 |
| variable | `index` | 199 |
| variable | `output` | 199 |
| variable | `result` | 200 |
| variable | `item` | 213 |
| function | `test_api_and_exports_preserve_locations_and_escape(tmp_path)` | 216 |
| parameter | `tmp_path` | 216 |
| variable | `project` | 218 |
| variable | `token` | 219 |
| variable | `headers` | 220 |
| variable | `client` | 221 |
| variable | `review` | 222 |
| variable | `store` | 224 |
| variable | `revision` | 225 |
| variable | `run` | 226 |
| variable | `result` | 227 |
| variable | `exported` | 243 |
| variable | `html` | 245 |
| variable | `archive` | 248 |
| variable | `saved` | 249 |
| function | `coverage_function(monkeypatch, tmp_path, data)` | 255 |
| parameter | `data` | 255 |
| parameter | `monkeypatch` | 255 |
| parameter | `tmp_path` | 255 |
| variable | `worker` | 257 |
| variable | `function` | 258 |
| variable | `node` | 259 |
| variable | `namespace` | 262 |
| parameter | `args` | 266 |
| parameter | `kwargs` | 266 |
| function | `test_private_runtime_preparation(tmp_path)` | 272 |
| parameter | `tmp_path` | 272 |
| variable | `tree` | 274 |
| variable | `function` | 275 |
| variable | `node` | 276 |
| variable | `environment` | 278 |
| variable | `namespace` | 279 |
| function | `test_coverage_exact_lists_multifile_unknown_and_generated_exclusion(monkeypatch, tmp_path)` | 286 |
| parameter | `monkeypatch` | 286 |
| parameter | `tmp_path` | 286 |
| variable | `project` | 288 |
| variable | `data` | 289 |
| variable | `measure` | 300 |
| variable | `result` | 301 |
| function | `test_coverage_budget_and_missing_entry(monkeypatch, tmp_path)` | 312 |
| parameter | `monkeypatch` | 312 |
| parameter | `tmp_path` | 312 |
| variable | `project` | 314 |
| variable | `data` | 315 |
| variable | `result` | 318 |
| function | `test_coverage_prioritizes_later_file_missing_lines(monkeypatch, tmp_path)` | 324 |
| parameter | `monkeypatch` | 324 |
| parameter | `tmp_path` | 324 |
| variable | `project` | 326 |
| variable | `data` | 327 |
| variable | `result` | 333 |

## tests/test_native_locations.py

| Kind | Declaration | Line |
|---|---|---|
| function | `evidence(language, source)` | 40 |
| parameter | `language` | 40 |
| parameter | `source` | 40 |
| variable | `project` | 42 |
| function | `test_source_binding_union_and_partial()` | 47 |
| variable | `item` | 49 |
| variable | `result` | 54 |
| function | `test_unknown_and_location_budget()` | 68 |
| variable | `item` | 70 |
| variable | `line` | 72 |
| variable | `result` | 73 |
| variable | `index` | 76 |
| function | `test_gcov_lcov_and_branch_ids(tmp_path)` | 81 |
| parameter | `tmp_path` | 81 |
| variable | `item` | 83 |
| variable | `path` | 84 |
| function | `test_xml_coverage_and_reject_entities(tmp_path)` | 107 |
| parameter | `tmp_path` | 107 |
| variable | `item` | 109 |
| variable | `path` | 110 |
| variable | `unknown` | 127 |
| function | `test_shell_ast_and_assembly_exports()` | 141 |
| variable | `item` | 149 |
| variable | `finding` | 151 |
| function | `test_sql_statement_start_anchors(text, lines)` | 166 |
| parameter | `lines` | 166 |
| parameter | `text` | 166 |
| variable | `item` | 168 |
| function | `test_bounded_tools_fail_closed(tmp_path, language)` | 172 |
| parameter | `language` | 172 |
| parameter | `tmp_path` | 172 |
| variable | `_` | 174 |
| variable | `project` | 174 |
| variable | `work` | 175 |
| function | `unavailable()` | 178 |
| parameter | `args` | 178 |
| parameter | `kwargs` | 178 |
| variable | `coverage` | 182 |
| variable | `unused` | 182 |
| function | `test_controller_rebinds_native_findings_and_escapes()` | 187 |
| variable | `_` | 189 |
| variable | `project` | 189 |
| variable | `item` | 190 |
| variable | `raw` | 192 |
| variable | `result` | 193 |
| variable | `report` | 196 |
| function | `test_native_parser_failures_are_not_clean_unused_reports(tmp_path)` | 201 |
| parameter | `tmp_path` | 201 |
| variable | `item` | 203 |
| function | `parsed_error(argv)` | 205 |
| parameter | `argv` | 205 |
| parameter | `kwargs` | 205 |
| variable | `result` | 226 |
| function | `test_native_duplicate_findings_do_not_consume_limit()` | 232 |
| variable | `item` | 234 |
| variable | `_` | 235 |
| function | `test_deep_shell_ast_walk_is_iterative()` | 241 |
| variable | `tree` | 243 |
| variable | `_` | 244 |
| variable | `tree` | 245 |
| function | `test_assembly_literal_unicode_separator_does_not_shift_lines()` | 249 |
| variable | `item` | 251 |
| function | `test_invalid_unicode_sql_whitespace_is_not_silently_removed()` | 256 |
| variable | `chunks` | 258 |
| function | `test_deep_native_json_fails_closed(tmp_path, monkeypatch)` | 263 |
| parameter | `monkeypatch` | 263 |
| parameter | `tmp_path` | 263 |
| function | `too_deep()` | 267 |
| parameter | `args` | 267 |
| parameter | `args` | 273 |
| variable | `_` | 275 |
| variable | `project` | 275 |
| variable | `_` | 276 |
| variable | `coverage` | 276 |

## tests/test_private.py

| Kind | Declaration | Line |
|---|---|---|
| variable | `PASSWORD` | 25 |
| variable | `KEY` | 26 |
| variable | `SALT` | 27 |
| variable | `HEADERS` | 28 |
| function | `client(tmp_path)` | 32 |
| parameter | `tmp_path` | 32 |
| variable | `app` | 34 |
| variable | `session` | 35 |
| function | `register(client, alias)` | 39 |
| parameter | `alias` | 39 |
| parameter | `client` | 39 |
| variable | `response` | 41 |
| function | `unlock(client, key)` | 46 |
| parameter | `client` | 46 |
| parameter | `key` | 46 |
| variable | `response` | 48 |
| function | `test_registration_private_headers_and_zero_secret_echo(client)` | 52 |
| parameter | `client` | 52 |
| variable | `response` | 56 |
| variable | `invalid` | 64 |
| variable | `db` | 68 |
| variable | `row` | 69 |
| function | `test_request_origin_host_mutation_rejected(client, headers)` | 83 |
| parameter | `client` | 83 |
| parameter | `headers` | 83 |
| function | `test_real_revisions_encrypted_lock_reopen(client, project)` | 93 |
| parameter | `client` | 93 |
| parameter | `project` | 93 |
| variable | `result` | 97 |
| variable | `identity` | 99 |
| variable | `manager` | 100 |
| variable | `owner` | 101 |
| variable | `archive` | 105 |
| variable | `wrong` | 108 |
| function | `test_two_accounts_and_same_account_new_session_need_key(client, project)` | 115 |
| parameter | `client` | 115 |
| parameter | `project` | 115 |
| variable | `identity` | 119 |
| variable | `original` | 120 |
| function | `test_recovery_logout_expiry_delete(client)` | 147 |
| parameter | `client` | 147 |
| variable | `recovery` | 149 |
| variable | `body` | 151 |
| variable | `changed` | 152 |
| function | `test_expiry_and_human_idle(client)` | 171 |
| parameter | `client` | 171 |
| variable | `manager` | 175 |
| variable | `human` | 176 |
| variable | `db` | 181 |
| function | `test_private_static_review_and_blocked_execution(client, project, monkeypatch)` | 186 |
| parameter | `client` | 186 |
| parameter | `monkeypatch` | 186 |
| parameter | `project` | 186 |
| function | `unavailable()` | 189 |
| parameter | `kwargs` | 189 |
| variable | `review` | 196 |
| variable | `identity` | 198 |
| variable | `job` | 199 |
| variable | `_` | 200 |
| variable | `result` | 201 |
| variable | `report` | 206 |
| function | `test_provider_keys_private_and_consent_version(client, project)` | 211 |
| parameter | `client` | 211 |
| parameter | `project` | 211 |
| variable | `config` | 215 |
| variable | `saved` | 227 |
| variable | `before` | 237 |
| variable | `repeated` | 238 |
| variable | `changed` | 240 |
| variable | `manager` | 247 |
| variable | `owner` | 248 |
| function | `test_recovery_save_failure_preserves_code(client, monkeypatch)` | 255 |
| parameter | `client` | 255 |
| parameter | `monkeypatch` | 255 |
| variable | `recovery` | 259 |
| variable | `original` | 262 |
| function | `unavailable()` | 264 |
| parameter | `args` | 264 |
| variable | `body` | 269 |
| function | `test_archive_paths(name)` | 278 |
| parameter | `name` | 278 |
| function | `test_archive_authentication_before_extract(tmp_path)` | 284 |
| parameter | `tmp_path` | 284 |
| variable | `root` | 286 |
| variable | `path` | 289 |
| variable | `damaged` | 292 |
| function | `test_single_instance_and_launcher_not_browser(client)` | 300 |
| parameter | `client` | 300 |
| function | `test_warning_budget_is_bounded(project)` | 307 |
| parameter | `project` | 307 |
| variable | `changed` | 311 |
| variable | `result` | 313 |
| function | `test_slow_worker_diagnostic_does_not_block_saving(client, project, monkeypatch)` | 317 |
| parameter | `client` | 317 |
| parameter | `monkeypatch` | 317 |
| parameter | `project` | 317 |
| function | `slow_probe()` | 321 |
| parameter | `kwargs` | 321 |
| variable | `started` | 328 |
| function | `test_history_capacity_stops_new_work_but_preserves_recovery(client, project, monkeypatch)` | 334 |
| parameter | `client` | 334 |
| parameter | `monkeypatch` | 334 |
| parameter | `project` | 334 |
| variable | `identity` | 340 |

## tests/test_providers.py

| Kind | Declaration | Line |
|---|---|---|
| function | `test_provider_protocols(tmp_path, project, monkeypatch, kind)` | 24 |
| parameter | `kind` | 24 |
| parameter | `monkeypatch` | 24 |
| parameter | `project` | 24 |
| parameter | `tmp_path` | 24 |
| variable | `path` | 26 |
| variable | `proposal` | 44 |
| variable | `captured` | 47 |
| function | `handler(request)` | 49 |
| parameter | `request` | 49 |
| variable | `body` | 51 |
| variable | `real_client` | 60 |
| parameter | `kwargs` | 62 |
| variable | `router` | 64 |
| variable | `result` | 65 |
| function | `test_provider_endpoint_validation(tmp_path, url)` | 84 |
| parameter | `tmp_path` | 84 |
| parameter | `url` | 84 |
| variable | `path` | 86 |
| function | `test_owned_key_never_uses_global_environment(project, monkeypatch)` | 92 |
| parameter | `monkeypatch` | 92 |
| parameter | `project` | 92 |
| variable | `settings` | 95 |
| variable | `router` | 107 |
| function | `test_owned_protocol_parameters_and_secret_echo(project, monkeypatch)` | 113 |
| parameter | `monkeypatch` | 113 |
| parameter | `project` | 113 |
| variable | `settings` | 115 |
| function | `handler(request)` | 129 |
| parameter | `request` | 129 |
| variable | `body` | 130 |
| variable | `real` | 148 |
| parameter | `kwargs` | 150 |

## tests/test_release.py

| Kind | Declaration | Line |
|---|---|---|
| function | `test_checksum_download_filename(tmp_path, name)` | 27 |
| parameter | `name` | 27 |
| parameter | `tmp_path` | 27 |
| variable | `path` | 29 |
| variable | `expected` | 32 |

## tests/web.spec.ts

| Kind | Declaration | Line |
|---|---|---|
| variable | `errors` | 23 |
| variable | `download` | 74 |
| variable | `locations` | 98 |
| variable | `unreachable` | 100 |
| variable | `locations` | 119 |
| variable | `locations` | 140 |

## training/__init__.py

| Kind | Declaration | Line |
|---|---|---|

## training/dataset.py

| Kind | Declaration | Line |
|---|---|---|
| variable | `LICENSES` | 19 |
| function | `prepare(path, seed)` | 22 |
| parameter | `path` | 22 |
| parameter | `seed` | 22 |
| variable | `seen` | 26 |
| variable | `groups` | 27 |
| variable | `duplicates` | 28 |
| variable | `line` | 29 |
| variable | `row` | 32 |
| variable | `value` | 35 |
| variable | `key` | 37 |
| variable | `duplicates` | 41 |
| parameter | `group` | 47 |
| variable | `ordered` | 47 |
| variable | `validation_count` | 48 |
| variable | `validation_projects` | 49 |
| variable | `group` | 50 |
| variable | `row` | 50 |
| variable | `train` | 50 |
| variable | `group` | 51 |
| variable | `row` | 51 |
| variable | `validation` | 51 |
| variable | `row` | 62 |

## training/serve.py

| Kind | Declaration | Line |
|---|---|---|
| function | `create_model_api(directory, token)` | 25 |
| parameter | `directory` | 25 |
| parameter | `token` | 25 |
| variable | `tokenizer` | 32 |
| variable | `model` | 33 |
| variable | `app` | 36 |
| class | `Completion` | 38 |
| variable | `model_config` | 41 |
| variable | `messages` | 42 |
| variable | `max_tokens` | 43 |
| function | `complete(request, authorization)` | 46 |
| parameter | `authorization` | 46 |
| parameter | `request` | 46 |
| variable | `message` | 50 |
| variable | `text` | 50 |
| variable | `context` | 53 |
| variable | `budget` | 54 |
| variable | `batch` | 55 |
| variable | `generated` | 58 |
| variable | `result` | 61 |
| function | `main()` | 67 |
| variable | `parser` | 71 |
| variable | `args` | 74 |
| variable | `token` | 75 |

## training/train.py

| Kind | Declaration | Line |
|---|---|---|
| function | `train(config, data, output)` | 23 |
| parameter | `config` | 23 |
| parameter | `data` | 23 |
| parameter | `output` | 23 |
| variable | `allowed` | 35 |
| variable | `seed` | 50 |
| variable | `steps` | 51 |
| variable | `context` | 52 |
| variable | `learning_rate` | 53 |
| variable | `provenance` | 61 |
| variable | `training` | 61 |
| variable | `validation` | 61 |
| variable | `row` | 63 |
| variable | `text` | 63 |
| variable | `heads` | 65 |
| variable | `hidden` | 65 |
| variable | `layers` | 65 |
| variable | `default` | 66 |
| variable | `key` | 66 |
| variable | `tokenizer_backend` | 70 |
| variable | `vocabulary_symbols` | 80 |
| variable | `tokenizer` | 81 |
| variable | `model` | 82 |
| variable | `base` | 96 |
| variable | `tokenizer` | 99 |
| variable | `model` | 100 |
| variable | `device` | 107 |
| variable | `optimizer` | 111 |
| variable | `losses` | 112 |
| variable | `step` | 114 |
| variable | `row` | 115 |
| variable | `batch` | 116 |
| variable | `batch` | 117 |
| variable | `key` | 117 |
| variable | `value` | 117 |
| variable | `labels` | 118 |
| variable | `loss` | 121 |
| variable | `held_out` | 130 |
| variable | `row` | 132 |
| variable | `batch` | 133 |
| variable | `batch` | 139 |
| variable | `key` | 139 |
| variable | `value` | 139 |
| variable | `result` | 145 |
| variable | `parameter` | 147 |
| function | `main()` | 157 |
| variable | `parser` | 159 |
| variable | `args` | 163 |

## ui/Account.tsx

| Kind | Declaration | Line |
|---|---|---|
| type | `FormEvent` | 10 |
| type | `Status` | 14 |
| type | `Provider` | 24 |
| type | `Config` | 33 |
| function | `Creator()` | 40 |
| function | `Help()` | 60 |
| function | `value(form: HTMLFormElement, name: string)` | 150 |
| function | `derive(phrase: string, salt: string / null)` | 155 |
| variable | `bytes` | 156 |
| variable | `material` | 159 |
| variable | `key` | 166 |
| variable | `result` | 173 |
| function | `Account()` | 182 |
| variable | `[status, setStatus]` | 183 |
| variable | `[loading, setLoading]` | 184 |
| variable | `[mode, setMode]` | 185 |
| variable | `[recovery, setRecovery]` | 186 |
| variable | `[notice, setNotice]` | 187 |
| variable | `[busy, setBusy]` | 188 |
| variable | `[settings, setSettings]` | 189 |
| variable | `[showSettings, setShowSettings]` | 190 |
| variable | `[idle, setIdle]` | 191 |
| variable | `lastHuman` | 192 |
| variable | `heartbeat` | 193 |
| function | `refresh()` | 195 |
| variable | `response` | 197 |
| variable | `data` | 210 |
| function | `run(task: ()` | 215 |
| variable | `disposed` | 236 |
| variable | `timer` | 245 |
| variable | `human` | 248 |
| variable | `close` | 257 |
| function | `authenticate(event: FormEvent<HTMLFormElement>)` | 278 |
| variable | `form` | 281 |
| variable | `data` | 283 |
| variable | `result` | 288 |
| function | `unlock(event: FormEvent<HTMLFormElement>)` | 303 |
| variable | `form` | 306 |
| variable | `payload` | 308 |
| function | `configure(event: FormEvent<HTMLFormElement>)` | 315 |
| variable | `form` | 318 |
| variable | `id` | 320 |
| variable | `provider` | 321 |
| variable | `providers` | 334 |
| variable | `routes` | 340 |
| variable | `task` | 341 |
| variable | `data` | 343 |
| variable | `a` | 532 |
| variable | `next` | 571 |
| variable | `data` | 684 |
| variable | `form` | 703 |

## ui/App.tsx

| Kind | Declaration | Line |
|---|---|---|
| variable | `languages` | 25 |
| variable | `cloneDemo` | 39 |
| variable | `[project, setProject]` | 47 |
| variable | `[revision, setRevision]` | 48 |
| variable | `[historyRows, setHistory]` | 49 |
| variable | `[run, setRun]` | 50 |
| variable | `[status, setStatus]` | 51 |
| variable | `[capabilities, setCapabilities]` | 52 |
| variable | `[tab, setTab]` | 53 |
| variable | `[fileName, setFileName]` | 54 |
| variable | `[error, setError]` | 55 |
| variable | `[busy, setBusy]` | 56 |
| variable | `[prompt, setPrompt]` | 57 |
| variable | `[consent, setConsent]` | 58 |
| variable | `[live, setLive]` | 59 |
| variable | `[proposal, setProposal]` | 60 |
| variable | `[caseText, setCaseText]` | 61 |
| variable | `[comparison, setComparison]` | 64 |
| variable | `[baseline, setBaseline]` | 65 |
| variable | `[review, setReview]` | 66 |
| variable | `generation` | 67 |
| variable | `selected` | 68 |
| function | `refresh()` | 71 |
| variable | `changed` | 81 |
| variable | `timer` | 93 |
| variable | `timer` | 102 |
| variable | `requestGeneration` | 117 |
| variable | `result` | 120 |
| variable | `timer` | 136 |
| function | `saveAndRun(execute = true)` | 145 |
| variable | `cases` | 150 |
| variable | `payload` | 151 |
| variable | `saved` | 152 |
| variable | `job` | 165 |
| function | `staticReview()` | 184 |
| function | `openRevision(id: string)` | 202 |
| variable | `saved` | 205 |
| function | `upload(files: FileList / null)` | 218 |
| variable | `additions` | 222 |
| variable | `bytes` | 226 |
| function | `acceptProposal()` | 259 |
| variable | `updates` | 262 |
| variable | `files` | 263 |
| variable | `checks` | 282 |
| variable | `metrics` | 283 |

## ui/Locations.tsx

| Kind | Declaration | Line |
|---|---|---|
| function | `Locations({ evidence }: { evidence: Record<string, any> })` | 13 |
| variable | `findings` | 15 |
| variable | `files` | 19 |
| variable | `unlocated` | 20 |
| variable | `parserLimits` | 21 |

## ui/api.ts

| Kind | Declaration | Line |
|---|---|---|
| variable | `privateMode` | 9 |
| variable | `providerRevision` | 10 |
| function | `enableLegacyMode()` | 13 |
| variable | `supplied` | 15 |
| function | `setProviderRevision(revision: string)` | 23 |
| variable | `response` | 33 |
| variable | `data` | 40 |
| variable | `headers` | 54 |
| variable | `response` | 63 |
| variable | `data` | 73 |
| function | `download(run: string, format: "zip" / "html" / "json")` | 84 |
| variable | `response` | 85 |
| variable | `url` | 103 |
| variable | `link` | 104 |

## ui/demo.ts

| Kind | Declaration | Line |
|---|---|---|
| variable | `demo` | 10 |

## ui/main.tsx

| Kind | Declaration | Line |
|---|---|---|
| variable | `root` | 35 |
| function | `boot()` | 37 |
| variable | `response` | 39 |
| variable | `health` | 41 |
| variable | `screen` | 44 |

## ui/types.ts

| Kind | Declaration | Line |
|---|---|---|
| type | `SourceFile` | 8 |
| type | `Case` | 13 |
| type | `Priorities` | 19 |
| type | `Project` | 26 |
| type | `Revision` | 43 |
| type | `Run` | 50 |
| type | `Finding` | 57 |
| type | `Capability` | 66 |
| type | `AIResult` | 72 |

## vite.config.ts

| Kind | Declaration | Line |
|---|---|---|
