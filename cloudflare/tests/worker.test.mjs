import { before, after, test } from "node:test";
import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import { createHash, pbkdf2Sync } from "node:crypto";
import { build } from "esbuild";
import { Miniflare, convertV4MiniflareOptions } from "miniflare";
import { prepareSite } from "../shared/domain.mjs";
import { scanSheet } from "../shared/import.mjs";
import { sheetContactNote } from "../shared/contacts.mjs";
import { WEBSITE_ORIGIN } from "../worker/routing.mjs";
let mf, db, authCookie;
const hash = (s) => createHash("sha256").update(s).digest("hex");
const salt = "1234567890abcdef1234567890abcdef";
const verifier = pbkdf2Sync(
  "test-only-password-not-for-deployment",
  Buffer.from(salt, "hex"),
  600000,
  32,
  "sha256",
).toString("hex");
async function call(
  path,
  {
    method = "GET",
    data,
    auth = false,
    origin = "https://gp.test",
    ip = "192.0.2.5",
  } = {},
) {
  const response = await mf.dispatchFetch("https://gp.test" + path, {
    method,
    headers: {
      ...(data !== undefined
        ? { "Content-Type": "application/json", Origin: origin }
        : {}),
      ...(auth ? { Cookie: typeof auth === "string" ? auth : authCookie } : {}),
      "CF-Connecting-IP": ip,
    },
    body: data !== undefined ? JSON.stringify(data) : undefined,
  });
  const body = await response.json();
  return { response, body, status: response.status };
}
before(async () => {
  const out = await build({
    entryPoints: ["worker/index.mjs"],
    bundle: true,
    write: false,
    format: "esm",
    platform: "browser",
    target: "es2022",
  });
  mf = new Miniflare(
    convertV4MiniflareOptions({
      name: "test-worker",
      modules: true,
      script: out.outputFiles[0].text,
      compatibilityDate: "2026-09-26",
      d1Databases: ["DB"],
      serviceBindings: {
        ASSETS: (request) => {
          const path = new URL(request.url).pathname;
          if (path === "/assets/test.js")
            return new Response("export default 'asset';", { headers: { "Content-Type": "text/javascript" } });
          if (path === "/index.html")
            return new Response(null, { status: 302, headers: { Location: "/" } });
          return new Response('<!doctype html><link href="./assets/test.css" rel="stylesheet"><link href="/favicon.svg"><script type="module" src="./assets/test.js"></script><a href="https://example.com/">External</a><a href="#main">Skip</a>', {
            headers: { "Content-Type": "text/html", ETag: '"original"' },
          });
        },
      },
      cf: false,
    }),
  );
  db = await mf.getD1Database("DB", "test-worker");
  const sql = (await Promise.all((await readdir("migrations")).filter((f) => f.endsWith(".sql")).sort().map((f) => readFile("migrations/" + f, "utf8")))).join("\n");
  await db.batch(
    sql
      .split(";")
      .map((s) => s.trim())
      .filter(Boolean)
      .map((s) => db.prepare(s)),
  );
  await db
    .prepare("INSERT INTO auth_users VALUES(?,?,?,600000)")
    .bind("testadmin", salt, hash(verifier))
    .run();
  const rows = [
    { site: "unknown.example.com" },
    {
      site: "pak.example.com",
      country: "PK",
      dr: "50",
      traffic: "12K",
      general_price: "100",
      source_file: "supplier.xlsx",
      sheet_name: "Tech",
    },
    {
      site: "manual.example.com",
      country: "USA",
      dr: "80",
      general_price: "95",
      original_price: "80",
      selling_price: "95",
      manual_price: 1,
      source_file: "supplier.xlsx",
      sheet_name: "Tech",
    },
  ];
  for (const data of rows) {
    const r = prepareSite(data, { legacy: true }),
      cols = Object.keys(r);
    await db
      .prepare(
        `INSERT INTO sites(${cols.join(",")}) VALUES(${cols.map(() => "?")})`,
      )
      .bind(...cols.map((c) => r[c]))
      .run();
  }
  const login = await call("/api/auth/login", {
    method: "POST",
    data: { username: "testadmin", verifier },
  });
  assert.equal(login.status, 200);
  authCookie = login.response.headers.get("Set-Cookie").split(";")[0];
  assert.match(
    login.response.headers.get("Set-Cookie"),
    /HttpOnly; SameSite=Strict.*Secure/,
  );
});
after(async () => {
  await mf?.dispose();
});

