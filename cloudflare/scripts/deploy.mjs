// Run on the account owner's computer. Uses only Workers + D1 (no R2 or paid plan).
import { spawnSync } from "node:child_process";
import { existsSync, readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { createHash } from "node:crypto";
import { resolve } from "node:path";
const isWindows = process.platform === "win32",
  npx = isWindows ? "npx.cmd" : "npx",
  npm = isWindows ? "npm.cmd" : "npm";
function run(program, args, { capture = false } = {}) {
  const r = spawnSync(program, args, {
    stdio: capture ? ["inherit", "pipe", "inherit"] : "inherit",
    encoding: "utf8",
    maxBuffer: 40 * 1024 * 1024,
    env: { ...process.env, WRANGLER_SEND_METRICS: "false" },
  });
  if (r.status !== 0)
    throw new Error(
      `${program} ${args[0]} failed. Fix the reported issue and rerun; existing data is kept.`,
    );
  return r.stdout || "";
}
function wrangler(args, options) {
  return run(npx, ["wrangler", ...args], options);
}
function query(sql) {
  const raw = wrangler(
    ["d1", "execute", "DB", "--remote", "--command", sql, "--json"],
    { capture: true },
  );
  return JSON.parse(raw)[0].results;
}
try {
  const input = process.argv[2];
  if (!input)
    throw new Error(
      "Pass a fresh Streamlit backup ZIP or the Streamlit project directory: npm run setup -- /path/to/backup.zip",
    );
  if (!existsSync(input)) throw new Error("The backup path does not exist.");
  run(npm, ["run", "check"]);
  console.log(
    "Sign in to the Cloudflare account that will own the free Worker and database.",
  );
  wrangler(["login"]);
  wrangler(["whoami"]);
  const config = JSON.parse(readFileSync("wrangler.jsonc", "utf8"));
  if (
    config.d1_databases[0].database_id ===
    "00000000-0000-0000-0000-000000000000"
  ) {
    const result = wrangler(
      ["d1", "create", config.d1_databases[0].database_name],
      { capture: true },
    );
    const id = result.match(
      /(?:database_id|databaseId)["\s:=]+([a-f0-9-]{36})/i,
    )?.[1];
    if (!id)
      throw new Error(
        "Database creation returned no ID. Inspect it in Cloudflare and put its ID in wrangler.jsonc before retrying.",
      );
    config.d1_databases[0].database_id = id;
    writeFileSync("wrangler.jsonc", JSON.stringify(config, null, 2) + "\n");
  }
  wrangler(["d1", "migrations", "apply", "DB", "--remote"]);
  mkdirSync("private", { recursive: true });
  const python = process.env.GP_PYTHON || (isWindows ? "python" : "python3");
  run(python, [
    "scripts/export_legacy.py",
    resolve(input),
    "private/legacy.json",
  ]);
  run(process.execPath, [
    "scripts/seed.mjs",
    "private/legacy.json",
    "private/seed.sql",
  ]);
  const digest = createHash("sha256")
    .update(readFileSync("private/legacy.json"))
    .digest("hex");
  const marker = query("SELECT value FROM app_meta WHERE key='initial_seed'")[0]
    ?.value;
  if (marker && marker !== digest)
    throw new Error(
      "This database was initialized from a different backup. Use the admin backup/restore tool or a new D1 database.",
    );
  if (!marker) {
    console.log("Migrating records and photos. This can take a few minutes.");
    wrangler(
      [
        "d1",
        "execute",
        "DB",
        "--remote",
        "--file",
        "private/seed.sql",
        "--yes",
      ],
      { capture: true },
    );
    const original =
      JSON.parse(readFileSync("private/legacy.json", "utf8")).tables.sites
        ?.length || 0;
    const count = query(
      "SELECT (SELECT COUNT(*) FROM sites)+(SELECT COUNT(*) FROM import_review) AS total",
    )[0].total;
    if (count !== original)
      throw new Error(
        "Record counts do not match; deployment stopped for review.",
      );
    query(`INSERT INTO app_meta(key,value) VALUES('initial_seed','${digest}')`);
    console.log(`Verified ${count.toLocaleString()} migrated source records.`);
  }
  if (!query("SELECT COUNT(*) AS count FROM auth_users")[0].count) {
    run(python, ["scripts/admin_user.py", "private/admin.sql"]);
    wrangler(
      [
        "d1",
        "execute",
        "DB",
        "--remote",
        "--file",
        "private/admin.sql",
        "--yes",
      ],
      { capture: true },
    );
  }
  wrangler(["deploy"]);
  console.log(
    "Deployment complete. Open the printed workers.dev URL, verify search and admin sign-in, then update the landing-page app links.",
  );
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
