import React from "react";
import { LockKeyhole } from "lucide-react";
import { hasContact } from "../shared/contacts.mjs";
import { ContactChannels } from "./contact-links.jsx";
import { useApp, useData, Loading, ErrorBox } from "./lib.jsx";

export function ContactDetails({ domain: target, siteId }) {
  const { user, go } = useApp();
  const params = new URLSearchParams({ domain: target, ...(siteId ? { site_id: siteId } : {}) });
  const { data, error, loading } = useData(user ? "/api/admin/contacts/detail?" + params : null);
  if (!user) return null;
  return <section className="contact-details">
    <h2><LockKeyhole size={18} /> Private contact details · admin only</h2>
    {loading ? <Loading label="Loading private contacts…" /> : error ? <ErrorBox error={error} /> : <>
      {data?.contact && hasContact(data.contact) && <ContactChannels contact={data.contact} country={data.country} />}
      {!!data?.suppliers?.length && <div><h3>Contacts from all source sheets</h3>
        <p className="subtle">Contacts from every workbook containing this website, grouped by tab. Sheet contacts may belong to a reseller; check the source before contacting them.</p>
        {data.suppliers.map((r, i) => <div className="contact-assignment" key={i}>
          <strong>{r.source_file} · {r.sheet_name || "Workbook contact"}</strong>
          <p className="subtle">{({ selected_sheet: "Current listing's sheet", matching_sheet: "This website is also listed in this sheet", shared_workbook: "Shared workbook contact", other_workbook_tab: "Another tab in the same workbook; publisher ownership is unconfirmed" })[r.scope]}</p>
          <ContactChannels contact={r} />
        </div>)}
      </div>}
      {!hasContact(data?.contact || {}) && !data?.suppliers?.length && <p>No contact retained for this website. Upload its original sheet to detect the email, WhatsApp and social links automatically.</p>}
      {(hasContact(data?.contact || {}) || !!data?.suppliers?.length) && <p className="subtle">Click a number to open WhatsApp, or use an email or social link to contact the source.</p>}
    </>}
    <button onClick={() => go("contact-analyzer", { domain: target })}>Analyze a contact sheet</button>
  </section>;
}
