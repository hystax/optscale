/**
 * Registrable domains of search engines whose referrer counts as organic traffic.
 * Matching is suffix-by-label (see matchSearchEngineDomain), so one entry covers every
 * subdomain (news.google.com, uk.search.yahoo.com). A missing country domain only
 * degrades organic to referral — utm_source stays correct, just loses "organic".
 *
 * Every entry must contain a dot — a single-label entry would match every hostname.
 */
export const SEARCH_ENGINE_DOMAINS: ReadonlySet<string> = new Set([
  // Google
  "google.com",
  "google.co.uk",
  "google.de",
  "google.fr",
  "google.es",
  "google.it",
  "google.nl",
  "google.be",
  "google.ch",
  "google.at",
  "google.pl",
  "google.se",
  "google.no",
  "google.dk",
  "google.fi",
  "google.pt",
  "google.ie",
  "google.gr",
  "google.cz",
  "google.sk",
  "google.ro",
  "google.hu",
  "google.bg",
  "google.hr",
  "google.rs",
  "google.lt",
  "google.lv",
  "google.ee",
  "google.ca",
  "google.com.mx",
  "google.com.br",
  "google.com.ar",
  "google.com.co",
  "google.cl",
  "google.com.au",
  "google.co.nz",
  "google.co.in",
  "google.co.jp",
  "google.co.kr",
  "google.com.hk",
  "google.com.tw",
  "google.com.sg",
  "google.com.my",
  "google.co.th",
  "google.com.ph",
  "google.co.id",
  "google.com.vn",
  "google.com.tr",
  "google.co.il",
  "google.ae",
  "google.com.sa",
  "google.com.eg",
  "google.co.za",
  "google.com.ng",
  "google.co.ke",
  "google.ru",
  "google.com.ua",
  "google.kz",
  // Bing
  "bing.com",
  // Yahoo
  "yahoo.com",
  "yahoo.co.jp",
  "yahoo.co.uk",
  "yahoo.co.in",
  "yahoo.ca",
  "yahoo.de",
  "yahoo.fr",
  "yahoo.es",
  "yahoo.it",
  "yahoo.com.au",
  "yahoo.com.br",
  "yahoo.com.mx",
  "yahoo.com.hk",
  "yahoo.com.tw",
  "yahoo.com.sg",
  // DuckDuckGo
  "duckduckgo.com",
  // Yandex
  "yandex.com",
  "yandex.ru",
  "yandex.by",
  "yandex.kz",
  "yandex.uz",
  "yandex.ua",
  "yandex.com.tr",
  "yandex.eu",
  "ya.ru",
  // Baidu
  "baidu.com",
  // Sogou / So.com (360 Search) — China, alongside Baidu
  "sogou.com",
  "so.com",
  // Ecosia
  "ecosia.org",
  // Brave Search — deliberately the "search." subdomain, not the bare "brave.com"
  // company/browser domain, which would misclassify visits from Brave's blog or
  // marketing pages as organic search
  "search.brave.com",
]);

/**
 * Hostnames that match a search engine domain by suffix but aren't a search results
 * page — e.g. Gmail (mail.google.com). Without this, links clicked from an email would
 * be misclassified as organic search instead of referral. Checked before the suffix
 * match in matchSearchEngineDomain.
 */
export const SEARCH_ENGINE_EXCLUDED_HOSTNAMES: ReadonlySet<string> = new Set([
  "mail.google.com",
  "docs.google.com",
  "drive.google.com",
  "groups.google.com",
  "translate.google.com",
  "mail.yahoo.com",
  "mail.yandex.ru",
  "mail.yandex.com",
]);

/**
 * Label-boundary suffixes of a hostname, longest first: "news.google.com" ->
 * ["news.google.com", "google.com", "com"].
 */
const hostnameSuffixes = (hostname: string): string[] => {
  const labels = hostname.split(".");
  return labels.map((_, index) => labels.slice(index).join("."));
};

/**
 * Matched search engine domain (e.g. "google.com" for "news.google.com"), or undefined.
 * Suffix-by-label, not `endsWith` — so "google.com.evil.com" doesn't match "google.com":
 * its suffixes are "google.com.evil.com", "com.evil.com", "evil.com", "com".
 *
 * The exclusion check also matches by suffix, not just exact hostname — otherwise a
 * subdomain like "foo.mail.google.com" would bypass it while still matching "google.com".
 */
export const matchSearchEngineDomain = (hostname: string): string | undefined => {
  const suffixes = hostnameSuffixes(hostname);

  if (suffixes.some((suffix) => SEARCH_ENGINE_EXCLUDED_HOSTNAMES.has(suffix))) {
    return undefined;
  }

  return suffixes.find((suffix) => SEARCH_ENGINE_DOMAINS.has(suffix));
};