test("mounted login uses the same username for its challenge and session when pasted with spaces", async () => {
  const challenge = await call(
    "/app/api/auth/challenge?username=%20testadmin%20",
  );
  assert.equal(challenge.status, 200);
  assert.equal(challenge.body.salt, salt);
  assert.equal(challenge.body.iterations, 600000);
  const result = await call("/app/api/auth/login", {
    method: "POST",
    data: { username: " testadmin ", verifier },
    origin: WEBSITE_ORIGIN,
    ip: "192.0.2.111",
  });
  assert.equal(result.status, 200);
  const sessionCookie = result.response.headers.get("Set-Cookie").split(";")[0];
  const me = await call("/app/api/auth/me", { auth: sessionCookie });
  assert.equal(me.body.user.username, "testadmin");
});

test("public search includes unknown metrics by default and excludes them only with explicit limits", async () => {
  const all = await call("/api/sites?fresh=1");
  assert.equal(all.status, 200);
  assert.equal(all.body.total, 3);
  assert.equal(all.body.rows[0].original_price, undefined);
  assert.equal(all.body.rows[0].markup_percent, undefined);
  const dr = await call("/api/sites?min_dr=45&fresh=1");
  assert.equal(dr.body.total, 2);
  const price = await call("/api/sites?max_price=100&fresh=1");
  assert.equal(price.body.total, 1);
  const pk = await call("/api/sites?country=Pakistan&page=99&limit=1&fresh=1");
  assert.equal(pk.body.total, 1);
  assert.equal(pk.body.page, 1);
  assert.equal(pk.body.rows[0].domain, "pak.example.com");
  const url = await call(
    "/api/sites?q=" +
      encodeURIComponent("https://www.pak.example.com/story?x=2") +
      "&fresh=1",
  );
  assert.equal(url.body.total, 1);
  const injected = await call(
    "/api/sites?q=" + encodeURIComponent("%' OR 1=1 --") + "&fresh=1",
  );
  assert.equal(injected.body.total, 0);
});
test("private routes and writes require a server-verified session and same-origin JSON", async () => {
  for (const p of [
    "/api/admin/sites",
    "/api/admin/resources/contacts",
    "/api/admin/resources/vault",
    "/api/admin/resources/messages",
    "/api/admin/backup?table=sites",
  ])
    assert.equal((await call(p)).status, 401);
  assert.equal(
    (
      await call("/api/admin/sites", {
        method: "POST",
        data: { site: "new.example.com" },
      })
    ).status,
    401,
  );
  assert.equal(
    (
      await call("/api/admin/sites", {
        method: "POST",
        data: { site: "new.example.com" },
        auth: true,
        origin: "https://evil.example",
      })
    ).status,
    403,
  );
  assert.equal(
    (
      await call("/api/admin/sites", {
        method: "POST",
        data: { site: "javascript:alert(1)" },
        auth: true,
      })
    ).status,
    400,
  );
});
test("repeated imports are idempotent and deliberate deletions survive re-import", async () => {
  const row = {
    site: "imported.example.com",
    country: "UK",
    general_price: "100",
    source_file: "import.csv",
    sheet_name: "CSV",
  };
  const first = await call("/api/admin/import", {
    method: "POST",
    data: { rows: [row] },
    auth: true,
  });
  assert.equal(first.body.inserted, 1);
  assert.equal(
    (
      await call("/api/admin/import", {
        method: "POST",
        data: { rows: [row] },
        auth: true,
      })
    ).body.inserted,
    0,
  );
  const found = await call("/api/admin/sites?q=imported.example.com", {
    auth: true,
  });
  const record = found.body.rows[0];
  assert.equal(record.general_price, "120.00");
  assert.equal(record.country, "United Kingdom");
  assert.equal(
    (
      await call("/api/admin/sites/" + record.id, {
        method: "DELETE",
        data: {},
        auth: true,
      })
    ).status,
    200,
  );
  assert.equal(
    (
      await call("/api/admin/import", {
        method: "POST",
        data: { rows: [row] },
        auth: true,
      })
    ).body.inserted,
    0,
  );
});
test("sheet markup is repeatable, keeps manual overrides and hides supplier costs publicly", async () => {
  for (let i = 0; i < 2; i++)
    assert.equal(
      (
        await call("/api/admin/pricing", {
          method: "POST",
          auth: true,
          data: {
            source_file: "supplier.xlsx",
            sheet_name: "Tech",
            markup_percent: 30,
          },
        })
      ).status,
      200,
    );
  const result = await call("/api/admin/sites?source_file=supplier.xlsx", {
    auth: true,
  });
  assert.equal(
    result.body.rows.find((r) => r.domain === "pak.example.com").general_price,
    "130.00",
  );
  assert.equal(
    result.body.rows.find((r) => r.domain === "manual.example.com")
      .general_price,
    "95",
  );
  const out = await call("/api/export");
  assert.ok(out.body.rows.length >= 3);
  assert.ok(
    out.body.rows.every(
      (r) => r.original_price === undefined && r.manual_price === undefined,
    ),
  );
});
test("private contacts, pipeline, inbox and media validation use the real D1 schema", async () => {
  const c = await call("/api/admin/resources/contacts", {
    method: "POST",
    auth: true,
    data: {
      domain: "https://www.pak.example.com",
      admin_name: "Private contact",
      email: "private@example.com",
      notes: "Private test note",
    },
  });
  assert.equal(c.status, 200);
  const result = await call("/api/admin/resources/contacts", { auth: true });
  assert.equal(result.body.rows[0].domain, "pak.example.com");
  assert.equal(result.body.rows[0].email, "private@example.com");
  assert.equal(
    (
      await call("/api/admin/resources/contacts", {
        method: "POST",
        auth: true,
        data: { domain: "pak.example.com", notes: "" },
      })
    ).status,
    200,
  );
  assert.equal(
    (await call("/api/admin/resources/contacts", { auth: true })).body.rows[0]
      .notes,
    "",
  );
  const note = {
    source_file: "supplier.xlsx",
    sheet_name: "Tech",
    field_name: "Contact",
    field_value: "reseller@example.com",
  };
  for (let i = 0; i < 2; i++)
    assert.equal(
      (
        await call("/api/admin/resource-batch", {
          method: "POST",
          auth: true,
          data: { resource: "resellers", rows: [note] },
        })
      ).status,
      200,
    );
  assert.equal(
    (await call("/api/admin/resources/resellers", { auth: true })).body.total,
    1,
  );
  assert.equal(
    (
      await call("/api/admin/resources/pipeline", {
        method: "POST",
        auth: true,
        data: {
          site: "pak.example.com",
          status: "Contacted",
          next_follow_up: "2026-10-01",
        },
      })
    ).status,
    200,
  );
  const msg = await call("/api/contact", {
    method: "POST",
    data: {
      full_name: "Test visitor",
      message: "Test contact message",
      email: "visitor@example.com",
    },
  });
  assert.equal(msg.status, 201);
  const inbox = await call("/api/admin/resources/messages", { auth: true });
  assert.equal(inbox.body.total, 1);
  assert.equal(
    (
      await call("/api/admin/media", {
        method: "POST",
        auth: true,
        data: { key: "x", content_type: "image/svg+xml", data: "PHN2Zz4=" },
      })
    ).status,
    400,
  );
  assert.equal(
    (
      await call("/api/admin/metrics", {
        method: "POST",
        auth: true,
        data: { site: "example.com" },
      })
    ).status,
    503,
  );
});
test("backups reject unknown tables and restore records without public exposure", async () => {
  const state = await call("/api/admin/status", { auth: true });
  assert.equal(
    (await call("/api/admin/backup?table=auth_users", { auth: true })).status,
    400,
  );
  assert.equal(
    (await call("/api/admin/backup?table=sites&version=old", { auth: true }))
      .status,
    409,
  );
  const backup = await call(
    "/api/admin/backup?table=contacts&version=" + state.body.version,
    { auth: true },
  );
  assert.equal(backup.status, 200);
  const merge = await call("/api/admin/restore", {
    method: "POST",
    auth: true,
    data: {
      table: "contacts",
      rows: backup.body.rows,
      confirm: "MERGE BACKUP",
    },
  });
  assert.equal(merge.status, 200);
  assert.equal(
    (await call("/api/admin/resources/contacts", { auth: true })).body.total,
    1,
  );
  assert.equal(
    (
      await call("/api/admin/restore", {
        method: "POST",
        auth: true,
        data: { table: "auth_users", rows: [{}], confirm: "MERGE BACKUP" },
      })
    ).status,
    400,
  );
});
test("private contact analyzer merges phones and emails, preserves manual fields and never exposes contacts publicly", async () => {
  const route = "/api/admin/contacts/merge";
  const sample = { domain: "manual.example.com", email: "sheet-private@example.com", phone: "+12025550143", contact_url: "https://manual.example.com/contact", notes: "Sheet: test.xlsx / Publishers / row 2" };
  assert.equal((await call(route, { method: "POST", data: { rows: [sample] } })).status, 401);
  assert.equal((await call("/api/admin/contacts/detail?domain=manual.example.com")).status, 401);
  assert.equal((await call("/api/admin/contacts/sources")).status, 401);
  assert.equal((await call(route, { method: "POST", auth: true, origin: "https://foreign.example", data: { rows: [sample] } })).status, 403);
  await call("/api/admin/resources/contacts", { method: "PUT", auth: true, data: { domain: sample.domain, email: "kept-private@example.com", status: "Replied", notes: "Manual note", quoted_price: "80" } });
  for (let i = 0; i < 2; i++) assert.equal((await call(route, { method: "POST", auth: true, data: { rows: [sample, sample] } })).status, 200);
  await call("/api/admin/resource-batch", { method: "POST", auth: true, data: { resource: "resellers", rows: [{ source_file: "supplier.xlsx", sheet_name: "Tech", field_name: "Phone", field_value: "+44 7700 900123; supplier-private@gmail.com" }] } });
  const detail = await call("/app/api/admin/contacts/detail?domain=manual.example.com", { auth: true });
  assert.equal(detail.status, 200);
  assert.equal(detail.response.headers.get("Cache-Control"), "no-store");
  assert.equal(detail.body.contact.email, "kept-private@example.com; sheet-private@example.com");
  assert.equal(detail.body.contact.phone, sample.phone);
  assert.equal(detail.body.contact.status, "Replied");
  assert.equal(detail.body.contact.quoted_price, "80");
  assert.equal(detail.body.contact.notes, "Manual note\n" + sample.notes);
  const supplier = detail.body.suppliers.find((r) => r.email === "supplier-private@gmail.com");
  assert.equal(supplier.phone, "+447700900123");
  for (const path of ["/api/sites?q=manual", "/api/export?q=manual", "/api/stats", "/api/options"]) {
    const pub = await call(path);
    assert.equal(pub.status, 200);
    assert.doesNotMatch(JSON.stringify(pub.body), /sheet-private|kept-private|supplier-private|12025550143|447700900123/);
  }
  const backup = await call("/api/admin/backup?table=contacts", { auth: true });
  assert.equal(backup.body.rows.find((r) => r.domain === sample.domain).phone, sample.phone);
  assert.equal((await call(route, { method: "POST", auth: true, data: { rows: [{ domain: "not a domain", phone: "123" }] } })).status, 400);
  assert.equal((await call("/api/admin/contacts/sources?table=auth_users", { auth: true })).status, 400);
});

