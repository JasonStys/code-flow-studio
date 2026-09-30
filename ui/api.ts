/** Authenticated, same-origin client; no provider keys in the renderer. Symbols: docs/code-index.md. */
const fragment = new URLSearchParams(location.hash.slice(1));
const supplied = fragment.get("token");
if (supplied) {
  sessionStorage.setItem("studio-token", supplied);
  history.replaceState(null, "", location.pathname);
}

export async function api<T>(
  path: string,
  method = "GET",
  body?: unknown,
): Promise<T> {
  /** Send a bounded API request and expose actionable errors without logging source or credentials. */
  const response = await fetch(`/api/${path}`, {
    method,
    headers: {
      Authorization: `Bearer ${sessionStorage.getItem("studio-token") ?? ""}`,
      "Content-Type": "application/json",
    },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(
      typeof error.detail === "string"
        ? error.detail
        : "Invalid project: check filenames, sizes and fields",
    );
  }
  return response.json() as Promise<T>;
}

export async function download(run: string, format: "zip" | "html" | "json") {
  /** Download artifacts through auth headers; tokens never appear in URLs or report bodies. */
  const response = await fetch(`/api/runs/${run}/report?format=${format}`, {
    headers: {
      Authorization: `Bearer ${sessionStorage.getItem("studio-token") ?? ""}`,
    },
  });
  if (!response.ok) throw new Error("Report download failed");
  const url = URL.createObjectURL(await response.blob());
  const link = document.createElement("a");
  link.href = url;
  link.download = `code-flow-evidence.${format}`;
  link.click();
  URL.revokeObjectURL(url);
}
