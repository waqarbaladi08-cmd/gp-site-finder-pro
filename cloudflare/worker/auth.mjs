export const hex = (bytes) =>
  [...new Uint8Array(bytes)]
    .map((x) => x.toString(16).padStart(2, "0"))
    .join("");
export async function sha(value) {
  return hex(
    await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value)),
  );
}
export function same(a, b) {
  let diff = a.length ^ b.length;
  for (let i = 0; i < Math.max(a.length, b.length); i++)
    diff |= (a.charCodeAt(i) || 0) ^ (b.charCodeAt(i) || 0);
  return diff === 0;
}
export function fail(message, status = 400) {
  throw Object.assign(new Error(message), { status });
}
export function originCheck(request, additionalOrigin) {
  const origin = request.headers.get("Origin");
  if (origin !== new URL(request.url).origin && origin !== additionalOrigin)
    fail("This action must come from this website.", 403);
  if (!request.headers.get("Content-Type")?.startsWith("application/json"))
    fail("JSON body required.", 415);
}
export async function body(request, limit = 200000) {
  if (Number(request.headers.get("Content-Length")) > limit)
    fail("Upload is too large.", 413);
  const reader = request.body?.getReader();
  if (!reader) fail("Request body required.");
  const chunks = [];
  let size = 0;
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    size += value.byteLength;
    if (size > limit) {
      await reader.cancel();
      fail("Upload is too large.", 413);
    }
    chunks.push(value);
  }
  const bytes = new Uint8Array(size);
  let pos = 0;
  for (const chunk of chunks) {
    bytes.set(chunk, pos);
    pos += chunk.length;
  }
  try {
    return JSON.parse(new TextDecoder().decode(bytes));
  } catch {
    fail("Invalid JSON body.");
  }
}
export async function rateLimit(db, key, max, seconds) {
  const now = Math.floor(Date.now() / 1000);
  const r = await db
    .prepare(
      `INSERT INTO rate_limits(key,count,expires_at) VALUES(?,1,?)
    ON CONFLICT(key) DO UPDATE SET count=CASE WHEN expires_at<=? THEN 1 ELSE count+1 END,
    expires_at=CASE WHEN expires_at<=? THEN excluded.expires_at ELSE expires_at END RETURNING count`,
    )
    .bind(key, now + seconds, now, now)
    .first();
  if (r.count > max) fail("Too many attempts. Please try again later.", 429);
}
export async function session(request, db) {
  const token = (request.headers.get("Cookie") || "").match(
    /(?:^|;\s*)gp_session=([a-f0-9]{64})(?:;|$)/,
  )?.[1];
  if (!token) return null;
  return db
    .prepare(
      "SELECT username FROM sessions WHERE token_hash=? AND expires_at>?",
    )
    .bind(await sha(token), Math.floor(Date.now() / 1000))
    .first();
}
export function cookie(request, token, seconds = 28800) {
  return `gp_session=${token}; Path=/; HttpOnly; SameSite=Strict; Max-Age=${seconds}${new URL(request.url).protocol === "https:" ? "; Secure" : ""}`;
}
export async function login(request, env) {
  const b = await body(request, 5000);
  const username = String(b.username || "")
    .trim()
    .slice(0, 100);
  const ip = await sha(request.headers.get("CF-Connecting-IP") || "local");
  await rateLimit(env.DB, `login-ip:${ip}`, 8, 900);
  await rateLimit(
    env.DB,
    `login-user:${await sha(username.toLowerCase())}`,
    30,
    3600,
  );
  if (!/^[a-f0-9]{64}$/.test(b.verifier || ""))
    fail("Incorrect username or password.", 401);
  const user = await env.DB.prepare("SELECT * FROM auth_users WHERE username=?")
    .bind(username)
    .first();
  const hashed = await sha(b.verifier);
  if (!user || !same(user.password_hash, hashed))
    fail("Incorrect username or password.", 401);
  const token = hex(crypto.getRandomValues(new Uint8Array(32)));
  await env.DB.batch([
    env.DB.prepare("INSERT INTO sessions VALUES(?,?,?)").bind(
      await sha(token),
      username,
      Math.floor(Date.now() / 1000) + 28800,
    ),
    env.DB.prepare("DELETE FROM sessions WHERE expires_at<?").bind(
      Math.floor(Date.now() / 1000),
    ),
    env.DB.prepare("DELETE FROM rate_limits WHERE expires_at<?").bind(
      Math.floor(Date.now() / 1000),
    ),
  ]);
  return { data: { username }, cookie: cookie(request, token) };
}
export async function setPassword(db, username, b) {
  if (
    !/^[a-f0-9]{32}$/.test(b.salt || "") ||
    !/^[a-f0-9]{64}$/.test(b.verifier || "") ||
    b.iterations !== 600000
  )
    fail("Invalid password setup.");
  await db.batch([
    db
      .prepare(
        "INSERT INTO auth_users VALUES(?,?,?,?) ON CONFLICT(username) DO UPDATE SET salt=excluded.salt,password_hash=excluded.password_hash,iterations=excluded.iterations",
      )
      .bind(username, b.salt, await sha(b.verifier), 600000),
    db.prepare("DELETE FROM sessions WHERE username=?").bind(username),
  ]);
}
