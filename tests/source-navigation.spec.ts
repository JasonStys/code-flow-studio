/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * functions: project()@L28; reference(overrides: Partial<SourceLocation> = {})@L34
 * variables: hash@L24; source@L26; normalized@L49; rows@L50; line@L51; [start, end]@L52; invalid@L60; language@L71; candidate@L85; candidate@L92; line@L103; candidate@L143; candidate@L160; generated@L167; candidate@L214
 * </code-map> */

/**
 * Independent content-binding regressions by Jason Stys; these tests never execute submitted code.
 * Node's SHA-256 supplies the oracle for the browser-compatible WebCrypto navigation implementation.
 * Exact declarations and fixture variables are indexed in docs/code-index.md.
 */
import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";
import { demo } from "../ui/demo";
import type { Project, SourceLocation } from "../ui/types";
import {
  sourceFingerprint,
  sourceLineCount,
  sourceLineSelection,
  verifySourceLocation,
} from "../ui/source-navigation";

const hash = (text: string) =>
  createHash("sha256").update(text, "utf8").digest("hex");
const source =
  "# Unicode é 🛰\r\ndef sample():\r    return 1\n# literal separator:\u2028tail\n";
function project(): Project {
  return {
    ...structuredClone(demo),
    files: [{ name: "helper.py", content: source, encoding: "text" }],
  };
}
function reference(overrides: Partial<SourceLocation> = {}): SourceLocation {
  return {
    file: "helper.py",
    line: 3,
    source_sha256: hash(source),
    artifact: "source",
    ...overrides,
  };
}

test("exact UTF-8 bytes and physical lines match the independent oracle", async () => {
  expect(await sourceFingerprint(source)).toBe(hash(source));
  expect(sourceLineCount(source)).toBe(5);
  expect(sourceLineCount("")).toBe(1);
  expect(sourceLineCount("a\r\nb\nc\rd")).toBe(4);
  const normalized = source.replace(/\r\n?/g, "\n");
  const rows = source.split(/\r\n|\r|\n/);
  for (let line = 1; line <= rows.length; line += 1) {
    const [start, end] = sourceLineSelection(source, line);
    expect(normalized.slice(start, end)).toBe(rows[line - 1]);
    expect(start).toBe(
      rows.slice(0, line - 1).reduce((size, row) => size + row.length + 1, 0),
    );
  }
  expect(sourceLineSelection("", 1)).toEqual([0, 0]);
  expect(() => sourceLineSelection(source, 6)).toThrow("outside");
  for (const invalid of [0, -1, 1.5, Number.NaN])
    expect(() => sourceLineSelection(source, invalid)).toThrow("positive");
  expect(await verifySourceLocation(reference(), project())).toEqual({
    ok: true,
    content: source,
    lines: 5,
    sha256: hash(source),
  });
});

test("binding works across all twelve language manifests without claiming compiler acceptance", async () => {
  for (const language of [
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
  ]) {
    const candidate = project();
    candidate.language = language;
    expect((await verifySourceLocation(reference(), candidate)).ok).toBe(true);
  }
});

test("stale bytes, CRLF normalization and out-of-bounds lines cannot be navigated", async () => {
  const candidate = project();
  candidate.files[0].content = "# newer draft\n" + source;
  expect(await verifySourceLocation(reference(), candidate)).toMatchObject({
    ok: false,
    reason: expect.stringContaining("fingerprint mismatch"),
  });
  candidate.files[0].content = source.replaceAll("\r\n", "\n");
  expect((await verifySourceLocation(reference(), candidate)).ok).toBe(false);
  expect(
    await verifySourceLocation(reference({ line: 6 }), project()),
  ).toMatchObject({ ok: false, reason: expect.stringContaining("outside") });
  for (const line of [0, -1, 1.5, Number.NaN, Number.POSITIVE_INFINITY])
    expect(
      (await verifySourceLocation(reference({ line }), project())).ok,
    ).toBe(false);
  expect(
    (
      await verifySourceLocation(
        reference({ source_sha256: "legacy" }),
        project(),
      )
    ).ok,
  ).toBe(false);
  expect(
    (
      await verifySourceLocation(
        reference({ source_sha256: hash(source) + "\n" }),
        project(),
      )
    ).ok,
  ).toBe(false);
  expect(
    (
      await verifySourceLocation(
        reference({ source_sha256: null as unknown as string }),
        project(),
      )
    ).ok,
  ).toBe(false);
});

test("unknown artifacts and binary fixtures never fall back to a filename or path", async () => {
  expect((await verifySourceLocation(reference(), null)).ok).toBe(false);
  expect(
    (
      await verifySourceLocation(
        reference({ file: "../private.txt" }),
        project(),
      )
    ).ok,
  ).toBe(false);
  const candidate = project();
  candidate.files[0].encoding = "base64";
  expect(await verifySourceLocation(reference(), candidate)).toMatchObject({
    ok: false,
    reason: expect.stringContaining("Binary"),
  });
  expect(
    (
      await verifySourceLocation(
        reference({ artifact: "generated" }),
        project(),
      )
    ).ok,
  ).toBe(false);
});

test("known generated tests/harnesses are distinct from same-named project files", async () => {
  const candidate = project();
  candidate.tests = "def test_demo():\n    assert 1 == 1\n";
  candidate.files.push({
    name: "test_generated.py",
    content: "# unrelated supplied file",
    encoding: "text",
  });
  const generated = reference({
    file: "test_generated.py",
    line: 2,
    artifact: "generated",
    source_sha256: hash(candidate.tests),
  });
  expect((await verifySourceLocation(generated, candidate)).ok).toBe(true);
  expect(
    (
      await verifySourceLocation(
        { ...generated, artifact: "source" },
        candidate,
      )
    ).ok,
  ).toBe(false);
  candidate.fuzz_engine = "atheris";
  candidate.fuzz_harness = "# approved inert harness\n";
  expect(
    (
      await verifySourceLocation(
        reference({
          file: "fuzz_harness.py",
          line: 1,
          artifact: "generated",
          source_sha256: hash(candidate.fuzz_harness),
        }),
        candidate,
      )
    ).ok,
  ).toBe(true);
  candidate.fuzz_engine = "libfuzzer";
  expect(
    (
      await verifySourceLocation(
        reference({
          file: "fuzz_harness.cpp",
          line: 1,
          artifact: "generated",
          source_sha256: hash(candidate.fuzz_harness),
        }),
        candidate,
      )
    ).ok,
  ).toBe(true);
});

test("invalid Unicode cannot collide with TextEncoder replacement and oversized sources are bounded", async () => {
  const candidate = project();
  candidate.files[0].content = "\ud800";
  expect(
    await verifySourceLocation(
      reference({ line: 1, source_sha256: hash("\ufffd") }),
      candidate,
    ),
  ).toMatchObject({
    ok: false,
    reason: expect.stringContaining("invalid Unicode"),
  });
  await expect(sourceFingerprint("x".repeat(1_048_577))).rejects.toThrow(
    "byte limit",
  );
  await expect(sourceFingerprint("🛰".repeat(262_145))).rejects.toThrow(
    "byte limit",
  );
});
