import { readFile, mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { BACKUP_TABLES, prepareSite, domain } from "../shared/domain.mjs";

export const sqlLiteral = (v) =>
  v == null
    ? "NULL"
    : typeof v === "number" && Number.isFinite(v)
      ? String(v)
      : "'" + String(v).replaceAll("'", "''") + "'";
export function seedStatements(data) {
  if (data.format !== "gp-streamlit-export")
    throw new Error("Expected a legacy export created by export_legacy.py.");
  const tables = { ...data.tables },
    imageKeys = new Set((data.media || []).map((r) => r.key));
  const imagePath = (p) => {
    const normalized = String(p || "").replaceAll("\\", "/"),
      idx = normalized.lastIndexOf("assets/"),
      key = idx >= 0 ? normalized.slice(idx) : normalized;
    return imageKeys.has(key) ? "/api/media/" + key : "";
  };
  const original = tables.sites || [];
  tables.import_review = original
    .filter((r) => !domain(r.site))
    .map((r) => ({
      id: r.id,
      site: r.site,
      source_file: r.source_file || "",
      sheet_name: r.sheet_name || "",
      reason: "Source row does not contain a valid website domain.",
      raw_record: JSON.stringify(r),
      created_at: r.created_at || new Date().toISOString(),
    }));
  tables.sites = original
    .filter((r) => domain(r.site))
    .map((r) => ({ id: r.id, ...prepareSite(r, { legacy: true }) }));
  tables.team_members = (tables.team_members || []).map((r) => ({
    ...r,
    image_path: imagePath(r.image_path),
  }));
  const profile = { ...data.profile };
  profile.image_path = imagePath(
    profile.image_path || "assets/aaquib_profile.png",
  );
  tables.settings = [{ key: "profile", value: JSON.stringify(profile) }];
  tables.media = data.media || [];
  const statements = [];
  for (const [table, rows] of Object.entries(tables)) {
    const allowed = BACKUP_TABLES[table];
    if (!allowed) throw new Error("Unexpected source table: " + table);
    for (const row of rows) {
      if (table === "media") {
        // D1 limits each SQL statement to 100 KB. Keep large photos in small,
        // restartable appends while parameterized API uploads remain unchanged.
        statements.push(
          `INSERT OR IGNORE INTO media(key,content_type,data) VALUES(${sqlLiteral(row.key)},${sqlLiteral(row.content_type)},'');`,
        );
        for (let offset = 0; offset < row.data.length; offset += 40000)
          statements.push(
            `UPDATE media SET data=data||${sqlLiteral(row.data.slice(offset, offset + 40000))} WHERE key=${sqlLiteral(row.key)} AND length(data)=${offset};`,
          );
        continue;
      }
      const keys = allowed.filter((k) => row[k] != null);
      statements.push(
        `INSERT OR IGNORE INTO ${table} (${keys.join(",")}) VALUES (${keys.map((k) => sqlLiteral(row[k])).join(",")});`,
      );
    }
  }
  return {
    statements,
    counts: Object.fromEntries(
      Object.entries(tables).map(([k, v]) => [k, v.length]),
    ),
  };
}
if (
  process.argv[1] &&
  resolve(process.argv[1]) === new URL(import.meta.url).pathname
) {
  const [input, output] = process.argv.slice(2);
  if (!input || !output)
    throw new Error(
      "Usage: node scripts/seed.mjs private/legacy.json private/seed.sql",
    );
  const { statements, counts } = seedStatements(
    JSON.parse(await readFile(input, "utf8")),
  );
  await mkdir(dirname(resolve(output)), { recursive: true });
  await writeFile(
    output,
    "-- Private migration; never commit or publish this file.\n" +
      statements.join("\n") +
      "\n",
    { mode: 0o600 },
  );
  console.log(
    JSON.stringify({ prepared: counts, credentials_included: false }),
  );
}