test("automatically detected sheet-only contacts save privately without a domain and repeated saves deduplicate", async () => {
  const report = scanSheet([
    ["Name", "Email", "Mobile"],
    ["Sheet supplier", "auto-private@example.com", "0300-1234567"],
  ], "contact-only.csv", "Team");
  const notes = report.unassigned.map(sheetContactNote);
  assert.equal(notes.length, 1);
  const request = { method: "POST", auth: true, data: { resource: "resellers", rows: notes } };
  assert.equal((await call("/api/admin/resource-batch", { ...request, auth: false })).status, 401);
  for (let i = 0; i < 2; i++) assert.equal((await call("/api/admin/resource-batch", request)).status, 200);
  const count = await db.prepare("SELECT COUNT(*) AS n FROM reseller_private WHERE source_file='contact-only.csv'").first();
  assert.equal(count.n, 1);
  const stored = await call("/api/admin/contacts/sources?table=reseller_private", { auth: true });
  assert.match(stored.body.rows.find((r) => r.source_file === "contact-only.csv").field_value, /auto-private@example.com/);
  const publisherCount = await db.prepare("SELECT COUNT(*) AS n FROM contacts WHERE email LIKE '%auto-private%'").first();
  assert.equal(publisherCount.n, 0);
  for (const path of ["/api/sites", "/api/export", "/api/stats", "/api/options"])
    assert.doesNotMatch(JSON.stringify((await call(path)).body), /auto-private|03001234567/);
});

