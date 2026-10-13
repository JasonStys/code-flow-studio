/* <code-map>
 * Generated definition map; @L is the exact declaration line.
 * Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
 * types: FormEvent@L10; Status@L14; Provider@L24; Config@L33
 * functions: Creator()@L40; Help()@L60; value(form: HTMLFormElement, name: string)@L150; derive(phrase: string, salt: string | null)@L155; Account()@L182; refresh()@L195; run(task: ()@L215; authenticate(event: FormEvent<HTMLFormElement>)@L278; unlock(event: FormEvent<HTMLFormElement>)@L303; configure(event: FormEvent<HTMLFormElement>)@L315
 * variables: bytes@L156; material@L159; key@L166; result@L173; [status, setStatus]@L183; [loading, setLoading]@L184; [mode, setMode]@L185; [recovery, setRecovery]@L186; [notice, setNotice]@L187; [busy, setBusy]@L188; [settings, setSettings]@L189; [showSettings, setShowSettings]@L190; [idle, setIdle]@L191; lastHuman@L192; heartbeat@L193; response@L197; data@L210; disposed@L236; timer@L245; human@L248; close@L257; form@L281; data@L283; result@L288; form@L306; payload@L308; form@L318; id@L320; provider@L321; providers@L334; routes@L340; task@L341; data@L343; a@L532; next@L571; data@L684; form@L703
 * </code-map> */

/** Jason Stys: private account/key gate, accessible help, explicit provider setup and recoverable local lifecycle. */
import { useEffect, useRef, useState, type FormEvent } from "react";
import App from "./App";
import { account, setProviderRevision } from "./api";

interface Status {
  alias: string;
  configured: boolean;
  salt: string | null;
  unlocked: boolean;
  engine_busy: boolean;
  recovery_pending: boolean;
  save_failed: boolean;
  idle_seconds: 600 | 1800 | 7200;
}
interface Provider {
  id: string;
  kind: "openai" | "anthropic" | "ollama";
  url: string;
  model: string;
  ready: boolean;
  token_parameter: "max_tokens" | "max_completion_tokens";
  temperature: number | null;
}
interface Config {
  providers: Provider[];
  routes: Record<string, string>;
  revision: string;
}

/** Creator identity is public and never combined with a user's source or credentials. */
function Creator() {
  return (
    <p className="creator">
      Made by Jason Stys ·{" "}
      <a href="https://github.com/JasonStys" target="_blank" rel="noreferrer">
        GitHub
      </a>{" "}
      ·{" "}
      <a
        href="https://www.linkedin.com/in/jason-stys-31b30b351/"
        target="_blank"
        rel="noreferrer"
      >
        Contact on LinkedIn
      </a>
    </p>
  );
}

