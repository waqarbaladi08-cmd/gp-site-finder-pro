import React from "react";
import { LockKeyhole } from "lucide-react";
import { hasContact } from "../shared/contacts.mjs";
import { ContactChannels } from "./contact-links.jsx";
import { useApp, useData, Loading, ErrorBox } from "./lib.jsx";

const scopes = {
  selected_sheet: "Current listing's sheet",
  matching_sheet: "This website is also listed in this sheet",
  shared_workbook: "Shared workbook contact",
  other_workbook_tab: "Another tab in the same workbook",
  other_source: "Contact detected in another source file",
};

function SourceContacts({ rows, country }) {
  return rows.map((r, i) => <div className="contact-assignment" key={i}>
    <strong>{r.source_file} · {r.sheet_name || "Workbook contact"}</strong>
    <p className="subtle">{r.kind === "publisher" ? "Website row contact" : "Sheet / supplier contact"} · {scopes[r.scope]}</p>
    <ContactChannels contact={r} country={r.kind === "publisher" && r.scope === "selected_sheet" ? country : ""} />
  </div>);
}

export function ContactDetailsContent({ data }) {
  const publishers = (data?.publisher_sources || []).map((r) => ({ ...r, kind: "publisher" }));
  const suppliers = (data?.suppliers || []).map((r) => ({ ...r, kind: "supplier" }));
  const sources = [...publishers, ...suppliers];
  const current = sources.filter((r) => r.scope === "selected_sheet" ||
    (r.scope === "shared_workbook" && r.source_file === data.source_file));
  const other = sources.filter((r) => !current.includes(r));
  const legacy = !publishers.length && hasContact(data?.contact || {});
  return <>
    {!!current.length && <div><h3>This sheet's contacts</h3>
      <SourceContacts rows={current} country={data.country} />
    </div>}
    {!current.length && data?.source_file && <p>No contact was detected in {data.source_file} · {data.sheet_name || "this sheet"}.</p>}
    {!!other.length && <details><summary>Contacts in other source sheets ({other.length})</summary>
      <p className="subtle">Each entry keeps its own file and tab. Supplier contacts are not assigned to the publisher.</p>
      <SourceContacts rows={other} country={data.country} />
    </details>}
    {legacy && <details open={!sources.length}><summary>Previously saved website contacts</summary>
      <p className="subtle">These older or manually saved contacts do not have a retained sheet assignment.</p>
      <ContactChannels contact={data.contact} country={data.country} />
    </details>}
    {!legacy && !sources.length && <p>Upload the original sheet to detect and save its email, WhatsApp and social links automatically.</p>}
    {(legacy || !!sources.length) && <p className="subtle">Click a number to open WhatsApp, or use its email, Gmail or social link.</p>}
  </>;
}

export function ContactDetails({ domain: target, siteId }) {
  const { user, go } = useApp();
  const params = new URLSearchParams({ domain: target, ...(siteId ? { site_id: siteId } : {}) });
  const { data, error, loading } = useData(user ? "/api/admin/contacts/detail?" + params : null);
  if (!user) return null;
  return <section className="contact-details">
    <h2><LockKeyhole size={18} /> Private contact details · admin only</h2>
    {loading ? <Loading label="Loading private contacts…" /> : error ? <ErrorBox error={error} /> : <ContactDetailsContent data={data} />}
    <button onClick={() => go("contact-analyzer", { domain: target })}>Analyze a contact sheet</button>
  </section>;
}
