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

For subsequent code updates, run `npm ci && npm run check && npm run deploy`. Schema changes must use a new migration followed by `npm run db:remote` **before** deploying code that requires it. Keep the existing `wrangler.jsonc` database ID.

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

`npm run deploy:ci` publishes the Worker and built frontend without querying D1. Use it for code updates when the required schema is already applied. The existing production schema includes `0002_private_contact_fields.sql`; the automatic sheet detection update does not require a new migration. This lets code updates publish even when D1's daily query quota is exhausted. It does not restore database access: queries remain unavailable until the quota resets at 00:00 UTC (05:00 Pakistan time).

For a **first deployment or any schema-changing release**, apply migrations successfully before publishing code that depends on them: run `npm run db:remote`, or use `npm run deploy:ci:migrate` as the dashboard deploy command for that release. The latter stops deployment if migration fails. Migration credentials must allow **Account: D1: Edit** in addition to Worker deployment; Cloudflare's generated build token may need that permission. Limit access to the account that owns this Worker and database. Keep the token in Cloudflare; do not paste it into chat or commit it to Git.

Neither deploy command deletes records, imports a repository snapshot, or creates a default admin. For a fresh installation, run the setup procedure above to create the schema, migrate a current Streamlit backup and create the admin. Keep existing app links until the new site's records and admin access have been verified.

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

Opening a website while signed in as admin shows clickable private contacts above
the price and metrics. Numbers open WhatsApp when an international number can be
determined; a separate Call link remains available. Email addresses offer both
mailto and Gmail compose links. Facebook, LinkedIn and Telegram links are retained
from spreadsheet cells and hyperlinks, including literal Excel HYPERLINK formulas.
Pakistani `03xx` mobile numbers are converted to `92` for WhatsApp; ambiguous local
numbers require a country code instead of generating an incorrect chat link.

Imports match contacts to the domain on the same row. Website details also scan
retained private notes from every workbook containing the domain, without a 100-note
cutoff. Contacts are grouped by file and tab; the selected sheet is shown first.
Other workbook tabs are labeled with unconfirmed publisher ownership.
Shared supplier contacts are labeled separately from publisher contacts. Explicitly
named website notes are shown only for that domain. Public APIs and exports continue
to exclude all contact values. Original cells discarded by an older importer require
the original sheet to be uploaded again; the app cannot reconstruct missing data.

Facebook and LinkedIn use encoded metadata in the existing private contact notes
column. The API decodes it for private forms and details; full backups retain it.
This update needs no D1 migration. `npm test` covers contact links, sheet matching,
source isolation, edits, backup round trips and unauthenticated/public access.

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

## Private Contact Analyzer

After administrator sign-in, open **More tools → Contact Analyzer** (`/app/contact-analyzer` on the main website). Selecting an XLSX/CSV/TSV automatically scans all worksheets and displays every detected contact, including rows without a website. You can also paste copied Google Sheets cells or analyze private notes retained from previous imports. Analysis runs in the browser without a paid contact API. Review candidates and choose **Save contacts privately**; website assignment is optional. The normal **Import Excel / CSV** flow uses the same automatic detector and saves contacts with the import.

- Detects email/Gmail, Phone/Mobile/Contact Number columns, WhatsApp links, contact-page links, multiple email columns, rich text, hyperlink targets and cached Excel formula results. Unknown metric and price values are not guessed as phone numbers. Leading zeros are preserved when present in the source; zeros already lost in a numeric spreadsheet cell cannot be recovered reliably.
- Contact-only sheets with Name/Email/Phone/WhatsApp headers are supported. Email and phone totals include contacts without a website and count unique values, so sheet contacts do not misleadingly appear as zero detections.
- The contact preview and private CSV retain a separate entry for each source sheet, even when the same domain occurs in several tabs. A per-sheet summary includes worksheets with zero detections; saving still merges duplicate domains without losing contact values.
- Sheet-level supplier contacts remain separate from publisher contacts. Contacts without a clear website are saved as private source-sheet records and included in the contact preview/export. Manual website assignment is optional; they are never silently attached as publisher contacts. Repeated saves deduplicate identical source-sheet notes, and existing saved notes are reused.
- Clicking a website after sign-in shows its private publisher contact details and contacts found in its saved supplier/sheet notes. Public search and export endpoints do not include these details.
- Merge imports keep existing emails, phone numbers, notes, status and quoted prices. Contact detection checks syntax only; it does not establish ownership or email deliverability.
- Earlier importers may have discarded unrecognized cells. **Analyze saved notes** can recover only retained notes and review records; upload the original sheet to analyze discarded columns.

The analyzer requires migration `0002_private_contact_fields.sql`, which is already applied in production. For a fresh installation, apply it with `npm run db:remote` before publishing. It adds phone and contact-page columns without replacing existing records; private backups include them. Public search is cached for five minutes and filter/statistics summaries for fifteen minutes; admin requests bypass those caches to reflect edits. This reduces repeated reads but does not remove Cloudflare account limits.

## Optional Ahrefs

Only if you already have API access:

```sh
npx wrangler secret put AHREFS_API_KEY
```

The key is stored as a Worker secret. Live requests require admin sign-in and explicit action. Ahrefs has separate API quotas/plan requirements; no subscription is purchased by this app. You can copy a returned metric into Manage websites.

## Validation

`npm run check` builds the production frontend, runs real workerd/D1 integration tests and pure import/migration tests, then dry-runs the Worker deployment. Tests cover public/private field separation, unauthorized writes, cross-origin rejection, country/metric filters, pagination, repeated imports, deletion markers, manual pricing, private contacts, pipeline, inbox, backup version checks and logout revocation.

Remote deployment and real-account sign-in must still be checked after Cloudflare authorization. Local tests do not establish production CPU usage or remaining account quota.
