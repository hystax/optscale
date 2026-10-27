import { matchSearchEngineDomain } from "./searchEngines";
import type { UtmParams } from "./types";

// No parentheses — deliberately not the "(direct)" spelling of the usual Google
// Analytics convention. utm_medium is left unset rather than filled with a placeholder
// like "(none)": an absent field and an empty string reach the backend the same way,
// both dropped before utm fields are forwarded to the Auth service.
const DIRECT_UTM_PARAMS: UtmParams = { utm_source: "direct" };

const normalizeHostname = (hostname: string): string =>
  hostname
    .toLowerCase()
    .replace(/^www\./, "")
    .replace(/\.$/, "");

/**
 * Parses and normalizes a referrer's hostname: lowercased, without a leading "www.", a
 * trailing dot, or path/port/credentials/query/fragment (`hostname` already excludes
 * the port that `host` would include).
 *
 * Returns undefined for an empty, malformed, or non-http(s) referrer.
 */
export const normalizeReferrerHostname = (referrer: string): string | undefined => {
  if (referrer === "") {
    return undefined;
  }

  let url: URL;
  try {
    url = new URL(referrer);
  } catch {
    return undefined;
  }

  if (url.protocol !== "http:" && url.protocol !== "https:") {
    return undefined;
  }

  if (url.hostname === "") {
    return undefined;
  }

  return normalizeHostname(url.hostname);
};

/**
 * Classifies the current visit from document.referrer into direct, organic, or referral.
 *
 * - empty / malformed / non-http(s) / same-hostname referrer         -> "direct" (no medium)
 * - recognized search engine                                         -> matched domain / organic
 * - any other external referrer (IP literals and localhost included) -> normalized hostname / referral
 */
export const getReferrerUtmParams = (referrer: string, currentHostname: string): UtmParams => {
  const hostname = normalizeReferrerHostname(referrer);

  if (hostname === undefined) {
    return DIRECT_UTM_PARAMS;
  }

  if (hostname === normalizeHostname(currentHostname)) {
    return DIRECT_UTM_PARAMS;
  }

  const searchEngineDomain = matchSearchEngineDomain(hostname);
  if (searchEngineDomain !== undefined) {
    return { utm_source: searchEngineDomain, utm_medium: "organic" };
  }

  return { utm_source: hostname, utm_medium: "referral" };
};
