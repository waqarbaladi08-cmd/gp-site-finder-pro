import test from "node:test";
import assert from "node:assert/strict";
import { build } from "esbuild";
import React from "react";
import { renderToStaticMarkup } from "react-dom/server";

const out = await build({ entryPoints: ["src/contact-links.jsx"], bundle: true, write: false, format: "esm", platform: "node" });
const { ContactChannels } = await import("data:text/javascript;base64," + Buffer.from(out.outputFiles[0].text).toString("base64"));

test("contact cards render WhatsApp, Gmail, Facebook and LinkedIn as real links", () => {
  const html = renderToStaticMarkup(React.createElement(ContactChannels, { contact: {
    email: "editor@gmail.com", phone: "03001234567", whatsapp: "+447700900123",
    facebook: "https://facebook.com/editor.one", linkedin: "https://linkedin.com/in/editor-one",
  } }));
  for (const href of ["https://wa.me/923001234567", "https://wa.me/447700900123", "mailto:editor@gmail.com", "https://facebook.com/editor.one", "https://linkedin.com/in/editor-one"])
    assert.ok(html.includes(`href="${href}"`), href);
  assert.match(html, /mail.google.com\/mail\/\?view=cm&amp;fs=1&amp;to=editor%40gmail.com/);
  assert.match(html, /href="tel:03001234567"/);
  assert.match(html, /rel="noopener noreferrer"/);
});

test("contact cards escape sheet content and cannot render executable contact links", () => {
  const html = renderToStaticMarkup(React.createElement(ContactChannels, { contact: {
    facebook: "javascript:alert(1)", linkedin: "https://linkedin.com.evil.example/editor", admin_name: '<img src=x onerror="alert(1)">',
  } }));
  assert.doesNotMatch(html, /href=|<img/);
  assert.match(html, /&lt;img/);
});
