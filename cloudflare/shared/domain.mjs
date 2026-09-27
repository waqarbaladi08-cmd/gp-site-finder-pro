import { COUNTRY_GROUPS, NICHE_RULES } from "./rules.mjs";
export const text = (value) =>
  value == null || /^(nan|none|null)$/i.test(String(value).trim())
    ? ""
    : String(value).trim();
const aliases = Object.fromEntries(
  Object.entries(COUNTRY_GROUPS).flatMap(([name, list]) =>
    list.map((v) => [v, name]),
  ),
);
export function country(value) {
  const s = text(value).replace(/\s+/g, " ");
  if (
    /^(unknown|n\/?a|all|global|worldwide|-|not specified)?$/i.test(s) ||
    s.length > 80 ||
    !/^[A-Za-zÀ-ÿ .,'()&/\-]+$/.test(s)
  )
    return "";
  return aliases[s.toLowerCase()] || s;
}
export function domain(value) {
  const s = text(value)
    .toLowerCase()
    .replace(/^https?:\/\//, "")
    .replace(/^www\./, "")
    .split(/[/?#]/)[0];
  return /^(?:[a-z0-9](?:[a-z0-9-]{0,62})\.)+[a-z]{2,63}$/.test(s) ? s : "";
}
export function number(value) {
  const s = text(value).replace(/,/g, "").toLowerCase();
  if (!s || /^(n\/?a|unknown|on request|-|free of charge)$/i.test(s))
    return null;
  const m = s.match(/(?:^|[^\d.])(-?\d+(?:\.\d+)?)\s*([kmb])?(?:\b|$)/i);
  return m ? Number(m[1]) * ({ k: 1e3, m: 1e6, b: 1e9 }[m[2]] || 1) : null;
}
export function niche(row) {
  const parts = [row.type, row.sheet_name, row.source_file, row.site].map(text);
  for (const s of [parts.slice(0, 2).join(" "), parts.join(" ")]) {
    for (const [name, words] of Object.entries(NICHE_RULES))
      if (words.some((w) => s.toLowerCase().includes(w))) return name;
  }
  return "General";
}
export const SITE_FIELDS = [
  "site",
  "country",
  "da",
  "dr",
  "traffic",
  "general_price",
  "casino_price",
  "payment_method",
  "tat",
  "type",
  "link_type",
  "source_file",
  "sheet_name",
  "favorite",
  "created_at",
  "original_price",
  "selling_price",
  "markup_percent",
  "manual_price",
  "casino_original_price",
  "casino_selling_price",
];
export const PUBLIC_FIELDS = [
  "id",
  "site",
  "domain",
  "country",
  "da",
  "dr",
  "traffic",
  "general_price",
  "casino_price",
  "payment_method",
  "tat",
  "type",
  "link_type",
  "source_file",
  "sheet_name",
  "created_at",
  "niche",
];
export function prepareSite(input, { imported = false, legacy = false } = {}) {
  const r = Object.fromEntries(
    SITE_FIELDS.map((k) => [k, text(input[k]).slice(0, 1000)]),
  );
  r.site = text(input.site);
  r.domain = domain(r.site);
  if (!r.domain)
    throw Object.assign(new Error("Enter a valid website domain."), {
      status: 400,
    });
  r.country = country(input.country);
  r.created_at = r.created_at || new Date().toISOString();
  r.markup_percent = Math.min(
    500,
    Math.max(0, Number(input.markup_percent ?? 20) || 0),
  );
  r.manual_price = Number(input.manual_price) === 1 ? 1 : 0;
  r.favorite = Number(input.favorite) === 1 ? 1 : 0;
  r.original_price = text(input.original_price) || r.general_price;
  r.casino_original_price = text(input.casino_original_price) || r.casino_price;
  const sale = (original, fallback) => {
    const v = legacy
      ? Number(
          String(original)
            .replaceAll("$", "")
            .replaceAll(",", "")
            .match(/^[+-]?\d+(?:\.\d+)?/)?.[0] || 0,
        )
      : number(original);
    return v != null && v > 0
      ? (v * (1 + (legacy ? 20 : r.markup_percent) / 100)).toFixed(2)
      : fallback;
  };
  // Legacy SQLite initialization applies markup once; existing selling prices win.
  if (legacy || imported) {
    r.selling_price =
      text(input.selling_price) || sale(r.original_price, r.general_price);
    r.casino_selling_price =
      text(input.casino_selling_price) ||
      sale(r.casino_original_price, r.casino_price);
  } else {
    r.selling_price = r.manual_price
      ? r.general_price
      : sale(r.original_price, r.general_price);
    r.casino_selling_price = r.manual_price
      ? r.casino_price
      : sale(r.casino_original_price, r.casino_price);
  }
  r.general_price = r.selling_price;
  r.casino_price = r.casino_selling_price;
  r.niche = niche(r);
  for (const [field, key] of [
    ["da", "da_value"],
    ["dr", "dr_value"],
    ["traffic", "traffic_value"],
    ["general_price", "price_value"],
    ["original_price", "original_value"],
    ["casino_original_price", "casino_original_value"],
  ])
    r[key] = number(r[field]);
  return r;
}
export const RESOURCES = {
  review: {
    table: "import_review",
    pk: ["id"],
    required: ["raw_record"],
    fields: [
      "id",
      "site",
      "source_file",
      "sheet_name",
      "reason",
      "raw_record",
      "created_at",
    ],
  },
  contacts: {
    table: "contacts",
    pk: ["domain"],
    required: ["domain"],
    fields: [
      "domain",
      "admin_name",
      "email",
      "whatsapp",
      "telegram",
      "status",
      "quoted_price",
      "notes",
      "updated_at",
    ],
  },
  pipeline: {
    table: "outreach_pipeline",
    pk: ["id"],
    required: ["site"],
    fields: [
      "id",
      "site_id",
      "site",
      "status",
      "contact_name",
      "contact_email",
      "whatsapp",
      "last_contacted",
      "next_follow_up",
      "notes",
      "created_at",
      "updated_at",
    ],
  },
  vault: {
    table: "admin_private_contacts",
    pk: ["id"],
    required: ["contact_type", "full_name"],
    fields: [
      "id",
      "contact_type",
      "full_name",
      "company",
      "job_title",
      "email",
      "phone",
      "whatsapp",
      "website",
      "linkedin",
      "address",
      "notes",
      "created_at",
      "updated_at",
    ],
  },
  resellers: {
    table: "reseller_private",
    pk: ["id"],
    required: ["source_file", "field_name"],
    fields: [
      "id",
      "source_file",
      "sheet_name",
      "field_name",
      "field_value",
      "updated_at",
    ],
  },
  structures: {
    table: "sheet_structure",
    pk: ["source_file", "sheet_name"],
    required: ["source_file", "sheet_name"],
    fields: [
      "source_file",
      "sheet_name",
      "header_row",
      "status",
      "mapped_fields",
      "private_count",
      "updated_at",
    ],
  },
  messages: {
    table: "contact_messages",
    pk: ["id"],
    required: ["full_name", "message"],
    fields: [
      "id",
      "full_name",
      "email",
      "phone",
      "company",
      "website",
      "subject",
      "message",
      "status",
      "created_at",
    ],
  },
  team: {
    table: "team_members",
    pk: ["id"],
    required: ["full_name", "designation", "level"],
    fields: [
      "id",
      "full_name",
      "designation",
      "level",
      "reports_to",
      "email",
      "phone",
      "linkedin",
      "website",
      "location",
      "bio",
      "skills",
      "image_path",
      "display_order",
      "active",
      "created_at",
      "updated_at",
    ],
  },
};
export const BACKUP_TABLES = {
  sites: [
    "id",
    ...SITE_FIELDS,
    "domain",
    "niche",
    "da_value",
    "dr_value",
    "traffic_value",
    "price_value",
    "original_value",
    "casino_original_value",
  ],
  ...Object.fromEntries(
    Object.values(RESOURCES).map((x) => [x.table, x.fields]),
  ),
  favorites: ["domain", "created_at"],
  deleted_sites: ["domain", "source_file", "sheet_name", "deleted_at"],
  reseller_settings: [
    "source_file",
    "sheet_name",
    "markup_percent",
    "updated_at",
  ],
  settings: ["key", "value"],
  media: ["key", "content_type", "data"],
};
export const PRIMARY_KEYS = Object.fromEntries([
  ["sites", ["id"]],
  ...Object.values(RESOURCES).map((r) => [r.table, r.pk]),
  ["favorites", ["domain"]],
  ["deleted_sites", ["domain", "source_file", "sheet_name"]],
  ["reseller_settings", ["source_file", "sheet_name"]],
  ["settings", ["key"]],
  ["media", ["key"]],
]);
export function safeWebURL(value) {
  const d = domain(value);
  return d ? `https://${d}` : "";
}
export function csvCell(value) {
  let s = text(value);
  if (/^[\s]*[=+@\-\t\r]/.test(s)) s = "'" + s;
  return '"' + s.replaceAll('"', '""') + '"';
}
export function toCSV(rows, fields = PUBLIC_FIELDS) {
  return (
    "\uFEFF" +
    [
      fields.map(csvCell).join(","),
      ...rows.map((r) => fields.map((f) => csvCell(r[f])).join(",")),
    ].join("\r\n")
  );
}
