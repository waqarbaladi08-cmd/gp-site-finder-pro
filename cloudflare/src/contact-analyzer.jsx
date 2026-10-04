import React, { useState } from "react";
import { UploadCloud, LockKeyhole, Download, Search } from "lucide-react";
import { scanSheet, parseCSV, headerField } from "../shared/import.mjs";
import { domain, toCSV } from "../shared/domain.mjs";
import { analyzeContactRows, CONTACT_FIELDS, extractContacts, hasContact, contactSummary, sheetContactNote, splitValues, contactURL, normalizePhone } from "../shared/contacts.mjs";
import { readWorkbook } from "./workbook.mjs";
import { useApp, useData, useTask, api, Loading, ErrorBox, Heading, Notice, Field, download, label } from "./lib.jsx";

export function ContactDetails({ domain: target }) {
  const { user, go } = useApp();
  const { data, error, loading } = useData(user ? "/api/admin/contacts/detail?" + new URLSearchParams({ domain: target }) : null);
  if (!user) return null;
  return <section className="contact-details">
    <h2><LockKeyhole size={18} /> Private contact details</h2>
    {loading ? <Loading label="Loading private contacts…" /> : error ? <ErrorBox error={error} /> : data?.contact ? <>
      <dl className="detail-grid">{[...CONTACT_FIELDS, "status", "notes"].map((key) => <div key={key}>
        <dt>{label(key)}</dt><dd>{splitValues(data.contact[key]).length ? splitValues(data.contact[key]).map((v, i) => {
          const email = key === "email" && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
          const phone = ["phone", "whatsapp"].includes(key) && normalizePhone(v);
          const url = key === "contact_url" && contactURL(v);
          const href = email ? `mailto:${v}` : phone ? `tel:${phone}` : url || "";
          return <div key={i}>{href ? <a href={href} {...(url ? { target: "_blank", rel: "noopener noreferrer" } : {})}>{v}</a> : v}</div>;
        }) : "Not recorded"}</dd>
      </div>)}</dl>
      <p className="subtle">Detected contact details need checking before outreach.</p>
    </> : <p>No contact saved for this website yet. Analyze the original sheet to find its email and phone number.</p>}
    {!!data?.suppliers?.length && <div><h3>Supplier / sheet contacts</h3><p className="subtle">These details were found in this listing’s source sheet. They may belong to a reseller rather than the publisher.</p>
      {data.suppliers.map((r, i) => <div className="contact-assignment" key={i}><strong>{r.source_file} · {r.sheet_name || "Sheet owner"}</strong><p>{[r.email, r.phone, r.whatsapp, r.contact_url].filter(Boolean).join(" · ")}</p></div>)}
    </div>}
    <button onClick={() => go("contact-analyzer", { domain: target })}>Open Contact Analyzer</button>
  </section>;
}

