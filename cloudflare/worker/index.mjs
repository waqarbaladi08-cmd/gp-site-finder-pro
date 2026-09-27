import {
  PUBLIC_FIELDS,
  RESOURCES,
  BACKUP_TABLES,
  PRIMARY_KEYS,
  prepareSite,
  text,
  domain,
} from "../shared/domain.mjs";
import {
  fail,
  body,
  originCheck,
  session,
  cookie,
  login,
  sha,
  same,
  rateLimit,
  setPassword,
  normalizeUsername,
} from "./auth.mjs";
import { appBase, stripAppBase } from "../shared/routing.mjs";
import { WEBSITE_ORIGIN, mountedResponse } from "./routing.mjs";

const json = (data, status = 200, headers = {}) =>
  Response.json(data, {
    status,
    headers: {
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff",
      "X-Frame-Options": "DENY",
      ...headers,
    },
  });
const now = () => new Date().toISOString();
const integer = (v, min = 0, max = 1e9) =>
  Math.min(max, Math.max(min, Math.floor(Number(v) || 0)));
const bump = (db) =>
  db.prepare(
    "UPDATE app_meta SET value=CAST(value AS INTEGER)+1 WHERE key='version'",
  );
const version = async (db) =>
  (await db.prepare("SELECT value FROM app_meta WHERE key='version'").first())
    ?.value || "0";
const validID = (v) => {
  const id = Number(v);
  if (!Number.isSafeInteger(id) || id < 1) fail("Invalid record ID.");
  return id;
};
const sqlValue = (v) =>
  v == null ? null : typeof v === "number" ? v : String(v);

