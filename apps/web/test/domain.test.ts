import { test } from "node:test";
import assert from "node:assert/strict";
import { createDemoState, isDemoState, advanceOrder, saveService, validateScans, publishScans, decideApplication, moderateReport, csvCell, MAX_SCAN_BYTES } from "../src/domain.ts";

test("saved demo state survives a JSON round trip with optional fields", () => {
  const state = saveService(createDemoState(), { id: "new", name: "E6 Develop", formats: "35mm", price: 320000, days: 3, status: "Active" });
  assert.equal(isDemoState(JSON.parse(JSON.stringify(state))), true);
  assert.equal(isDemoState({ ...state, orders: [{ ...state.orders[0], status: "Forged" }] }), false);
  assert.equal(isDemoState({ ...state, audit: [{ action: "Incomplete event" }] }), false);
  assert.equal(isDemoState(null), false);
});

test("orders advance exactly one stage and original state is unchanged", () => {
  const state = createDemoState(); const next = advanceOrder(state, "FL-2048");
  assert.equal(next.orders[0].status, "Film received");
  assert.equal(state.orders[0].status, "New"); assert.equal(next.audit.length, 1);
});
test("scan orders cannot finish before reviewed publication", () => {
  assert.throws(() => advanceOrder(createDemoState(), "FL-2036"), /Publish reviewed/);
  assert.throws(() => advanceOrder(createDemoState(), "FL-2028"), /no next/);
});
test("service price, turnaround, duplicate name and required fields are validated", () => {
  const state = createDemoState(); const seed = { ...state.services[0], id: "new" };
  for (const change of [{ price: -1 }, { price: 1.5 }, { days: 0 }, { days: 61 }, { name: " " }]) assert.throws(() => saveService(state, { ...seed, ...change }));
  assert.throws(() => saveService(state, seed), /already exists/);
  const next = saveService(state, { ...seed, name: "E6 Develop" });
  assert.equal(next.services.length, state.services.length + 1);
  assert.equal(saveService(next, { ...seed, name: "E6 Develop", price: 300000 }).services.at(-1)?.price, 300000);
});
const file = { name: "scan.jpg", type: "image/jpeg", size: 100 };
test("scan validation covers empty, MIME, extension, size, count and duplicates", () => {
  assert.deepEqual(validateScans([file]), []);
  assert.deepEqual(validateScans([{ name: "scan.tiff", type: "", size: MAX_SCAN_BYTES }]), []);
  for (const files of [[], [{ ...file, name: "scan.exe" }], [{ ...file, type: "text/html" }], [{ ...file, size: 0 }], [{ ...file, size: MAX_SCAN_BYTES + 1 }], [file, file], Array(101).fill(file)]) assert.ok(validateScans(files).length);
});
test("publication requires quality checks and records metadata once", () => {
  const state = createDemoState();
  assert.throws(() => publishScans(state, "FL-2036", [file], false, true));
  assert.throws(() => publishScans(state, "FL-2048", [file], true, true));
  const next = publishScans(state, "FL-2036", [file], true, true);
  assert.equal(next.deliveries[0].private, true);
  assert.equal(next.orders.find(item => item.id === "FL-2036")?.status, "Completed");
  assert.equal(next.audit.length, 1);
  assert.throws(() => publishScans(next, "FL-2036", [file], true, true));
});
test("incomplete labs cannot be approved and rejection requires a reason", () => {
  const state = createDemoState();
  assert.throws(() => decideApplication(state, "LAB-118", "Approved", ""));
  assert.throws(() => decideApplication(state, "LAB-118", "Rejected", "short"));
  const next = decideApplication(state, "LAB-114", "Approved", "");
  assert.equal(next.applications.find(item => item.id === "LAB-114")?.status, "Approved");
  assert.throws(() => decideApplication(next, "LAB-114", "Rejected", "Changed my decision"));
});
test("moderation requires explanations and changes only the linked listing", () => {
  const state = createDemoState();
  assert.throws(() => moderateReport(state, "RP-081", "Hide listing", "", ""));
  assert.throws(() => moderateReport(state, "RP-079", "Hide listing", "Evidence reviewed", "Please update the listing"));
  const next = moderateReport(state, "RP-081", "Hide listing", "Evidence reviewed", "Please update the listing");
  assert.equal(next.listings[0].status, "Hidden"); assert.equal(next.listings[1].status, state.listings[1].status);
  assert.throws(() => moderateReport(next, "RP-081", "Dismiss", "Evidence reviewed", "Please update the listing"));
});
test("CSV export escapes quotes and spreadsheet formulas", () => {
  assert.equal(csvCell('a"b'), '"a""b"'); assert.equal(csvCell("=SUM(A1)"), '"\'=SUM(A1)"');
});
