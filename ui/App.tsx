/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * functions: App()@L40; refresh()@L65; saveAndRun()@L121; openRevision(id: string)@L154; upload(files: FileList | null)@L169; acceptProposal()@L210
 * variables: languages@L24; cloneDemo@L38; [project, setProject]@L42; [revision, setRevision]@L43; [historyRows, setHistory]@L44; [run, setRun]@L45; [status, setStatus]@L46; [capabilities, setCapabilities]@L47; [tab, setTab]@L48; [fileName, setFileName]@L49; [error, setError]@L50; [busy, setBusy]@L51; [prompt, setPrompt]@L52; [consent, setConsent]@L53; [live, setLive]@L54; [proposal, setProposal]@L55; [caseText, setCaseText]@L56; [comparison, setComparison]@L59; [baseline, setBaseline]@L60; generation@L61; selected@L62; timer@L78; requestGeneration@L93; result@L96; timer@L112; cases@L126; payload@L127; saved@L128; job@L135; saved@L157; additions@L173; bytes@L177; updates@L213; files@L214; checks@L233; metrics@L234
 * </code-map> */

/** Evidence-first editor, runner and history UI. Symbols/variables: docs/code-index.md.
 * Sources are inert editor text. Proposals require approval; no silent oracle edits.
 */
import { useEffect, useRef, useState } from "react";
import Editor from "@monaco-editor/react";
import { api, download } from "./api";
import { demo } from "./demo";
import type {
  AIResult,
  Capability,
  Case,
  Project,
  Revision,
  Run,
} from "./types";

const languages = [
  "python",
  "javascript",
  "typescript",
  "cpp",
  "c",
  "java",
  "csharp",
  "rust",
  "php",
  "bash",
  "sql",
  "assembly",
];
const cloneDemo = () => structuredClone(demo);

