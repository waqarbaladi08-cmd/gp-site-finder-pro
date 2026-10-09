import { domain, text } from "./domain.mjs";
import { analyzeContactRows, sheetContactNote } from "./contacts.mjs";
export const IMPORT_FIELDS = [
  "site",
  "country",
  "da",
  "dr",
  "traffic",
  "general_price",
  "casino_price",
  "payment_method",
  "tat",
  "link_type",
  "type",
];
const patterns = [
  ["contact_url", /contact.*(?:page|url|link|form)|submission.*(?:page|url|link)|write for us|editorial.*(?:page|url|link)/],
  ["site", /^(web ?site|site|domain|url)s?( (?:url|links?|name|address))?$|website address/],
  ["country", /country|geography|location/],
  ["da", /^(da|domain authority)$/],
  ["dr", /^(dr|ahrefs dr|domain rating)$/],
  ["traffic", /traffic|monthly visits|organic visits/],
  [
    "casino_price",
    /(casino|gambling).*(price|cost|usd|pkr)|(price|cost).*(casino|gambling)/,
  ],
  ["general_price", /price|cost|guest post rate|^rate$|^gp (usd|pkr)$/],
  ["payment_method", /payment method|pay method|payment terms|payment mode/],
  ["tat", /^tat$|turnaround|turn around|delivery time/],
  ["link_type", /^links?$|link type|dofollow|nofollow/],
  ["type", /niche|category|site type/],
  ["email", /e ?mail|gmail/],
  ["whatsapp", /whats ?app/],
  ["phone", /phone|mobile|telephone|cell|contact (?:no|number)|^contact$|^tel$|فون|موبائل/],
  ["telegram", /telegram/],
  ["facebook", /facebook|^fb(?: link| url| profile| page)?$/],
  ["linkedin", /linked ?in/],
  ["admin_name", /owner|contact name|admin name|publisher name|^(?:full )?name$/],
];
export function headerField(value) {
  const s = text(value)
    .toLowerCase()
    .replace(/[_\-]/g, " ")
    .replace(/[^a-z0-9 \u0600-\u06ff]/g, "")
    .trim();
  return patterns.find(([, p]) => p.test(s))?.[0] || "";
}
export function detectHeader(rows) {
  let best = -1,
    score = -1, contactBest = -1, contactScore = -1;
  rows.slice(0, 100).forEach((row, i) => {
    // Values containing an address or phone are data, not header labels.
    const fields = new Set(row.map((cell) => domain(cell) || /@|https?:\/\/|\d{3}/i.test(text(cell))
      ? "" : headerField(cell)).filter(Boolean));
    if (fields.has("site")) {
      const s = fields.size * 3 + (fields.has("general_price") ? 4 : 0);
      if (s > score) {
        best = i;
        score = s;
      }
    }
    const contactFields = [...fields].filter((field) => ["email", "phone", "whatsapp", "telegram", "facebook", "linkedin", "contact_url"].includes(field));
    const singleContactLabel = row.filter((cell) => text(cell)).length === 1 && row.some((cell) =>
      /^(?:e[ -]?mail(?: address| id)?|gmail|phone(?: number| no)?|mobile(?: number| no)?|contact(?: number| no)?|whats ?app(?: number| no)?|telephone|tel)[\s.#:]*$/i.test(text(cell)));
    if (contactFields.length && (fields.size >= 2 || singleContactLabel) && fields.size > contactScore) {
      contactBest = i; contactScore = fields.size;
    }
  });
  return best >= 0 ? best : contactBest;
}
export function parseCSV(input, delimiter = ",") {
  const rows = [];
  let row = [],
    cell = "",
    quoted = false;
  const s = input.replace(/^\uFEFF/, "");
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (c === '"') {
      if (quoted && s[i + 1] === '"') {
        cell += '"';
        i++;
      } else if (quoted || cell === "") quoted = !quoted;
      else cell += c;
    } else if (c === delimiter && !quoted) {
      row.push(cell);
      cell = "";
    } else if ((c === "\n" || c === "\r") && !quoted) {
      if (c === "\r" && s[i + 1] === "\n") i++;
      row.push(cell);
      if (row.some((x) => x !== "")) rows.push(row);
      row = [];
      cell = "";
    } else cell += c;
  }
  if (quoted) throw new Error("The CSV has an unclosed quoted field.");
  row.push(cell);
  if (row.some((x) => x !== "")) rows.push(row);
  return rows;
}
export function scanSheet(raw, source_file, sheet_name, override = null) {
  const header = override ?? detectHeader(raw),
    mapping = header >= 0 ? raw[header].map(headerField) : [],
    rows = [],
    privateFields = [], retainedRows = new Set();
  const { contacts, unassigned } = analyzeContactRows(raw, source_file, sheet_name, header, mapping);
  let invalid = 0;
  if (header >= 0) {
    for (const values of raw.slice(header + 1)) {
      if (!values.some((v) => text(v))) continue;
      const all = {};
      mapping.forEach((field, i) => {
        if (field && !all[field]) all[field] = text(values[i]);
      });
      const d = domain(all.site);
      if (!d) {
        invalid++;
        continue;
      }
      rows.push({
        ...Object.fromEntries(IMPORT_FIELDS.map((k) => [k, all[k] || ""])),
        source_file,
        sheet_name,
      });
    }
  }
  for (const [index, row] of raw.slice(
    0,
    header < 0 ? Math.min(raw.length, 100) : header,
  ).entries()) {
    const value = row.map(text).filter(Boolean).join(" | ");
    if (
      value &&
      /email|whatsapp|contact|phone|telegram|facebook|linkedin|fb\.|wa\.me|paypal|bank|iban|@/i.test(value)
    ) {
      privateFields.push({
        source_file,
        sheet_name,
        field_name: "Sheet contact / payment note",
        field_value: value.slice(0, 2000),
      });
      retainedRows.add(index + 1);
    }
  }
  for (const record of unassigned.filter((r) => !retainedRows.has(r.row)))
    privateFields.push(sheetContactNote(record));
  return {
    source_file,
    sheet_name,
    header_row: header + 1,
    mapping,
    rows,
    contacts,
    unassigned,
    privateFields,
    invalid,
  };
}
