# Always-on hosting for GP Site Finder Pro

Status: prepared and locally verified; no paid service has been provisioned.

Streamlit Community Cloud hibernates an app after 12 hours without traffic.
The prepared Render deployment uses paid compute, which does not hibernate
because of inactivity. It still has normal restarts for maintenance and deploys.
It does not depend on automated visits or scheduled pings.

## Proposed service

| Setting | Value |
| --- | --- |
| Workspace | Hobby ($0 workspace fee) |
| Compute | `0.5c-512mb` — $7/month |
| Storage | 1 GB persistent disk — $0.25/month |
| Base total | $7.25/month, before taxes or usage overages |
| Region | Singapore |
| Instances | One |
| Automatic deploys | Off |

Prices checked against Render's official documentation on 27 September 2026.
The dashboard's quote must be reviewed before activating billing. A larger
instance might be needed for heavy imports or many concurrent users; no
automatic scaling or instance upgrade is configured.

## Deployment and data migration

1. Obtain approval for the recurring hosting cost and access to the chosen Render
   account. Create a Blueprint from this branch using `render.yaml`.
2. Before changing the public links, export a fresh full backup from the existing
   Streamlit app's admin tools. Pause admin edits during the final export and
   restore. Keep this backup private; it includes contacts and authentication
   settings. The repository's seed database is **not** a live production backup.
3. Review the compute, disk and workspace charges. Set any existing
   `SUPABASE_URL`, `SUPABASE_SECRET_KEY` and `AHREFS_API_KEY` in Render's private
   environment settings, if those integrations are currently used. Never put
   these values in Git or chat. Approve transferring private backup data and
   secrets to the new host before that transfer.
4. Deploy. The startup command initializes `/var/data/gp-site-finder` once, then
   starts Streamlit on Render's assigned port. The disk is initialized at runtime,
   when it is available, not during the build or pre-deploy phase.
5. Use the app's existing admin restore tool to restore the latest backup on the
   new instance. Verify publisher counts, saved sites, contacts, team/profile
   images and any active cloud sync against the old app. Do not import both a
   stale repository database and current production data into the cloud service.
6. Restart the new service and re-check the restored data. Check the service's
   memory under representative imports and several simultaneous sessions before
   directing normal traffic to it. The health endpoint is `/_stcore/health`;
   a successful health response alone does not validate database contents.
7. Update the Vercel landing website's app links to the verified new URL. Keep the
   original Streamlit app available until the migration has been confirmed.

The new host will provide a new URL. A `streamlit.app` URL cannot be repointed
to a different hosting provider. The landing website remains on Vercel.

## Storage behavior

`GP_STORAGE_DIR` changes the root used for all existing databases, JSON settings,
profile/team images and backup/restore paths. Without it, the app uses its
existing source-directory layout. `prepare_storage.py` seeds missing files on
the first start only and preserves already-restored files. Later restarts keep
edits and intentional deletions. Do not remove the initialization marker.

A disk is mounted on a single instance, so deploys can briefly interrupt service.
Continue taking independent backups; a persistent disk is not a substitute for
a verified backup. Before switching back after new writes, export the current
data first to avoid losing those writes.

## Verification

```sh
python -m pip install -r requirements-hosting.txt pytest
python -m pytest -q tests
```

Tests cover search/save/navigation, persistent storage initialization, keeping
restored data, and retaining saved sites in a new app session after startup.
Local tests do not establish production capacity or complete a hosting migration.

## Official references

- https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app
- https://render.com/pricing
- https://render.com/articles/how-much-does-cloud-application-hosting-cost-for-small-businesses
- https://render.com/docs/free
- https://render.com/docs/disks
- https://render.com/docs/blueprint-spec