export function ContactAnalyzer() {
  const [reports, setReports] = useState([]), [rawSheets, setRawSheets] = useState([]);
  const [filename, setFilename] = useState(""), [pasted, setPasted] = useState("");
  const [progress, setProgress] = useState(""), [complete, setComplete] = useState(false);
  const [page, setPage] = useState(1), [query, setQuery] = useState("");
  const [assignments, setAssignments] = useState({});
  const { busy, run } = useTask(), { refresh, notify, go } = useApp();
  const { contacts, unassigned, all, emails, phones } = contactSummary(reports);
  const filtered = all.filter((r) => [r.domain, r.email, r.phone, r.whatsapp, r.source_file, r.sheet_name, r.admin_name].join(" ").toLowerCase().includes(query.toLowerCase()));
  const displayPage = Math.min(page, Math.max(1, Math.ceil(filtered.length / 25)));
  const rows = filtered.slice((displayPage - 1) * 25, displayPage * 25);
  function showSheets(sheets, name) {
    const next = sheets.map((s) => scanSheet(s.rows, name, s.name));
    const detected = contactSummary(next);
    setRawSheets(sheets); setFilename(name); setReports(next);
    setComplete(false); setAssignments({}); setPage(1); setQuery("");
    setProgress(detected.all.length
      ? `Automatically detected ${detected.emails} email addresses and ${detected.phones} phone / WhatsApp numbers across ${sheets.length} sheets. Contacts without a website can also be saved privately.`
      : "No email, phone or contact link was found in this sheet. Check that it contains contact details.");
  }
  async function save() {
    let saved = 0, savedNotes = 0;
    const selected = unassigned.flatMap((r, i) => {
      const value = assignments[i]?.trim();
      if (!value) return [];
      const d = domain(value);
      if (!d) throw new Error(`Enter a valid website for unassigned contact ${i + 1}.`);
      return [{ ...r, domain: d }];
    });
    const matched = contactSummary([{ contacts: [...contacts, ...selected] }]).contacts;
    const sheetContacts = unassigned.filter((r, i) => !assignments[i]?.trim());
    const pendingNotes = sheetContacts.filter((r) => !r.persisted).map(sheetContactNote);
    for (let i = 0; i < matched.length; i += 20) {
      const r = await api("/api/admin/contacts/merge", { method: "POST", body: { rows: matched.slice(i, i + 20) } });
      saved += r.saved; setProgress(`${saved} / ${matched.length} website contacts saved privately…`);
    }
    for (let i = 0; i < pendingNotes.length; i += 20) {
      const r = await api("/api/admin/resource-batch", { method: "POST", body: { resource: "resellers", rows: pendingNotes.slice(i, i + 20) } });
      savedNotes += r.saved; setProgress(`${savedNotes} / ${pendingNotes.length} sheet contacts saved privately…`);
    }
    if (!saved && !sheetContacts.length) throw new Error("Upload a sheet containing contact details first.");
    setComplete(true); refresh();
    setProgress(!saved && !pendingNotes.length
      ? `${sheetContacts.length} sheet contact entries are already saved privately. No website assignment is needed.`
      : `${saved} website contact records saved. ${sheetContacts.length} sheet contact entries available privately. Existing contacts and notes were preserved.`);
    notify("Private contacts saved.");
  }
  async function analyzeSaved() {
    const scanned = []; let count = 0;
    for (const table of ["reseller_private", "import_review"]) {
      let after = 0;
      do {
        const result = await api("/api/admin/contacts/sources?" + new URLSearchParams({ table, after }));
        for (const row of result.rows) {
          let values = [row.field_value || row.raw_record || ""], fields = [];
          try {
            const obj = JSON.parse(row.raw_record || "null");
            if (obj && typeof obj === "object" && !Array.isArray(obj)) { values = Object.values(obj); fields = Object.keys(obj).map(headerField); }
          } catch { /* Free-form saved note. */ }
          const found = extractContacts(values, fields);
          if (!hasContact(found)) continue;
          const detected = analyzeContactRows([values], row.source_file || "Saved notes", row.sheet_name || "", -1);
          const d = domain(row.site) || detected.contacts[0]?.domain || "";
          const candidate = { ...found, domain: d, source_file: row.source_file || "Saved notes", sheet_name: row.sheet_name || "",
            persisted: table === "reseller_private", notes: `Saved sheet note: ${row.source_file || ""} / ${row.sheet_name || ""} / ${table} ${row.id}` };
          scanned.push({ sheet_name: `${table} ${row.id}`, contacts: d ? [candidate] : [], unassigned: d ? [] : [candidate] });
        }
        count += result.rows.length; setProgress(`${count} saved sheet notes analyzed…`); after = result.next;
      } while (after !== null);
    }
    setReports(scanned); setRawSheets([]); setFilename("Saved sheet notes"); setComplete(false); setAssignments({}); setPage(1); setQuery("");
    const detected = contactSummary(scanned);
    setProgress(scanned.length ? `Automatically detected ${detected.emails} email addresses and ${detected.phones} phone / WhatsApp numbers in saved notes. Website assignment is optional.` : "No contact details found in saved notes. Upload the original sheet to analyze cells that were not retained during the earlier import.");
  }
  return <>
    <Heading title="Contact Analyzer" eyebrow="PRIVATE ADMIN TOOL" actions={<button onClick={() => go("contacts")}>Open private database</button>}>
      Upload a sheet to automatically detect emails, phone numbers and WhatsApp across every worksheet. No website column is required.
    </Heading>
    <Notice><LockKeyhole size={18} /> Contacts are visible only after admin sign-in. Detection checks format; it does not verify ownership or deliverability.</Notice>
    <div className="contact-analyzer-inputs">
      <label className={"upload-zone " + (busy ? "disabled" : "")}><UploadCloud size={30} /><strong>{filename || "Upload sheet — contacts are detected automatically"}</strong>
        <span>XLSX, CSV or TSV · up to 20 MB · all worksheet tabs · email and phone columns detected automatically</span>
        <input aria-label="Upload sheet for contact analysis" type="file" accept=".xlsx,.csv,.tsv" disabled={busy} onChange={(e) => { const file = e.target.files[0]; if (file) run(async () => { setProgress("Reading sheet…"); showSheets(await readWorkbook(file), file.name); }); e.target.value = ""; }} />
      </label>
      <div className="panel form-panel"><h2>Analyze existing sheet notes</h2><p>Search the private notes preserved from earlier imports.</p>
        <button disabled={busy} onClick={() => run(analyzeSaved)}><Search size={17} /> Analyze saved notes</button>
        <p className="subtle">If an earlier import discarded a cell, upload the original sheet to recover it.</p>
      </div>
    </div>
    <details className="panel form-panel"><summary>Paste cells from Google Sheets</summary>
      <label className="field"><span>Copied sheet cells</span><textarea rows={5} value={pasted} onChange={(e) => setPasted(e.target.value)} placeholder="Copy the website and contact columns, then paste them here." /></label>
      <button disabled={busy || !pasted.trim()} onClick={() => run(async () => {
        if (pasted.length > 2000000) throw new Error("Paste fewer than 2 million characters at a time.");
        showSheets([{ name: "Pasted cells", rows: parseCSV(pasted, pasted.includes("\t") ? "\t" : ",") }], "Google Sheets paste");
      })}>Analyze pasted cells</button>
    </details>
    {progress && <Notice><span role="status">{progress}</span></Notice>}
    {reports.length > 0 && <>
      <div className="stats-grid mini"><div className="stat-card"><small>Emails detected</small><strong>{emails.toLocaleString()}</strong></div>
        <div className="stat-card"><small>Phone / WhatsApp numbers</small><strong>{phones.toLocaleString()}</strong></div>
        <div className="stat-card"><small>Website matches</small><strong>{contacts.length.toLocaleString()}</strong></div>
        <div className="stat-card"><small>Sheet contacts</small><strong>{unassigned.length.toLocaleString()}</strong></div></div>
      {rawSheets.length > 0 && <details className="panel form-panel"><summary>Review detected headers</summary>{reports.map((r, i) => <div key={i}>
        <h3>{r.sheet_name}</h3><Field label="Header row (0 for no header)" type="number" min="0" max={Math.min(rawSheets[i].rows.length, 100)} disabled={busy || complete} value={r.header_row} onChange={(v) => {
          const h = Number(v); if (!Number.isInteger(h) || h < 0 || h > Math.min(rawSheets[i].rows.length, 100)) return;
          setReports((old) => old.map((x, n) => n === i ? scanSheet(rawSheets[i].rows, filename, x.sheet_name, h - 1) : x)); setAssignments({}); setPage(1);
        }} /><div className="mapping">{r.mapping.map((f, n) => f && <span className="tag" key={n}>{label(f)}</span>)}</div>
      </div>)}</details>}
      <section className="panel form-panel"><div className="panel-heading flush"><h2>Detected contacts</h2>
        <button disabled={!all.length || busy} onClick={() => download("private-contact-candidates.csv", toCSV(all, ["domain", ...CONTACT_FIELDS, "source_file", "sheet_name", "notes"]), "text/csv;charset=utf-8")}><Download size={17} /> Export private CSV</button></div>
        <Field label="Filter contacts" value={query} onChange={(v) => { setQuery(v); setPage(1); }} />
        <div className="table-wrap"><table><thead><tr><th>Website / source</th><th>Email / Gmail</th><th>Phone</th><th>WhatsApp</th><th>Contact page</th></tr></thead><tbody>{rows.map((r, i) => <tr key={`${r.domain}-${i}`}><td>{r.domain || <><strong>Sheet contact</strong><br /><small>{r.source_file} · {r.sheet_name}</small></>}</td><td>{r.email || "—"}</td><td>{r.phone || "—"}</td><td>{r.whatsapp || "—"}</td><td>{r.contact_url || "—"}</td></tr>)}</tbody></table></div>
        {!rows.length && <p>No matching contacts.</p>}
        <div className="form-actions"><button disabled={displayPage <= 1} onClick={() => setPage(displayPage - 1)}>Previous</button><span>Page {displayPage} of {Math.max(1, Math.ceil(filtered.length / 25))}</span><button disabled={displayPage * 25 >= filtered.length} onClick={() => setPage(displayPage + 1)}>Next</button></div>
      </section>
      {!!unassigned.length && <details className="panel form-panel"><summary>Optional: link {unassigned.length} sheet contacts to websites</summary><p>These contacts can be saved privately with their source sheet. Add a website only when you know the contact belongs to that publisher.</p>
        {unassigned.slice(0, 100).map((r, i) => <div className="contact-assignment" key={i}><p>{[r.email, r.phone, r.whatsapp].filter(Boolean).join(" · ")}</p><small>{r.notes}</small><Field label={`Website for contact ${i + 1}`} placeholder="publisher.com" disabled={busy || complete} value={assignments[i] || ""} onChange={(v) => setAssignments((old) => ({ ...old, [i]: v }))} /></div>)}
        {unassigned.length > 100 && <p>Showing the first 100. Export all candidates below to review the remaining contacts.</p>}
        <button onClick={() => download("unassigned-private-contacts.csv", toCSV(unassigned, ["domain", ...CONTACT_FIELDS, "notes"]), "text/csv;charset=utf-8")}>Export unassigned contacts</button>
      </details>}
      <div className="form-actions"><button className="primary" disabled={busy || complete || !all.length} onClick={() => run(save)}>{busy ? "Working…" : complete ? "Saved privately" : "Save contacts privately"}</button>
        {!!unassigned.length && <button onClick={() => go("resellers")}>View saved sheet contacts</button>}</div>
    </>}
  </>;
}
