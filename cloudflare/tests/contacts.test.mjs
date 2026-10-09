import test from "node:test";
import assert from "node:assert/strict";
import { scanSheet, parseCSV } from "../shared/import.mjs";
import { extractContacts, normalizePhone, mergeContacts, contactSummary, sheetContactNote, whatsappURL, contactLink, hydrateContact, storeContact } from "../shared/contacts.mjs";
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

test("contact-only sheets auto-detect formatted local phones and retain every contact without a website", () => {
  const r = scanSheet([
    ["Name", "Gmail", "Mobile No", "WhatsApp", "Traffic", "Price"],
    ["Sheet owner", "owner@gmail.com", "0300-1234567", "0044 7700 900123", "12345678901", "9876543210"],
    ["Editor", "editor@example.com", "(202) 555-0143", "", "", ""],
  ], "contacts-only.xlsx", "Team");
  assert.equal(r.header_row, 1);
  assert.equal(r.contacts.length, 0);
  assert.equal(r.unassigned.length, 2);
  assert.equal(r.unassigned[0].phone, "03001234567");
  assert.equal(r.unassigned[0].whatsapp, "+447700900123");
  assert.equal(r.unassigned[1].phone, "2025550143");
  assert.equal(r.unassigned[0].admin_name, "Sheet owner");
  assert.equal(r.privateFields.length, 2);
  assert.deepEqual(r.privateFields[0], sheetContactNote(r.unassigned[0]));
  assert.match(r.privateFields[0].field_value, /owner@gmail.com/);
  assert.equal(r.privateFields[0].source_file, "contacts-only.xlsx");
  assert.equal(r.privateFields[0].sheet_name, "Team");
  assert.deepEqual(contactSummary([r]), {
    contacts: [], unassigned: r.unassigned, all: r.unassigned, emails: 2, phones: 3, links: 0,
  });
  const single = scanSheet([["Mobile"], ["0300-1234567"]], "numbers.csv", "Phones");
  assert.equal(single.unassigned[0].phone, "03001234567");
  assert.equal(single.privateFields.length, 1);
});

test("automatic totals count unique contacts across sheets and pre-header phone-only rows are retained", () => {
  const r = scanSheet([
    ["+44 7700 900123"],
    ["Website", "Email", "Phone"],
    ["publisher.example.com", "hello@example.com", "+44 7700 900123"],
  ], "auto.csv", "Sheet");
  assert.equal(r.header_row, 2);
  assert.equal(r.privateFields.length, 1);
  assert.match(r.privateFields[0].field_value, /447700900123/);
  const summary = contactSummary([r, { contacts: [], unassigned: [{ email: "HELLO@example.com", whatsapp: "+447700900123" }] }]);
  assert.equal(summary.contacts.length, 1);
  assert.equal(summary.emails, 1);
  assert.equal(summary.phones, 1);
});

test("adjacent social and contact columns match the website and stay out of public listing rows", () => {
  const r = scanSheet([
    ["Website Link", "Gmail", "Contact Number", "FB Link", "Linked In", "WhatsApp"],
    ["https://www.one.example.com/path", "owner@gmail.com", "03001234567", "facebook.com/publisher.one", "https://www.linkedin.com/in/editor-one", "https://api.whatsapp.com/send?text=Hello&phone=447700900123"],
    ["two.example.com", "second@example.com", "+1 202 555 0143", "https://fb.com/publisher.two", "linkedin.com/company/publisher-two", ""],
  ], "sites-and-contacts.xlsx", "Publishers");
  assert.equal(r.contacts.length, 2);
  assert.equal(r.contacts[0].domain, "one.example.com");
  assert.equal(r.contacts[0].facebook, "https://facebook.com/publisher.one");
  assert.equal(r.contacts[0].linkedin, "https://www.linkedin.com/in/editor-one");
  assert.equal(r.contacts[0].whatsapp, "+447700900123");
  assert.equal(r.contacts[0].source_file, "sites-and-contacts.xlsx");
  assert.equal(r.contacts[1].email, "second@example.com");
  assert.doesNotMatch(JSON.stringify(r.rows), /owner@gmail|03001234567|facebook|linkedin|447700900123/);
  const bare = scanSheet([["one.example.com", "https://facebook.com/publisher.one", "https://wa.me/923001234567"]], "no-header.csv", "Sheet");
  assert.equal(bare.contacts[0].domain, "one.example.com");
  assert.equal(bare.contacts[0].whatsapp, "+923001234567");
  const contactOnly = scanSheet([["facebook.com/publisher.one", "linkedin.com/in/editor-one"]], "only-social.csv", "Sheet");
  assert.equal(contactOnly.contacts.length, 0);
  assert.equal(contactOnly.unassigned.length, 1);
});

