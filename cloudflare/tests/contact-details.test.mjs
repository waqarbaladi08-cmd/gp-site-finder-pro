import test from "node:test";
import assert from "node:assert/strict";
import { build } from "esbuild";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

const out = await build({ entryPoints: ["src/contact-details.jsx"], bundle: true, write: false,
  format: "esm", platform: "node", define: { "location.pathname": JSON.stringify("/app/search") } });
const { ContactDetailsContent } = await import("data:text/javascript;base64," + Buffer.from(out.outputFiles[0].text).toString("base64"));

test("a listing shows its own sheet's links first and keeps other files in labeled source groups", () => {
  const html = renderToStaticMarkup(React.createElement(ContactDetailsContent, { data: {
    source_file: "Elite.xlsx", sheet_name: "Publishers", country: "Pakistan",
    contact: { phone: "03001234567; +447700900123; 03021234567" },
    publisher_sources: [
      { source_file: "Elite.xlsx", sheet_name: "Publishers", scope: "selected_sheet", phone: "03001234567", facebook: "https://facebook.com/elite.editor" },
      { source_file: "GP Post.xlsx", sheet_name: "Publishers", scope: "matching_sheet", whatsapp: "+447700900123", linkedin: "https://linkedin.com/in/gp-editor" },
    ],
    suppliers: [{ source_file: "Elite.xlsx", sheet_name: "Publishers", scope: "selected_sheet", email: "elite-owner@gmail.com" }],
  } }));
  const primary = html.split("<details>")[0];
  assert.match(primary, /This sheet&#x27;s contacts/);
  assert.match(primary, /href="https:\/\/wa.me\/923001234567"/);
  assert.match(primary, /href="https:\/\/facebook.com\/elite.editor"/);
  assert.match(primary, /mailto:elite-owner@gmail.com/);
  assert.doesNotMatch(primary, /GP Post|447700900123|gp-editor/);
  assert.match(html, /Contacts in other source sheets \(1\)/);
  assert.match(html, /GP Post.xlsx/);
  assert.match(html, /href="https:\/\/wa.me\/447700900123"/);
  assert.doesNotMatch(html, /03021234567|Previously saved website contacts/);
});

test("an older contact without source attribution is labeled separately from a sheet's detected supplier", () => {
  const html = renderToStaticMarkup(React.createElement(ContactDetailsContent, { data: {
    source_file: "Elite.xlsx", sheet_name: "Publishers", contact: { phone: "+447700900123" },
    suppliers: [{ source_file: "Elite.xlsx", sheet_name: "Publishers", scope: "selected_sheet", phone: "03001234567" }],
  } }));
  assert.doesNotMatch(html.split("<details>")[0], /447700900123/);
  assert.match(html, /Previously saved website contacts/);
  assert.match(html, /do not have a retained sheet assignment/);
});
