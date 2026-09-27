import test from "node:test";
import assert from "node:assert/strict";
import {
  country,
  domain,
  number,
  prepareSite,
  toCSV,
} from "../shared/domain.mjs";
import { parseCSV, scanSheet } from "../shared/import.mjs";
import { seedStatements } from "../scripts/seed.mjs";
import { outreach } from "../shared/outreach.mjs";

test("country aliases are explicit, missing values stay unknown", () => {
  assert.equal(country("  PK  "), "Pakistan");
  assert.equal(country("USA"), "United States");
  assert.equal(country("uk"), "United Kingdom");
  for (const v of ["worldwide", "global", "unknown", "1000", null])
    assert.equal(country(v), "");
  assert.equal(prepareSite({ site: "publisher.co.uk" }).country, "");
});
test("domains and metrics normalize without accepting javascript or email addresses", () => {
  assert.equal(domain("https://www.Example.com/article?x=1"), "example.com");
  for (const v of [
    "javascript:alert(1)",
    "note",
    "admin@example.com",
    "example.com.evil@evil.org",
    "https://evil.org:443",
  ])
    assert.equal(domain(v), "");
  assert.equal(number("1.2K"), 1200);
  assert.equal(number("4,000"), 4000);
  assert.equal(number("On request"), null);
});
test("price migration applies the old initialization once and preserves manual pricing", () => {
  const r = prepareSite(
    { site: "example.com", general_price: "$100", casino_price: "200" },
    { legacy: true },
  );
  assert.equal(r.general_price, "120.00");
  assert.equal(r.casino_price, "240.00");
  assert.equal(prepareSite(r, { legacy: true }).general_price, "120.00");
  assert.equal(
    prepareSite(
      { ...r, manual_price: 1, general_price: "95", selling_price: "95" },
      { legacy: true },
    ).general_price,
    "95",
  );
  assert.equal(
    prepareSite(
      { site: "example.com", general_price: "PKR 100" },
      { legacy: true },
    ).general_price,
    "PKR 100",
  );
  assert.equal(
    prepareSite(
      { site: "example.com", general_price: "On request" },
      { imported: true },
    ).general_price,
    "On request",
  );
});
test("spreadsheet notes, private contacts and country columns do not enter public website columns", () => {
  const raw = parseCSV(
    'Email: reseller@example.com\r\nWebsite,Country,DR,Price,Email\r\nexample.com,PK,45,100,owner@example.com\r\n"second.com",UK,,"On request",\r\n"A note, with commas",,,,\r\n',
  );
  const report = scanSheet(raw, "suppliers.csv", "Sheet 1");
  assert.equal(report.header_row, 2);
  assert.equal(report.rows.length, 2);
  assert.equal(report.invalid, 1);
  assert.equal(report.privateFields.length, 1);
  assert.equal(report.contacts.length, 1);
  assert.equal(report.rows[0].country, "PK");
  assert.equal(report.rows[0].email, undefined);
  assert.deepEqual(parseCSV('a,b\n"hello\nworld","a""b"'), [
    ["a", "b"],
    ["hello\nworld", 'a"b'],
  ]);
  assert.throws(() => parseCSV('"unterminated'), /unclosed/);
});
test("CSV export neutralizes spreadsheet formulas and correctly escapes quotes", () => {
  const csv = toCSV(
    [{ site: '=HYPERLINK("evil")', country: "+CMD" }],
    ["site", "country"],
  );
  assert.match(csv, /"'=HYPERLINK\(""evil""\)"/);
  assert.match(csv, /"'\+CMD"/);
});
test("migration preserves invalid legacy records privately without copying credentials", () => {
  const original = {
    id: 3,
    site: "payment note",
    general_price: "100",
    created_at: "2020-01-01",
  };
  const result = seedStatements({
    format: "gp-streamlit-export",
    tables: {
      sites: [{ id: 1, site: "example.com", general_price: "100" }, original],
    },
    profile: { name: "Test" },
    media: [],
    password_hash: "secret",
  });
  assert.equal(result.counts.sites, 1);
  assert.equal(result.counts.import_review, 1);
  assert.match(result.statements.join("\n"), /payment note/);
  assert.doesNotMatch(
    result.statements.join("\n"),
    /password_hash|auth_users|secret/,
  );
});
test("changing the target regenerates outreach and proof is never invented", () => {
  const first = outreach({
    site: "one.example.com",
    sender: "Sender",
    company: "Business",
  });
  const next = outreach({
    site: "two.example.com",
    sender: "Sender",
    company: "Business",
  });
  assert.match(first.Email, /one.example.com/);
  assert.match(next.Email, /two.example.com/);
  assert.doesNotMatch(next.Email, /one.example.com/);
  const client = outreach({ site: "example.com" }, true);
  assert.doesNotMatch(client.Email, /increased .*%|guarantee|rank #1/i);
});
