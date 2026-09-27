import { test } from "node:test";
import assert from "node:assert/strict";
import { appBase, stripAppBase, withAppBase } from "../shared/routing.mjs";

test("root and website-mounted navigation preserve queries without capturing unrelated paths", () => {
  for (const path of ["/", "/search", "/application", "/app-example"])
    assert.equal(appBase(path), "");
  for (const path of ["/app", "/app/", "/app/search"])
    assert.equal(appBase(path), "/app");
  assert.equal(stripAppBase("/app"), "/");
  assert.equal(stripAppBase("/app/search"), "/search");
  assert.equal(stripAppBase("/search"), "/search");
  assert.equal(withAppBase("/search?q=example.com&page=2", "/app"), "/app/search?q=example.com&page=2");
  assert.equal(withAppBase("/api/media/photo.png", "/app"), "/app/api/media/photo.png");
  for (const path of ["/app/search", "/app?x=1", "https://example.com/", "//example.com/", "data:image/png;base64,AA", "blob:example", "#main", undefined])
    assert.equal(withAppBase(path, "/app"), path);
  assert.equal(withAppBase("/search", ""), "/search");
});
