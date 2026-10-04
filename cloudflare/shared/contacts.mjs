import { domain, text } from "./domain.mjs";

export const CONTACT_FIELDS = ["email", "phone", "whatsapp", "telegram", "contact_url", "admin_name"];
const contactHint = /phone|mobile|cell(?:phone)?|telephone|tel\b|contact(?:\s*(?:no|number))?|whats\s*app|واٹس|فون|موبائل/i;
const metricFields = new Set(["site", "country", "da", "dr", "traffic", "general_price", "casino_price", "payment_method", "tat", "link_type", "type"]);
const unique = (items) => [...new Map(items.filter(Boolean).map((v) => [v.toLowerCase(), v])).values()];
export const splitValues = (value) => text(value).split(/[;\n]+/).map((s) => s.trim()).filter(Boolean);

export function normalizePhone(value) {
  let v = text(value).replace(/^tel:/i, "").split(/[?;]/)[0].trim();
  if (!/^(?:\+|00)?[\d\s().-]+$/.test(v)) return "";
  let digits = v.replace(/\D/g, "");
  if (/^\d{4}-\d{2}-\d{2}$|^\d{1,2}[/.]\d{1,2}[/.]\d{2,4}$/.test(v)) return "";
  if (v.startsWith("00")) { digits = digits.slice(2); v = "+"; }
  if (digits.length < 7 || digits.length > 15 || /^(\d)\1+$/.test(digits)) return "";
  return (v.startsWith("+") ? "+" : "") + digits;
}

export function contactURL(value) {
  try {
    const u = new URL(text(value));
    return ["http:", "https:"].includes(u.protocol) && domain(u.hostname) && !u.username && !u.password
      ? u.href.slice(0, 1500) : "";
  } catch { return ""; }
}

