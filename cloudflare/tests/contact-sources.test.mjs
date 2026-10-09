import test from "node:test";
import assert from "node:assert/strict";
import ExcelJS from "exceljs";
import { scanSheet } from "../shared/import.mjs";
import { contactSummary } from "../shared/contacts.mjs";
import { contactPreviewRows, contactSourceSummaries, savedSourceContact } from "../shared/contact-sources.mjs";
import { readWorkbook } from "../src/workbook.mjs";

test("the same website keeps every sheet's number and source in preview and export, while saving merges domains", () => {
  const reports = [
    scanSheet([["Website", "Phone"], ["publisher.example.com", "03001234567"]], "all-tabs.xlsx", "Alpha"),
    scanSheet([["Website", "Phone"], ["publisher.example.com", "+44 7700 900123"]], "all-tabs.xlsx", "Beta"),
    scanSheet([["Name", "Mobile"], ["Supplier", "03011234567"]], "all-tabs.xlsx", "Contact directory"),
    scanSheet([["Website", "Price"], ["other.example.com", "50"]], "all-tabs.xlsx", "No contacts"),
  ];
  const rows = contactPreviewRows(reports);
  assert.equal(rows.length, 3);
  assert.deepEqual(rows.map((r) => r.sheet_name), ["Alpha", "Beta", "Contact directory"]);
  assert.equal(rows.find((r) => r.sheet_name === "Alpha").phone, "03001234567");
  assert.equal(rows.find((r) => r.sheet_name === "Beta").phone, "+447700900123");
  const saved = contactSummary(reports);
  assert.equal(saved.contacts.length, 1);
  assert.equal(saved.contacts[0].phone, "03001234567; +447700900123");
  assert.equal(saved.unassigned[0].phone, "03011234567");
  const summary = contactSourceSummaries(reports);
  assert.equal(summary.length, 4);
  assert.deepEqual(summary.map((r) => r.phones), [1, 1, 1, 0]);
  assert.equal(summary[3].entries, 0);
});

test("saved JSON records use website headers even when another domain appears in a contact-page column", () => {
  const r = savedSourceContact({ id: 12, source_file: "source.xlsx", sheet_name: "Beta", raw_record: JSON.stringify({
    "Website Link": "https://publisher.example.com/article", "Contact page": "https://agency.example.com/contact",
    "Mobile No": "0300-1234567", Gmail: "editor-private@gmail.com",
  }) }, "import_review");
  assert.equal(r.domain, "publisher.example.com");
  assert.equal(r.phone, "03001234567");
  assert.equal(r.contact_url, "https://agency.example.com/contact");
  assert.equal(r.email, "editor-private@gmail.com");
  assert.equal(r.persisted, false);
});

test("saved labeled notes preserve local numbers and explicit ownership, and exclude bank fields", () => {
  const r = savedSourceContact({ id: 13, source_file: "source.xlsx", sheet_name: "Contacts", field_name: "Retained row",
    field_value: "Website link: publisher.example.com | Mobile: 0300-1234567 | Bank account: 123456789012 | Gmail: owner-private@gmail.com" });
  assert.equal(r.domain, "publisher.example.com");
  assert.equal(r.phone, "03001234567");
  assert.equal(r.email, "owner-private@gmail.com");
  assert.equal(r.persisted, true);
  assert.equal(savedSourceContact({ field_name: "Phone", field_value: "(202) 555-0143" }).phone, "2025550143");
  assert.equal(savedSourceContact({ field_name: "Bank account", field_value: "Account: 123456789012" }).phone, "");
});

test("XLSX scanning keeps distinct numbers in all worksheet tabs including the last and hidden contact tabs", async () => {
  const wb = new ExcelJS.Workbook();
  for (const [name, phone] of [["First", "03001234567"], ["Second", "03011234567"], ["Third", "03021234567"]]) {
    const ws = wb.addWorksheet(name);
    ws.addRow(["Website", "WhatsApp"]);
    ws.addRow(["publisher.example.com", phone]);
  }
  const last = wb.addWorksheet("Supplier contacts", { state: "hidden" });
  last.addRow(["Name", "Phone"]);
  last.addRow(["Workbook supplier", "+44 7700 900123"]);
  const bytes = await wb.xlsx.writeBuffer();
  const sheets = await readWorkbook({ name: "all-tabs.xlsx", size: bytes.length, arrayBuffer: async () => bytes });
  const reports = sheets.map((s) => scanSheet(s.rows, "all-tabs.xlsx", s.name));
  assert.equal(sheets.length, 4);
  assert.deepEqual(contactSourceSummaries(reports).map((r) => r.phones), [1, 1, 1, 1]);
  assert.equal(contactPreviewRows(reports).length, 4);
  assert.equal(contactSummary(reports).phones, 4);
});
