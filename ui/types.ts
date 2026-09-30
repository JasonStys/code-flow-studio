/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * types: docs@L3; SourceFile@L8; Case@L13; Priorities@L19; Project@L26; Revision@L43; Run@L50; Capability@L56; AIResult@L62
 * </code-map> */

/** Shared renderer contracts. Server validation is authoritative. Symbols: docs/code-index.md. */
export interface SourceFile {
  name: string;
  content: string;
  encoding: "text" | "base64";
}
export interface Case {
  name: string;
  stdin: string;
  stdout: string;
  exit_code: number;
}
export interface Priorities {
  runtime: number;
  memory: number;
  readability: number;
  footprint: number;
  scrutiny: "standard" | "strict";
}
export interface Project {
  title: string;
  language: string;
  entry: string;
  files: SourceFile[];
  cases: Case[];
  requirements: string;
  tests: string;
  fuzz_methods: string[];
  fuzz_cases: number;
  seed: number;
  benchmark_repeats: number;
  mutation: boolean;
  fuzz_engine: string;
  fuzz_harness: string;
  priorities: Priorities;
}
export interface Revision {
  id: string;
  parent_id: string | null;
  title?: string;
  project: Project;
  runs?: Run[];
}
export interface Run {
  id: string;
  revision_id: string;
  status: string;
  result: Record<string, any>;
}
export interface Capability {
  id: number;
  name: string;
  mode: string;
  requirement: string;
}
export interface AIResult {
  provider: string;
  model: string;
  task: string;
  verified: boolean;
  proposal: {
    explanation: string;
    files: SourceFile[];
    tests: string;
    suggestions: string[];
  };
}
