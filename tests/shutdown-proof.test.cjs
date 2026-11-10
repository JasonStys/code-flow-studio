/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * variables: { test }@L8; assert@L9; { shutdownProof }@L10; body@L14; status@L16; canceled@L25; body@L26
 * </code-map> */

/** Jason Stys: actual response-stream oracles for bounded native shutdown diagnostics. Symbols: docs/code-index.md. */
const { test } = require("node:test");
const assert = require("node:assert/strict");
const { shutdownProof } = require("../desktop/shutdown-proof.cjs");

test("only an actual successful boolean stopping receipt proves acknowledgement", async () => {
  assert.equal(await shutdownProof(Response.json({ stopping: true })), true);
  for (const body of [{ stopping: false }, { stopping: "true" }, [], null])
    assert.equal(await shutdownProof(Response.json(body)), false);
  for (const status of [403, 409, 429, 500])
    assert.equal(
      await shutdownProof(Response.json({ stopping: true }, { status })),
      false,
    );
  assert.equal(await shutdownProof(new Response("not-json")), false);
});

test("oversized actual streams are canceled before accepting a trailing success object", async () => {
  let canceled = false;
  const body = new ReadableStream({
    start(controller) {
      controller.enqueue(new TextEncoder().encode(" ".repeat(1025)));
      controller.enqueue(new TextEncoder().encode('{"stopping":true}'));
    },
    cancel() {
      canceled = true;
    },
  });
  assert.equal(await shutdownProof(new Response(body)), false);
  assert.equal(canceled, true);
});
