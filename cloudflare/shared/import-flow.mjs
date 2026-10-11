import { contactSummary } from "./contacts.mjs";

// Respect both row and body limits, including Unicode and long contact notes.
export function* importBatches(rows, maxRows = 20, maxBytes = 180000) {
  const encoder = new TextEncoder();
  let batch = [], size = 100;
  for (const row of rows) {
    const bytes = encoder.encode(JSON.stringify(row)).length + 1;
    if (bytes + 100 > maxBytes) throw new Error("A sheet row is too long to import. Shorten its notes and try again.");
    if (batch.length && (batch.length >= maxRows || size + bytes > maxBytes)) {
      yield batch; batch = []; size = 100;
    }
    batch.push(row); size += bytes;
  }
  if (batch.length) yield batch;
}

export async function saveContactRows(rows, request, onProgress = () => {}) {
  let processed = 0;
  for (const batch of importBatches(rows)) {
    await request("/api/admin/contacts/merge", { method: "POST", body: { rows: batch } });
    processed += batch.length;
    onProgress(`${processed.toLocaleString()} / ${rows.length.toLocaleString()} website / sheet contact records saved privately…`);
  }
  return processed;
}

export async function savePrivateRows(resource, rows, request) {
  for (const batch of importBatches(rows))
    await request("/api/admin/resource-batch", { method: "POST", body: { resource, rows: batch } });
}

export async function importSheetReports(reports, request, onProgress = () => {}) {
  const total = reports.reduce((n, r) => n + r.rows.length, 0);
  let inserted = 0, processed = 0, contactRecords = 0;
  for (const report of reports) {
    onProgress(`Importing ${report.source_file} · ${report.sheet_name}…`);
    for (const batch of importBatches(report.rows, 25)) {
      const result = await request("/api/admin/import", { method: "POST", body: { rows: batch } });
      inserted += result.inserted; processed += result.submitted;
      onProgress(`${processed.toLocaleString()} / ${total.toLocaleString()} websites processed · ${report.sheet_name}`);
    }
    // Never merge different tabs before saving their source records.
    const contacts = report.contacts.map((r) => ({ ...r,
      source_file: r.source_file || report.source_file, sheet_name: r.sheet_name ?? report.sheet_name }));
    contactRecords += await saveContactRows(contacts, request, onProgress);
    await savePrivateRows("resellers", report.privateFields, request);
    await savePrivateRows("structures", [{ source_file: report.source_file, sheet_name: report.sheet_name,
      header_row: report.header_row, mapped_fields: JSON.stringify(report.mapping),
      status: report.rows.length ? "Imported" : report.contacts.length || report.unassigned.length ? "Contacts imported" : "No valid website table",
      private_count: report.contacts.length + report.privateFields.length }], request);
  }
  return { inserted, processed, total, contactRecords, detected: contactSummary(reports) };
}
