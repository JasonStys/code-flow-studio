/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * functions: shutdownProof(response)@L10
 * variables: reader@L12; chunks@L13; length@L14; part@L17; value@L23
 * </code-map> */

/** Jason Stys: bounded, value-free launcher shutdown receipt inspection. Symbols: docs/code-index.md. */
/** Read at most 1024 response bytes; malformed, oversized or negative receipts never prove shutdown. */
async function shutdownProof(response) {
  if (response.status !== 200 || !response.body) return false;
  const reader = response.body.getReader();
  const chunks = [];
  let length = 0;
  try {
    while (true) {
      const part = await reader.read();
      if (part.done) break;
      length += part.value.byteLength;
      if (length > 1024) return false;
      chunks.push(Buffer.from(part.value));
    }
    const value = JSON.parse(Buffer.concat(chunks).toString("utf8"));
    return value !== null && !Array.isArray(value) && value.stopping === true;
  } catch {
    return false;
  } finally {
    await reader.cancel();
    reader.releaseLock();
  }
}
module.exports = { shutdownProof };