/** Contextual help makes execution/privacy/AI costs visible without advertising or tracking. */
function Help() {
  return (
    <details className="account-help">
      <summary>Help, privacy & installation</summary>
      <h3>Your development loop</h3>
      <ol>
        <li>
          Create a local alias and a unique 15–128 character login password.
          Save the once-shown recovery code privately.
        </li>
        <li>
          Choose a separate 20–256 character vault phrase, preferably six random
          words. No developer recovery backdoor exists.
        </li>
        <li>
          Use the offline editor or import flat source/data files; define
          independent expected stdin/stdout cases. Save revisions before
          locking.
        </li>
        <li>
          Static review measures source and flags syntax/readability risks
          without execution. Actual compile/test/fuzz/performance jobs require
          the reviewed isolated local Docker worker image.
        </li>
        <li>
          Review genuine run reports and history; export HTML/JSON/ZIP
          explicitly. AI proposals never become verified results without
          independent tests.
        </li>
      </ol>
      <h3>Isolation and AI</h3>
      <p>
        Submitted code never runs directly on this PC. Without a local Docker
        engine/image, jobs are blocked—not passed. Worker jobs have no network,
        a read-only root, restricted memory/CPU/processes and only one read-only
        project mount. Docker is a local defense-in-depth boundary, not a
        certified public multi-tenant sandbox. This app does not install or
        repair Docker, drivers or system protections.
      </p>
      <p>
        No outside AI calls, model downloads, telemetry, ads, external fonts or
        unsolicited popups occur by default. Configure your own local model or
        HTTPS provider and review the selected destinations before consenting to
        source transmission. Remote providers can receive/store your source and
        incur charges according to their terms. Live suggestions remain opt-in.
        Unknown models/protocols may not support the chosen token/temperature
        settings.
      </p>
      <h3>Private data and keys</h3>
      <p>
        Accounts/history/provider settings live outside Git and installation
        files. Login passwords are scrypt hashes; locked source/history/provider
        keys use AES-256-GCM. The browser derives a key and gives it to the
        trusted local service while unlocked. Source, model API keys and memory
        are then plaintext on your device; an OS owner/admin, malware, untrusted
        Docker engine or modified app can access them. Use device encryption and
        a private OS login. This is not browser-only E2EE.
      </p>
      <p>
        Each session proves its vault phrase before reading active source. Other
        accounts cannot read its revisions, runs or provider settings. Lock/sign
        out cancels owned jobs, seals and removes managed plaintext; idle lock
        defaults to ten minutes and polling does not renew it. Choose a longer
        limit explicitly for slow jobs. Crashes can leave owner-bound recovery
        files. Failed saving preserves working data; free disk space, then
        retry. Forgotten vault phrases cannot be recovered.
      </p>
      <h3>Backups and installation</h3>
      <p>
        Encrypted archive downloads also need their account/key configuration:
        cold-back up the entire protected account root after quitting. An
        archive alone does not restore login settings. Plaintext source/report
        exports need separate protection. Delete removes live account data, not
        backups or disk sectors.
      </p>
      <p>
        Use official checksummed Windows/macOS/Linux releases; packages are
        unsigned, not notarized or independently certified. Do not blindly
        bypass OS warnings. Browser UI is responsive, but no public host or
        native mobile installer is provided. Limits: one unlocked account
        engine, 500 revisions, 128 MiB history, 512 MiB archived workspace, 20
        flat files/1 MiB per project and 4 MiB account requests. Never put
        credentials/private code into GitHub issues.
      </p>
      <Creator />
    </details>
  );
}

/** Extract values from submitted forms only; no browser storage or background credential collection. */
function value(form: HTMLFormElement, name: string) {
  return String(new FormData(form).get(name) || "");
}

/** Derive a local vault key; clear its byte array after sending, without claiming secure JS memory erasure. */
async function derive(phrase: string, salt: string | null) {
  const bytes = salt
    ? Uint8Array.from(atob(salt), (c) => c.charCodeAt(0))
    : crypto.getRandomValues(new Uint8Array(16));
  const material = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(phrase),
    "PBKDF2",
    false,
    ["deriveBits"],
  );
  const key = new Uint8Array(
    await crypto.subtle.deriveBits(
      { name: "PBKDF2", salt: bytes, iterations: 600000, hash: "SHA-256" },
      material,
      256,
    ),
  );
  const result = {
    key: btoa(String.fromCharCode(...key)),
    salt: btoa(String.fromCharCode(...bytes)),
  };
  key.fill(0);
  return result;
}

