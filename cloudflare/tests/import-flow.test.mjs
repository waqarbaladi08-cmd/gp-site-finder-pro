import test from "node:test";
import assert from "node:assert/strict";
import { importBatches, importSheetReports } from "../shared/import-flow.mjs";
import { scanSheet } from "../shared/import.mjs";

test("long and Unicode sheet notes stay within API body limits without dropping rows", () => {
  const rows = Array.from({ length: 45 }, (_, i) => ({ source_file: "notes.xlsx", field_name: `Contact ${i}`, field_value: "فون".repeat(4000) }));
  const batches = [...importBatches(rows)];
  assert.deepEqual(batches.flat(), rows);
  for (const batch of batches) {
    assert.ok(batch.length <= 20);
    assert.ok(new TextEncoder().encode(JSON.stringify({ resource: "resellers", rows: batch })).length < 200000);
  }
});

test("a failed contact save stops import completion and retry keeps all source associations", async () => {
  const reports = [scanSheet([["Website", "Phone"], ["publisher.example.com", "03001234567"]], "Elite.xlsx", "First"),
    scanSheet([["Website", "Phone"], ["publisher.example.com", "03011234567"]], "GP Post.xlsx", "Last")];
  const calls = [];
  const request = async (path, options) => {
    calls.push({ path, ...options });
    if (path.endsWith("contacts/merge")) throw new Error("Storage temporarily unavailable");
    return { inserted: options.body.rows.length, submitted: options.body.rows.length };
  };
  await assert.rejects(() => importSheetReports(reports, request), /Storage temporarily unavailable/);
  assert.ok(!calls.some((r) => r.body.resource === "structures"));
  const saved = [];
  await importSheetReports(reports, async (path, options) => {
    if (path.endsWith("contacts/merge")) saved.push(...options.body.rows);
    return { inserted: 0, submitted: options.body.rows.length, saved: options.body.rows.length };
  });
  assert.deepEqual(saved.map((r) => [r.source_file, r.sheet_name, r.phone]), [
    ["Elite.xlsx", "First", "03001234567"], ["GP Post.xlsx", "Last", "03011234567"],
  ]);
});