test("sign-out revokes the existing server session", async () => {
  assert.equal(
    (await call("/api/auth/me", { auth: true })).body.user.username,
    "testadmin",
  );
  assert.equal(
    (await call("/api/auth/logout", { method: "POST", auth: true, data: {} }))
      .status,
    200,
  );
  assert.equal((await call("/api/admin/status", { auth: true })).status, 401);
});

test("website mount serves HTML, assets and API queries through the same origin", async () => {
  for (const path of ["/app", "/app/", "/app/search", "/app/search/"]) {
    const response = await mf.dispatchFetch("https://gp.test" + path);
    assert.equal(response.status, 200);
    assert.equal(response.headers.get("Cache-Control"), "no-cache");
    assert.equal(response.headers.get("ETag"), null);
    const html = await response.text();
    assert.match(html, /src="\/app\/assets\/test.js"/);
    assert.match(html, /href="\/app\/assets\/test.css"/);
    assert.match(html, /href="\/app\/favicon.svg"/);
    assert.match(html, /href="https:\/\/example.com\/"/);
    assert.match(html, /href="#main"/);
  }
  const asset = await mf.dispatchFetch("https://gp.test/app/assets/test.js");
  assert.match(await asset.text(), /export default 'asset'/);
  const redirect = await mf.dispatchFetch("https://gp.test/app/index.html", { redirect: "manual" });
  assert.equal(redirect.headers.get("Location"), "/app/");
  assert.equal((await call("/app/api/health")).body.ok, true);
  const filtered = await call("/app/api/sites?q=pak.example.com&fresh=1");
  assert.equal(filtered.body.total, 1);
  assert.equal(filtered.body.rows[0].domain, "pak.example.com");
  assert.equal(filtered.response.headers.get("Cache-Control"), "no-store");
  assert.equal((await call("/app/api/admin/status")).status, 401);
  const root = await mf.dispatchFetch("https://gp.test/search");
  assert.match(await root.text(), /src="\.\/assets\/test.js"/);
});