// Candidate detection checks syntax, not ownership or deliverability.
// Numeric metrics are never treated as telephone numbers.
export function extractContacts(cells, fields = []) {
  const out = Object.fromEntries(CONTACT_FIELDS.map((k) => [k, []]));
  cells.forEach((cell, i) => {
    const field = fields[i] || "";
    let s = text(cell).slice(0, 10000)
      .replace(/\s*[\[(]\s*at\s*[\])]\s*/gi, "@")
      .replace(/\s*[\[(]\s*dot\s*[\])]\s*/gi, ".");
    try { s = decodeURIComponent(s); } catch { /* Plain text is still useful. */ }
    const emails = s.match(/[A-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Z0-9](?:[A-Z0-9.-]*[A-Z0-9])?\.[A-Z]{2,63}/gi) || [];
    out.email.push(...emails.map((e) => e.toLowerCase()).filter((e) =>
      e.length <= 254 && !e.includes("..") && !/\.(png|jpg|jpeg|gif|webp|svg)$/i.test(e)));
    for (const m of s.matchAll(/(?:https?:\/\/)?(?:wa\.me\/|api\.whatsapp\.com\/send\?phone=)(\+?\d{7,15})/gi))
      out.whatsapp.push(normalizePhone("+" + m[1].replace(/^\+/, "")));
    for (const m of s.matchAll(/https?:\/\/(?:t\.me|telegram\.me)\/[A-Za-z0-9_]+/gi)) out.telegram.push(m[0]);
    if (field === "telegram") out.telegram.push(...splitValues(s).filter((v) => /^@?[a-z0-9_]{5,32}$/i.test(v)));
    if (field === "admin_name" && !emails.length) out.admin_name.push(s);
    for (const url of s.match(/https?:\/\/[^\s<>"')]+/gi) || []) {
      if (field === "contact_url" || /\/(?:contact|about|write-for-us|contribut|editorial|submit)/i.test(url))
        out.contact_url.push(contactURL(url.replace(/[.,;]+$/, "")));
    }
    const isPhone = field === "phone" || field === "whatsapp";
    if (metricFields.has(field)) return;
    const cleaned = s.replace(/https?:\/\/\S+|\S+@\S+/g, " ");
    for (const m of cleaned.matchAll(/(?:\+|00)?\d[\d ().-]{5,24}\d/g)) {
      const candidate = m[0].trim();
      const explicit = isPhone || contactHint.test(cleaned.slice(Math.max(0, m.index - 25), m.index)) || candidate.startsWith("+");
      const bare = !field && cleaned.trim() === candidate && /^0?\d{10,15}$/.test(candidate);
      if (!explicit && !bare) continue;
      const phone = normalizePhone(candidate);
      if (phone) out[field === "whatsapp" || /whats\s*app/i.test(cleaned.slice(0, m.index)) ? "whatsapp" : "phone"].push(phone);
    }
  });
  return Object.fromEntries(Object.entries(out).map(([k, v]) => [k, unique(v).join("; ")]));
}

export function hasContact(row) {
  return ["email", "phone", "whatsapp", "telegram", "contact_url"].some((k) => text(row[k]));
}

export function contactSummary(reports) {
  const byDomain = new Map();
  for (const report of reports) for (const row of report.contacts || [])
    byDomain.set(row.domain, mergeContacts(byDomain.get(row.domain), row));
  const contacts = [...byDomain.values()];
  const unassigned = reports.flatMap((r) => r.unassigned || []);
  const all = [...contacts, ...unassigned];
  return {
    contacts, unassigned, all,
    emails: unique(all.flatMap((r) => splitValues(r.email))).length,
    phones: unique(all.flatMap((r) => [...splitValues(r.phone), ...splitValues(r.whatsapp)])).length,
  };
}

// Keep sheet contacts even when there is no publisher domain to assign.
// The existing private-notes store deduplicates identical imports.
export function sheetContactNote(record) {
  return {
    source_file: record.source_file || "Uploaded sheet",
    sheet_name: record.sheet_name || "",
    field_name: `Detected sheet contact${record.row ? ` (row ${record.row})` : ""}`,
    field_value: CONTACT_FIELDS.filter((key) => record[key])
      .map((key) => `${key}: ${record[key]}`).join(" | "),
  };
}

export function mergeContacts(old = {}, incoming = {}) {
  const result = { ...old, domain: domain(incoming.domain || old.domain) };
  for (const k of CONTACT_FIELDS) {
    const items = [...splitValues(old[k]), ...splitValues(incoming[k])];
    result[k] = unique(items).join("; ").slice(0, 2000);
  }
  result.notes = unique([...text(old.notes).split("\n"), ...text(incoming.notes).split("\n")]).join("\n").slice(0, 10000);
  // Imports preserve manually maintained workflow details.
  for (const k of ["status", "quoted_price"]) result[k] = text(old[k]) || text(incoming[k]);
  return result;
}

export function detectRowDomain(cells, fields = []) {
  const mapped = fields.indexOf("site");
  if (mapped >= 0) return domain(cells[mapped]);
  // Never infer a publisher from an email address or a contact-page link.
  const candidates = unique(cells.map((v) => {
    const s = text(v);
    return !s.includes("@") && !/\s/.test(s) && !/\/(?:contact|about|write-for-us)/i.test(s) ? domain(s) : "";
  }));
  return candidates.length === 1 ? candidates[0] : "";
}

export function analyzeContactRows(raw, source, sheet, header = -1, mapping = []) {
  const byDomain = new Map(), unassigned = [];
  raw.forEach((cells, index) => {
    if (index === header) return;
    const fields = header >= 0 && index > header ? mapping : [];
    const found = extractContacts(cells, fields);
    if (!hasContact(found) && !found.admin_name) return;
    const d = detectRowDomain(cells, fields);
    const record = { ...found, domain: d, source_file: source, sheet_name: sheet,
      notes: `Sheet: ${source} / ${sheet} / row ${index + 1}`, row: index + 1 };
    if (d) byDomain.set(d, mergeContacts(byDomain.get(d), record));
    else if (hasContact(found)) unassigned.push(record);
  });
  return { contacts: [...byDomain.values()], unassigned };
}
