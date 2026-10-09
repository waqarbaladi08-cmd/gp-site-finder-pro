import { domain, text } from "./domain.mjs";

export const SOCIAL_FIELDS = ["facebook", "linkedin"];
export const CONTACT_FIELDS = ["email", "phone", "whatsapp", "facebook", "linkedin", "telegram", "contact_url", "admin_name"];
const linksMarker = "[private-contact-links] ";
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

const channelHosts = {
  facebook: ["facebook.com", "www.facebook.com", "m.facebook.com", "web.facebook.com", "fb.com", "www.fb.com", "fb.me"],
  linkedin: ["linkedin.com", "www.linkedin.com", "m.linkedin.com"],
  telegram: ["t.me", "telegram.me", "www.telegram.me"],
  whatsapp: ["wa.me", "api.whatsapp.com", "web.whatsapp.com", "chat.whatsapp.com"],
};
export function channelURL(channel, value) {
  const s = text(value).replace(/[.,;]+$/, "");
  const href = contactURL(/^https?:\/\//i.test(s) ? s : `https://${s}`);
  if (!href) return "";
  const u = new URL(href);
  return channelHosts[channel]?.includes(u.hostname.toLowerCase()) && u.pathname !== "/" ? href : "";
}

export function whatsappURL(value, country = "") {
  const link = channelURL("whatsapp", value);
  if (link) return link;
  const phone = normalizePhone(value);
  if (!phone) return "";
  let digits = phone.replace(/^\+/, "");
  if (phone.startsWith("+")) return /^[1-9]\d{7,14}$/.test(digits) ? `https://wa.me/${digits}` : "";
  // Pakistani mobile numbers have a distinctive national prefix.
  if (/^03[0-4]\d{8}$/.test(digits)) digits = "92" + digits.slice(1);
  else {
    const codes = { pakistan: "92", pk: "92", india: "91", in: "91", "united states": "1", usa: "1", us: "1", canada: "1", ca: "1", "united kingdom": "44", uk: "44", gb: "44", "united arab emirates": "971", uae: "971", australia: "61", au: "61" };
    const code = codes[text(country).toLowerCase()];
    if (code && (digits.startsWith("0") || digits.length === 10)) digits = code + digits.replace(/^0/, "");
    else if (digits.startsWith("0") || digits.length <= 10) return "";
  }
  return /^[1-9]\d{7,14}$/.test(digits) ? `https://wa.me/${digits}` : "";
}

export function contactLink(field, value, country = "") {
  if (field === "email") return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
    ? `mailto:${encodeURIComponent(value).replace(/%40/g, "@")}` : "";
  if (field === "phone" || field === "whatsapp") return whatsappURL(value, country) || (normalizePhone(value) ? `tel:${normalizePhone(value)}` : "");
  if (["facebook", "linkedin"].includes(field)) return channelURL(field, value);
  if (field === "telegram") return channelURL(field, value) || (/^@?[a-z0-9_]{5,32}$/i.test(value) ? `https://t.me/${value.replace(/^@/, "")}` : "");
  return field === "contact_url" ? contactURL(value) : "";
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
    const urls = s.match(/(?:https?:\/\/[^\s<>"')|]+|(?<![a-z0-9.-])(?:www\.|m\.|web\.)?(?:facebook\.com|fb\.com|fb\.me|linkedin\.com|wa\.me|api\.whatsapp\.com|web\.whatsapp\.com|chat\.whatsapp\.com|t\.me|telegram\.me)\/[^\s<>"')|]+)/gi) || [];
    for (const url of urls) {
      for (const channel of ["facebook", "linkedin", "telegram", "whatsapp"]) {
        const href = channelURL(channel, url);
        if (!href) continue;
        if (channel !== "whatsapp") { out[channel].push(href); continue; }
        const u = new URL(href);
        const digits = u.hostname === "wa.me" ? u.pathname.slice(1) : u.searchParams.get("phone");
        const number = digits && normalizePhone("+" + digits.replace(/^\+/, ""));
        out.whatsapp.push(number || href);
      }
    }
    if (field === "telegram") out.telegram.push(...splitValues(s).filter((v) => /^@?[a-z0-9_]{5,32}$/i.test(v)));
    if (field === "admin_name" && !emails.length) out.admin_name.push(s);
    for (const url of urls) {
      if ((field === "contact_url" || /\/(?:contact|about|write-for-us|contribut|editorial|submit)/i.test(url)) && !Object.keys(channelHosts).some((k) => channelURL(k, url)))
        out.contact_url.push(contactURL(url.replace(/[.,;]+$/, "")));
    }
    const isPhone = field === "phone" || field === "whatsapp";
    if (metricFields.has(field)) return;
    const cleaned = urls.reduce((v, url) => v.replace(url, " "), s).replace(/\S+@\S+/g, " ");
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
  return CONTACT_FIELDS.filter((k) => k !== "admin_name").some((k) => text(row[k]));
}

// Social channels use the existing private notes column, so this release does
// not need a remote schema migration. Backups retain the encoded links.
export function hydrateContact(row = {}) {
  const encoded = {}, notes = [];
  for (const line of text(row.notes).split("\n")) {
    if (line.startsWith(linksMarker)) {
      try {
        const parsed = JSON.parse(line.slice(linksMarker.length));
        for (const key of SOCIAL_FIELDS) encoded[key] = unique([...splitValues(encoded[key]), ...splitValues(parsed[key])]).join("; ");
        continue;
      } catch { /* Keep invalid metadata as a normal note. */ }
    }
    notes.push(line);
  }
  const cleanNotes = notes.join("\n").trim();
  const found = extractContacts([cleanNotes, row.contact_url], ["notes", "contact_url"]);
  return { ...row, notes: cleanNotes, ...Object.fromEntries(CONTACT_FIELDS.map((key) => [key,
    unique([...splitValues(row[key]), ...splitValues(encoded[key]), ...splitValues(found[key])]).join("; ").slice(0, 2000)])) };
}

export function storeContact(row) {
  const r = hydrateContact(row);
  const social = Object.fromEntries(SOCIAL_FIELDS.map((key) => [key, unique(splitValues(r[key]).map((v) => channelURL(key, v))).join("; ")]));
  const prefix = Object.values(social).some(Boolean) ? linksMarker + JSON.stringify(social) + "\n" : "";
  if (prefix.length + r.notes.length > 10000) throw Object.assign(new Error("Contact notes and links are too long. Shorten the notes before saving."), { status: 400 });
  return { ...r, notes: prefix + r.notes };
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
    links: unique(all.flatMap((r) => ["facebook", "linkedin", "telegram", "contact_url"].flatMap((k) => splitValues(r[k])))).length,
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
  old = hydrateContact(old); incoming = hydrateContact(incoming);
  const result = { ...old, ...incoming, domain: domain(incoming.domain || old.domain) };
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
  const mapped = cells.map((v, i) => fields[i] === "site" ? domain(v) : "").find(Boolean);
  if (mapped) return mapped;
  // Never infer a publisher from an email address or a contact-page link.
  const candidates = unique(cells.map((v, i) => {
    const s = text(v);
    return !CONTACT_FIELDS.includes(fields[i]) && !s.includes("@") && !/\s/.test(s) && !Object.keys(channelHosts).some((k) => channelURL(k, s)) && !/\/(?:contact|about|write-for-us)/i.test(s) ? domain(s) : "";
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
