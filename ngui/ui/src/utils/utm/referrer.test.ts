import { describe, expect, it } from "vitest";
import { getReferrerUtmParams, normalizeReferrerHostname } from "./referrer";
import { SEARCH_ENGINE_DOMAINS } from "./searchEngines";

describe("normalizeReferrerHostname", () => {
  it("returns undefined for an empty referrer", () => {
    expect(normalizeReferrerHostname("")).toBeUndefined();
  });

  it("returns undefined for a malformed referrer", () => {
    expect(normalizeReferrerHostname("not a url")).toBeUndefined();
  });

  it("returns undefined for a non-http(s) referrer", () => {
    expect(normalizeReferrerHostname("android-app://com.google.android.gm")).toBeUndefined();
  });

  it("lowercases the hostname", () => {
    expect(normalizeReferrerHostname("https://GOOGLE.com/search")).toBe("google.com");
  });

  it("strips a leading www.", () => {
    expect(normalizeReferrerHostname("https://www.hystax.com/")).toBe("hystax.com");
  });

  it("strips a trailing dot", () => {
    expect(normalizeReferrerHostname("https://google.com./search")).toBe("google.com");
  });

  it("drops path, port, query, fragment, and credentials", () => {
    expect(normalizeReferrerHostname("https://user:pass@example.com:8443/path?q=1#frag")).toBe("example.com");
  });
});

describe("getReferrerUtmParams", () => {
  it("classifies an empty referrer as direct", () => {
    expect(getReferrerUtmParams("", "app.example.com")).toEqual({ utm_source: "direct" });
  });

  it("classifies a malformed referrer as direct", () => {
    expect(getReferrerUtmParams("not a url", "app.example.com")).toEqual({ utm_source: "direct" });
  });

  it("classifies a same-hostname referrer as direct", () => {
    expect(getReferrerUtmParams("https://app.example.com/some-page", "app.example.com")).toEqual({
      utm_source: "direct",
    });
  });

  it("classifies a same-hostname referrer as direct regardless of www./case", () => {
    expect(getReferrerUtmParams("https://WWW.App.Example.com/page", "app.example.com")).toEqual({
      utm_source: "direct",
    });
  });

  it("classifies a recognized search engine as organic, using the matched base domain", () => {
    expect(getReferrerUtmParams("https://www.google.com/search?q=x", "app.example.com")).toEqual({
      utm_source: "google.com",
      utm_medium: "organic",
    });
  });

  it("classifies a search engine subdomain as organic under its base domain", () => {
    expect(getReferrerUtmParams("https://news.google.com/", "app.example.com")).toEqual({
      utm_source: "google.com",
      utm_medium: "organic",
    });
  });

  it.each([
    ["google.co.uk"],
    ["google.de"],
    ["google.co.jp"],
    ["bing.com"],
    ["yahoo.com"],
    ["duckduckgo.com"],
    ["yandex.ru"],
    ["baidu.com"],
    ["sogou.com"],
    ["so.com"],
    ["ecosia.org"],
    ["search.brave.com"],
  ])("classifies %s as organic", (domain) => {
    expect(getReferrerUtmParams(`https://${domain}/search`, "app.example.com")).toEqual({
      utm_source: domain,
      utm_medium: "organic",
    });
  });

  it("does not match a spoofed domain built on top of a search engine name", () => {
    expect(getReferrerUtmParams("https://google.com.evil.com/", "app.example.com")).toEqual({
      utm_source: "google.com.evil.com",
      utm_medium: "referral",
    });
  });

  it("classifies Gmail as referral, not organic", () => {
    expect(getReferrerUtmParams("https://mail.google.com/mail/u/0", "app.example.com")).toEqual({
      utm_source: "mail.google.com",
      utm_medium: "referral",
    });
  });

  it("classifies a subdomain of an excluded host as referral, not organic", () => {
    // The exclusion must match by suffix too — an exact-only check would let this bypass
    // the mail.google.com exclusion while still matching "google.com" by suffix
    expect(getReferrerUtmParams("https://foo.mail.google.com/x", "app.example.com")).toEqual({
      utm_source: "foo.mail.google.com",
      utm_medium: "referral",
    });
  });

  it("classifies a non-search brave.com subdomain as referral, not organic", () => {
    // Only "search.brave.com" is listed, deliberately not the bare "brave.com" domain
    expect(getReferrerUtmParams("https://blog.brave.com/some-post", "app.example.com")).toEqual({
      utm_source: "blog.brave.com",
      utm_medium: "referral",
    });
  });

  it("classifies any other external referrer as referral", () => {
    expect(getReferrerUtmParams("https://blog.example.org/post", "app.example.com")).toEqual({
      utm_source: "blog.example.org",
      utm_medium: "referral",
    });
  });

  it("does not special-case IP-literal or localhost referrers", () => {
    expect(getReferrerUtmParams("http://127.0.0.1/page", "app.example.com")).toEqual({
      utm_source: "127.0.0.1",
      utm_medium: "referral",
    });
  });
});

describe("SEARCH_ENGINE_DOMAINS safety", () => {
  it("contains no single-label entries that would match every hostname", () => {
    SEARCH_ENGINE_DOMAINS.forEach((domain) => {
      expect(domain).toContain(".");
    });
  });
});