test("WhatsApp links use international digits, preserve chat links and do not guess ambiguous local numbers", () => {
  assert.equal(whatsappURL("0300-1234567"), "https://wa.me/923001234567");
  assert.equal(whatsappURL("+44 7700 900123"), "https://wa.me/447700900123");
  assert.equal(whatsappURL("0092 300 1234567"), "https://wa.me/923001234567");
  assert.equal(whatsappURL("12025550143"), "https://wa.me/12025550143");
  assert.equal(whatsappURL("2025550143"), "");
  assert.equal(whatsappURL("2025550143", "United States"), "https://wa.me/12025550143");
  assert.equal(whatsappURL("https://wa.me/message/ABCDEF"), "https://wa.me/message/ABCDEF");
  assert.equal(contactLink("phone", "03001234567"), "https://wa.me/923001234567");
  assert.equal(contactLink("whatsapp", "+923001234567"), "https://wa.me/923001234567");
  assert.equal(contactLink("email", "owner@gmail.com"), "mailto:owner@gmail.com");
  assert.equal(contactLink("telegram", "@editor_one"), "https://t.me/editor_one");
});

test("private social links survive merging, backups and legacy notes without a schema migration", () => {
  const original = { domain: "one.example.com", notes: "Manually checked", facebook: "https://facebook.com/editor.one", linkedin: "https://linkedin.com/in/editor-one" };
  const stored = storeContact(original);
  assert.match(stored.notes, /private-contact-links/);
  assert.equal(hydrateContact(stored).notes, "Manually checked");
  assert.equal(hydrateContact(stored).facebook, original.facebook);
  const updated = mergeContacts(stored, { domain: original.domain, email: "editor@example.com", facebook: original.facebook, notes: "Sheet: contacts.xlsx" });
  assert.equal(updated.linkedin, original.linkedin);
  assert.equal(updated.notes, "Manually checked\nSheet: contacts.xlsx");
  assert.deepEqual(hydrateContact(storeContact(updated)), updated);
  assert.deepEqual(mergeContacts(updated, original), updated);
  assert.equal(hydrateContact({ notes: "Facebook: https://facebook.com/legacy.editor; phone: +923001234567" }).phone, "+923001234567");
});

test("social detection rejects lookalike hosts, unsafe protocols and numeric profile IDs as phones", () => {
  const r = extractContacts(["notfacebook.com/page", "https://facebook.com.evil.example/page", "javascript:alert(1)", "https://facebook.com/profile.php?id=123456789012345"], ["facebook", "facebook", "linkedin", "facebook"]);
  assert.equal(r.facebook, "https://facebook.com/profile.php?id=123456789012345");
  assert.equal(r.phone, "");
  assert.equal(contactLink("facebook", "https://facebook.com.evil.example/page"), "");
  assert.equal(contactLink("linkedin", "javascript:alert(1)"), "");
  assert.equal(contactLink("contact_url", "https://user:password@example.com/contact"), "");
});

test("Excel HYPERLINK formulas and formatted zero-prefixed phone cells retain row matching", async () => {
  const wb = new ExcelJS.Workbook(), ws = wb.addWorksheet("Links");
  ws.addRow(["Website", "Phone", "Facebook", "LinkedIn"]);
  ws.addRow([{ formula: 'HYPERLINK("https://one.example.com", "Visit")', result: "Visit" }, 3001234567, { formula: 'HYPERLINK("https://facebook.com/editor.one", "Facebook")', result: "Facebook" }, { text: "LinkedIn", hyperlink: "https://linkedin.com/in/editor-one" }]);
  ws.getCell("B2").numFmt = "00000000000";
  const bytes = await wb.xlsx.writeBuffer();
  const [sheet] = await readWorkbook({ name: "formulas.xlsx", size: bytes.length, arrayBuffer: async () => bytes });
  const r = scanSheet(sheet.rows, "formulas.xlsx", sheet.name);
  assert.equal(r.contacts[0].domain, "one.example.com");
  assert.equal(r.contacts[0].phone, "03001234567");
  assert.equal(r.contacts[0].facebook, "https://facebook.com/editor.one");
  assert.equal(r.contacts[0].linkedin, "https://linkedin.com/in/editor-one");
});
