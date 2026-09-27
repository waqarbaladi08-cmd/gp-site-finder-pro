# GP Site Finder Pro on Cloudflare

A React frontend, Cloudflare Worker API and persistent D1 database. This replaces the Streamlit runtime so opening the app does not depend on a sleeping Python server. The existing Streamlit app and Vercel landing page are unchanged.

Uses the **Workers Free** and **D1 Free** plans only. No card, R2, paid database, keep-alive bot or scheduled ping is required. Free plans still have usage limits: Workers 100,000 dynamic requests/day and 10 ms CPU/request; D1 5 million rows read/day, 100,000 rows written/day and 500 MB per database. Static assets are served separately. Check the current [Workers pricing](https://developers.cloudflare.com/workers/platform/pricing/) and [D1 limits](https://developers.cloudflare.com/d1/platform/limits/) before launch. Quota exhaustion can cause errors until reset; this is separate from app sleeping.

## Deploy from a fresh backup

Requires Node.js 22.12+ (Node 24 tested), Python 3.10+, a Cloudflare account and the latest `main` branch of this repository.

1. In the current Streamlit app, sign in as admin and download **Backup & Restore → backup ZIP**. Keep it private. A repository snapshot can be used for a preview, but it may not contain recent live changes or contacts.
2. Open a terminal in `cloudflare/` and run:

   ```sh
   npm ci
   npm run setup -- /absolute/path/to/streamlit-backup.zip
   ```

   Windows accepts a quoted Windows file path. If your Python command differs, set `GP_PYTHON` to its executable.

3. Complete the Cloudflare login in your own browser when Wrangler opens it. Choose the free plan if prompted. The script does not upgrade billing or register a paid domain.
4. Enter a **new admin username and password** in the terminal prompt. There is no default password. The old repository-stored password hash is deliberately not reused.
5. Open the printed `workers.dev` URL and check public search, a private contact, saved sites, an import, an export and a complete backup. Confirm the record totals and your latest live changes before switching the landing-page app links.

The setup script runs tests, creates/binds D1, applies the schema, migrates records/photos, verifies the source count and deploys. `wrangler.jsonc` receives the real database ID. Authentication, private SQL and backup files stay out of Git. Setup is resumable with the same backup. A different backup after initialization requires explicit review rather than silently replacing live data.

For subsequent code updates, run `npm ci && npm run check && npm run deploy`. Schema changes must use a new migration followed by `npm run db:remote`. Keep the existing `wrangler.jsonc` database ID.

## Cloudflare dashboard / GitHub deployment

The owner-created D1 database is `gp-site-finder-pro`, ID `a79b65f4-49c6-462b-b6f0-a478b4230465`. Its `DB` binding is already configured in `wrangler.jsonc`. The database ID is an identifier, not an API credential.

Use these settings when connecting this repository to Workers Builds:

| Setting | Value |
| --- | --- |
| Project / Worker name | `gp-site-finder-pro` |
| Production branch | `main` |
| Root directory | `cloudflare` |
| Build command | `npm run build` |
| Deploy command | `npm run deploy:ci` |
| Node version | `24` (set by `.nvmrc`) |

The deploy command applies pending schema migrations before publishing. It does not delete records, import a repository snapshot, or create a default admin. The build credential must allow D1 writes as well as Worker deployment. Cloudflare's automatically generated Workers Builds token does not include D1 permission by default, so add **Account: D1: Edit** to the build token in **My Profile > API Tokens**, or select an owner-created token with that permission before running this deploy command. Limit access to the account that owns this Worker and database. Keep the token in Cloudflare; do not paste it into chat or commit it to Git.

This creates the application and empty database tables. A fresh Streamlit backup and a new admin account are still required before cutover. Run the setup procedure above to migrate the fresh backup and create the admin. Keep existing app links until the new site's records and admin access have been verified.

## Local preview

```sh
npm ci
python3 scripts/export_legacy.py ../ private/legacy.json
node scripts/seed.mjs private/legacy.json private/seed.sql
npm run db:local
npx wrangler d1 execute DB --local --file private/seed.sql > private/local-import.log
npm run build
npm run preview
```

An alternative preview for restricted containers is `npm run preview:portable`. It runs the same Worker in workerd, automatically loads `private/legacy.json` into a separate local D1 store, and serves the built frontend at `http://127.0.0.1:8787`. This is only a development server.

To create a local admin, run `python3 scripts/admin_user.py private/admin.sql` and apply it using `wrangler d1 execute DB --local --file private/admin.sql`. The portable preview has a separate database; admin integration tests use disposable accounts rather than production credentials.

## Feature mapping

| Streamlit tool                              | Cloudflare workspace                                                                                         |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| Dashboard, Search, Statistics               | Live D1 counts, indexed filters, pagination and publisher detail dialog                                      |
| Favorites                                   | Browser-persistent shortlist; existing saved records can be loaded after admin sign-in                       |
| Outreach / Client Outreach                  | Editable email, follow-ups, LinkedIn and WhatsApp drafts; copy/download only                                 |
| Add / Edit / Delete Site                    | Manage websites, with deletion records preventing accidental reimport                                        |
| Excel Import / Sheet Scanner                | XLSX/CSV multi-sheet preview, header detection, country mapping, private contact extraction and scan reports |
| Export Results                              | Public-field CSV/XLSX, including filtered search results                                                     |
| Private Contacts / Reseller Details / Vault | Authenticated records, search, edit and delete                                                               |
| Outreach Pipeline                           | Status, contact details, dates and notes                                                                     |
| Price Manager                               | Supplier cost, sheet markup and preserved manual overrides                                                   |
| Duplicate Finder                            | Review repeated domains and open all supplier listings before deleting                                       |
| Cloud Sync                                  | Direct D1 writes; no separate or destructive Supabase synchronization                                        |
| Team / Profile / Contact Us                 | Public business pages, private inbox and authenticated editing                                               |
| Backup & Restore                            | Version-checked full JSON backup and explicitly confirmed merge restore                                      |
| Real Metrics                                | Optional server-side Ahrefs access; recorded metrics remain usable without a key                             |

Old `?page=Search Websites` and other Streamlit page aliases resolve to the corresponding new page. Old Streamlit URLs are not automatically redirected; update landing links only after cutover verification. XLS files must first be saved as XLSX. New Cloudflare backups are JSON; the migration CLI reads old Streamlit ZIP backups.

## Data integrity and privacy

- Source databases are read without modification, including committed SQLite WAL data when reading a directory. All 13,639 records in the available snapshot are retained: **13,416 valid website listings** and **223 non-website / incomplete rows in private Import review**. No source record is discarded.
- Existing IDs, source/sheet names, original prices, selling prices, manual flags, contacts, pipeline records, team profiles, deletion markers and photos are preserved where supplied. Existing calculated selling prices win; legacy initialization markup is applied once.
- Unknown countries and metrics remain unknown. Niche labels are inferred from existing type/sheet/domain rules and are labeled as estimates.
- Search/export endpoints explicitly select public columns. Admin authorization is checked on the server for every private route. Password hashes, sessions and API keys never appear in frontend assets or backups.
- Login uses salted PBKDF2-SHA256 with 600,000 iterations in the browser; the server stores an additional SHA256 digest of the derived value. This keeps expensive password stretching outside the free Worker CPU budget. Login attempts are rate limited; sessions are random, hashed in D1, expire after eight hours, and use HttpOnly / Secure / SameSite cookies. Writes require same-origin JSON.
- Imports are batched, repeated source listings are skipped, and SQL is parameterized. CSV formulas are neutralized. Imported spreadsheet contact columns and notes are stored privately.
- Initial SQL photo migration uses short statements to respect D1's 100 KB statement limit. New photo uploads are limited to 500 KB; existing migration photos support 1 MB each.
- Free-tier quotas are not bypassed. Caching, cursor exports, limited import batches and a small index set reduce database/CPU use. Check the Cloudflare usage dashboard before unusually large imports.

## Optional Ahrefs

Only if you already have API access:

```sh
npx wrangler secret put AHREFS_API_KEY
```

The key is stored as a Worker secret. Live requests require admin sign-in and explicit action. Ahrefs has separate API quotas/plan requirements; no subscription is purchased by this app. You can copy a returned metric into Manage websites.

## Validation

`npm run check` builds the production frontend, runs real workerd/D1 integration tests and pure import/migration tests, then dry-runs the Worker deployment. Tests cover public/private field separation, unauthorized writes, cross-origin rejection, country/metric filters, pagination, repeated imports, deletion markers, manual pricing, private contacts, pipeline, inbox, backup version checks and logout revocation.

Remote deployment and real-account sign-in must still be checked after Cloudflare authorization. Local tests do not establish production CPU usage or remaining account quota.
