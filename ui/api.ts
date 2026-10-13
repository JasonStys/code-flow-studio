/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * functions: enableLegacyMode()@L13; setProviderRevision(revision: string)@L23; download(run: string, format: "zip" | "html" | "json")@L84
 * variables: privateMode@L9; providerRevision@L10; supplied@L15; response@L33; data@L40; headers@L54; response@L63; data@L73; response@L85; url@L103; link@L104
 * </code-map> */

/** Jason Stys: mode-locked transport; private credentials never enter browser storage or URLs. */
let privateMode = true;
let providerRevision = "";

/** Explicit historical-mode selection only after verifying its ready service, never after an auth failure. */
export function enableLegacyMode() {
  privateMode = false;
  const supplied = new URLSearchParams(location.hash.slice(1)).get("token");
  if (supplied) {
    sessionStorage.setItem("studio-token", supplied);
    history.replaceState(null, "", location.pathname);
  }
}

/** Remember only a nonsecret reviewed configuration version; rotate consent when settings change. */
export function setProviderRevision(revision: string) {
  providerRevision = revision;
}

/** Send local cookie/CSRF account requests; secret fields are not logged or reflected in errors. */
export async function account<T = any>(
  path: string,
  body?: unknown,
  method?: string,
): Promise<T> {
  const response = await fetch("/private/" + path, {
    method: method || (body === undefined ? "GET" : "POST"),
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", "X-CFS-Request": "v1" },
    body: body === undefined ? undefined : JSON.stringify(body),
    cache: "no-store",
  });
  const data = await response.json();
  if (!response.ok)
    throw new Error(
      typeof data.detail === "string" ? data.detail : "Invalid account request",
    );
  return data;
}

/** Use only the selected service mode; no downgrade or legacy-token fallback after a private denial. */
export async function api<T>(
  path: string,
  method = "GET",
  body?: unknown,
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  if (privateMode) {
    headers["X-CFS-Request"] = "v1";
    if (path === "ai") headers["X-CFS-Provider-Revision"] = providerRevision;
  } else
    headers.Authorization =
      "Bearer " + (sessionStorage.getItem("studio-token") || "");
  const response = await fetch(
    (privateMode ? "/private/api/" : "/api/") + path,
    {
      method,
      credentials: "same-origin",
      headers,
      cache: "no-store",
      body: body === undefined ? undefined : JSON.stringify(body),
    },
  );
  const data = await response.json();
  if (!response.ok)
    throw new Error(
      typeof data.detail === "string"
        ? data.detail
        : "Invalid project: check filenames, sizes and fields",
    );
  return data as T;
}

/** Download plaintext exports only after explicit selection; no auth values appear in filenames/URLs. */
export async function download(run: string, format: "zip" | "html" | "json") {
  const response = await fetch(
    (privateMode ? "/private/api/" : "/api/") +
      "runs/" +
      run +
      "/report?format=" +
      format,
    {
      credentials: "same-origin",
      cache: "no-store",
      headers: privateMode
        ? { "X-CFS-Request": "v1" }
        : {
            Authorization:
              "Bearer " + (sessionStorage.getItem("studio-token") || ""),
          },
    },
  );
  if (!response.ok) throw new Error("Report download failed");
  const url = URL.createObjectURL(await response.blob());
  const link = document.createElement("a");
  link.href = url;
  link.download = "code-flow-evidence." + format;
  link.click();
  URL.revokeObjectURL(url);
}
