/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * types: SourceVerification@L21
 * functions: reveal(target: editor.IStandaloneCodeEditor, selectedLine: number)@L87
 * variables: [verification, setVerification]@L37; contextMatches@L44; verified@L48; draftMatches@L49; [line, setLine]@L50; [jump, setJump]@L51; [notice, setNotice]@L52; editorRef@L53; decorations@L54; heading@L55; generation@L56; request@L59; target@L156
 * </code-map> */

/**
 * Verified read-only evidence source inspector by Jason Stys.
 * Hashes the retained snapshot and current draft independently; stale edits never replace history.
 * Parameters/state are private in-memory text only; no target code runs and no provider receives it.
 * Exact symbol/variable locations are generated in docs/code-index.md.
 */
import { useEffect, useRef, useState } from "react";
import Editor from "@monaco-editor/react";
import type { editor } from "monaco-editor";
import type { Project, SourceLocation } from "./types";
import {
  verifySourceLocation,
  type SourceVerification,
} from "./source-navigation";

export default function SourceInspector({
  location,
  snapshot,
  draft,
  onClose,
  onEditDraft,
}: {
  location: SourceLocation;
  snapshot: Project | null;
  draft: Project;
  onClose: () => void;
  onEditDraft: (location: SourceLocation) => Promise<void>;
}) {
  const [verification, setVerification] = useState<{
    location: SourceLocation;
    snapshot: Project | null;
    draft: Project;
    result: SourceVerification;
    draftMatches: boolean;
  } | null>(null);
  const contextMatches =
    verification?.location === location &&
    verification.snapshot === snapshot &&
    verification.draft === draft;
  const verified = contextMatches ? verification.result : null;
  const draftMatches = contextMatches && verification.draftMatches;
  const [line, setLine] = useState(location.line);
  const [jump, setJump] = useState(String(location.line));
  const [notice, setNotice] = useState("");
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const decorations = useRef<editor.IEditorDecorationsCollection | null>(null);
  const heading = useRef<HTMLHeadingElement | null>(null);
  const generation = useRef(0);

  useEffect(() => {
    const request = ++generation.current;
    setVerification(null);
    editorRef.current = null;
    decorations.current = null;
    setLine(location.line);
    setJump(String(location.line));
    setNotice("");
    void Promise.all([
      verifySourceLocation(location, snapshot),
      verifySourceLocation(location, draft),
    ]).then(([evidence, current]) => {
      if (generation.current !== request) return;
      setVerification({
        location,
        snapshot,
        draft,
        result: evidence,
        draftMatches: current.ok && location.artifact === "source",
      });
      heading.current?.focus({ preventScroll: true });
      heading.current?.scrollIntoView({ block: "start", behavior: "instant" });
    });
    return () => {
      ++generation.current;
    };
  }, [location, snapshot, draft]);

  /** Focus a line only after its containing source fingerprint and bounds were verified. */
  function reveal(target: editor.IStandaloneCodeEditor, selectedLine: number) {
    target.setPosition({ lineNumber: selectedLine, column: 1 });
    target.revealLineInCenter(selectedLine);
    if (decorations.current === null)
      decorations.current = target.createDecorationsCollection();
    decorations.current.set([
      {
        range: {
          startLineNumber: selectedLine,
          startColumn: 1,
          endLineNumber: selectedLine,
          endColumn: target.getModel()?.getLineMaxColumn(selectedLine) ?? 1,
        },
        options: { isWholeLine: true, className: "evidence-source-line" },
      },
    ]);
  }
  useEffect(() => {
    if (verified?.ok && editorRef.current) reveal(editorRef.current, line);
  }, [verified, line]);

  return (
    <section
      className="panel source-inspector"
      aria-label="Evidence source inspector"
    >
      <div className="panel-head">
        <h3 ref={heading} tabIndex={-1}>
          Evidence source inspector
        </h3>
        <button className="secondary" onClick={onClose}>
          Close source inspector
        </button>
      </div>
      <p role="status">
        {location.file}:{contextMatches ? line : location.line} ·{" "}
        {location.artifact === "generated"
          ? "Generated harness/test artifact"
          : "Project source snapshot"}
      </p>
      {verified === null ? (
        <p role="status">Checking exact source fingerprint…</p>
      ) : !verified.ok ? (
        <p role="alert">{verified.reason}</p>
      ) : (
        <>
          <p className="note">
            Read-only evidence snapshot.{" "}
            {draftMatches
              ? "Current draft matches these exact source bytes."
              : "Current draft differs or this is a generated artifact; no draft was overwritten."}
            {location.column !== undefined && (
              <>
                {" "}
                Tool-reported column {location.column} (
                {location.column_unit ?? "unit unspecified"}); the whole
                verified line is highlighted.
              </>
            )}
          </p>
          <details>
            <summary>Verified SHA-256</summary>
            <code>{verified.sha256}</code>
          </details>
          <form
            className="source-jump"
            noValidate
            onSubmit={(event) => {
              event.preventDefault();
              const target = Number(jump);
              if (
                !Number.isSafeInteger(target) ||
                target < 1 ||
                target > verified.lines
              ) {
                setNotice(
                  `Choose a physical line from 1 through ${verified.lines}.`,
                );
                return;
              }
              setNotice("");
              setLine(target);
            }}
          >
            <label>
              Browse snapshot line
              <input
                aria-label="Browse snapshot line"
                type="number"
                min={1}
                max={verified.lines}
                value={jump}
                onChange={(event) => setJump(event.target.value)}
              />
            </label>
            <button className="secondary" type="submit">
              Go to snapshot line
            </button>
          </form>
          {notice && <p role="alert">{notice}</p>}
          <Editor
            height="370px"
            path={`inmemory://cfs-evidence/${verified.sha256}/${encodeURIComponent(location.file)}`}
            language={
              location.artifact === "generated"
                ? location.file.endsWith(".py")
                  ? "python"
                  : "cpp"
                : snapshot?.language === "assembly"
                  ? "plaintext"
                  : snapshot?.language
            }
            theme="vs-dark"
            value={verified.content}
            onMount={(instance) => {
              editorRef.current = instance;
              reveal(instance, line);
            }}
            options={{
              readOnly: true,
              ariaLabel: "Verified evidence source",
              minimap: { enabled: false },
              automaticLayout: true,
              scrollBeyondLastLine: false,
              lineNumbersMinChars: 3,
            }}
          />
          <button
            className="secondary"
            disabled={!draftMatches}
            onClick={() => void onEditDraft({ ...location, line })}
          >
            Edit matching draft at line {line}
          </button>
          <p className="note">
            Editing is enabled only for a project source file whose current
            bytes still match. It is rechecked before switching editors.
            Snapshot browsing does not classify additional lines as issues.
          </p>
        </>
      )}
    </section>
  );
}