function siteQuery(params) {
  const parts = [],
    values = [];
  const raw = (params.get("q") || "").trim().toLowerCase().slice(0, 200);
  if (raw) {
    const q = domain(raw) || raw;
    parts.push(
      "(domain LIKE ? ESCAPE '\\' OR type LIKE ? ESCAPE '\\' OR niche LIKE ? ESCAPE '\\')",
    );
    const term = "%" + q.replace(/[\\%_]/g, "\\$&") + "%";
    values.push(term, term, term);
  }
  for (const col of [
    "country",
    "niche",
    "payment_method",
    "link_type",
    "source_file",
    "sheet_name",
  ]) {
    const val = params.get(col);
    if (val) {
      parts.push(`${col}=?`);
      values.push(val.slice(0, 1000));
    }
  }
  for (const [param, col, op] of [
    ["min_dr", "dr_value", ">="],
    ["max_price", "price_value", "<="],
    ["min_traffic", "traffic_value", ">="],
  ]) {
    const val = Number(params.get(param));
    if (Number.isFinite(val) && val > 0) {
      parts.push(`${col}${op}?`);
      values.push(val);
    }
  }
  if (params.has("ids")) {
    const ids = (params.get("ids") || "")
      .split(",")
      .map(Number)
      .filter((x) => Number.isSafeInteger(x) && x > 0)
      .slice(0, 1000);
    if (!ids.length) parts.push("0");
    else {
      parts.push("id IN (SELECT value FROM json_each(?))");
      values.push(JSON.stringify(ids));
    }
  }
  return { where: parts.length ? " WHERE " + parts.join(" AND ") : "", values };
}
async function sites(db, params, admin = false) {
  const { where, values } = siteQuery(params);
  const limit = integer(params.get("limit") || 25, 1, 100);
  const count = await db
    .prepare("SELECT COUNT(*) AS total FROM sites" + where)
    .bind(...values)
    .first();
  const pages = Math.max(1, Math.ceil(count.total / limit)),
    page = integer(params.get("page") || 1, 1, pages);
  const sort =
    {
      newest: "id DESC",
      domain: "domain ASC,id ASC",
      dr: "dr_value DESC,id ASC",
      traffic: "traffic_value DESC,id ASC",
      price: "price_value IS NULL,price_value ASC,id ASC",
    }[params.get("sort")] || "id DESC";
  const rows = await db
    .prepare(
      `SELECT ${admin ? "*" : PUBLIC_FIELDS.join(",")} FROM sites${where} ORDER BY ${sort} LIMIT ? OFFSET ?`,
    )
    .bind(...values, limit, (page - 1) * limit)
    .all();
  return { rows: rows.results, total: count.total, page, pages, limit };
}
async function options(db) {
  const cols = [
    "country",
    "niche",
    "payment_method",
    "link_type",
    "source_file",
    "sheet_name",
  ];
  const rows = await db.batch(
    cols.map((c) =>
      db.prepare(
        `SELECT DISTINCT ${c} AS value FROM sites WHERE ${c}<>'' ORDER BY ${c} LIMIT 500`,
      ),
    ),
  );
  return Object.fromEntries(
    cols.map((c, i) => [c, rows[i].results.map((r) => r.value)]),
  );
}
async function stats(db) {
  const result = await db.batch([
    db.prepare(
      "SELECT COUNT(*) AS total,COUNT(DISTINCT domain) AS domains,COUNT(DISTINCT NULLIF(country,'')) AS countries,COUNT(DISTINCT source_file) AS sources,ROUND(AVG(dr_value),1) AS average_dr,COUNT(dr_value) AS recorded_dr,COUNT(price_value) AS recorded_prices FROM sites",
    ),
    db.prepare(
      "SELECT niche AS name,COUNT(*) AS count FROM sites GROUP BY niche ORDER BY count DESC",
    ),
    db.prepare(
      "SELECT COALESCE(NULLIF(country,''),'Not specified') AS name,COUNT(*) AS count FROM sites GROUP BY country ORDER BY count DESC LIMIT 12",
    ),
    db.prepare(
      `SELECT ${PUBLIC_FIELDS.join(",")} FROM sites ORDER BY id DESC LIMIT 5`,
    ),
  ]);
  return {
    ...result[0].results[0],
    niches: result[1].results,
    countries_breakdown: result[2].results,
    recent: result[3].results,
  };
}
async function cachePublic(request, ctx, loader, seconds = 60) {
  // Admin refreshes and imported data bypass short public caches.
  if (
    request.headers.get("Cookie")?.includes("gp_session=") ||
    new URL(request.url).searchParams.has("fresh")
  )
    return json(await loader());
  const cache = globalThis.caches?.default,
    key = new Request(request.url);
  if (cache) {
    const hit = await cache.match(key);
    if (hit) return hit;
  }
  const response = json(await loader(), 200, {
    "Cache-Control": `public, max-age=${seconds}`,
  });
  if (cache) ctx.waitUntil(cache.put(key, response.clone()));
  return response;
}
function insert(db, table, row, { replace = false, pk = ["id"] } = {}) {
  const cols = Object.keys(row),
    marks = cols.map(() => "?").join(",");
  let query = `INSERT INTO ${table} (${cols.join(",")}) VALUES(${marks})`;
  if (replace) {
    const updates = cols
      .filter((k) => !pk.includes(k))
      .map((k) => `${k}=excluded.${k}`)
      .join(",");
    query += ` ON CONFLICT(${pk.join(",")}) DO ${updates ? "UPDATE SET " + updates : "NOTHING"}`;
  }
  return db.prepare(query).bind(...cols.map((k) => sqlValue(row[k])));
}
function resourceRow(resource, input) {
  const row = {};
  for (const k of resource.fields) {
    if (input[k] != null && (k !== "id" || input[k] !== ""))
      row[k] = text(input[k]).slice(
        0,
        k === "raw_record"
          ? 50000
          : k === "notes" || k === "bio" || k === "message"
            ? 10000
            : 2000,
      );
  }
  if (row.id != null) row.id = validID(row.id);
  if (resource.table === "contacts") row.domain = domain(input.domain);
  if (resource.table === "outreach_pipeline") {
    row.site = domain(input.site);
    row.status = row.status || "New";
    if (row.site_id) row.site_id = validID(row.site_id);
  }
  if (resource.table === "team_members") {
    row.active = Number(input.active ?? 1) === 1 ? 1 : 0;
    row.display_order = integer(input.display_order ?? 100, 0, 10000);
    row.image_path = text(input.image_path);
    if (row.image_path && !/^\/api\/media\/[\w./-]+$/.test(row.image_path))
      fail("Upload the team photo using the photo tool.");
  }
  for (const key of resource.required)
    if (!row[key]) fail(`${key.replaceAll("_", " ")} is required.`);
  for (const key of ["created_at", "updated_at"])
    if (resource.fields.includes(key))
      row[key] = key === "created_at" ? row[key] || now() : now();
  return row;
}
async function route(request, env, ctx, additionalOrigin) {
  const url = new URL(request.url),
    p = url.pathname,
    m = request.method,
    db = env.DB;
  if (!p.startsWith("/api/")) return env.ASSETS.fetch(request);
  if (m !== "GET" && m !== "HEAD") originCheck(request, additionalOrigin);
  if (p === "/api/health" && m === "GET") {
    await db.prepare("SELECT 1").first();
    return json({ ok: true, storage: "Cloudflare D1" });
  }
  if (p === "/api/auth/challenge" && m === "GET") {
    const username = normalizeUsername(url.searchParams.get("username")),
      user = await db
        .prepare("SELECT salt,iterations FROM auth_users WHERE username=?")
        .bind(username)
        .first();
    return json(
      user || {
        salt: (await sha("gp-login:" + username)).slice(0, 32),
        iterations: 600000,
      },
    );
  }
  if (p === "/api/auth/login" && m === "POST") {
    const r = await login(request, env);
    return json(r.data, 200, { "Set-Cookie": r.cookie });
  }
  if (p === "/api/auth/logout" && m === "POST") {
    const token = (request.headers.get("Cookie") || "").match(
      /gp_session=([a-f0-9]{64})/,
    )?.[1];
    if (token)
      await db
        .prepare("DELETE FROM sessions WHERE token_hash=?")
        .bind(await sha(token))
        .run();
    return json({ ok: true }, 200, { "Set-Cookie": cookie(request, "", 0) });
  }
  if (p === "/api/auth/me" && m === "GET")
    return json({ user: await session(request, db) });
  if (p === "/api/sites" && m === "GET")
    return cachePublic(request, ctx, () => sites(db, url.searchParams));
  if (p === "/api/export" && m === "GET") {
    const { where, values } = siteQuery(url.searchParams),
      after = integer(url.searchParams.get("after"));
    const rows = (
      await db
        .prepare(
          `SELECT ${PUBLIC_FIELDS.join(",")} FROM sites${where ? where + " AND" : " WHERE"} id>? ORDER BY id LIMIT 250`,
        )
        .bind(...values, after)
        .all()
    ).results;
    return json({ rows, next: rows.length === 250 ? rows.at(-1).id : null });
  }
  if (p === "/api/options" && m === "GET")
    return cachePublic(request, ctx, () => options(db), 120);
  if (p === "/api/stats" && m === "GET")
    return cachePublic(request, ctx, () => stats(db), 120);
  if (p === "/api/profile" && m === "GET") {
    const r = await db
      .prepare("SELECT value FROM settings WHERE key='profile'")
      .first();
    return json(r ? JSON.parse(r.value) : { brand_name: "GP Site Finder Pro" });
  }
  if (p === "/api/team" && m === "GET")
    return json(
      (
        await db
          .prepare(
            "SELECT * FROM team_members WHERE active=1 ORDER BY display_order,id",
          )
          .all()
      ).results,
    );
  if (p.startsWith("/api/media/") && m === "GET") {
    const key = decodeURIComponent(p.slice(11));
    const r = await db
      .prepare("SELECT * FROM media WHERE key=?")
      .bind(key)
      .first();
    if (!r) fail("Photo not found.", 404);
    const bytes = Uint8Array.from(atob(r.data), (c) => c.charCodeAt(0));
    return new Response(bytes, {
      headers: {
        "Content-Type": r.content_type,
        "X-Content-Type-Options": "nosniff",
        "Cache-Control": "public,max-age=3600",
      },
    });
  }
  if (p === "/api/contact" && m === "POST") {
    const b = await body(request, 20000);
    if (b.company_website) return json({ ok: true });
    await rateLimit(
      db,
      "contact:" +
        (await sha(request.headers.get("CF-Connecting-IP") || "local")),
      5,
      3600,
    );
    const row = resourceRow(RESOURCES.messages, { ...b, status: "New" });
    delete row.id;
    await db.batch([insert(db, "contact_messages", row), bump(db)]);
    return json({ ok: true }, 201);
  }
  if (p.startsWith("/api/admin/") || p === "/api/auth/password") {
    const user = await session(request, db);
    if (!user) fail("Sign in as an administrator to use this tool.", 401);
    if (p === "/api/auth/password" && m === "POST") {
      await setPassword(db, user.username, await body(request, 5000));
      return json({ ok: true }, 200, { "Set-Cookie": cookie(request, "", 0) });
    }
    if (p === "/api/admin/status" && m === "GET")
      return json({
        ok: true,
        version: await version(db),
        ahrefs: !!env.AHREFS_API_KEY,
        tables: Object.keys(BACKUP_TABLES),
      });
    if (p === "/api/admin/sites" && m === "GET")
      return json(await sites(db, url.searchParams, true));
    if (p === "/api/admin/legacyfavorites" && m === "GET")
      return json(
        (
          await db
            .prepare(
              "SELECT id FROM sites WHERE favorite=1 OR domain IN (SELECT domain FROM favorites) LIMIT 1000",
            )
            .all()
        ).results.map((r) => r.id),
      );
    if (p === "/api/admin/resource-batch" && m === "POST") {
      const b = await body(request),
        r = RESOURCES[b.resource];
      if (!r || !Array.isArray(b.rows) || b.rows.length > 20 || !b.rows.length)
        fail("Invalid resource batch.");
      await db.batch([
        ...b.rows.map((input) => {
          const row = resourceRow(r, input);
          if (r.table === "reseller_private" && !row.id) {
            const keys = Object.keys(row);
            return db
              .prepare(
                `INSERT INTO reseller_private(${keys.join(",")}) SELECT ${keys.map(() => "?")} WHERE NOT EXISTS(SELECT 1 FROM reseller_private WHERE source_file=? AND COALESCE(sheet_name,'')=? AND field_name=? AND COALESCE(field_value,'')=?)`,
              )
              .bind(
                ...keys.map((k) => sqlValue(row[k])),
                row.source_file,
                row.sheet_name || "",
                row.field_name,
                row.field_value || "",
              );
          }
          return insert(db, r.table, row, {
            replace: true,
            pk: r.table === "outreach_pipeline" && !row.id ? ["site"] : r.pk,
          });
        }),
        bump(db),
      ]);
      return json({ saved: b.rows.length });
    }
    if (p === "/api/admin/sites" && m === "POST") {
      const b = await body(request, 30000),
        r = prepareSite(b);
      const result = await db.batch([insert(db, "sites", r), bump(db)]);
      return json({ id: result[0].meta.last_row_id }, 201);
    }
    const siteID = p.match(/^\/api\/admin\/sites\/(\d+)$/)?.[1];
    if (siteID) {
      const id = validID(siteID),
        old = await db
          .prepare("SELECT * FROM sites WHERE id=?")
          .bind(id)
          .first();
      if (!old) fail("Website not found.", 404);
      if (m === "GET") return json(old);
      if (m === "PUT") {
        const r = prepareSite({ ...old, ...(await body(request, 30000)) }),
          keys = Object.keys(r);
        await db.batch([
          db
            .prepare(`UPDATE sites SET ${keys.map((k) => k + "=?")} WHERE id=?`)
            .bind(...keys.map((k) => r[k]), id),
          bump(db),
        ]);
        return json({ ok: true });
      }
      if (m === "DELETE") {
        await db.batch([
          db
            .prepare("INSERT OR REPLACE INTO deleted_sites VALUES(?,?,?,?)")
            .bind(
              old.domain,
              old.source_file || "",
              old.sheet_name || "",
              now(),
            ),
          db.prepare("DELETE FROM sites WHERE id=?").bind(id),
          bump(db),
        ]);
        return json({ ok: true });
      }
    }
    if (p === "/api/admin/import" && m === "POST") {
      const b = await body(request);
      if (!Array.isArray(b.rows) || b.rows.length > 25 || !b.rows.length)
        fail("Send 1–25 websites per batch.");
      const rows = b.rows.map((x) => prepareSite(x, { imported: true })),
        statements = rows.map((r) => {
          const cols = Object.keys(r);
          return db
            .prepare(
              `INSERT INTO sites(${cols.join(",")}) SELECT ${cols.map(() => "?")} WHERE NOT EXISTS(SELECT 1 FROM sites WHERE domain=? AND source_file=? AND sheet_name=?) AND NOT EXISTS(SELECT 1 FROM deleted_sites WHERE domain=? AND source_file=? AND sheet_name=?)`,
            )
            .bind(
              ...cols.map((k) => r[k]),
              r.domain,
              r.source_file,
              r.sheet_name,
              r.domain,
              r.source_file,
              r.sheet_name,
            );
        });
      const result = await db.batch([...statements, bump(db)]);
      return json({
        inserted: result.slice(0, -1).reduce((n, r) => n + r.meta.changes, 0),
        submitted: rows.length,
      });
    }
    if (p === "/api/admin/duplicates" && m === "GET") {
      const result = await db
        .prepare(
          "SELECT domain,COUNT(*) AS count,MIN(id) AS first_id FROM sites GROUP BY domain HAVING COUNT(*)>1 ORDER BY count DESC LIMIT 250",
        )
        .all();
      return json(result.results);
    }
    if (p === "/api/admin/pricing" && m === "POST") {
      const b = await body(request, 10000),
        markup = Number(b.markup_percent);
      if (!Number.isFinite(markup) || markup < 0 || markup > 500)
        fail("Markup must be between 0 and 500.");
      if (typeof b.source_file !== "string" || typeof b.sheet_name !== "string")
        fail("Select a source and sheet.");
      const result = await db.batch([
        db
          .prepare(
            `UPDATE sites SET markup_percent=?,selling_price=CASE WHEN manual_price=0 AND original_value>0 THEN printf('%.2f',original_value*(1+?/100.0)) ELSE selling_price END,general_price=CASE WHEN manual_price=0 AND original_value>0 THEN printf('%.2f',original_value*(1+?/100.0)) ELSE general_price END,price_value=CASE WHEN manual_price=0 AND original_value>0 THEN round(original_value*(1+?/100.0),2) ELSE price_value END,casino_selling_price=CASE WHEN manual_price=0 AND casino_original_value>0 THEN printf('%.2f',casino_original_value*(1+?/100.0)) ELSE casino_selling_price END,casino_price=CASE WHEN manual_price=0 AND casino_original_value>0 THEN printf('%.2f',casino_original_value*(1+?/100.0)) ELSE casino_price END WHERE source_file=? AND sheet_name=?`,
          )
          .bind(
            markup,
            markup,
            markup,
            markup,
            markup,
            markup,
            b.source_file,
            b.sheet_name,
          ),
        insert(
          db,
          "reseller_settings",
          {
            source_file: b.source_file,
            sheet_name: b.sheet_name,
            markup_percent: markup,
            updated_at: now(),
          },
          { replace: true, pk: ["source_file", "sheet_name"] },
        ),
        bump(db),
      ]);
      return json({ updated: result[0].meta.changes });
    }
    const resourceKey = p.match(/^\/api\/admin\/resources\/([a-z]+)$/)?.[1];
    if (resourceKey) {
      const r = RESOURCES[resourceKey];
      if (!r) fail("Tool not found.", 404);
      if (m === "GET") {
        const page = integer(url.searchParams.get("page") || 1, 1, 100000),
          q = (url.searchParams.get("q") || "").slice(0, 200),
          search = r.fields.filter(
            (k) => !["id", "site_id", "image_path"].includes(k),
          );
        const where = q
            ? " WHERE " + search.map((k) => `${k} LIKE ?`).join(" OR ")
            : "",
          values = q ? search.map(() => "%" + q.replaceAll("%", "") + "%") : [];
        const result = await db.batch([
          db
            .prepare(`SELECT COUNT(*) AS total FROM ${r.table}${where}`)
            .bind(...values),
          db
            .prepare(
              `SELECT * FROM ${r.table}${where} ORDER BY ${r.pk.join(",")} DESC LIMIT 50 OFFSET ?`,
            )
            .bind(...values, (page - 1) * 50),
        ]);
        return json({
          rows: result[1].results,
          total: result[0].results[0].total,
          page,
          pages: Math.max(1, Math.ceil(result[0].results[0].total / 50)),
        });
      }
      const input = await body(request, 100000);
      if (m === "POST" || m === "PUT") {
        const row = resourceRow(r, input);
        await db.batch([
          insert(db, r.table, row, {
            replace: true,
            pk: r.table === "outreach_pipeline" && !row.id ? ["site"] : r.pk,
          }),
          bump(db),
        ]);
        return json({ ok: true });
      }
      if (m === "DELETE") {
        const values = r.pk.map((k) => input[k]);
        if (values.some((v) => v == null)) fail("Missing record key.");
        await db.batch([
          db
            .prepare(
              `DELETE FROM ${r.table} WHERE ${r.pk.map((k) => k + "=?").join(" AND ")}`,
            )
            .bind(...values),
          bump(db),
        ]);
        return json({ ok: true });
      }
    }
    if (p === "/api/admin/profile" && m === "PUT") {
      const b = await body(request, 20000),
        keys = [
          "brand_name",
          "name",
          "role",
          "phone",
          "email",
          "website",
          "linkedin",
          "location",
          "about",
          "image_path",
        ];
      const profile = Object.fromEntries(
        keys.map((k) => [k, text(b[k]).slice(0, k === "about" ? 10000 : 500)]),
      );
      if (
        profile.image_path &&
        !/^\/api\/media\/[\w./-]+$/.test(profile.image_path)
      )
        fail("Upload a profile photo using the photo tool.");
      await db.batch([
        insert(
          db,
          "settings",
          { key: "profile", value: JSON.stringify(profile) },
          { replace: true, pk: ["key"] },
        ),
        bump(db),
      ]);
      return json({ ok: true });
    }
    if (p === "/api/admin/media" && m === "POST") {
      const b = await body(request, 800000);
      if (
        !/^image\/(png|jpeg|webp)$/.test(b.content_type) ||
        !/^[-\w./]{1,160}$/.test(b.key) ||
        typeof b.data !== "string" ||
        b.data.length > 700000
      )
        fail("Use a PNG, JPG or WebP photo under 500 KB.");
      let magic;
      try {
        magic = atob(b.data.slice(0, 64));
      } catch {
        fail("Invalid photo.");
      }
      if (!(
        (b.content_type === "image/png" &&
          magic.startsWith("\x89PNG\r\n\x1a\n")) ||
        (b.content_type === "image/jpeg" && magic.startsWith("\xff\xd8\xff")) ||
        (b.content_type === "image/webp" &&
          magic.startsWith("RIFF") &&
          magic.slice(8, 12) === "WEBP")
      ))
        fail("Photo format does not match its contents.");
      await db.batch([
        insert(
          db,
          "media",
          { key: b.key, content_type: b.content_type, data: b.data },
          { replace: true, pk: ["key"] },
        ),
        bump(db),
      ]);
      return json({ url: "/api/media/" + b.key });
    }
    if (p === "/api/admin/backup" && m === "GET") {
      const table = url.searchParams.get("table");
      if (!BACKUP_TABLES[table]) fail("Unknown backup table.");
      const v = await version(db);
      if (
        url.searchParams.has("version") &&
        url.searchParams.get("version") !== v
      )
        fail("Data changed during backup. Please restart the download.", 409);
      const offset = integer(url.searchParams.get("offset")),
        limit = table === "media" ? 1 : 100;
      const result = await db
        .prepare(
          `SELECT ${BACKUP_TABLES[table].join(",")} FROM ${table} ORDER BY ${PRIMARY_KEYS[table].join(",")} LIMIT ? OFFSET ?`,
        )
        .bind(limit, offset)
        .all();
      return json({
        version: v,
        rows: result.results,
        next: result.results.length === limit ? offset + limit : null,
      });
    }
    if (p === "/api/admin/restore" && m === "POST") {
      const b = await body(request, 1600000),
        cols = BACKUP_TABLES[b.table];
      if (
        !cols ||
        !Array.isArray(b.rows) ||
        !b.rows.length ||
        b.rows.length > (b.table === "media" ? 1 : 20) ||
        b.confirm !== "MERGE BACKUP"
      )
        fail("Invalid backup batch or missing confirmation.");
      const statements = b.rows.map((row) => {
        let r = Object.fromEntries(
          cols.filter((k) => row[k] != null).map((k) => [k, sqlValue(row[k])]),
        );
        if (b.table === "sites")
          r = { id: validID(row.id), ...prepareSite(row, { legacy: true }) };
        if (PRIMARY_KEYS[b.table].some((k) => r[k] == null))
          fail("Backup record has no primary key.");
        if (
          b.table === "media" &&
          (!/^image\/(png|jpeg|webp)$/.test(r.content_type) ||
            r.data.length > 1500000)
        )
          fail("Unsupported backup media.");
        if (b.table === "settings" && r.key !== "profile")
          fail("Unsupported setting.");
        return insert(db, b.table, r, {
          replace: true,
          pk: PRIMARY_KEYS[b.table],
        });
      });
      await db.batch([...statements, bump(db)]);
      return json({ restored: b.rows.length });
    }
    if (p === "/api/admin/metrics" && m === "POST") {
      if (!env.AHREFS_API_KEY)
        fail(
          "Live metrics require your existing Ahrefs API key. Recorded metrics remain available in Search.",
          503,
        );
      const b = await body(request, 5000),
        target = domain(b.site);
      if (!target) fail("Enter a valid domain.");
      await rateLimit(db, "metrics:" + user.username, 30, 3600);
      const kind = b.kind === "traffic" ? "traffic" : "dr",
        api = new URL(
          kind === "dr"
            ? "https://api.ahrefs.com/v3/public/domain-rating-free"
            : "https://api.ahrefs.com/v3/site-explorer/metrics",
        );
      api.search = new URLSearchParams(
        kind === "dr"
          ? { target, output: "json" }
          : {
              target,
              output: "json",
              date: now().slice(0, 10),
              mode: "domain",
              protocol: "both",
              volume_mode: "monthly",
              traffic_mode: "static",
            },
      );
      const result = await fetch(api, {
        headers: {
          Authorization: `Bearer ${env.AHREFS_API_KEY}`,
          Accept: "application/json",
        },
        signal: AbortSignal.timeout(20000),
      });
      if (!result.ok)
        fail(
          `Ahrefs returned ${result.status}. Check API access or quota.`,
          502,
        );
      const data = await result.json();
      return json({ kind, target, data });
    }
    fail("Tool not found.", 404);
  }
  fail("Endpoint not found.", 404);
}

export default {
  async fetch(request, env, ctx) {
    try {
      const url = new URL(request.url);
      const base = appBase(url.pathname);
      if (base) {
        url.pathname = stripAppBase(url.pathname);
        request = new Request(url, request);
      }
      const response = await route(request, env, ctx, base ? WEBSITE_ORIGIN : undefined);
      return mountedResponse(response, base);
    } catch (error) {
      if (error.status) return json({ error: error.message }, error.status);
      // No request bodies, secrets or contact data are logged.
      console.error(
        "Request failed",
        new URL(request.url).pathname,
        error.name,
      );
      return json(
        {
          error:
            "The request could not be completed. Please retry. If the free daily quota is exhausted, it resets at midnight UTC.",
        },
        503,
      );
    }
  },
};
