/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * variables: [selectedFile, setSelectedFile]@L71; [category, setCategory]@L72; findings@L77; files@L81; unlocated@L85; parserLimits@L87; names@L90; filtered@L100; unused@L101; coverageFiles@L108; missing@L244
 * </code-map> */

/** Located, content-bound snapshot evidence by Jason Stys.
 * Source references remain untrusted until the inspector verifies their exact UTF-8 fingerprint.
 * Functions/state: filtering is bounded; missing hashes remain honest legacy text, not guessed links.
 * Exact source/variable declarations are generated in docs/code-index.md.
 */
import { Fragment, useEffect, useState } from "react";
import type { Finding, SourceLocation } from "./types";

/** Render a one-based reference only when a source fingerprint is available; never open a URL/path. */
function LocationLink({
  file,
  line,
  fingerprint,
  artifact = "source",
  column,
  unit,
  onNavigate,
}: {
  file: unknown;
  line: unknown;
  fingerprint: unknown;
  artifact?: unknown;
  column?: number;
  unit?: string;
  onNavigate: (location: SourceLocation) => void;
}) {
  if (
    typeof file !== "string" ||
    typeof line !== "number" ||
    !Number.isSafeInteger(line) ||
    line < 1 ||
    typeof fingerprint !== "string" ||
    fingerprint.length !== 64 ||
    !/^[a-f0-9]{64}$/i.test(fingerprint) ||
    (artifact !== "source" && artifact !== "generated")
  )
    return <>{line == null ? "Unavailable" : String(line)}</>;
  return (
    <button
      className="source-location-link"
      aria-label={`Inspect ${artifact} ${file}:${line}`}
      onClick={() =>
        onNavigate({
          file,
          line,
          source_sha256: fingerprint,
          artifact,
          ...(column === undefined ? {} : { column }),
          ...(unit === undefined ? {} : { column_unit: unit }),
        })
      }
    >
      {line}
    </button>
  );
}

