import test from "node:test";
import assert from "node:assert/strict";
import { scanSheet, parseCSV } from "../shared/import.mjs";
import { extractContacts, normalizePhone, mergeContacts } from "../shared/contacts.mjs";
import { cellText, readWorkbook } from "../src/workbook.mjs";
import ExcelJS from "exceljs";

test("phone/mobile/contact-number headers and Gmail/notes are detected without exposing contacts in listing fields", () => {
  const r = scanSheet([
    ["Website", "Contact Number", "Mobile", "Gmail", "Notes", "Traffic", "Price"],
    ["https://www.publisher.example.com", "+92 (300) 123-4567", "03001234567", "EDITOR@GMAIL.COM", "Backup: editor [at] publisher [dot] com; WhatsApp +44 7700 900123", "12345678901", "9876543210"],
  ], "test.xlsx", "Publishers");
  assert.equal(r.contacts.length, 1);
  assert.equal(r.contacts[0].phone, "+923001234567; 03001234567");
  assert.equal(r.contacts[0].email, "editor@gmail.com; editor@publisher.com");
  assert.equal(r.contacts[0].whatsapp, "+447700900123");
  assert.doesNotMatch(JSON.stringify(r.rows), /gmail|03001234567|editor@/);
  assert.doesNotMatch(r.contacts[0].phone, /12345678901|9876543210/);
});

test("sheet owner notes stay unassigned; headerless website rows and multiple contact columns are supported", () => {
  const r = scanSheet([
    ["Supplier WhatsApp: +44 7700 900123 / reseller@gmail.com"],
    ["Website", "Email", "Email 2", "Contact page"],
    ["one.example.com", "a@example.com", "b@example.com", "https://one.example.com/contact"],
    ["one.example.com", "a@example.com", "c@example.com", ""],
  ], "test.csv", "Sheet");
  assert.equal(r.contacts.length, 1);
  assert.equal(r.contacts[0].email, "a@example.com; b@example.com; c@example.com");
  assert.equal(r.contacts[0].contact_url, "https://one.example.com/contact");
  assert.equal(r.unassigned.length, 1);
  assert.equal(r.unassigned[0].email, "reseller@gmail.com");
  assert.doesNotMatch(r.contacts[0].email, /reseller/);
  const bare = scanSheet([["two.example.com", "one@gmail.com", "+1 202 555 0143"]], "no-header.csv", "Sheet");
  assert.equal(bare.contacts[0].domain, "two.example.com");
  assert.equal(bare.contacts[0].phone, "+12025550143");
});

test("contact parsing avoids dates, metrics, bank data and preserves phone prefixes", () => {
  assert.equal(normalizePhone("0044 7700 900123"), "+447700900123");
  assert.equal(normalizePhone("0300-1234567"), "03001234567");
  assert.equal(normalizePhone("2026-10-04"), "");
  const c = extractContacts(["2026-10-04", "PK12 1234567890123456", "1234567890", "9876543210"], ["", "payment_method", "traffic", "general_price"]);
  assert.equal(c.phone, "");
  assert.equal(extractContacts(["https://wa.me/447700900123"]).whatsapp, "+447700900123");
});

test("merging is idempotent and preserves previous emails, local phones and workflow notes", () => {
  const a = { domain: "example.com", email: "a@example.com", phone: "03001234567", notes: "Manually checked", status: "Replied", quoted_price: "75" };
  const b = { domain: "example.com", email: "A@example.com; b@example.com", notes: "Sheet: test.xlsx", status: "New" };
  const result = mergeContacts(a, b);
  assert.equal(result.email.toLowerCase(), "a@example.com; b@example.com");
  assert.equal(result.phone, a.phone);
  assert.equal(result.status, "Replied");
  assert.equal(result.quoted_price, "75");
  assert.deepEqual(mergeContacts(result, b), result);
});

test("Excel hyperlinks, formula results, rich text and multi-sheet files retain contact information", async () => {
  const wb = new ExcelJS.Workbook(), ws = wb.addWorksheet("Contacts");
  ws.addRow(["Website", "Email", "Phone"]);
  ws.addRow([{ text: "Publisher", hyperlink: "https://example.com" }, { text: "Email editor", hyperlink: "mailto:editor@gmail.com" }, "03001234567"]);
  wb.addWorksheet("More").addRow(["two.example.com", { richText: [{ text: "phone +1 " }, { text: "202 555 0143" }] }]);
  const bytes = await wb.xlsx.writeBuffer();
  const sheets = await readWorkbook({ name: "test.xlsx", size: bytes.length, arrayBuffer: async () => bytes });
  assert.equal(sheets.length, 2);
  const r = scanSheet(sheets[0].rows, "test.xlsx", sheets[0].name);
  assert.equal(r.contacts[0].email, "editor@gmail.com");
  assert.equal(r.contacts[0].phone, "03001234567");
  assert.equal(cellText({ value: { formula: '"a@example.com"', result: "a@example.com" } }), "a@example.com");
  assert.deepEqual(parseCSV('Website\tEmail\nexample.com\t"a@example.com\nb@example.com"', "\t"), [["Website", "Email"], ["example.com", "a@example.com\nb@example.com"]]);
});
