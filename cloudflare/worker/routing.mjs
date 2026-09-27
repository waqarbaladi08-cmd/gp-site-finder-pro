import { withAppBase } from "../shared/routing.mjs";

// A fixed allowlist, never a client-provided forwarded-host header.
export const WEBSITE_ORIGIN = "https://gp-site-finder-pro-landing.vercel.app";

export function mountedResponse(response, base) {
  if (!base) return response;
  const result = new Response(response.body, response);
  const redirect = result.headers.get("Location");
  if (redirect) result.headers.set("Location", withAppBase(redirect, base));
  if (!result.headers.get("Content-Type")?.includes("text/html")) return result;

  result.headers.set("Cache-Control", "no-cache");
  result.headers.delete("Content-Length");
  result.headers.delete("ETag");
  const attributes = {
    element(element) {
      for (const name of ["src", "href"]) {
        const value = element.getAttribute(name);
        if (value == null) continue;
        // Vite's relative base also keeps lazy-loaded chunks within this mount.
        const path = value.startsWith("./") ? value.slice(1) : value;
        element.setAttribute(name, withAppBase(path, base));
      }
    },
  };
  return new HTMLRewriter().on("[src], [href]", attributes).transform(result);
}
