import React, { useState } from "react";
import {
  UploadCloud,
  Download,
  FileSpreadsheet,
  Copy,
  Cloud,
  CheckCircle2,
  ArrowRight,
  Search,
  RefreshCw,
} from "lucide-react";
import {
  scanSheet,
  parseCSV,
  detectHeader,
  headerField,
  IMPORT_FIELDS,
} from "../shared/import.mjs";
import { readWorkbook } from "./workbook.mjs";
import { contactSummary } from "../shared/contacts.mjs";
import { outreach } from "../shared/outreach.mjs";
import { BACKUP_TABLES, RESOURCES, domain } from "../shared/domain.mjs";
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
  download,
  label,
} from "./lib.jsx";
import { exportSites, SiteEditor } from "./sites.jsx";

export function OutreachPage({ client = false }) {
  const profile = useData("/api/profile", {}),
    { notify } = useApp(),
    { busy, run } = useTask();
  const [form, setForm] = useState({
      site: new URLSearchParams(location.search).get("site") || "",
      tone: "Professional",
      purpose: "Guest Post",
      service: "SEO + Guest Posting",
    }),
    [drafts, setDrafts] = useState(null),
    [tab, setTab] = useState("Email");
  React.useEffect(() => {
    if (profile.data)
      setForm((s) => ({
        ...s,
        sender: s.sender || profile.data.name || "",
        company: s.company || profile.data.brand_name || "",
        role: s.role || profile.data.role || "",
      }));
  }, [profile.data]);
  return (
    <>
      <Heading
        title={client ? "Client outreach" : "Publisher outreach"}
        eyebrow="BUILD RELATIONSHIPS"
      >
        Write a personalized message, review it and copy the draft when you’re
        ready.
      </Heading>
      <div className="outreach-layout">
        <form
          className="panel form-panel"
          onSubmit={(e) => {
            e.preventDefault();
            setDrafts(outreach(form, client));
            setTab("Email");
          }}
        >
          <h2>Message details</h2>
          <Fields
            value={form}
            setValue={setForm}
            required={["site", "sender", "company"]}
            fields={[
              "site",
              {
                name: "recipient",
                label: client ? "Client name" : "Recipient name",
              },
              ...(client
                ? [
                    { name: "client_company", label: "Client company" },
                    {
                      name: "service",
                      options: [
                        "SEO",
                        "Guest Posting",
                        "Link Building",
                        "SEO + Guest Posting",
                        "Content Outreach",
                        "Digital PR / Outreach",
                      ],
                    },
                    {
                      name: "observation",
                      label: "Your verified observation",
                      type: "textarea",
                    },
                    {
                      name: "proof",
                      label: "Relevant experience or results",
                      type: "textarea",
                    },
                    { name: "cta", label: "Call to action", type: "textarea" },
                  ]
                : [
                    {
                      name: "purpose",
                      options: [
                        "Guest Post",
                        "Link Insertion",
                        "Guest Post + Link Insertion",
                        "Long-term Partnership",
                        "Price Inquiry",
                      ],
                    },
                    {
                      name: "offer",
                      label: "Offer / extra context",
                      type: "textarea",
                    },
                  ]),
              { name: "niche", label: "Niche / industry" },
              { name: "sender", label: "Your name" },
              { name: "company", label: "Your company" },
              { name: "role", label: "Your role" },
              {
                name: "tone",
                options: ["Professional", "Friendly", "Short & Direct"],
              },
            ]}
          />
          <div className="form-actions">
            <button className="primary">
              {drafts ? "Update drafts" : "Generate drafts"}
            </button>
          </div>
        </form>
        <div className="panel draft-panel">
          {drafts ? (
            <>
              <div className="tabs">
                {Object.keys(drafts).map((k) => (
                  <button
                    className={tab === k ? "selected" : ""}
                    key={k}
                    onClick={() => setTab(k)}
                  >
                    {k}
                  </button>
                ))}
              </div>
              <label className="field">
                <span>{tab}</span>
                <textarea
                  className="draft-text"
                  value={drafts[tab]}
                  onChange={(e) =>
                    setDrafts({ ...drafts, [tab]: e.target.value })
                  }
                />
              </label>
              <div className="form-actions">
                <button
                  disabled={busy}
                  className="primary"
                  onClick={() =>
                    run(async () => {
                      await navigator.clipboard.writeText(drafts[tab]);
                      notify("Draft copied.");
                    })
                  }
                >
                  <Copy size={16} /> Copy draft
                </button>
                <button
                  onClick={() =>
                    download(
                      "outreach-drafts.txt",
                      Object.entries(drafts)
                        .map(([k, v]) => `${k}\n\n${v}`)
                        .join("\n\n──────────\n\n"),
                      "text/plain",
                    )
                  }
                >
                  <Download size={16} /> Download all
                </button>
              </div>
              <small>
                Drafts are created in your browser. Nothing is sent
                automatically.
              </small>
            </>
          ) : (
            <Empty icon={Copy} title="Your next conversation starts here">
              Add a website and your details to create an email, follow-ups and
              social messages.
            </Empty>
          )}
        </div>
      </div>
    </>
  );
}
export function ImportPage() {
  const [sheets, setSheets] = useState([]),
    [filename, setFilename] = useState(""),
    [reports, setReports] = useState([]),
    [progress, setProgress] = useState(""),
    [complete, setComplete] = useState(false),
    { refresh, notify } = useApp(),
    { busy, run } = useTask();
  const total = reports.reduce((n, r) => n + r.rows.length, 0),
    detected = contactSummary(reports),
    privateCount = reports.reduce(
      (n, r) => n + r.contacts.length + r.privateFields.length,
      0,
    );
  async function batchResource(resource, rows) {
    for (let i = 0; i < rows.length; i += 20)
      await api("/api/admin/resource-batch", {
        method: "POST",
        body: { resource, rows: rows.slice(i, i + 20) },
      });
  }
  const start = () =>
    run(async () => {
      let inserted = 0,
        processed = 0;
      setComplete(false);
      for (const report of reports) {
        for (let i = 0; i < report.rows.length; i += 25) {
          const r = await api("/api/admin/import", {
            method: "POST",
            body: { rows: report.rows.slice(i, i + 25) },
          });
          inserted += r.inserted;
          processed += r.submitted;
          setProgress(
            `${processed.toLocaleString()} / ${total.toLocaleString()} websites processed`,
          );
        }
        for (let i = 0; i < report.contacts.length; i += 20)
          await api("/api/admin/contacts/merge", { method: "POST", body: { rows: report.contacts.slice(i, i + 20) } });
        await batchResource("resellers", report.privateFields);
        await batchResource("structures", [
          {
            source_file: filename,
            sheet_name: report.sheet_name,
            header_row: report.header_row,
            status: report.rows.length ? "Imported" : report.unassigned.length ? "Contacts imported" : "No valid website table",
            mapped_fields: JSON.stringify(report.mapping),
            private_count: report.contacts.length + report.privateFields.length,
          },
        ]);
      }
      setProgress(
        `${inserted.toLocaleString()} websites added. ${(total - inserted).toLocaleString()} existing or previously deleted listings skipped. ${detected.emails} emails, ${detected.phones} phone / WhatsApp numbers and ${detected.links} social / contact links saved privately.`,
      );
      setComplete(true);
      refresh();
      notify("Import completed.");
    });
  return (
    <>
      <Heading title="Import Excel / CSV" eyebrow="GROW YOUR DIRECTORY">
        Email, phone, WhatsApp, Facebook and LinkedIn contacts are matched to websites automatically and saved for admins with the import.
      </Heading>
      <label className={"upload-zone " + (busy ? "disabled" : "")}>
        <UploadCloud size={36} />
        <strong>{filename || "Choose a publisher spreadsheet"}</strong>
        <span>.xlsx, .csv or .tsv · up to 20 MB · all sheets scanned automatically</span>
        <input
          type="file"
          accept=".xlsx,.csv,.tsv"
          aria-label="Upload publisher spreadsheet"
          disabled={busy}
          onChange={(e) =>
            run(async () => {
              const file = e.target.files[0];
              if (!file) return;
              e.target.value = "";
              setProgress("Reading spreadsheet…");
              setFilename(file.name);
              const s = await readWorkbook(file);
              setSheets(s);
              const next = s.map((x) => scanSheet(x.rows, file.name, x.name));
              setReports(next);
              const found = contactSummary(next);
              setComplete(false);
              setProgress(`Automatically detected ${found.emails} emails, ${found.phones} phone / WhatsApp numbers and ${found.links} social / contact links. Review the preview, then import to save them privately.`);
            })
          }
        />
      </label>
      {progress && (
        <Notice>
          <span role="status">{progress}</span>
        </Notice>
      )}
      {reports.length > 0 && (
        <>
          <div className="stats-grid mini">
            <div className="stat-card">
              <small>Websites found</small>
              <strong>{total.toLocaleString()}</strong>
            </div>
            <div className="stat-card">
              <small>Emails detected</small>
              <strong>{detected.emails.toLocaleString()}</strong>
            </div>
            <div className="stat-card">
              <small>Phone / WhatsApp numbers</small>
              <strong>{detected.phones.toLocaleString()}</strong>
            </div>
            <div className="stat-card">
              <small>Sheets scanned</small>
              <strong>{reports.length}</strong>
            </div>
          </div>
          {reports.map((r, index) => (
            <section className="panel form-panel" key={r.sheet_name}>
              <div className="panel-heading flush">
                <h2>
                  <FileSpreadsheet size={20} />
                  {r.sheet_name}
                </h2>
                <span>
                  {r.rows.length.toLocaleString()} websites · {r.invalid}{" "}
                  non-website rows skipped
                </span>
              </div>
              <Field
                label="Header row"
                type="number"
                min="1"
                max={Math.min(sheets[index].rows.length, 100)}
                value={r.header_row || ""}
                help="Change this if the table starts below introductory notes."
                disabled={busy || complete}
                onChange={(v) => {
                  const n = Number(v);
                  if (n >= 1 && n <= 100)
                    setReports(
                      reports.map((s, i) =>
                        i === index
                          ? scanSheet(
                              sheets[index].rows,
                              filename,
                              s.sheet_name,
                              n - 1,
                            )
                          : s,
                      ),
                    );
                }}
              />
              <div className="mapping">
                {r.mapping.map(
                  (m, i) =>
                    m && (
                      <span className="tag" key={i}>
                        {sheets[index].rows[r.header_row - 1]?.[i]} → {label(m)}
                      </span>
                    ),
                )}
              </div>
              {r.rows.length ? (
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Website</th>
                        <th>Country</th>
                        <th>DR</th>
                        <th>Original price</th>
                      </tr>
                    </thead>
                    <tbody>
                      {r.rows.slice(0, 3).map((row, i) => (
                        <tr key={i}>
                          <td>{row.site}</td>
                          <td>{row.country || "—"}</td>
                          <td>{row.dr || "—"}</td>
                          <td>{row.general_price || "—"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <Notice>
                  {r.unassigned.length ? `${r.unassigned.length} sheet contact entries detected. They will be saved privately without a website assignment.` : "No website column detected. Contact and payment notes will still be kept privately."}
                </Notice>
              )}
            </section>
          ))}
          <Notice>
            Imported prices are original supplier costs; the default 20% markup
            is applied once. Existing listings from the same source and sheet
            are skipped. Contact and payment notes remain in admin tools.
          </Notice>
          <div className="form-actions">
            <button
              className="primary"
              disabled={busy || complete || (!total && !privateCount)}
              onClick={start}
            >
              {busy
                ? "Importing…"
                : complete
                  ? "Import complete"
                  : "Import websites & private details"}
            </button>
          </div>
        </>
      )}
    </>
  );
}
export function ExportPage() {
  const [format, setFormat] = useState("csv"),
    [q, setQ] = useState(""),
    { busy, run } = useTask(),
    { notify } = useApp();
  return (
    <>
      <Heading title="Export websites">
        Download the publisher directory, or export filtered results directly
        from Search.
      </Heading>
      <div className="panel form-panel narrow">
        <Fields
          fields={[
            { name: "q", label: "Domain / niche filter" },
            {
              name: "format",
              label: "File format",
              options: [
                { value: "csv", label: "CSV" },
                { value: "xlsx", label: "Excel (.xlsx)" },
              ],
            },
          ]}
          value={{ q, format }}
          setValue={(fn) => {
            const next = fn({ q, format });
            setQ(next.q);
            setFormat(next.format);
          }}
        />
        <Notice>
          Exports contain public publisher information and listed selling
          prices.
        </Notice>
        <button
          className="primary"
          disabled={busy}
          onClick={() =>
            run(async () => {
              const n = await exportSites({ q }, format);
              notify(`${n.toLocaleString()} websites exported.`);
            })
          }
        >
          <Download size={17} />
          {busy ? "Preparing file…" : "Download websites"}
        </button>
      </div>
    </>
  );
}
export function BackupPage() {
  const { busy, run } = useTask(),
    { notify, refresh } = useApp(),
    [progress, setProgress] = useState(""),
    [backup, setBackup] = useState(null),
    [confirmed, setConfirmed] = useState(false);
  return (
    <>
      <Heading title="Backup & restore" eyebrow="ADMIN WORKSPACE">
        Keep a private copy of websites, contacts, settings and team photos.
      </Heading>
      <div className="panel form-panel">
        <h2>Download a complete backup</h2>
        <p className="subtle">
          Includes private contacts and original prices. Store the downloaded
          file somewhere safe. Passwords and sessions are excluded.
        </p>
        <button
          className="primary"
          disabled={busy}
          onClick={() =>
            run(async () => {
              const status = await api("/api/admin/status"),
                tables = {};
              for (const table of status.tables) {
                let offset = 0;
                tables[table] = [];
                do {
                  setProgress(`Backing up ${table.replaceAll("_", " ")}…`);
                  const chunk = await api(
                    "/api/admin/backup?" +
                      new URLSearchParams({
                        table,
                        offset,
                        version: status.version,
                      }),
                  );
                  tables[table].push(...chunk.rows);
                  offset = chunk.next;
                } while (offset !== null);
              }
              if ((await api("/api/admin/status")).version !== status.version)
                throw new Error("Data changed during backup. Please retry.");
              download(
                `gp-backup-${new Date().toISOString().slice(0, 10)}.json`,
                JSON.stringify({
                  format: "gp-cloudflare",
                  version: 1,
                  created_at: new Date().toISOString(),
                  tables,
                }),
              );
              setProgress("Backup downloaded.");
              notify("Complete backup downloaded.");
            })
          }
        >
          <Download size={17} /> Download private backup
        </button>
      </div>
      <div className="panel form-panel">
        <h2>Merge a backup</h2>
        <p className="subtle">
          Restore a backup created by this Cloudflare app. Matching record IDs
          are updated; other existing records are kept. Use a backup from this
          same workspace.
        </p>
        <input
          aria-label="Choose backup file"
          type="file"
          accept="application/json,.json"
          disabled={busy}
          onChange={(e) =>
            run(async () => {
              const f = e.target.files[0];
              if (!f) return;
              if (f.size > 100 * 1024 * 1024)
                throw new Error("Backup exceeds 100 MB.");
              const b = JSON.parse(await f.text());
              if (
                b.format !== "gp-cloudflare" ||
                b.version !== 1 ||
                !b.tables ||
                Object.entries(b.tables).some(
                  ([k, v]) => !BACKUP_TABLES[k] || !Array.isArray(v),
                )
              )
                throw new Error("Unsupported backup format.");
              setBackup(b);
              setConfirmed(false);
            })
          }
        />
        {backup && (
          <>
            <p>
              {Object.values(backup.tables)
                .reduce((n, r) => n + r.length, 0)
                .toLocaleString()}{" "}
              records · Created {backup.created_at}
            </p>
            <label className="check">
              <input
                type="checkbox"
                checked={confirmed}
                onChange={(e) => setConfirmed(e.target.checked)}
              />
              I have a current backup and want to replace matching records.
            </label>
            <button
              className="primary"
              disabled={busy || !confirmed}
              onClick={() =>
                run(async () => {
                  for (const [table, rows] of Object.entries(backup.tables)) {
                    const size = table === "media" ? 1 : 20;
                    for (let i = 0; i < rows.length; i += size) {
                      setProgress(`Restoring ${table}: ${i} / ${rows.length}`);
                      await api("/api/admin/restore", {
                        method: "POST",
                        body: {
                          table,
                          rows: rows.slice(i, i + size),
                          confirm: "MERGE BACKUP",
                        },
                      });
                    }
                  }
                  setProgress("Backup merged successfully.");
                  setBackup(null);
                  refresh();
                  notify("Restore completed.");
                })
              }
            >
              Merge backup
            </button>
          </>
        )}
      </div>
      {progress && (
        <Notice>
          <span role="status">{progress}</span>
        </Notice>
      )}
    </>
  );
}
export function DuplicatesPage() {
  const { data, loading, error } = useData("/api/admin/duplicates", []),
    { go } = useApp();
  return (
    <>
      <Heading title="Duplicate finder" eyebrow="ADMIN WORKSPACE">
        Compare repeated domains before deciding which supplier listing to keep.
      </Heading>
      <ErrorBox error={error} />
      <div className="panel">
        {loading ? (
          <Loading />
        ) : data.length ? (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Domain</th>
                  <th>Listings</th>
                  <th>Review</th>
                </tr>
              </thead>
              <tbody>
                {data.map((r) => (
                  <tr key={r.domain}>
                    <td>{r.domain}</td>
                    <td>{r.count}</td>
                    <td>
                      <button onClick={() => go("manage", { q: r.domain })}>
                        Review listings <ArrowRight size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <Empty icon={CheckCircle2} title="No duplicate domains">
            Every recorded domain has one listing.
          </Empty>
        )}
      </div>
      <Notice>
        Multiple listings may be valid when different suppliers offer the same
        website. Nothing is deleted automatically.
      </Notice>
    </>
  );
}
export function PricingPage() {
  const { data, loading, error } = useData("/api/options", {}),
    [form, setForm] = useState({
      source_file: "",
      sheet_name: "",
      markup_percent: 20,
    }),
    [result, setResult] = useState(""),
    { busy, run } = useTask(),
    { refresh } = useApp();
  return (
    <>
      <Heading title="Reseller price manager" eyebrow="ADMIN WORKSPACE">
        Apply a sheet markup or edit an individual website’s selling price.
      </Heading>
      <ErrorBox error={error} />
      {loading ? (
        <Loading />
      ) : (
        <form
          className="panel form-panel narrow"
          onSubmit={(e) => {
            e.preventDefault();
            run(async () => {
              const r = await api("/api/admin/pricing", {
                method: "POST",
                body: form,
              });
              setResult(
                `${r.updated} listings updated. Manual prices were preserved.`,
              );
              refresh();
            });
          }}
        >
          <Fields
            fields={[
              {
                name: "source_file",
                options: [
                  { value: "", label: "Select source…" },
                  ...(data.source_file || []),
                ],
              },
              {
                name: "sheet_name",
                options: [
                  { value: "", label: "Select sheet…" },
                  ...(data.sheet_name || []),
                ],
              },
              { name: "markup_percent", type: "number", min: 0, max: 500 },
            ]}
            value={form}
            setValue={setForm}
            required={["source_file", "sheet_name"]}
          />
          <Notice>
            Automatic selling price = original supplier cost × (1 + markup /
            100). Manual price overrides are kept.
          </Notice>
          <button className="primary" disabled={busy}>
            Apply markup to sheet
          </button>
          {result && <Notice>{result}</Notice>}
        </form>
      )}
    </>
  );
}
export function CloudPage() {
  const { data, loading, error } = useData("/api/admin/status");
  return (
    <>
      <Heading title="Cloud storage" eyebrow="ADMIN WORKSPACE">
        Your workspace saves directly to its cloud database.
      </Heading>
      <ErrorBox error={error} />
      {loading ? (
        <Loading />
      ) : (
        data && (
          <div className="panel form-panel narrow">
            <Cloud size={36} className="blue" />
            <h2>Cloudflare D1 connected</h2>
            <p>
              Changes are stored immediately. There is no separate sync step.
            </p>
            <dl className="detail-grid">
              <div>
                <dt>Database version</dt>
                <dd>{data.version}</dd>
              </div>
              <div>
                <dt>Ahrefs integration</dt>
                <dd>{data.ahrefs ? "Configured" : "Not configured"}</dd>
              </div>
            </dl>
            <Notice>
              The free plan has daily usage limits. Check usage in your
              Cloudflare dashboard. No paid services are enabled by this app.
            </Notice>
            <a
              href="https://dash.cloudflare.com/"
              target="_blank"
              rel="noopener noreferrer"
            >
              Open Cloudflare dashboard <ArrowRight size={16} />
            </a>
          </div>
        )
      )}
    </>
  );
}
export function MetricsPage() {
  const [site, setSite] = useState(""),
    [kind, setKind] = useState("dr"),
    [result, setResult] = useState(null),
    { busy, run } = useTask();
  return (
    <>
      <Heading title="Real metrics search" eyebrow="ADMIN WORKSPACE">
        Request current metrics through your existing Ahrefs API access.
      </Heading>
      <form
        className="panel form-panel narrow"
        onSubmit={(e) => {
          e.preventDefault();
          run(async () =>
            setResult(
              await api("/api/admin/metrics", {
                method: "POST",
                body: { site, kind },
              }),
            ),
          );
        }}
      >
        <Field
          label="Website"
          placeholder="example.com"
          value={site}
          onChange={setSite}
          required
        />
        <Field
          label="Metric"
          value={kind}
          onChange={setKind}
          options={[
            { value: "dr", label: "Domain rating" },
            { value: "traffic", label: "Organic traffic" },
          ]}
        />
        <Notice>
          Each request uses your Ahrefs API quota. Traffic metrics may require
          paid Ahrefs access; this is separate from the free app hosting.
        </Notice>
        <button className="primary" disabled={busy}>
          {busy ? "Checking…" : "Fetch live metric"}
        </button>
        {result && (
          <div className="metric-result">
            <h3>{result.target}</h3>
            <pre>{JSON.stringify(result.data, null, 2)}</pre>
            <p className="subtle">
              You can copy a verified value into the website’s record in Manage
              websites.
            </p>
          </div>
        )}
      </form>
    </>
  );
}
