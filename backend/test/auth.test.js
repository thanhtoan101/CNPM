const { test, before, after } = require("node:test");
const assert = require("node:assert/strict");
const jwt = require("jsonwebtoken");
const bcrypt = require("bcrypt");
const { getJwtSecret, signAccessToken } = require("../authConfig");
const queries = [];
let passwordHash;
// An isolated pool stub makes authorization tests independent of a live database.
require.cache[require.resolve("../db")] = { exports: { query: async (sql, params) => {
  queries.push({ sql, params });
  if (sql.includes("FROM users WHERE email")) return { rows: params[0] === "demo@example.test" ? [{ id: 7, email: params[0], role: "photographer", password_hash: passwordHash }] : [] };
  if (sql.includes("SELECT price FROM services")) return { rows: params[0] === 2 && params[1] === 1 ? [{ price: "200000" }] : [] };
  if (sql.includes("INSERT INTO orders")) return { rows: [{ id: 1, total_price: params[4], quantity: params[5] }] };
  return { rows: [] };
} } };
const app = require("../server");
const originalSecret = process.env.JWT_SECRET;
let server, base;
before(async () => {
  process.env.JWT_SECRET = "test-only-secret-with-at-least-32-characters";
  passwordHash = await bcrypt.hash("correct-password", 4);
  server = await new Promise(resolve => { const instance = app.listen(0, "127.0.0.1", () => resolve(instance)); });
  base = `http://127.0.0.1:${server.address().port}`;
});
after(async () => {
  if (originalSecret === undefined) delete process.env.JWT_SECRET; else process.env.JWT_SECRET = originalSecret;
  await new Promise(resolve => server.close(resolve));
});
const tokenFor = (role = "photographer") => signAccessToken({ id: 7, email: "demo@example.test", role });
const request = (path, token, options = {}) => fetch(base + path, { ...options, headers: { ...(token ? { Authorization: token } : {}), ...options.headers } });

test("signing and verification share a configured non-default secret", async () => {
  const response = await request("/labs", `Bearer ${tokenFor()}`);
  assert.equal(response.status, 200);
});
test("missing, malformed and forged tokens are rejected", async () => {
  const forged = jwt.sign({ id: 7, role: "admin" }, "SECRET_KEY");
  for (const token of [undefined, "Basic abc", "Bearer a b", `Bearer ${forged}`]) {
    assert.equal((await request("/labs", token)).status, 401);
  }
});
test("expired tokens are rejected", async () => {
  const token = jwt.sign({ id: 7, role: "admin" }, getJwtSecret(), { expiresIn: -1 });
  assert.equal((await request("/labs", `Bearer ${token}`)).status, 401);
});
test("user and database inspection endpoints require an administrator", async () => {
  for (const path of ["/users", "/users/full", "/tables", "/schema/users"]) {
    assert.equal((await request(path)).status, 401);
    assert.equal((await request(path, `Bearer ${tokenFor()}`)).status, 403);
    assert.equal((await request(path, `Bearer ${tokenFor("admin")}`)).status, 200);
  }
  const fullUserQuery = queries.find(q => q.sql.includes("LIMIT 5"));
  assert.match(fullUserQuery.sql, /SELECT id, email, role/);
  assert.doesNotMatch(fullUserQuery.sql, /SELECT \*/);
});
test("photographers can only query their own orders", async () => {
  assert.equal((await request("/orders", `Bearer ${tokenFor()}`)).status, 200);
  assert.deepEqual(queries.at(-1).params, [7]);
  assert.match(queries.at(-1).sql, /WHERE user_id = \$1/);
});
test("login returns a usable token without a password hash", async () => {
  const response = await request("/auth/login", null, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email: "demo@example.test", password: "correct-password" }) });
  assert.equal(response.status, 200);
  const data = await response.json();
  assert.equal(data.user.password_hash, undefined);
  assert.equal((await request("/labs", `Bearer ${data.token}`)).status, 200);
});
test("unknown users and wrong passwords receive the same response", async () => {
  const replies = [];
  for (const email of ["demo@example.test", "unknown@example.test"]) {
    const response = await request("/auth/login", null, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password: "wrong" }) });
    assert.equal(response.status, 401); replies.push(await response.json());
  }
  assert.deepEqual(replies[0], replies[1]);
});
test("missing and weak JWT configuration fails closed", () => {
  const secret = process.env.JWT_SECRET;
  try {
    for (const value of ["", "SECRET_KEY"]) { process.env.JWT_SECRET = value; assert.throws(getJwtSecret, /at least 32/); }
  } finally { process.env.JWT_SECRET = secret; }
});
test("photographers cannot create labs or courses", async () => {
  for (const path of ["/labs", "/courses"]) assert.equal((await request(path, `Bearer ${tokenFor()}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: "{}" })).status, 403);
});
test("order total is derived from the service catalogue, ignoring a tampered total", async () => {
  const response = await request("/orders", `Bearer ${tokenFor()}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ lab_id: 1, service_id: 2, quantity: 2, total_price: 1 }) });
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { id: 1, total_price: 400000, quantity: 2 });
});
test("order validation rejects invalid quantities and mismatched lab/service", async () => {
  for (const body of [{ lab_id: 1, service_id: 2, quantity: 0 }, { lab_id: 1, service_id: 2, quantity: 1.5 }, { lab_id: 999, service_id: 2 }]) {
    assert.equal((await request("/orders", `Bearer ${tokenFor()}`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) })).status, 400);
  }
});
