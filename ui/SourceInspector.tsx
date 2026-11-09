/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * types: SourceVerification@L19
 * variables: [verification, setVerification]@L35; contextMatches@L42; verified@L46; draftMatches@L47; [line, setLine]@L48; [jump, setJump]@L49; [notice, setNotice]@L50; sourceRef@L51; heading@L52; generation@L53; request@L56; target@L83; [start, end]@L85; target@L139
 * </code-map> */

/**
 * Verified read-only evidence source inspector by Jason Stys.
 * Hashes the retained snapshot and current draft independently; stale edits never replace history.
 * Parameters/state are private in-memory text only; no target code runs and no provider receives it.
 * Exact symbol/variable locations are generated in docs/code-index.md.
 */
import { useEffect, useLayoutEffect, useRef, useState } from "react";
import type { Project, SourceLocation } from "./types";
import {
  verifySourceLocation,
  sourceLineSelection,
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
  const sourceRef = useRef<HTMLTextAreaElement | null>(null);
  const heading = useRef<HTMLHeadingElement | null>(null);
  const generation = useRef(0);

  useEffect(() => {
    const request = ++generation.current;
    setVerification(null);
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

  /** Select the verified physical line in one native read-only control, without another editor model. */
  useLayoutEffect(() => {
    const target = sourceRef.current;
    if (!verified?.ok || target === null) return;
    const [start, end] = sourceLineSelection(verified.content, line);
    target.focus({ preventScroll: true });
    target.setSelectionRange(start, end);
    target.scrollTop = Math.max(0, (line - 1) * 20 - target.clientHeight / 2);
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
          <textarea
            ref={sourceRef}
            className="verified-source"
            aria-label="Verified evidence source"
            readOnly
            spellCheck={false}
            wrap="off"
            value={verified.content}
          />
          <p className="note">
            The native read-only view selects physical line {line}. Displayed
            line endings are normalized by the browser; hashing retains the
            original bytes. Copy source text here or download the full
            source/report ZIP for original bytes.
          </p>
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
