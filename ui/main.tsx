/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * types: docs@L3
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
createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