test("proxy login cookies authenticate and logout while foreign origins stay rejected", async () => {
  const credentials = { username: "testadmin", verifier };
  const login = await call("/app/api/auth/login", {
    method: "POST", data: credentials, origin: WEBSITE_ORIGIN, ip: "192.0.2.20",
  });
  assert.equal(login.status, 200);
  const setCookie = login.response.headers.get("Set-Cookie");
  assert.match(setCookie, /HttpOnly; SameSite=Strict.*Secure/);
  assert.doesNotMatch(setCookie, /Domain=/i);
  const auth = setCookie.split(";")[0];
  assert.equal((await call("/app/api/auth/me", { auth })).body.user.username, "testadmin");
  assert.equal((await call("/app/api/admin/status", { auth })).status, 200);
  for (const origin of ["https://evil.example", WEBSITE_ORIGIN + ".evil.example", "null"]) {
    assert.equal((await call("/app/api/auth/logout", { method: "POST", data: {}, auth, origin })).status, 403);
  }
  assert.equal((await call("/api/auth/login", { method: "POST", data: credentials, origin: WEBSITE_ORIGIN })).status, 403);
  const forged = await mf.dispatchFetch("https://gp.test/app/api/auth/logout", {
    method: "POST",
    headers: { Origin: "https://evil.example", "Content-Type": "application/json", "X-Forwarded-Host": "gp-site-finder-pro-landing.vercel.app", Cookie: auth },
    body: "{}",
  });
  assert.equal(forged.status, 403);
  const noOrigin = await mf.dispatchFetch("https://gp.test/app/api/auth/logout", {
    method: "POST", headers: { "Content-Type": "application/json", Cookie: auth }, body: "{}",
  });
  assert.equal(noOrigin.status, 403);
  const wrongType = await mf.dispatchFetch("https://gp.test/app/api/auth/logout", {
    method: "POST", headers: { Origin: WEBSITE_ORIGIN, "Content-Type": "text/plain", Cookie: auth }, body: "{}",
  });
  assert.equal(wrongType.status, 415);
  assert.equal((await call("/app/api/auth/logout", { method: "POST", data: {}, auth, origin: WEBSITE_ORIGIN })).status, 200);
  assert.equal((await call("/app/api/admin/status", { auth })).status, 401);
});
