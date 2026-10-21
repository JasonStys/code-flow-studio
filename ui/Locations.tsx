/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * functions: Locations({ evidence }: { evidence: Record<string, any> })@L13
 * variables: findings@L15; files@L19; unlocated@L20; parserLimits@L21
 * </code-map> */

/** Located snapshot evidence by Jason Stys. Never infer a root-cause line or render logs as HTML.
 * Source/variable declaration map: docs/code-index.md. Legacy evidence is explicitly distinguished.
 */
import type { Finding } from "./types";

export default function Locations({ evidence }: { evidence: Record<string, any> }) {
  /** Present exact source references, per-file missing lines and honest unavailable/legacy states. */
  const findings: Finding[] = [
    ...(evidence.static?.findings ?? []),
    ...(evidence.diagnostics ?? []),
  ];
  const files = Object.entries(evidence.coverage?.files ?? {}) as [string, any][];
  const unlocated: { stage: string; reason: string }[] = evidence.unlocated_failures ?? [];
  const parserLimits = Object.entries(evidence.static?.files ?? {}).filter(([, value]) => (value as any).parsed === false) as [string, any][];
  return (
    <section className="panel" aria-label="Located diagnostics">
      <h3>Exact source locations</h3>
      <p className="note">Locations refer to this evidence snapshot, not an unsaved draft. Unused-code candidates are not coverage results or proof of a bug. Tool output is untrusted evidence.</p>
      {findings.length ? (
        <div className="location-table">
          <table>
            <thead><tr><th>File</th><th>Line</th><th>Column</th><th>Finding</th></tr></thead>
            <tbody>{findings.slice(0, 200).map((finding, index) => (
              <tr key={index}>
                <td><code>{finding.file ?? "Legacy: filename unavailable"}</code></td>
                <td>{finding.line ?? "Unavailable"}</td><td>{finding.column ?? "—"}</td>
                <td>{finding.code && <strong>{finding.code}: </strong>}{finding.message}
                  {finding.stage && <small> · {finding.stage}</small>}</td>
              </tr>
            ))}</tbody>
          </table>
        </div>
      ) : <p>No located findings were recorded. This is not proof that the source is bug-free.</p>}
      {(findings.length > 200 || evidence.static?.findings_truncated || evidence.diagnostics_truncated) &&
        <p>Display limited to 200 rows; inspect the JSON/HTML/ZIP for all retained findings. Analyzer limits may also truncate results.</p>}
      {unlocated.map((item, index) => <p key={index}><strong>{item.stage}</strong>: {item.reason}</p>)}
      {parserLimits.map(([name, value]) => <p key={name}><strong>{name}</strong>: parser stopped ({value.reason}). {value.location_available ? "See the located syntax diagnostic." : "Exact line unavailable; this file was not successfully analyzed."}</p>)}
      <h4>Uncovered Python lines</h4>
      <p className="note">Measured only under approved CLI inputs; generated pytest tests are outside this coverage run. Non-Python coverage is not built in.</p>
      {files.length ? files.map(([name, file]) => (
        <div className="coverage-file" key={name}>
          <h5>{name}</h5>
          {file.status === "measured" ? <>
            <p>Uncovered lines: <code>{file.missing_lines?.length ? file.missing_lines.join(", ") : "None recorded"}</code></p>
            <p>Missing branch arcs: <code>{file.missing_branches?.length ? file.missing_branches.map(([from, to]: number[]) => `${from} → ${to < 0 ? `exit(${to})` : to}`).join(", ") : "None recorded"}</code></p>
            {file.truncated && <p>Location list truncated; counts remain in the raw summary. An empty retained list does not establish full coverage.</p>}
          </> : <p>{file.reason ?? "Not measured; coverage unknown"}</p>}
        </div>
      )) : <p>{evidence.coverage?.status === "measured" ? "Legacy report: totals only, exact missing lines unavailable. Rerun the saved revision with the updated worker." : "Not measured. Run approved Python cases with the updated isolated worker to obtain exact missing lines."}</p>}
    </section>
  );
}