export default function Locations({
  evidence,
  onNavigate,
}: {
  evidence: Record<string, any>;
  onNavigate: (location: SourceLocation) => void;
}) {
  const [selectedFile, setSelectedFile] = useState("");
  const [category, setCategory] = useState("all");
  useEffect(() => {
    setSelectedFile("");
    setCategory("all");
  }, [evidence]);
  const findings: Finding[] = [
    ...(evidence.static?.findings ?? []),
    ...(evidence.diagnostics ?? []),
  ];
  const files = Object.entries(evidence.coverage?.files ?? {}) as [
    string,
    any,
  ][];
  const unlocated: { stage: string; reason: string }[] =
    evidence.unlocated_failures ?? [];
  const parserLimits = Object.entries(evidence.static?.files ?? {}).filter(
    ([, value]) => (value as any).parsed === false,
  ) as [string, any][];
  const names = [
    ...new Set([
      ...findings
        .map((finding) => finding.file)
        .filter((file): file is string => typeof file === "string"),
      ...files.map(([name]) => name),
    ]),
  ]
    .sort()
    .slice(0, 64);
  const filtered = findings.filter((finding) => {
    const unused =
      finding.stage === "unused-code" || /unused/i.test(finding.code ?? "");
    return (
      (!selectedFile || finding.file === selectedFile) &&
      (category === "all" || (category === "unused" ? unused : !unused))
    );
  });
  const coverageFiles = files
    .filter(([name]) => !selectedFile || name === selectedFile)
    .slice(0, 32);
  return (
    <section className="panel" aria-label="Located diagnostics">
      <h3>Exact source locations</h3>
      <p className="note">
        Locations refer to the retained evidence snapshot. Select a linked line
        to verify and inspect its exact source, then edit only a matching draft.
        Missing fingerprints in legacy reports cannot enable navigation.
        Unused-code candidates are not coverage results or proof of a bug. A
        tool-reported location is a reference, not a proven root cause.
      </p>
      <div className="location-filters">
        <label>
          Evidence file
          <select
            aria-label="Evidence file"
            value={selectedFile}
            onChange={(event) => setSelectedFile(event.target.value)}
          >
            <option value="">All files</option>
            {names.map((name) => (
              <option key={name}>{name}</option>
            ))}
          </select>
        </label>
        <label>
          Finding category
          <select
            aria-label="Finding category"
            value={category}
            onChange={(event) => setCategory(event.target.value)}
          >
            <option value="all">All findings</option>
            <option value="unused">Unused-code candidates</option>
            <option value="other">Other findings</option>
          </select>
        </label>
      </div>
      <p role="status">
        {filtered.length} retained findings match these filters. Showing at most
        200 rows.
      </p>
      {filtered.length ? (
        <div className="location-table">
          <table>
            <thead>
              <tr>
                <th>File</th>
                <th>Line</th>
                <th>Column</th>
                <th>Finding</th>
              </tr>
            </thead>
            <tbody>
              {filtered.slice(0, 200).map((finding, index) => (
                <tr key={index}>
                  <td>
                    <code>
                      {finding.file ?? "Legacy: filename unavailable"}
                    </code>
                    {finding.artifact === "generated" && (
                      <small>Generated artifact</small>
                    )}
                  </td>
                  <td>
                    <LocationLink
                      file={finding.file}
                      line={finding.line}
                      fingerprint={finding.source_sha256}
                      artifact={finding.artifact ?? "source"}
                      column={finding.column}
                      unit={finding.column_unit}
                      onNavigate={onNavigate}
                    />
                  </td>
                  <td>{finding.column ?? "—"}</td>
                  <td>
                    {finding.code && <strong>{finding.code}: </strong>}
                    {finding.message}
                    {finding.stage && <small> · {finding.stage}</small>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p>
          No located findings match these filters. This is not proof that the
          source is bug-free.
        </p>
      )}
      {(filtered.length > 200 ||
        evidence.static?.findings_truncated ||
        evidence.diagnostics_truncated) && (
        <p>
          Display limited to 200 rows; inspect JSON/HTML/ZIP for all retained
          findings. Analyzer limits may also truncate results.
        </p>
      )}
      {unlocated.map((item, index) => (
        <p key={index}>
          <strong>{item.stage}</strong>: {item.reason}
        </p>
      ))}
      {parserLimits.map(([name, value]) => (
        <p key={name}>
          <strong>{name}</strong>: parser stopped ({value.reason}).{" "}
          {value.location_available
            ? "See the located syntax diagnostic."
            : "Exact line unavailable; this file was not successfully analyzed."}
        </p>
      ))}
      {evidence.unused && (
        <p>
          Unused-code tool: {evidence.unused.tool ?? "Unavailable"} ·{" "}
          {evidence.unused.status}. {evidence.unused.reason}{" "}
          {evidence.unused.scope}
        </p>
      )}
      <h4>Uncovered source locations</h4>
      <p className="note">
        Approved CLI reruns only, separate from benchmarks and generated pytest
        tests. Coverage is language-specific, not proof of correctness. Bash
        measures command-entry lines, SQL completed statement-start lines, and
        assembly instruction-backed debug lines.
      </p>
      <p>
        {evidence.coverage?.tool ?? "Python coverage / legacy"} ·{" "}
        {evidence.coverage?.status ?? "Not measured"} ·{" "}
        {evidence.coverage?.metric} {evidence.coverage?.reason}
      </p>
      {coverageFiles.length ? (
        coverageFiles.map(([name, file]) => {
          const missing: unknown[] = Array.isArray(file.missing_lines)
            ? file.missing_lines
            : [];
          return (
            <div className="coverage-file" key={name}>
              <h5>{name}</h5>
              {file.status === "measured" ? (
                <>
                  <p>
                    Uncovered lines:{" "}
                    <code>
                      {missing.length
                        ? missing.slice(0, 200).map((line, index) => (
                            <Fragment key={index}>
                              {index > 0 && ", "}
                              <LocationLink
                                file={name}
                                line={line}
                                fingerprint={file.source_sha256}
                                onNavigate={onNavigate}
                              />
                            </Fragment>
                          ))
                        : "None recorded"}
                    </code>
                  </p>
                  {missing.length > 200 && (
                    <p>
                      First 200 of {missing.length} retained missing lines
                      shown; the full retained location list remains in
                      JSON/HTML/ZIP. Browse the verified snapshot or narrow the
                      file filter.
                    </p>
                  )}
                  {file.metric && <p>Measurement: {file.metric}</p>}
                  <p>
                    Missing branch arcs:{" "}
                    <code>
                      {file.missing_branches?.length
                        ? file.missing_branches
                            .map(
                              ([from, to]: number[]) =>
                                `${from} → ${to < 0 ? `exit(${to})` : to}`,
                            )
                            .join(", ")
                        : "None recorded"}
                    </code>
                  </p>
                  {!!file.branch_points?.length && (
                    <p>
                      Native branch points (IDs/counts, not destination lines):{" "}
                      <code>
                        {JSON.stringify(file.branch_points).slice(0, 6000)}
                      </code>
                      . Full retained records in JSON.
                    </p>
                  )}
                  {file.truncated && (
                    <p>
                      Location list truncated; counts remain in the raw summary.
                      An empty retained list does not establish full coverage.
                    </p>
                  )}
                </>
              ) : (
                <p>{file.reason ?? "Not measured; coverage unknown"}</p>
              )}
            </div>
          );
        })
      ) : (
        <p>
          {evidence.coverage?.status === "measured"
            ? "No per-file coverage matches this filter, or legacy totals have no locations. Rerun the saved revision if exact locations are unavailable."
            : "Not measured. Run approved cases with the updated isolated worker to obtain exact missing locations."}
        </p>
      )}
    </section>
  );
}
