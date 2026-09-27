// Portable local preview using the same workerd runtime and built frontend.
// Useful in containers where Wrangler's network-interface discovery is unavailable.
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { resolve, extname } from "node:path";
import { build } from "esbuild";
import { Miniflare, convertV4MiniflareOptions } from "miniflare";
import { seedStatements } from "./seed.mjs";
const script = (
  await build({
    entryPoints: ["worker/index.mjs"],
    bundle: true,
    write: false,
    format: "esm",
    platform: "browser",
  })
).outputFiles[0].text;
const mf = new Miniflare(
  convertV4MiniflareOptions({
    modules: true,
    script,
    compatibilityDate: "2026-09-26",
    d1Databases: ["DB"],
    d1Persist: ".wrangler/portable",
    cf: false,
  }),
);
const db = await mf.getD1Database("DB");
const schema = await readFile("migrations/0001_initial.sql", "utf8");
await db.batch(
  schema
    .split(";")
    .map((s) => s.trim())
    .filter(Boolean)
    .map((s) => db.prepare(s)),
);
if (!(await db.prepare("SELECT COUNT(*) AS total FROM sites").first()).total) {
  try {
    const data = JSON.parse(
      await readFile(
        process.argv.slice(2).find((arg) => !arg.startsWith("--")) ||
          "private/legacy.json",
        "utf8",
      ),
    );
    const { statements, counts } = seedStatements(data);
    for (let i = 0; i < statements.length; i += 40)
      await db.batch(statements.slice(i, i + 40).map((s) => db.prepare(s)));
    console.log("Loaded local preview:", JSON.stringify(counts));
  } catch (error) {
    if (error.code !== "ENOENT") throw error;
    console.log(
      "No local data snapshot; preview starts with an empty database.",
    );
  }
}
const root = resolve("dist");
const server = createServer(async (req, res) => {
  try {
    const url = new URL(req.url, "http://" + req.headers.host);
    if (url.pathname.startsWith("/api/")) {
      const chunks = [];
      for await (const c of req) chunks.push(c);
      const response = await mf.dispatchFetch(url.href, {
        method: req.method,
        headers: req.headers,
        body: ["GET", "HEAD"].includes(req.method)
          ? undefined
          : Buffer.concat(chunks),
      });
      res.writeHead(response.status, Object.fromEntries(response.headers));
      res.end(Buffer.from(await response.arrayBuffer()));
      return;
    }
    const path = resolve(root, "." + decodeURIComponent(url.pathname));
    if (!path.startsWith(root + "/") && path !== root) {
      res.writeHead(404);
      res.end();
      return;
    }
    let file = path;
    let content;
    try {
      content = await readFile(file);
    } catch {
      file = resolve(root, "index.html");
      content = await readFile(file);
    }
    const types = {
      ".html": "text/html",
      ".css": "text/css",
      ".js": "text/javascript",
      ".svg": "image/svg+xml",
      ".txt": "text/plain",
      ".png": "image/png",
    };
    res.writeHead(200, {
      "Content-Type": types[extname(file)] || "application/octet-stream",
      "X-Content-Type-Options": "nosniff",
    });
    res.end(content);
  } catch {
    res.writeHead(500);
    res.end("Preview request failed.");
  }
});
server.listen(
  process.argv.includes("--smoke") ? 8788 : 8787,
  "0.0.0.0",
  async () => {
    console.log("Local preview ready");
    if (process.argv.includes("--smoke")) {
      try {
        const base = "http://127.0.0.1:8788";
        const health = await (await fetch(base + "/api/health")).json();
        const stats = await (await fetch(base + "/api/stats")).json();
        const listing = await (
          await fetch(base + "/api/sites?limit=25")
        ).json();
        const privateStatus = (await fetch(base + "/api/admin/status")).status;
        const asset = await fetch(base + "/search");
        if (
          !health.ok ||
          stats.total !== listing.total ||
          listing.rows.length !== Math.min(25, stats.total) ||
          privateStatus !== 401 ||
          asset.status !== 200
        )
          throw new Error("HTTP smoke verification failed.");
        console.log(
          JSON.stringify({
            health: health.ok,
            listings: stats.total,
            first_page: listing.rows.length,
            private_status: privateStatus,
            spa_status: asset.status,
          }),
        );
      } catch (error) {
        console.error(error.message);
        process.exitCode = 1;
      } finally {
        server.close();
        await mf.dispose();
      }
    }
  },
);
process.on("SIGINT", async () => {
  server.close();
  await mf.dispose();
  process.exit(0);
});
