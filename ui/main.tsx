/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * functions: boot()@L37
 * variables: root@L35; response@L39; health@L41; screen@L44
 * </code-map> */

/** App entry and offline Monaco worker registry. Symbols/variables: docs/code-index.md. */
import React from "react";
import { createRoot } from "react-dom/client";
import { loader } from "@monaco-editor/react";
import * as monaco from "monaco-editor";
import EditorWorker from "monaco-editor/editor/editor.worker.js?worker";
import TSWorker from "monaco-editor/languages/features/typescript/ts.worker.js?worker";
import JSONWorker from "monaco-editor/languages/features/json/json.worker.js?worker";
import CSSWorker from "monaco-editor/languages/features/css/css.worker.js?worker";
import HTMLWorker from "monaco-editor/languages/features/html/html.worker.js?worker";
import App from "./App";
import Account from "./Account";
import { enableLegacyMode } from "./api";
import "./style.css";

self.MonacoEnvironment = {
  getWorker(_moduleId: string, label: string) {
    if (label === "typescript" || label === "javascript") return new TSWorker();
    if (label === "json") return new JSONWorker();
    if (label === "css" || label === "scss" || label === "less")
      return new CSSWorker();
    if (label === "html" || label === "handlebars" || label === "razor")
      return new HTMLWorker();
    return new EditorWorker();
  },
};
loader.config({ monaco });
const root = createRoot(document.getElementById("root")!);
/** Select a verified service mode; an auth failure never downgrades to legacy access. */
async function boot() {
  try {
    const response = await fetch("/health", { cache: "no-store" });
    if (!response.ok) throw new Error("The local service is unavailable.");
    const health = await response.json();
    if (health.status !== "ready")
      throw new Error("The local service is not ready.");
    let screen;
    if (health.mode === "private-local-accounts") screen = <Account />;
    else if (health.version === "0.1.0" && !health.mode) {
      enableLegacyMode();
      screen = <App />;
    } else
      throw new Error("Unrecognized service. Account access has been blocked.");
    root.render(<React.StrictMode>{screen}</React.StrictMode>);
  } catch (error) {
    root.render(
      <main className="account-card">
        <h1>Code Flow Studio</h1>
        <p role="alert">{(error as Error).message}</p>
        <p>Restart your local application, then reload this page.</p>
      </main>,
    );
  }
}
void boot();
