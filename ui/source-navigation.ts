/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * types: SourceVerification@L19
 * functions: sourceFingerprint(content: string)@L24; sourceLineCount(content: string)@L47
 * variables: MAX_SOURCE_BYTES@L17; character@L28; point@L29; bytes@L33; digest@L40; lines@L48; index@L49; content@L83; harnessName@L87; file@L94; digest@L108; lines@L121
 * </code-map> */

/**
 * Content-bound in-memory source navigation by Jason Stys.
 * Functions validate references, bind only supplied snapshots and hash exact UTF-8 content.
 * State is ephemeral; no source is uploaded, persisted, executed or loaded from a filesystem path.
 * Exact symbol/variable locations are generated in docs/code-index.md.
 */
import type { Project, SourceLocation } from "./types";

const MAX_SOURCE_BYTES = 1_048_576;

export type SourceVerification =
  | { ok: true; content: string; lines: number; sha256: string }
  | { ok: false; reason: string };

/** Return a cryptographic fingerprint of exact source bytes, without normalizing newlines. */
export async function sourceFingerprint(content: string): Promise<string> {
  if (content.length > MAX_SOURCE_BYTES)
    throw new Error("Source exceeds the navigation byte limit.");
  // TextEncoder replaces lone surrogates; reject them so a replacement cannot masquerade as exact bytes.
  for (const character of content) {
    const point = character.codePointAt(0)!;
    if (point >= 0xd800 && point <= 0xdfff)
      throw new Error("Source contains invalid Unicode.");
  }
  const bytes = new TextEncoder().encode(content);
  if (bytes.byteLength > MAX_SOURCE_BYTES)
    throw new Error("Source exceeds the navigation byte limit.");
  if (!globalThis.crypto?.subtle)
    throw new Error(
      "Secure browser hashing is unavailable; use the local app or HTTPS.",
    );
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)]
    .map((value) => value.toString(16).padStart(2, "0"))
    .join("");
}

/** Count physical lines exactly like backend location validation; Unicode separators are literal text. */
export function sourceLineCount(content: string): number {
  let lines = 1;
  for (let index = 0; index < content.length; index += 1) {
    if (content[index] === "\r") {
      lines += 1;
      if (content[index + 1] === "\n") index += 1;
    } else if (content[index] === "\n") lines += 1;
  }
  return lines;
}

/** Verify source identity and bounds against one immutable manifest; never infer missing evidence. */
export async function verifySourceLocation(
  location: SourceLocation,
  snapshot: Project | null,
): Promise<SourceVerification> {
  if (
    !Number.isSafeInteger(location.line) ||
    location.line < 1 ||
    typeof location.file !== "string" ||
    typeof location.source_sha256 !== "string" ||
    location.source_sha256.length !== 64 ||
    !/^[a-f0-9]{64}$/i.test(location.source_sha256)
  ) {
    return {
      ok: false,
      reason:
        "This reference has no valid content fingerprint or one-based source line. Rerun legacy evidence.",
    };
  }
  if (snapshot === null)
    return {
      ok: false,
      reason:
        "The evidence source snapshot is unavailable. Open its saved revision or rerun a static review.",
    };
  let content: string | undefined;
  if (location.artifact === "generated") {
    if (location.file === "test_generated.py" && snapshot.tests)
      content = snapshot.tests;
    const harnessName =
      snapshot.fuzz_engine === "atheris"
        ? "fuzz_harness.py"
        : "fuzz_harness.cpp";
    if (location.file === harnessName && snapshot.fuzz_harness)
      content = snapshot.fuzz_harness;
  } else if (location.artifact === "source") {
    const file = snapshot.files.find((item) => item.name === location.file);
    if (file?.encoding === "base64")
      return {
        ok: false,
        reason: "Binary fixtures have no navigable source lines.",
      };
    content = file?.content;
  }
  if (content === undefined)
    return {
      ok: false,
      reason:
        "This exact artifact is not present in the evidence snapshot; no path was opened.",
    };
  let digest: string;
  try {
    digest = await sourceFingerprint(content);
  } catch (error) {
    return { ok: false, reason: (error as Error).message };
  }
  if (digest !== location.source_sha256.toLowerCase()) {
    return {
      ok: false,
      reason:
        "Source fingerprint mismatch. The content changed or is not the source measured by this evidence; navigation is blocked.",
    };
  }
  const lines = sourceLineCount(content);
  if (location.line > lines)
    return {
      ok: false,
      reason: `Line ${location.line} is outside the verified source (${lines} physical lines); navigation is blocked.`,
    };
  return { ok: true, content, lines, sha256: digest };
}