export default function App() {
  /** Coordinate editor state, explicit source snapshots, bounded polling and optional AI suggestions. */
  const [project, setProject] = useState<Project>(cloneDemo);
  const [revision, setRevision] = useState<string | null>(null);
  const [historyRows, setHistory] = useState<Revision[]>([]);
  const [run, setRun] = useState<Run | null>(null);
  const [status, setStatus] = useState<any>(null);
  const [capabilities, setCapabilities] = useState<Capability[]>([]);
  const [tab, setTab] = useState("workspace");
  const [fileName, setFileName] = useState(project.entry);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [consent, setConsent] = useState(false);
  const [live, setLive] = useState(false);
  const [proposal, setProposal] = useState<AIResult | null>(null);
  const [caseText, setCaseText] = useState(
    JSON.stringify(project.cases, null, 2),
  );
  const [comparison, setComparison] = useState<any>(null);
  const [baseline, setBaseline] = useState<Run | null>(null);
  const generation = useRef(0);
  const selected =
    project.files.find((file) => file.name === fileName) ?? project.files[0];

  async function refresh() {
    /** Refresh non-secret metadata and durable revision history. */
    await Promise.all([
      api<any>("status").then(setStatus),
      api<Revision[]>("revisions").then(setHistory),
      api<Capability[]>("catalog").then(setCapabilities),
    ]);
  }
  useEffect(() => {
    refresh().catch((reason) => setError(reason.message));
  }, []);
  useEffect(() => {
    if (!run || !["queued", "running"].includes(run.status)) return;
    const timer = setInterval(
      () =>
        api<Run>(`runs/${run.id}`)
          .then(setRun)
          .catch((reason) => setError(reason.message)),
      1000,
    );
    return () => clearInterval(timer);
  }, [run?.id, run?.status]);

  async function ask(
    task: "generate" | "tests" | "improve" | "suggest",
    silent = false,
  ) {
    /** Debounced suggestions are still consented; stale AI responses never replace the latest editor. */
    const requestGeneration = ++generation.current;
    if (!silent) setBusy(true);
    try {
      const result = await api<AIResult>("ai", "POST", {
        task,
        project: { ...project, cases: JSON.parse(caseText) as Case[] },
        prompt,
        consent,
      });
      if (generation.current === requestGeneration) setProposal(result);
    } catch (reason) {
      setError((reason as Error).message);
      if (silent) setLive(false);
    } finally {
      if (!silent) setBusy(false);
    }
  }
  useEffect(() => {
    if (!live || !consent) return;
    const timer = setTimeout(() => {
      void ask("suggest", true);
    }, 1800);
    return () => {
      clearTimeout(timer);
      ++generation.current;
    };
  }, [selected.content, live, consent]);

  async function saveAndRun() {
    /** Save a new revision before execution; retain approved case oracles for a candidate. */
    setBusy(true);
    setError("");
    try {
      const cases = JSON.parse(caseText) as Case[];
      const payload = { ...project, cases };
      const saved = await api<Revision>(
        `revisions${revision ? `?parent=${revision}` : ""}`,
        "POST",
        payload,
      );
      setProject(payload);
      setRevision(saved.id);
      const job = await api<{ id: string; status: string }>(
        `revisions/${saved.id}/run`,
        "POST",
      );
      setRun({
        id: job.id,
        status: job.status,
        revision_id: saved.id,
        result: {},
      });
      setTab("evidence");
      await refresh();
    } catch (reason) {
      setError((reason as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function openRevision(id: string) {
    /** Restore the exact source snapshot and its latest attempt without re-running it. */
    try {
      const saved = await api<Revision>(`revisions/${id}`);
      setProject(saved.project);
      setRevision(id);
      setFileName(saved.project.entry);
      setCaseText(JSON.stringify(saved.project.cases, null, 2));
      setRun(saved.runs?.at(-1) ?? null);
      setTab("workspace");
    } catch (reason) {
      setError((reason as Error).message);
    }
  }

  async function upload(files: FileList | null) {
    /** Import bounded flat files; unsupported binary data remains an inert fixture, not a parsed claim. */
    if (!files) return;
    try {
      const additions = await Promise.all(
        Array.from(files).map(async (file) => {
          if (file.size > 196608)
            throw new Error("Each uploaded file must be under 192 KiB");
          const bytes = new Uint8Array(await file.arrayBuffer());
          try {
            return {
              name: file.name,
              encoding: "text" as const,
              content: new TextDecoder("utf-8", { fatal: true }).decode(bytes),
            };
          } catch {
            return {
              name: file.name,
              encoding: "base64" as const,
              content: btoa(
                Array.from(bytes, (byte) => String.fromCharCode(byte)).join(""),
              ),
            };
          }
        }),
      );
      setProject({
        ...project,
        files: [
          ...project.files.filter(
            (file) => !additions.some((item) => item.name === file.name),
          ),
          ...additions,
        ],
      });
      setError("");
    } catch (reason) {
      setError((reason as Error).message);
    }
  }

  function acceptProposal() {
    /** Apply only reviewed source/tests to the draft, never to saved history or approved cases. */
    if (!proposal) return;
    const updates = proposal.proposal.files;
    const files = [
      ...project.files.filter(
        (file) => !updates.some((item) => item.name === file.name),
      ),
      ...updates,
    ];
    setProject({
      ...project,
      files,
      tests: proposal.proposal.tests
        ? proposal.proposal.tests.startsWith(project.tests)
          ? proposal.proposal.tests
          : project.tests + "\n" + proposal.proposal.tests
        : project.tests,
    });
    setProposal(null);
    setTab("workspace");
  }

  const checks = run?.result.checks;
  const metrics = run?.result.benchmark;
  return (
    <div className="shell">
      <aside className="rail">
        <div className="brand-mark">
          CF<span>↗</span>
        </div>
        <h1>
          Code Flow<span>STUDIO</span>
        </h1>
        <p className="rail-label">DEVELOP · VERIFY · COMPARE</p>
        <nav aria-label="Main navigation">
          {[
            ["workspace", "⌘", "Workspace"],
            ["evidence", "◈", "Run evidence"],
            ["catalog", "▦", "Test catalog"],
            ["settings", "⚙", "Priorities & AI"],
          ].map(([id, icon, title]) => (
            <button
              aria-label={title}
              key={id}
              className={tab === id ? "nav active" : "nav"}
              onClick={() => setTab(id)}
            >
              <span aria-hidden="true">{icon}</span>
              {title}
            </button>
          ))}
        </nav>
        <div className="rail-history">
          <h2>REVISION HISTORY</h2>
          {historyRows.length === 0 && <p>No saved runs yet.</p>}
          {historyRows.slice(0, 12).map((row) => (
            <button key={row.id} onClick={() => void openRevision(row.id)}>
              {row.title}
              <small>
                {row.id.slice(0, 8)}{" "}
                {row.parent_id ? "· candidate" : "· baseline"}
              </small>
            </button>
          ))}
        </div>
        <div className="rail-foot">
          <span className="dot" />
          LOCAL-FIRST WORKSPACE
          <small>Private by default. Evidence, not guesses.</small>
        </div>
      </aside>
      <main>
        <header>
          <div>
            <span className="eyebrow">ENGINEERING WORKBENCH / v0.1</span>
            <h2>
              {tab === "workspace"
                ? "Make your next iteration count."
                : tab === "evidence"
                  ? "Every claim needs evidence."
                  : tab === "catalog"
                    ? "Choose the right checks."
                    : "Define your trade-offs."}
            </h2>
          </div>
          <div
            className={`status ${status?.worker.ready ? "ready" : "pending"}`}
          >
            <span className="dot" />
            {status?.worker.ready
              ? "Isolated runner ready"
              : "Runner needs setup"}
          </div>
        </header>
        {error && (
          <div className="alert" role="alert" aria-label="Workspace error">
            {error}
            <button aria-label="Dismiss error" onClick={() => setError("")}>
              ×
            </button>
          </div>
        )}
        {tab === "workspace" && (
          <>
            <section className="intro">
              <div>
                <span className="eyebrow">A CLEARER DEVELOPMENT LOOP</span>
                <h3>Code. Test. Learn. Improve.</h3>
                <p>
                  Start with a reviewed contract, run it in isolation, and
                  compare revisions before accepting an AI change.
                </p>
              </div>
              <button
                className="secondary"
                onClick={() => {
                  setProject(cloneDemo());
                  setCaseText(JSON.stringify(demo.cases, null, 2));
                  setRevision(null);
                  setRun(null);
                  setFileName(demo.entry);
                }}
              >
                Load CSV example
              </button>
            </section>
            <div className="workspace-grid">
              <section className="panel editor-panel">
                <div className="panel-head">
                  <label>
                    Project
                    <input
                      value={project.title}
                      onChange={(event) =>
                        setProject({ ...project, title: event.target.value })
                      }
                    />
                  </label>
                  <label>
                    Language
                    <select
                      aria-label="Language"
                      value={project.language}
                      onChange={(event) =>
                        setProject({ ...project, language: event.target.value })
                      }
                    >
                      {languages.map((language) => (
                        <option key={language}>{language}</option>
                      ))}
                    </select>
                  </label>
                </div>
                <div className="file-bar">
                  {project.files.map((file) => (
                    <button
                      key={file.name}
                      className={selected.name === file.name ? "selected" : ""}
                      onClick={() => setFileName(file.name)}
                    >
                      {file.name}
                    </button>
                  ))}
                  <label className="upload">
                    + files
                    <input
                      type="file"
                      multiple
                      onChange={(event) => void upload(event.target.files)}
                    />
                  </label>
                </div>
                {selected.encoding === "text" ? (
                  <Editor
                    height="430px"
                    language={
                      project.language === "assembly"
                        ? "plaintext"
                        : project.language
                    }
                    theme="vs-dark"
                    value={selected.content}
                    onChange={(value) =>
                      setProject({
                        ...project,
                        files: project.files.map((file) =>
                          file.name === selected.name
                            ? { ...file, content: value ?? "" }
                            : file,
                        ),
                      })
                    }
                    options={{
                      minimap: { enabled: false },
                      fontSize: 14,
                      padding: { top: 18 },
                      scrollBeyondLastLine: false,
                      automaticLayout: true,
                    }}
                  />
                ) : (
                  <p className="binary">
                    Binary attachment retained as a fixture. No unsupported
                    content extraction is claimed.
                  </p>
                )}
                <div className="editor-footer">
                  <label>
                    Entry
                    <select
                      value={project.entry}
                      onChange={(event) =>
                        setProject({ ...project, entry: event.target.value })
                      }
                    >
                      {project.files
                        .filter((file) => file.encoding === "text")
                        .map((file) => (
                          <option key={file.name}>{file.name}</option>
                        ))}
                    </select>
                  </label>
                  <span>
                    {selected.content.length.toLocaleString()} characters
                  </span>
                  <label>
                    <input
                      type="checkbox"
                      checked={live}
                      disabled={!consent}
                      onChange={(event) => setLive(event.target.checked)}
                    />
                    Live AI suggestions
                  </label>
                </div>
              </section>
              <section className="panel contract-panel">
                <span className="eyebrow">01 / DEFINE THE CONTRACT</span>
                <h3>What should this code do?</h3>
                <label>
                  Requirements
                  <textarea
                    value={project.requirements}
                    onChange={(event) =>
                      setProject({
                        ...project,
                        requirements: event.target.value,
                      })
                    }
                  />
                </label>
                <label>
                  Approved stdin/stdout cases{" "}
                  <small>JSON · candidates cannot weaken these</small>
                  <textarea
                    className="code-text cases"
                    value={caseText}
                    onChange={(event) => setCaseText(event.target.value)}
                  />
                </label>
                <label>
                  Generated / custom pytest harness
                  <textarea
                    className="code-text"
                    value={project.tests}
                    onChange={(event) =>
                      setProject({ ...project, tests: event.target.value })
                    }
                  />
                </label>
                <p className="note">
                  Fixtures, harnesses and code are untrusted. Only the isolated
                  worker executes them.
                </p>
                <button
                  className="primary"
                  disabled={
                    busy || ["queued", "running"].includes(run?.status ?? "")
                  }
                  onClick={() => void saveAndRun()}
                >
                  Save revision & run checks <span>→</span>
                </button>
              </section>
            </div>
            <section className="panel ai-panel">
              <div>
                <span className="eyebrow">
                  02 / PROPOSE · NEVER AUTO-PROMOTE
                </span>
                <h3>Your configurable AI copilot</h3>
                <p>
                  Generate code from requirements, create tests, or propose an
                  improvement. Each proposal needs review and a fresh run.
                </p>
              </div>
              <label>
                Additional prompt
                <textarea
                  value={prompt}
                  onChange={(event) => setPrompt(event.target.value)}
                  placeholder="Describe behavior, constraints and edge cases…"
                />
              </label>
              <label className="consent">
                <input
                  type="checkbox"
                  checked={consent}
                  onChange={(event) => setConsent(event.target.checked)}
                />
                I approve sending this project's text to the configured model.
              </label>
              <div className="actions">
                {[
                  ["generate", "Generate code"],
                  ["tests", "Generate tests"],
                  ["improve", "Propose improvement"],
                ].map(([task, title]) => (
                  <button
                    className="secondary"
                    disabled={busy || !consent}
                    key={task}
                    onClick={() =>
                      void ask(task as "generate" | "tests" | "improve")
                    }
                  >
                    {title}
                  </button>
                ))}
              </div>
            </section>
          </>
        )}
        {proposal && (
          <section className="panel proposal">
            <span className="eyebrow">
              UNVERIFIED PROPOSAL · {proposal.provider} / {proposal.model}
            </span>
            <h3>Review before applying</h3>
            <p>{proposal.proposal.explanation}</p>
            {proposal.proposal.suggestions.map((suggestion, index) => (
              <p key={index}>• {suggestion}</p>
            ))}
            {proposal.proposal.files.map((file) => (
              <details key={file.name}>
                <summary>{file.name}</summary>
                <pre>{file.content}</pre>
              </details>
            ))}
            {proposal.proposal.tests && (
              <details>
                <summary>Proposed test harness</summary>
                <pre>{proposal.proposal.tests}</pre>
              </details>
            )}
            <button className="primary" onClick={acceptProposal}>
              Apply to draft, then test
            </button>
            <button className="secondary" onClick={() => setProposal(null)}>
              Discard
            </button>
          </section>
        )}
        {tab === "evidence" && (
          <>
            <section className="metric-grid">
              {[
                ["Tool status", run?.status ?? "No run"],
                [
                  "Approved cases",
                  checks
                    ? `${checks.passed} passed · ${checks.failed} failed`
                    : "Not executed",
                ],
                [
                  "Median process time",
                  metrics?.median_ms != null
                    ? `${metrics.median_ms.toFixed(2)} ms`
                    : "Not measured",
                ],
                [
                  "Peak child memory",
                  metrics
                    ? `${(metrics.max_rss_kib / 1024).toFixed(1)} MiB`
                    : "Not measured",
                ],
              ].map(([label, value]) => (
                <div className="metric" key={label}>
                  <span>{label}</span>
                  <strong>{value}</strong>
                </div>
              ))}
            </section>
            <section className="panel">
              <div className="evidence-head">
                <div>
                  <span className="eyebrow">RAW, REPLAYABLE EVIDENCE</span>
                  <h3>
                    {run
                      ? `Run ${run.id.slice(0, 8)}`
                      : "Save and run a project to begin"}
                  </h3>
                </div>
                {run && (
                  <div className="actions">
                    {["html", "json", "zip"].map((format) => (
                      <button
                        key={format}
                        className="secondary"
                        onClick={() =>
                          void download(
                            run.id,
                            format as "html" | "json" | "zip",
                          ).catch((reason) => setError(reason.message))
                        }
                      >
                        {format.toUpperCase()}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              <p className="note">
                A completed tool run can contain failing code. Missing methods,
                manual checks and unsupported coverage remain explicit. Timing
                includes process startup.
              </p>
              <pre className="evidence">
                {JSON.stringify(
                  run?.result ?? { notice: "No evidence yet" },
                  null,
                  2,
                )}
              </pre>
            </section>
            <section className="panel">
              <h3>Compare independently tested revisions</h3>
              <p>
                Keep the same approved oracles and environment. Correctness
                gates come before weighted preferences.
              </p>
              <div className="actions">
                <button
                  className="secondary"
                  disabled={!run || run.status !== "completed"}
                  onClick={() => setBaseline(run)}
                >
                  Use this run as baseline
                </button>
                <button
                  className="secondary"
                  disabled={!baseline || !run || baseline.id === run.id}
                  onClick={() =>
                    api<any>(
                      `compare?baseline=${baseline!.id}&candidate=${run!.id}`,
                    )
                      .then(setComparison)
                      .catch((reason) => setError(reason.message))
                  }
                >
                  Compare against {baseline?.id.slice(0, 8) ?? "baseline"}
                </button>
              </div>
              {comparison && <pre>{JSON.stringify(comparison, null, 2)}</pre>}
            </section>
          </>
        )}
        {tab === "catalog" && (
          <section className="panel">
            <p className="note">
              These are capabilities and integration requirements—not 48
              automatically passing test suites. Built-in methods depend on
              language and reviewed input/output oracles. Hardware, human
              usability and penetration testing need explicit scope and
              evidence.
            </p>
            <div className="catalog-grid">
              {capabilities.map((item) => (
                <article key={item.id}>
                  <span className={`tag ${item.mode}`}>{item.mode}</span>
                  <h3>
                    {String(item.id).padStart(2, "0")} · {item.name}
                  </h3>
                  <p>{item.requirement}</p>
                </article>
              ))}
            </div>
          </section>
        )}
        {tab === "settings" && (
          <div className="settings-grid">
            <section className="panel">
              <span className="eyebrow">
                PREFERENCES, NOT PERMISSION TO BREAK CODE
              </span>
              <h3>Optimization priorities</h3>
              <p>
                Correctness and strict review cannot be traded away for speed.
                Readability uses transparent proxies plus human review.
              </p>
              {(["runtime", "memory", "readability", "footprint"] as const).map(
                (key) => (
                  <label key={key} className="slider-label">
                    {key}
                    <strong>
                      {Math.round(project.priorities[key] * 100)}%
                    </strong>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.05"
                      value={project.priorities[key]}
                      onChange={(event) =>
                        setProject({
                          ...project,
                          priorities: {
                            ...project.priorities,
                            [key]: Number(event.target.value),
                          },
                        })
                      }
                    />
                  </label>
                ),
              )}
              <label>
                Review scrutiny
                <select
                  value={project.priorities.scrutiny}
                  onChange={(event) =>
                    setProject({
                      ...project,
                      priorities: {
                        ...project.priorities,
                        scrutiny: event.target.value as "strict" | "standard",
                      },
                    })
                  }
                >
                  <option value="strict">Strict: warnings block ranking</option>
                  <option value="standard">
                    Standard: warnings remain visible
                  </option>
                </select>
              </label>
            </section>
            <section className="panel">
              <span className="eyebrow">REPRODUCIBLE RUN BUDGETS</span>
              <h3>Fuzzing & validation</h3>
              <label>
                Fuzz engine
                <select
                  value={project.fuzz_engine}
                  onChange={(event) =>
                    setProject({ ...project, fuzz_engine: event.target.value })
                  }
                >
                  {["blackbox", "libfuzzer", "aflplusplus", "atheris"].map(
                    (engine) => (
                      <option key={engine}>{engine}</option>
                    ),
                  )}
                </select>
              </label>
              <label>
                Seed
                <input
                  type="number"
                  value={project.seed}
                  onChange={(event) =>
                    setProject({ ...project, seed: Number(event.target.value) })
                  }
                />
              </label>
              <label>
                Fuzz cases (0–128)
                <input
                  type="number"
                  min="0"
                  max="128"
                  value={project.fuzz_cases}
                  onChange={(event) =>
                    setProject({
                      ...project,
                      fuzz_cases: Number(event.target.value),
                    })
                  }
                />
              </label>
              <label>
                Reviewed instrumentation harness
                <textarea
                  className="code-text"
                  value={project.fuzz_harness}
                  onChange={(event) =>
                    setProject({ ...project, fuzz_harness: event.target.value })
                  }
                />
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={project.mutation}
                  onChange={(event) =>
                    setProject({ ...project, mutation: event.target.checked })
                  }
                />
                Bounded Python operator mutation
              </label>
            </section>
            <section className="panel">
              <h3>AI routing stays on the server</h3>
              <p>
                Configure providers and per-task routes in a private config
                file. Keys belong in environment variables, never in this
                editor, reports or compiler workers.
              </p>
              <pre>{JSON.stringify(status?.providers ?? [], null, 2)}</pre>
              <p className="note">
                No configured provider means no AI generation. Deterministic
                fixtures are not represented as an AI model.
              </p>
              <button
                className="secondary"
                onClick={() =>
                  void refresh().catch((reason) => setError(reason.message))
                }
              >
                Refresh readiness
              </button>
            </section>
          </div>
        )}
        <footer>
          CODE FLOW STUDIO{" "}
          <span>
            Independent successor · local-first · no unverified promotion
          </span>
        </footer>
      </main>
    </div>
  );
}
