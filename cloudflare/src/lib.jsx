import React, { createContext, useContext, useEffect, useState } from "react";
import { LoaderCircle, X, AlertCircle, LockKeyhole } from "lucide-react";
import { appBase, withAppBase } from "../shared/routing.mjs";
const base = appBase(location.pathname);
export const appPath = (path) => withAppBase(path, base);
export const AppContext = createContext(null);
export const useApp = () => useContext(AppContext);
export async function api(path, options = {}) {
  const response = await fetch(appPath(path), {
    ...options,
    headers: {
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
    body: options.body ? JSON.stringify(options.body) : undefined,
  });
  const data = await response
    .json()
    .catch(() => ({ error: "The server returned an unexpected response." }));
  if (!response.ok)
    throw new Error(data.error || `Request failed (${response.status}).`);
  return data;
}
export function useData(url, fallback = null) {
  const { revision } = useApp();
  const [state, set] = useState({ data: fallback, loading: true, error: "" });
  useEffect(() => {
    if (!url) {
      set({ data: fallback, loading: false, error: "" });
      return;
    }
    let current = true;
    const controller = new AbortController();
    set((s) => ({ ...s, loading: true, error: "" }));
    api(url, { signal: controller.signal })
      .then((data) => {
        if (current) set({ data, loading: false, error: "" });
      })
      .catch((e) => {
        if (current && e.name !== "AbortError")
          set((s) => ({ ...s, loading: false, error: e.message }));
      });
    return () => {
      current = false;
      controller.abort();
    };
  }, [url, revision]);
  return state;
}
export function useTask() {
  const { notify } = useApp(),
    [busy, setBusy] = useState(false);
  return {
    busy,
    run: async (fn) => {
      if (busy) return;
      setBusy(true);
      try {
        return await fn();
      } catch (e) {
        notify(e.message, "error");
      } finally {
        setBusy(false);
      }
    },
  };
}
export function Loading({ label = "Loading…" }) {
  return (
    <div className="loading" role="status">
      <LoaderCircle className="spin" size={20} />
      {label}
    </div>
  );
}
export function ErrorBox({ error }) {
  return error ? (
    <div className="notice error" role="alert">
      <AlertCircle size={18} />
      <span>{error}</span>
    </div>
  ) : null;
}
export function Notice({ children }) {
  return <div className="notice">{children}</div>;
}
export function Empty({ icon: Icon = AlertCircle, title, children }) {
  return (
    <div className="empty">
      <Icon size={30} />
      <h3>{title}</h3>
      <p>{children}</p>
    </div>
  );
}
export function AdminGate({ children }) {
  const { user, authLoading, go } = useApp();
  if (authLoading) return <Loading />;
  if (!user)
    return (
      <Empty icon={LockKeyhole} title="Administrator access">
        <span>Sign in to manage websites and private workspace data.</span>
        <button className="primary" onClick={() => go("login")}>
          Admin sign in
        </button>
      </Empty>
    );
  return children;
}
export function Heading({ eyebrow = "WORKSPACE", title, children, actions }) {
  return (
    <header className="page-heading">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        {children && <p className="subtitle">{children}</p>}
      </div>
      {actions && <div className="heading-actions">{actions}</div>}
    </header>
  );
}
export function Field({
  label,
  name,
  value,
  onChange,
  type = "text",
  options,
  required = false,
  placeholder,
  help,
  ...props
}) {
  const id = React.useId();
  return (
    <label
      className={"field " + (type === "textarea" ? "wide" : "")}
      htmlFor={id}
    >
      <span>
        {label}
        {required && " *"}
      </span>
      {options ? (
        <select
          id={id}
          name={name}
          value={value ?? ""}
          onChange={(e) => onChange(e.target.value)}
          required={required}
          {...props}
        >
          {options.map((v) => (
            <option
              key={typeof v === "object" ? v.value : v}
              value={typeof v === "object" ? v.value : v}
            >
              {typeof v === "object" ? v.label : v}
            </option>
          ))}
        </select>
      ) : type === "textarea" ? (
        <textarea
          id={id}
          name={name}
          value={value ?? ""}
          onChange={(e) => onChange(e.target.value)}
          required={required}
          placeholder={placeholder}
          rows={4}
          {...props}
        />
      ) : (
        <input
          id={id}
          name={name}
          type={type}
          value={value ?? ""}
          onChange={(e) => onChange(e.target.value)}
          required={required}
          placeholder={placeholder}
          {...props}
        />
      )}{" "}
      {help && <small>{help}</small>}
    </label>
  );
}
export const label = (k) =>
  ({
    da: "DA",
    dr: "DR",
    tat: "Turnaround time",
    general_price: "Selling price",
    casino_price: "Casino selling price",
    original_price: "Original cost",
    casino_original_price: "Original casino cost",
    type: "Listed niche / type",
    site: "Website",
    active: "Visible on team page",
    manual_price: "Manual selling price",
    source_file: "Source file",
    image_path: "Photo",
    markup_percent: "Markup %",
  })[k] || k.replaceAll("_", " ").replace(/^./, (c) => c.toUpperCase());
export function Fields({ fields, value, setValue, required = [] }) {
  return (
    <div className="form-grid">
      {fields.map((f) => {
        const spec = typeof f === "string" ? { name: f } : f;
        return (
          <Field
            key={spec.name}
            label={spec.label || label(spec.name)}
            type={
              [
                "notes",
                "message",
                "bio",
                "about",
                "field_value",
                "mapped_fields",
                "raw_record",
              ].includes(spec.name)
                ? "textarea"
                : /email$/.test(spec.name)
                  ? "email"
                  : spec.name.includes("follow_up") ||
                      spec.name === "last_contacted"
                    ? "date"
                    : "text"
            }
            {...spec}
            value={value[spec.name] ?? ""}
            onChange={(v) => setValue((s) => ({ ...s, [spec.name]: v }))}
            required={required.includes(spec.name)}
          />
        );
      })}
    </div>
  );
}
export function Modal({ title, onClose, children }) {
  const ref = React.useRef(null);
  useEffect(() => {
    ref.current.showModal();
    return () => ref.current?.close();
  }, []);
  return (
    <dialog ref={ref} onCancel={onClose} className="modal">
      <div className="modal-title">
        <h2>{title}</h2>
        <button className="icon" aria-label="Close dialog" onClick={onClose}>
          <X size={20} />
        </button>
      </div>
      {children}
    </dialog>
  );
}
export function Pager({ page, pages, total, onPage }) {
  return (
    <div className="pager">
      <span>
        {Number(total).toLocaleString()} records · Page {page} of {pages}
      </span>
      <div>
        <button disabled={page <= 1} onClick={() => onPage(page - 1)}>
          Previous
        </button>
        <button disabled={page >= pages} onClick={() => onPage(page + 1)}>
          Next
        </button>
      </div>
    </div>
  );
}
export function download(name, data, type = "application/json") {
  const url = URL.createObjectURL(new Blob([data], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
export function formatNumber(v) {
  return v == null ? "Not recorded" : Number(v).toLocaleString();
}
export async function derive(password, salt, iterations = 600000) {
  const bytes = Uint8Array.from(salt.match(/../g), (s) => parseInt(s, 16));
  const key = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(password),
    "PBKDF2",
    false,
    ["deriveBits"],
  );
  return [
    ...new Uint8Array(
      await crypto.subtle.deriveBits(
        { name: "PBKDF2", hash: "SHA-256", salt: bytes, iterations },
        key,
        256,
      ),
    ),
  ]
    .map((x) => x.toString(16).padStart(2, "0"))
    .join("");
}
