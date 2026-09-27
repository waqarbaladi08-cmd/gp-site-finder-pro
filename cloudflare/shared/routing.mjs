// Both the Worker URL and the existing website's /app mount serve this app.
export const APP_MOUNT = "/app";

export function appBase(pathname) {
  return pathname === APP_MOUNT || pathname.startsWith(APP_MOUNT + "/")
    ? APP_MOUNT
    : "";
}

export function stripAppBase(pathname) {
  return pathname.slice(appBase(pathname).length) || "/";
}

export function withAppBase(path, base) {
  if (
    !base ||
    typeof path !== "string" ||
    !path.startsWith("/") ||
    path.startsWith("//") ||
    appBase(path.split(/[?#]/, 1)[0])
  ) return path;
  return base + path;
}
