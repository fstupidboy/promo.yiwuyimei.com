// Block pages.dev duplicate: 301 promo-yiwuyimei-com.pages.dev → https://promo.yiwuyimei.com
// Runs on every request; redirects ONLY when hostname IS the pages.dev mirror,
// preserving path + query. Other hostnames (incl. the canonical domain) pass
// through — no redirect loop possible. Pure JS, no imports.
export async function onRequest(context) {
  const url = new URL(context.request.url);
  if (url.hostname === "promo-yiwuyimei-com.pages.dev") {
    return Response.redirect("https://promo.yiwuyimei.com" + url.pathname + url.search, 301);
  }
  return context.next();
}
