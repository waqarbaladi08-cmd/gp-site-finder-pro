import { domain, text } from "./domain.mjs";
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
  ["site", /^(website|site|domain|url)s?( url)?$|website address/],
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
  ["email", /e ?mail/],
  ["whatsapp", /whats ?app/],
  ["telegram", /telegram/],
  ["admin_name", /owner|contact name|admin name|publisher name/],
];
export function headerField(value) {
  const s = text(value)
    .toLowerCase()
    .replace(/[_\-]/g, " ")
    .replace(/[^a-z0-9 ]/g, "")
    .trim();
  return patterns.find(([, p]) => p.test(s))?.[0] || "";
}
export function detectHeader(rows) {
  let best = -1,
    score = -1;
  rows.slice(0, 100).forEach((row, i) => {
    const fields = new Set(row.map(headerField).filter(Boolean));
    if (fields.has("site")) {
      const s = fields.size * 3 + (fields.has("general_price") ? 4 : 0);
      if (s > score) {
        best = i;
        score = s;
      }
    }
  });
  return best;
}
export function parseCSV(input) {
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
    } else if (c === "," && !quoted) {
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
    contacts = [],
    privateFields = [];
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
      const contact = {
        domain: d,
        ...Object.fromEntries(
          ["email", "whatsapp", "telegram", "admin_name"]
            .filter((k) => all[k])
            .map((k) => [k, all[k]]),
        ),
      };
      if (
        ["email", "whatsapp", "telegram", "admin_name"].some((k) => contact[k])
      )
        contacts.push(contact);
    }
  }
  for (const row of raw.slice(
    0,
    header < 0 ? Math.min(raw.length, 100) : header,
  )) {
    const value = row.map(text).filter(Boolean).join(" | ");
    if (
      value &&
      /email|whatsapp|contact|phone|telegram|paypal|bank|iban|@/i.test(value)
    )
      privateFields.push({
        source_file,
        sheet_name,
        field_name: "Sheet contact / payment note",
        field_value: value.slice(0, 2000),
      });
  }
  return {
    source_file,
    sheet_name,
    header_row: header + 1,
    mapping,
    rows,
    contacts,
    privateFields,
    invalid,
  };
}
