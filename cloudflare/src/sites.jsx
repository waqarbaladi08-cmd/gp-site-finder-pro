import React, { useState } from "react";
import {
  Search,
  Bookmark,
  ArrowUpRight,
  Download,
  SlidersHorizontal,
  Mail,
  Pencil,
  Trash2,
  Globe2,
  Plus,
} from "lucide-react";
import { PUBLIC_FIELDS, toCSV, safeWebURL } from "../shared/domain.mjs";
import { ContactDetails } from "./contact-analyzer.jsx";
import {
  useApp,
  useData,
  useTask,
  api,
  Loading,
  ErrorBox,
  Empty,
  Heading,
  Field,
  Fields,
  Notice,
  Modal,
  Pager,
  label,
  download,
} from "./lib.jsx";

export function SiteTable({ rows, onEdit, onDelete }) {
  const { saved, toggleSaved, go, user } = useApp(),
    [detail, setDetail] = useState(null);
  return (
    <>
      <div className="table-wrap">
        <table className="sites-table">
          <thead>
            <tr>
              <th aria-label="Save" />
              <th>Website</th>
              <th>Niche / country</th>
              <th>DR</th>
              <th>Traffic</th>
              <th>Listed price</th>
              <th>Link type</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id}>
                <td>
                  <button
                    className={
                      "icon bookmark " + (saved.includes(r.id) ? "saved" : "")
                    }
                    aria-label={`${saved.includes(r.id) ? "Unsave" : "Save"} ${r.domain}`}
                    onClick={() => toggleSaved(r.id)}
                  >
                    <Bookmark
                      size={18}
                      fill={saved.includes(r.id) ? "currentColor" : "none"}
                    />
                  </button>
                </td>
                <td>
                  <button className="site-link" onClick={() => setDetail(r)}>
                    {r.domain || r.site}
                  </button>
                  <small>{r.type || r.sheet_name || "Publisher"}</small>
                </td>
                <td>
                  <span className="tag">{r.niche}</span>
                  <small>{r.country || "Country not specified"}</small>
                </td>
                <td>
                  <span className={r.dr ? "metric-badge" : ""}>
                    {r.dr || "—"}
                  </span>
                </td>
                <td>{r.traffic || "—"}</td>
                <td className="price">{r.general_price || "On request"}</td>
                <td>{r.link_type || "—"}</td>
                <td>
                  <div className="row-actions">
                    <button
                      className="icon"
                      aria-label={`Outreach for ${r.domain}`}
                      onClick={() => go("outreach", { site: r.domain })}
                    >
                      <Mail size={17} />
                    </button>
                    <a
                      className="icon"
                      href={safeWebURL(r.site)}
                      target="_blank"
                      rel="noopener noreferrer"
                      aria-label={`Visit ${r.domain}`}
                    >
                      <ArrowUpRight size={17} />
                    </a>
                    {onEdit && (
                      <button
                        className="icon"
                        aria-label={`Edit ${r.domain}`}
                        onClick={() => onEdit(r)}
                      >
                        <Pencil size={16} />
                      </button>
                    )}
                    {onDelete && (
                      <button
                        className="icon danger"
                        aria-label={`Delete ${r.domain}`}
                        onClick={() => onDelete(r)}
                      >
                        <Trash2 size={16} />
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {detail && (
        <Modal
          title={detail.domain || detail.site}
          onClose={() => setDetail(null)}
        >
          {user && <ContactDetails key={detail.domain} domain={detail.domain} />}
          <dl className="detail-grid">
            {PUBLIC_FIELDS.filter(
              (k) => !["id", "site", "domain", "created_at"].includes(k),
            ).map((k) => (
              <div key={k}>
                <dt>{label(k)}</dt>
                <dd>{detail[k] || "Not recorded"}</dd>
              </div>
            ))}
          </dl>
          <div className="form-actions">
            <button
              className="primary"
              onClick={() => go("outreach", { site: detail.domain })}
            >
              Create outreach
            </button>
            <button onClick={() => toggleSaved(detail.id)}>
              {saved.includes(detail.id) ? "Remove from saved" : "Save website"}
            </button>
          </div>
        </Modal>
      )}
    </>
  );
}
export async function exportSites(filters, format = "csv") {
  const rows = [];
  let after = 0;
  do {
    const params = new URLSearchParams({ ...filters, after });
    const r = await api("/api/export?" + params);
    rows.push(...r.rows);
    after = r.next;
  } while (after);
  if (format === "xlsx") {
    const { default: ExcelJS } = await import("exceljs");
    const wb = new ExcelJS.Workbook(),
      ws = wb.addWorksheet("Websites");
    ws.columns = PUBLIC_FIELDS.map((k) => ({
      header: label(k),
      key: k,
      width: 22,
    }));
    ws.addRows(
      rows.map((r) =>
        Object.fromEntries(PUBLIC_FIELDS.map((k) => [k, r[k] ?? ""])),
      ),
    );
    ws.getRow(1).font = { bold: true };
    ws.autoFilter = {
      from: { row: 1, column: 1 },
      to: { row: 1, column: PUBLIC_FIELDS.length },
    };
    download(
      "gp-websites.xlsx",
      await wb.xlsx.writeBuffer(),
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    );
  } else download("gp-websites.csv", toCSV(rows), "text/csv;charset=utf-8");
  return rows.length;
}
export function SearchPage({ mode = "search" }) {
  const { saved, user, go, notify, refresh } = useApp(),
    { busy, run } = useTask();
  const [filters, setFilters] = useState({
      q: new URLSearchParams(location.search).get("q") || "",
      sort: "newest",
    }),
    [draft, setDraft] = useState(filters),
    [page, setPage] = useState(1),
    [advanced, setAdvanced] = useState(false),
    [edit, setEdit] = useState(null),
    [remove, setRemove] = useState(null);
  const isSaved = mode === "saved",
    manage = mode === "manage";
  const options = useData("/api/options", {});
  const params = new URLSearchParams({
    ...filters,
    page,
    limit: 25,
    ...(isSaved ? { ids: saved.join(",") } : {}),
  });
  const { data, loading, error } = useData("/api/sites?" + params);
  const apply = (e) => {
    e.preventDefault();
    setFilters({ ...draft });
    setPage(1);
  };
  return (
    <>
      <Heading
        eyebrow={manage ? "DATABASE" : "DISCOVER PUBLISHERS"}
        title={
          isSaved
            ? "Saved websites"
            : manage
              ? "Manage websites"
              : "Search websites"
        }
        actions={
          <>
            {manage && (
              <button className="primary" onClick={() => setEdit({})}>
                <Plus size={17} /> Add website
              </button>
            )}
            <button
              disabled={busy || !data?.total}
              onClick={() =>
                run(async () => {
                  const n = await exportSites({
                    ...filters,
                    ...(isSaved ? { ids: saved.join(",") } : {}),
                  });
                  notify(`${n.toLocaleString()} websites exported.`);
                })
              }
            >
              <Download size={17} /> Export CSV
            </button>
          </>
        }
      >
        {isSaved
          ? "Your shortlist, saved in this browser."
          : manage
            ? "Add, update and remove publishers from your database."
            : "Find relevant publishers by niche, country, authority and price."}
      </Heading>
      <form className="panel filters" onSubmit={apply}>
        <div className="search-row">
          <div className="search-input">
            <Search size={20} />
            <input
              aria-label="Search websites"
              placeholder="Search a domain, website URL or niche…"
              value={draft.q || ""}
              onChange={(e) => setDraft({ ...draft, q: e.target.value })}
            />
          </div>
          <button className="primary" type="submit">
            Search
          </button>
          <button
            type="button"
            className={advanced ? "active" : ""}
            aria-expanded={advanced}
            onClick={() => setAdvanced(!advanced)}
          >
            <SlidersHorizontal size={17} />
            <span>More filters</span>
          </button>
        </div>
        <div className="filter-grid">
          <Field
            label="Country"
            value={draft.country || ""}
            onChange={(v) => setDraft({ ...draft, country: v })}
            options={[
              { value: "", label: "All countries" },
              ...(options.data?.country || []),
            ]}
          />
          <Field
            label="Niche"
            value={draft.niche || ""}
            onChange={(v) => setDraft({ ...draft, niche: v })}
            options={[
              { value: "", label: "All niches" },
              ...(options.data?.niche || []),
            ]}
          />
          <Field
            label="Minimum DR"
            type="number"
            min="0"
            max="100"
            value={draft.min_dr || ""}
            placeholder="Any"
            onChange={(v) => setDraft({ ...draft, min_dr: v })}
          />
          <Field
            label="Maximum price"
            type="number"
            min="0"
            value={draft.max_price || ""}
            placeholder="Any"
            onChange={(v) => setDraft({ ...draft, max_price: v })}
          />
          <Field
            label="Sort by"
            value={draft.sort}
            onChange={(v) => setDraft({ ...draft, sort: v })}
            options={[
              { value: "newest", label: "Recently added" },
              { value: "dr", label: "Highest DR" },
              { value: "traffic", label: "Highest traffic" },
              { value: "price", label: "Lowest price" },
              { value: "domain", label: "Website A–Z" },
            ]}
          />
        </div>
        {advanced && (
          <div className="filter-grid advanced">
            {["payment_method", "link_type", "source_file", "sheet_name"].map(
              (k) => (
                <Field
                  key={k}
                  label={label(k)}
                  value={draft[k] || ""}
                  onChange={(v) => setDraft({ ...draft, [k]: v })}
                  options={[
                    { value: "", label: "All" },
                    ...(options.data?.[k] || []),
                  ]}
                />
              ),
            )}
            <Field
              label="Minimum traffic"
              type="number"
              min="0"
              value={draft.min_traffic || ""}
              onChange={(v) => setDraft({ ...draft, min_traffic: v })}
            />
          </div>
        )}
        <div className="filter-footer">
          <small>
            Metrics and prices are supplied by publishers. “—” means not
            recorded. Niche labels are estimated from listings.
          </small>
          <button
            className="text-button"
            type="button"
            onClick={() => {
              setDraft({ q: "", sort: "newest" });
              setFilters({ q: "", sort: "newest" });
              setPage(1);
            }}
          >
            Reset filters
          </button>
        </div>
      </form>
      {isSaved && user && (
        <button
          className="text-button"
          disabled={busy}
          onClick={() =>
            run(async () => {
              const ids = await api("/api/admin/legacyfavorites");
              for (const id of ids)
                if (!saved.includes(id))
                  window.dispatchEvent(
                    new CustomEvent("gp:save", { detail: id }),
                  );
              notify(
                ids.length
                  ? `${ids.length} earlier saved websites loaded.`
                  : "No saved websites in the original backup.",
              );
            })
          }
        >
          Load saved websites from the original backup
        </button>
      )}
      <ErrorBox error={error || options.error} />
      <div className="panel results">
        <div className="panel-heading">
          <h2>
            {data?.total?.toLocaleString() ?? "…"}{" "}
            {isSaved ? "saved matches" : "websites found"}
          </h2>
          <span className="subtle">
            {loading ? "Updating…" : "Publisher directory"}
          </span>
        </div>
        {loading ? (
          <Loading label="Finding websites…" />
        ) : data?.rows.length ? (
          <SiteTable
            rows={data.rows}
            onEdit={manage ? (r) => setEdit(r) : null}
            onDelete={manage ? (r) => setRemove(r) : null}
          />
        ) : (
          <Empty
            icon={isSaved ? Bookmark : Globe2}
            title={
              isSaved
                ? "Your shortlist starts here"
                : "No websites match these filters"
            }
          >
            {isSaved
              ? "Use the bookmark button in Search to save a website."
              : "Try a different country or remove a filter."}
            {isSaved && (
              <button onClick={() => go("search")}>Browse websites</button>
            )}
          </Empty>
        )}
        {data && (
          <Pager
            page={data.page}
            pages={data.pages}
            total={data.total}
            onPage={setPage}
          />
        )}
      </div>
      {edit && <SiteEditor site={edit} onClose={() => setEdit(null)} />}{" "}
      {remove && (
        <Modal
          title={`Delete ${remove.domain}?`}
          onClose={() => setRemove(null)}
        >
          <p>
            This removes this listing from the database. A deletion record
            prevents future imports from silently adding it again.
          </p>
          <div className="form-actions">
            <button onClick={() => setRemove(null)}>Cancel</button>
            <button
              className="danger-button"
              disabled={busy}
              onClick={() =>
                run(async () => {
                  await api("/api/admin/sites/" + remove.id, {
                    method: "DELETE",
                    body: {},
                  });
                  setRemove(null);
                  refresh();
                  notify("Website deleted.");
                })
              }
            >
              Delete website
            </button>
          </div>
        </Modal>
      )}
    </>
  );
}
export function SiteEditor({ site, onClose }) {
  const [form, setForm] = useState({
      markup_percent: 20,
      manual_price: 0,
      ...site,
    }),
    { refresh, notify } = useApp(),
    { busy, run } = useTask();
  const full = useData(site.id ? "/api/admin/sites/" + site.id : null);
  React.useEffect(() => {
    if (full.data) setForm(full.data);
  }, [full.data]);
  return (
    <Modal title={site.id ? "Edit website" : "Add website"} onClose={onClose}>
      <ErrorBox error={full.error} />
      {site.id && full.loading ? (
        <Loading />
      ) : (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            run(async () => {
              await api("/api/admin/sites" + (site.id ? "/" + site.id : ""), {
                method: site.id ? "PUT" : "POST",
                body: form,
              });
              refresh();
              notify("Website saved.");
              onClose();
            });
          }}
        >
          <Fields
            value={form}
            setValue={setForm}
            required={["site"]}
            fields={[
              "site",
              "country",
              "type",
              "da",
              "dr",
              "traffic",
              "original_price",
              "casino_original_price",
              { name: "markup_percent", type: "number", min: 0, max: 500 },
              {
                name: "manual_price",
                options: [
                  { value: 0, label: "Automatic markup" },
                  { value: 1, label: "Use manual price" },
                ],
              },
              ...(Number(form.manual_price) === 1
                ? ["general_price", "casino_price"]
                : []),
              "payment_method",
              "tat",
              "link_type",
              "source_file",
              "sheet_name",
            ]}
          />
          <Notice>
            Automatic prices are calculated from original cost and markup.
            Unknown prices remain unknown.
          </Notice>
          <div className="form-actions">
            <button type="button" onClick={onClose}>
              Cancel
            </button>
            <button className="primary" disabled={busy}>
              Save website
            </button>
          </div>
        </form>
      )}
    </Modal>
  );
}
