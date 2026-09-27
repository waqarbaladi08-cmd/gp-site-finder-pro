import React, { useState } from "react";
import {
  Plus,
  Pencil,
  Trash2,
  Search,
  Upload,
  Users,
  Mail,
  ShieldCheck,
  KeyRound,
} from "lucide-react";
import { RESOURCES, safeWebURL } from "../shared/domain.mjs";
import {
  useApp,
  useData,
  useTask,
  api,
  Loading,
  ErrorBox,
  Empty,
  Heading,
  Field,
  Fields,
  Notice,
  Modal,
  Pager,
  label,
  derive,
} from "./lib.jsx";

export const RESOURCE_INFO = {
  review: [
    "Import review",
    "Original rows that need a valid website domain. Records are preserved for review.",
  ],
  contacts: [
    "Private contacts",
    "Publisher contacts, quotes and relationship notes.",
  ],
  pipeline: [
    "Outreach pipeline",
    "Keep track of conversations and follow-up dates.",
  ],
  vault: [
    "Admin contact vault",
    "Keep private business contacts in one place.",
  ],
  resellers: [
    "Reseller private details",
    "Supplier contacts and private sheet notes.",
  ],
  structures: [
    "Sheet structure scanner",
    "Review the columns and private fields found in uploaded sheets.",
  ],
  messages: [
    "Contact messages",
    "Messages submitted through your contact page.",
  ],
  team: [
    "Manage team",
    "Manage the people displayed on your public team page.",
  ],
};
const statusOptions = [
  "New",
  "Contacted",
  "Replied",
  "Negotiating",
  "Approved",
  "Published",
  "Rejected",
  "Follow-up",
];
async function uploadPhoto(file) {
  if (!file || file.size > 500 * 1024)
    throw new Error("Choose a photo smaller than 500 KB.");
  const data = await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result).split(",")[1]);
    reader.onerror = () => reject(new Error("Unable to read the image."));
    reader.readAsDataURL(file);
  });
  return (
    await api("/api/admin/media", {
      method: "POST",
      body: { key: crypto.randomUUID(), content_type: file.type, data },
    })
  ).url;
}
export function PhotoField({ value, onChange }) {
  const { busy, run } = useTask();
  return (
    <div className="photo-field">
      {value && <img src={value} alt="Profile preview" />}
      <label className="file-button">
        <Upload size={17} />
        {busy ? "Uploading…" : "Upload photo"}
        <input
          type="file"
          accept="image/png,image/jpeg,image/webp"
          disabled={busy}
          onChange={(e) =>
            run(async () => onChange(await uploadPhoto(e.target.files[0])))
          }
        />
      </label>
      <small>PNG, JPG or WebP · up to 500 KB</small>
    </div>
  );
}
export function ResourcePage({ name }) {
  const r = RESOURCES[name],
    info = RESOURCE_INFO[name],
    { refresh, notify } = useApp(),
    { busy, run } = useTask();
  const [q, setQ] = useState(""),
    [search, setSearch] = useState(""),
    [page, setPage] = useState(1),
    [edit, setEdit] = useState(null),
    [remove, setRemove] = useState(null);
  const { data, loading, error } = useData(
    "/api/admin/resources/" +
      name +
      "?" +
      new URLSearchParams({ q: search, page }),
  );
  const fields = r.fields
    .filter(
      (k) =>
        !["id", "created_at", "updated_at", "image_path", "site_id"].includes(
          k,
        ),
    )
    .map((k) =>
      k === "status"
        ? {
            name: k,
            options:
              name === "messages"
                ? ["New", "Read", "Replied", "Closed"]
                : statusOptions,
          }
        : k === "active"
          ? {
              name: k,
              options: [
                { value: 1, label: "Visible" },
                { value: 0, label: "Hidden" },
              ],
            }
          : k === "display_order"
            ? { name: k, type: "number" }
            : k,
    );
  const tableFields = r.fields
    .filter(
      (k) =>
        !["id", "created_at", "updated_at", "image_path", "site_id"].includes(
          k,
        ),
    )
    .slice(0, name === "pipeline" ? 7 : 5);
  return (
    <>
      <Heading
        title={info[0]}
        eyebrow="ADMIN WORKSPACE"
        actions={
          <button
            className="primary"
            onClick={() =>
              setEdit({
                active: 1,
                display_order: 100,
                status: "New",
                level: "Team member",
              })
            }
          >
            <Plus size={17} />
            Add record
          </button>
        }
      >
        {info[1]}
      </Heading>
      <form
        className="search-row panel compact"
        onSubmit={(e) => {
          e.preventDefault();
          setSearch(q);
          setPage(1);
        }}
      >
        <div className="search-input">
          <Search size={19} />
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search records…"
            aria-label="Search records"
          />
        </div>
        <button>Search</button>
      </form>
      <ErrorBox error={error} />
      <div className="panel">
        {loading ? (
          <Loading />
        ) : data?.rows?.length ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  {tableFields.map((k) => (
                    <th key={k}>{label(k)}</th>
                  ))}
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.rows.map((row, i) => (
                  <tr key={i}>
                    {tableFields.map((k) => (
                      <td key={k}>
                        <span
                          className={k === "status" ? "tag" : ""}
                          title={String(row[k] ?? "")}
                        >
                          {String(row[k] ?? "—").slice(0, 100)}
                        </span>
                      </td>
                    ))}
                    <td>
                      <div className="row-actions">
                        <button
                          className="icon"
                          aria-label="Edit record"
                          onClick={() => setEdit(row)}
                        >
                          <Pencil size={17} />
                        </button>
                        <button
                          className="icon danger"
                          aria-label="Delete record"
                          onClick={() => setRemove(row)}
                        >
                          <Trash2 size={17} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <Empty title="No records yet">
            Add a record to start organizing this part of your workspace.
          </Empty>
        )}
        {data && (
          <Pager
            page={page}
            pages={data.pages}
            total={data.total}
            onPage={setPage}
          />
        )}
      </div>
      {edit && (
        <Modal
          title={edit.id || edit.domain ? "Edit record" : "New record"}
          onClose={() => setEdit(null)}
        >
          <form
            onSubmit={(e) => {
              e.preventDefault();
              run(async () => {
                await api("/api/admin/resources/" + name, {
                  method: "POST",
                  body: edit,
                });
                setEdit(null);
                refresh();
                notify("Record saved.");
              });
            }}
          >
            {name === "team" && (
              <PhotoField
                value={edit.image_path}
                onChange={(v) => setEdit((s) => ({ ...s, image_path: v }))}
              />
            )}
            <Fields
              fields={fields}
              value={edit}
              setValue={setEdit}
              required={r.required}
            />
            <div className="form-actions">
              <button type="button" onClick={() => setEdit(null)}>
                Cancel
              </button>
              <button className="primary" disabled={busy}>
                Save record
              </button>
            </div>
          </form>
        </Modal>
      )}
      {remove && (
        <Modal title="Delete this record?" onClose={() => setRemove(null)}>
          <p>
            This will permanently remove this record. Download a backup first if
            you need a copy.
          </p>
          <div className="form-actions">
            <button onClick={() => setRemove(null)}>Cancel</button>
            <button
              className="danger-button"
              disabled={busy}
              onClick={() =>
                run(async () => {
                  await api("/api/admin/resources/" + name, {
                    method: "DELETE",
                    body: remove,
                  });
                  setRemove(null);
                  refresh();
                  notify("Record deleted.");
                })
              }
            >
              Delete record
            </button>
          </div>
        </Modal>
      )}
    </>
  );
}
export function TeamPage() {
  const { data, loading, error } = useData("/api/team", []),
    { user, go } = useApp();
  return (
    <>
      <Heading
        title="Our team"
        actions={
          user && <button onClick={() => go("team-admin")}>Manage team</button>
        }
      >
        Meet the people behind your publisher workspace.
      </Heading>
      <ErrorBox error={error} />
      {loading ? (
        <Loading />
      ) : data.length ? (
        <div className="team-grid">
          {data.map((r) => (
            <article key={r.id} className="panel team-card">
              {r.image_path ? (
                <img src={r.image_path} alt={r.full_name} />
              ) : (
                <div className="avatar">{r.full_name.slice(0, 1)}</div>
              )}
              <h2>{r.full_name}</h2>
              <p className="blue">{r.designation}</p>
              <small>
                {r.level}
                {r.location ? " · " + r.location : ""}
              </small>
              <p>{r.bio}</p>
              {r.skills && <small>{r.skills}</small>}
              <div className="team-links">
                {r.email && <a href={"mailto:" + r.email}>Email</a>}
                {safeWebURL(r.website) && (
                  <a
                    href={safeWebURL(r.website)}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Website
                  </a>
                )}
              </div>
            </article>
          ))}
        </div>
      ) : (
        <Empty icon={Users} title="Team profiles are being prepared">
          Published team members will appear here.
        </Empty>
      )}
    </>
  );
}
export function ContactPage() {
  const [form, setForm] = useState({}),
    [sent, setSent] = useState(false),
    { busy, run } = useTask();
  return (
    <>
      <Heading title="Contact us">
        Have a publishing or outreach question? Leave a message for the team.
      </Heading>
      {sent ? (
        <Empty icon={Mail} title="Your message has been received">
          The team can now see it in the contact inbox.
          <button
            onClick={() => {
              setSent(false);
              setForm({});
            }}
          >
            Write another message
          </button>
        </Empty>
      ) : (
        <form
          className="panel form-panel narrow"
          onSubmit={(e) => {
            e.preventDefault();
            run(async () => {
              await api("/api/contact", { method: "POST", body: form });
              setSent(true);
            });
          }}
        >
          <Fields
            fields={[
              "full_name",
              "email",
              "phone",
              "company",
              "website",
              "subject",
              "message",
            ]}
            value={form}
            setValue={setForm}
            required={["full_name", "message"]}
          />
          <label className="honey" aria-hidden="true">
            Company website
            <input
              tabIndex="-1"
              autoComplete="off"
              value={form.company_website || ""}
              onChange={(e) =>
                setForm({ ...form, company_website: e.target.value })
              }
            />
          </label>
          <div className="form-actions">
            <button className="primary" disabled={busy}>
              {busy ? "Submitting…" : "Submit message"}
            </button>
          </div>
        </form>
      )}
    </>
  );
}
export function ProfilePage() {
  const { data, loading, error } = useData("/api/profile", {}),
    { user, go } = useApp();
  return (
    <>
      <Heading
        title="Profile & contact"
        actions={
          user && <button onClick={() => go("settings")}>Edit profile</button>
        }
      >
        Your business information and contact details.
      </Heading>
      <ErrorBox error={error} />
      {loading ? (
        <Loading />
      ) : (
        <article className="panel form-panel narrow profile-card">
          {data.image_path && (
            <img
              src={data.image_path}
              alt={data.name || "Profile"}
              className="profile-photo"
            />
          )}
          <h2>{data.name || data.brand_name || "GP Site Finder Pro"}</h2>
          <p className="blue">{data.role}</p>
          <p>{data.about}</p>
          <dl className="detail-grid">
            {[
              "brand_name",
              "email",
              "phone",
              "location",
              "website",
              "linkedin",
            ].map(
              (k) =>
                data[k] && (
                  <div key={k}>
                    <dt>{label(k)}</dt>
                    <dd>{data[k]}</dd>
                  </div>
                ),
            )}
          </dl>
        </article>
      )}
    </>
  );
}
export function SettingsPage() {
  const { data } = useData("/api/profile", {}),
    [form, setForm] = useState({}),
    [password, setPassword] = useState(""),
    [confirm, setConfirm] = useState(""),
    { notify, refresh, loadAuth } = useApp(),
    { busy, run } = useTask();
  React.useEffect(() => {
    if (data) setForm(data);
  }, [data]);
  return (
    <>
      <Heading title="Settings" eyebrow="ADMIN WORKSPACE">
        Update your public profile and secure your administrator account.
      </Heading>
      <form
        className="panel form-panel"
        onSubmit={(e) => {
          e.preventDefault();
          run(async () => {
            await api("/api/admin/profile", { method: "PUT", body: form });
            refresh();
            notify("Profile updated.");
          });
        }}
      >
        <h2>Business profile</h2>
        <PhotoField
          value={form.image_path}
          onChange={(v) => setForm((s) => ({ ...s, image_path: v }))}
        />
        <Fields
          fields={[
            "brand_name",
            "name",
            "role",
            "phone",
            "email",
            "website",
            "linkedin",
            "location",
            "about",
          ]}
          value={form}
          setValue={setForm}
        />
        <div className="form-actions">
          <button className="primary" disabled={busy}>
            Save profile
          </button>
        </div>
      </form>
      <form
        className="panel form-panel narrow"
        onSubmit={(e) => {
          e.preventDefault();
          run(async () => {
            if (password !== confirm)
              throw new Error("The two passwords do not match.");
            const salt = [...crypto.getRandomValues(new Uint8Array(16))]
              .map((v) => v.toString(16).padStart(2, "0"))
              .join("");
            await api("/api/auth/password", {
              method: "POST",
              body: {
                salt,
                iterations: 600000,
                verifier: await derive(password, salt),
              },
            });
            setPassword("");
            setConfirm("");
            await loadAuth();
            notify("Password changed. Sign in again with your new password.");
          });
        }}
      >
        <h2>
          <KeyRound size={20} /> Change password
        </h2>
        <div className="form-grid">
          <Field
            label="New password"
            type="password"
            minLength={12}
            autoComplete="new-password"
            required
            value={password}
            onChange={setPassword}
          />
          <Field
            label="Confirm password"
            type="password"
            minLength={12}
            autoComplete="new-password"
            required
            value={confirm}
            onChange={setConfirm}
          />
        </div>
        <small>
          Use at least 12 characters. Changing your password signs out all
          sessions.
        </small>
        <div className="form-actions">
          <button disabled={busy}>Change password</button>
        </div>
      </form>
    </>
  );
}
export function LoginPage() {
  const [username, setUsername] = useState(""),
    [password, setPassword] = useState(""),
    { user, loadAuth, go, notify } = useApp(),
    { busy, run } = useTask();
  return (
    <>
      <Heading title="Admin sign in">
        Manage your database, contacts and publishing tools.
      </Heading>
      {user ? (
        <Empty icon={ShieldCheck} title={`Signed in as ${user.username}`}>
          Your administrator workspace is ready.
          <button onClick={() => go("manage")}>Manage websites</button>
        </Empty>
      ) : (
        <form
          className="panel login-card"
          onSubmit={(e) => {
            e.preventDefault();
            run(async () => {
              const c = await api(
                "/api/auth/challenge?" + new URLSearchParams({ username }),
              );
              await api("/api/auth/login", {
                method: "POST",
                body: {
                  username,
                  verifier: await derive(password, c.salt, c.iterations),
                },
              });
              setPassword("");
              await loadAuth();
              go("manage");
              notify("Signed in successfully.");
            });
          }}
        >
          <div className="login-icon">
            <ShieldCheck size={28} />
          </div>
          <h2>Welcome back</h2>
          <p className="subtle">Sign in to your private workspace.</p>
          <Field
            label="Username"
            autoComplete="username"
            required
            value={username}
            onChange={setUsername}
          />
          <Field
            label="Password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={setPassword}
          />
          <button className="primary" disabled={busy}>
            {busy ? "Signing in…" : "Sign in"}
          </button>
          <small>
            Public website search and outreach drafts are available without
            signing in.
          </small>
        </form>
      )}
    </>
  );
}
