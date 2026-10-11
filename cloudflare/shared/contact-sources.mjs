import { domain, text } from "./domain.mjs";
import { headerField } from "./import.mjs";
import { CONTACT_FIELDS, contactSummary, detectRowDomain, extractContacts, hasContact, hydrateContact } from "./contacts.mjs";

// Preserve each source both in the preview and when saving. Counts can still
// aggregate by domain without losing the file that supplied a particular value.
export function contactPreviewRows(reports) {
  return reports.flatMap((report) => [...(report.contacts || []), ...(report.unassigned || [])]
    .map((row) => ({ ...row, source_file: row.source_file || report.source_file || "",
      sheet_name: row.sheet_name ?? report.sheet_name ?? "" })));
}

export function contactSourceSummaries(reports) {
  const groups = new Map();
  const group = (source_file, sheet_name) => {
    const key = JSON.stringify([source_file, sheet_name]);
    if (!groups.has(key)) groups.set(key, { source_file, sheet_name, rows: [] });
    return groups.get(key);
  };
  // Include worksheets with zero detections so missing data is visible.
  for (const r of reports) if (r.header_row !== undefined)
    group(r.source_file || "", r.sheet_name || "");
  for (const r of contactPreviewRows(reports)) group(r.source_file, r.sheet_name).rows.push(r);
  return [...groups.values()].map(({ rows, ...source }) => {
    const summary = contactSummary([{ contacts: rows.filter((r) => r.domain), unassigned: rows.filter((r) => !r.domain) }]);
    return { ...source, entries: rows.length, websites: summary.contacts.length,
      emails: summary.emails, phones: summary.phones, links: summary.links };
  });
}

export const websiteContactField = (value) => `Detected website contact: ${domain(value)}`;

// Use the existing private sheet store so attribution survives backups without
// requiring a production schema migration. The JSON keeps the website explicit.
export function sourceContactNote(record) {
  const d = domain(record.domain), source_file = text(record.source_file);
  if (!d || !source_file || !hasContact(record)) return null;
  const contact = hydrateContact(record);
  return { source_file, sheet_name: text(record.sheet_name),
    field_name: websiteContactField(d),
    field_value: JSON.stringify({ domain: d, ...Object.fromEntries(
      CONTACT_FIELDS.filter((key) => contact[key]).map((key) => [key, contact[key]])) }) };
}

// Older imports can retain JSON rows or labeled free-form notes. Use their
// original column labels when deciding which domain owns a contact.
export function savedSourceContact(row, table = "reseller_private") {
  const raw = text(row.raw_record || row.field_value);
  let values = [], fields = [];
  let parsed;
  try { parsed = JSON.parse(raw); } catch { /* Plain sheet note. */ }
  if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
    fields = Object.keys(parsed).map(headerField);
    values = Object.values(parsed);
  } else if (Array.isArray(parsed)) {
    values = parsed;
  } else {
    const fallback = headerField(row.field_name);
    for (const part of raw.split(/[|\n]+/).filter((v) => text(v))) {
      const pair = part.match(/^\s*([^:]{1,100})\s*:\s*(.*)$/);
      const field = pair && headerField(pair[1]);
      if (field) { values.push(pair[2]); fields.push(field); }
      else if (pair && /bank|iban|account|payment|paypal/i.test(pair[1])) {
        values.push(pair[2]); fields.push("payment_method");
      } else { values.push(part); fields.push(fallback); }
    }
  }
  const found = extractContacts(values, fields);
  const assigned = domain(row.site) || detectRowDomain(values, fields) || domain(raw.match(
    /(?:^|[|\n])\s*(?:website(?:\s+(?:link|url|name|address))?|site|domain|url)\s*:\s*(\S+)/i)?.[1]);
  return { ...found, domain: assigned, source_file: row.source_file || "Saved notes",
    sheet_name: row.sheet_name || "", persisted: table === "reseller_private",
    notes: `Saved sheet note: ${row.source_file || ""} / ${row.sheet_name || ""} / ${table} ${row.id}` };
}