/** Manage one authenticated local session; every unlock/unmount drops the previous editor state. */
export default function Account() {
  const [status, setStatus] = useState<Status | null>(null);
  const [loading, setLoading] = useState(true);
  const [mode, setMode] = useState("login");
  const [recovery, setRecovery] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const [settings, setSettings] = useState<Config | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [idle, setIdle] = useState<600 | 1800 | 7200>(600);
  const lastHuman = useRef(Date.now());
  const heartbeat = useRef(0);

  async function refresh() {
    /** 401 means signed out; other failures stay visible rather than silently switching transport modes. */
    const response = await fetch("/private/account", {
      credentials: "same-origin",
      cache: "no-store",
    });
    if (response.status === 401) {
      setStatus(null);
      setSettings(null);
      return;
    }
    if (!response.ok)
      throw new Error(
        "Cannot read account status; refresh or wait for local service",
      );
    const data = (await response.json()) as Status;
    setStatus(data);
    setIdle(data.idle_seconds);
  }

  async function run(task: () => Promise<void>) {
    /** Serialize intentional actions and show errors without logging supplied secret fields. */
    if (busy) return;
    setBusy(true);
    setNotice("");
    try {
      await task();
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Action failed");
    } finally {
      setBusy(false);
    }
  }

  useEffect(() => {
    void refresh()
      .catch((e) => setNotice(e.message))
      .finally(() => setLoading(false));
  }, []);
  useEffect(() => {
    if (!status?.unlocked) return;
    let disposed = false;
    void account<Config>("providers")
      .then((data) => {
        if (!disposed) {
          setSettings(data);
          setProviderRevision(data.revision);
        }
      })
      .catch((e) => setNotice(e.message));
    const timer = setInterval(() => {
      void refresh().catch((e) => setNotice(e.message));
    }, 4000);
    const human = () => {
      lastHuman.current = Date.now();
      if (Date.now() - heartbeat.current > 30000) {
        heartbeat.current = Date.now();
        void account("activity", { idle_seconds: idle }).catch((e) =>
          setNotice(e.message),
        );
      }
    };
    const close = () => {
      void fetch("/private/lock", {
        method: "POST",
        credentials: "same-origin",
        keepalive: true,
        headers: { "Content-Type": "application/json", "X-CFS-Request": "v1" },
        body: "{}",
      });
    };
    window.addEventListener("keydown", human);
    window.addEventListener("pointerdown", human);
    window.addEventListener("pagehide", close);
    return () => {
      disposed = true;
      clearInterval(timer);
      window.removeEventListener("keydown", human);
      window.removeEventListener("pointerdown", human);
      window.removeEventListener("pagehide", close);
    };
  }, [status?.unlocked, idle]);

  async function authenticate(event: FormEvent<HTMLFormElement>) {
    /** Registration/recovery codes are shown once; password fields are cleared after success. */
    event.preventDefault();
    const form = event.currentTarget;
    await run(async () => {
      const data: Record<string, string> = {
        alias: value(form, "alias"),
        password: value(form, "password"),
      };
      if (mode === "recover") data.recovery = value(form, "recovery");
      const result = await account(
        mode === "register"
          ? "register"
          : mode === "recover"
            ? "reset"
            : "login",
        data,
      );
      form.reset();
      if (result.recovery) setRecovery(result.recovery);
      setMode("login");
      await refresh();
    });
  }

  async function unlock(event: FormEvent<HTMLFormElement>) {
    /** Phrase never leaves this page; the derived key goes only to the trusted local service. */
    event.preventDefault();
    const form = event.currentTarget;
    await run(async () => {
      const payload = await derive(value(form, "phrase"), status?.salt || null);
      await account("unlock", payload);
      form.reset();
      await refresh();
    });
  }

  async function configure(event: FormEvent<HTMLFormElement>) {
    /** Save explicitly chosen own secrets; destination changes never reuse an old provider key. */
    event.preventDefault();
    const form = event.currentTarget;
    await run(async () => {
      const id = value(form, "id");
      const provider = {
        id,
        kind: value(form, "kind"),
        url: value(form, "url"),
        model: value(form, "model"),
        key: value(form, "key"),
        retain_key: value(form, "retain") === "on",
        token_parameter: value(form, "parameter"),
        temperature:
          value(form, "temperature") === ""
            ? null
            : Number(value(form, "temperature")),
      };
      const providers = [
        ...(settings?.providers || [])
          .filter((p) => p.id !== id)
          .map((p) => ({ ...p, ready: undefined, retain_key: true })),
        provider,
      ];
      const routes: Record<string, string> = { ...settings?.routes };
      for (const task of ["generate", "tests", "improve", "suggest"])
        if (value(form, task) === "on") routes[task] = id;
      const data = await account<Config>(
        "providers",
        { providers, routes },
        "PUT",
      );
      setSettings(data);
      setProviderRevision(data.revision);
      window.dispatchEvent(new Event("cfs-settings-changed"));
      form.reset();
      setNotice(
        "Provider saved privately. Review destinations and renew source consent before AI use.",
      );
    });
  }

  if (loading)
    return (
      <main className="account-card">
        <h1>Code Flow Studio</h1>
        <p>Connecting to your local account service…</p>
        {notice && <p role="alert">{notice}</p>}
      </main>
    );
  if (!status?.unlocked)
    return (
      <main className="account-card">
        <span className="eyebrow">YOUR CODE. YOUR LOCAL WORKSPACE.</span>
        <h1>Code Flow Studio</h1>
        {recovery ? (
          <section>
            <h2>Save your login recovery code</h2>
            <p>
              This is shown once. It cannot recover a forgotten vault phrase.
            </p>
            <code id="recovery-code">{recovery}</code>
            <button onClick={() => setRecovery("")}>
              I saved it privately
            </button>
          </section>
        ) : status ? (
          <section>
            <h2>Unlock your private code workspace</h2>
            <p>
              Signed in as {status.alias}. Every session proves its own vault
              phrase.
            </p>
            {status.engine_busy && (
              <p>
                Another account is using the local engine. Ask its owner to lock
                first.
              </p>
            )}
            {status.recovery_pending && (
              <p>
                Interrupted working files were preserved. The same owner must
                unlock and lock to recover them.
              </p>
            )}
            <form onSubmit={unlock}>
              <label>
                Vault phrase
                <input
                  name="phrase"
                  type="password"
                  autoComplete="off"
                  minLength={20}
                  maxLength={256}
                  required
                />
              </label>
              <button disabled={busy}>Unlock or create workspace</button>
            </form>
            <button
              onClick={() =>
                void run(async () => {
                  await account("logout", {});
                  await refresh();
                })
              }
            >
              Sign out
            </button>
          </section>
        ) : (
          <section>
            <h2>
              {mode === "register"
                ? "Create your local account"
                : mode === "recover"
                  ? "Recover your login"
                  : "Sign in to your local studio"}
            </h2>
            <p>
              Local-only accounts. No public host, tracking or shared demo
              passwords.
            </p>
            <form onSubmit={authenticate}>
              <label>
                Account alias
                <input
                  name="alias"
                  autoComplete="username"
                  pattern="[a-z0-9_][a-z0-9_-]{2,39}"
                  required
                />
              </label>
              <label>
                {mode === "recover" ? "New login password" : "Login password"}
                <input
                  name="password"
                  type="password"
                  autoComplete={
                    mode === "login" ? "current-password" : "new-password"
                  }
                  minLength={15}
                  maxLength={128}
                  required
                />
              </label>
              {mode === "recover" && (
                <label>
                  Login recovery code
                  <input
                    name="recovery"
                    autoComplete="off"
                    minLength={32}
                    maxLength={128}
                    required
                  />
                </label>
              )}
              <button disabled={busy}>
                {mode === "register"
                  ? "Register account"
                  : mode === "recover"
                    ? "Reset login"
                    : "Sign in securely"}
              </button>
            </form>
            <div className="account-actions">
              {[
                ["login", "Sign in"],
                ["register", "Create account"],
                ["recover", "Recover login"],
              ].map(([id, label]) => (
                <button
                  key={id}
                  onClick={() => {
                    setMode(id);
                    setNotice("");
                  }}
                >
                  {label}
                </button>
              ))}
            </div>
          </section>
        )}
        <p role="status" id="account-notice">
          {notice}
        </p>
        <Creator />
        <Help />
      </main>
    );

  return (
    <>
      <section
        className="account-toolbar"
        aria-label="Private account controls"
      >
        <span>Private · {status.alias}</span>
        <button
          disabled={busy}
          onClick={() =>
            void run(async () => {
              await account("save", {});
              setNotice("Complete encrypted snapshot saved.");
            })
          }
        >
          Save encrypted snapshot
        </button>
        <button
          disabled={busy}
          onClick={() =>
            void run(async () => {
              await account("save", {});
              const a = document.createElement("a");
              a.href = "/private/backup";
              a.download = "code-flow-encrypted.cfsvault";
              a.click();
            })
          }
        >
          Download encrypted archive
        </button>
        <button
          disabled={busy}
          onClick={() =>
            void run(async () => {
              await account("lock", {});
              await refresh();
            })
          }
        >
          Lock workspace
        </button>
        <button
          disabled={busy}
          onClick={() =>
            void run(async () => {
              await account("logout", {});
              await refresh();
            })
          }
        >
          Sign out
        </button>
        <button onClick={() => setShowSettings(!showSettings)}>
          Private AI settings
        </button>
        <label>
          Human-idle lock
          <select
            value={idle}
            onChange={(event) => {
              const next = Number(event.target.value) as typeof idle;
              setIdle(next);
              void run(async () => {
                await account("activity", { idle_seconds: next });
              });
            }}
          >
            <option value={600}>10 minutes</option>
            <option value={1800}>30 minutes</option>
            <option value={7200}>2 hours</option>
          </select>
        </label>
        <p id="account-notice" role="status">
          {notice ||
            (status.save_failed
              ? "Saving failed. Preserve recovery data and retry after freeing disk space."
              : "Save revisions before locking. Plaintext exports need your own protection.")}
        </p>
        <Creator />
        <Help />
      </section>
      {showSettings && (
        <section className="account-settings">
          <h2>Your private AI providers</h2>
          <p>
            Source may leave this device only after your explicit consent.
            Configured/key-available does not prove a model is reachable or
            useful.
          </p>
          <ul>
            {settings?.providers.map((p) => (
              <li key={p.id}>
                {p.id} · {p.kind} · {p.model} · {p.url} ·{" "}
                {p.ready ? "configured" : "key missing"}
              </li>
            ))}
          </ul>
          <form onSubmit={configure}>
            <label>
              Provider ID
              <input name="id" pattern="[a-z][a-z0-9_-]{0,39}" required />
            </label>
            <label>
              Protocol
              <select name="kind">
                <option value="openai">OpenAI-compatible</option>
                <option value="anthropic">Anthropic</option>
                <option value="ollama">Ollama</option>
              </select>
            </label>
            <label>
              Full API endpoint
              <input
                name="url"
                type="url"
                required
                placeholder="Your approved HTTPS or loopback endpoint"
              />
            </label>
            <label>
              Model identifier
              <input name="model" maxLength={128} required />
            </label>
            <label>
              Own API key / local API token
              <input
                name="key"
                type="password"
                autoComplete="off"
                maxLength={4096}
              />
            </label>
            <label>
              <input name="retain" type="checkbox" />
              Retain this provider's saved key only if its destination is
              unchanged
            </label>
            <label>
              Completion limit parameter
              <select name="parameter">
                <option value="max_tokens">
                  max_tokens (legacy compatible)
                </option>
                <option value="max_completion_tokens">
                  max_completion_tokens
                </option>
              </select>
            </label>
            <label>
              Temperature (blank = provider default)
              <input
                name="temperature"
                type="number"
                min={0}
                max={2}
                step="0.1"
              />
            </label>
            <fieldset>
              <legend>Route selected tasks to this provider</legend>
              {["generate", "tests", "improve", "suggest"].map((task) => (
                <label key={task}>
                  <input type="checkbox" name={task} defaultChecked />
                  {task}
                </label>
              ))}
            </fieldset>
            <button disabled={busy}>Save provider privately</button>
          </form>
          <button
            disabled={busy}
            onClick={() =>
              void run(async () => {
                const data = await account<Config>(
                  "providers",
                  { providers: [], routes: {} },
                  "PUT",
                );
                setSettings(data);
                setProviderRevision(data.revision);
                window.dispatchEvent(new Event("cfs-settings-changed"));
                setNotice("All own provider settings removed.");
              })
            }
          >
            Remove all my providers
          </button>
          <details>
            <summary>Delete local account</summary>
            <form
              onSubmit={(event) => {
                event.preventDefault();
                const form = event.currentTarget;
                void run(async () => {
                  await account("delete", {
                    password: value(form, "password"),
                    confirm: value(form, "confirm") === "on",
                  });
                  form.reset();
                  await refresh();
                });
              }}
            >
              <label>
                Current login password
                <input
                  name="password"
                  type="password"
                  autoComplete="current-password"
                  required
                />
              </label>
              <label>
                <input name="confirm" type="checkbox" required />I backed up
                what I need and approve permanent deletion of this local
                account.
              </label>
              <button disabled={busy}>Delete my local account</button>
            </form>
          </details>
        </section>
      )}
      <App privateAccounts />
    </>
  );
}
