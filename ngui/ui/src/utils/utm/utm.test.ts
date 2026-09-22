import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { captureUtmParams, clearUtmParams, consumeUtmParams, getStoredUtmParams } from "./utm";

const STORAGE_KEY = "utmParams";

const setLocationSearch = (search: string) => {
  window.history.replaceState(null, "", search === "" ? window.location.pathname : `?${search}`);
};

describe("utm", () => {
  beforeEach(() => {
    localStorage.clear();
    setLocationSearch("");
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it("captures whitelisted utm parameters from the URL", () => {
    setLocationSearch(
      "utm_source=google&utm_medium=cpc&utm_campaign=spring&utm_term=shoes&utm_content=ad1&utm_nonsense=x&foo=bar"
    );

    captureUtmParams();

    expect(getStoredUtmParams()).toEqual({
      utm_source: "google",
      utm_medium: "cpc",
      utm_campaign: "spring",
      utm_term: "shoes",
      utm_content: "ad1",
    });
  });

  it("removes the captured utm parameters from the URL, keeping other parameters", () => {
    setLocationSearch("utm_source=google&utm_campaign=spring&foo=bar");

    captureUtmParams();

    expect(getStoredUtmParams()).toEqual({ utm_source: "google", utm_campaign: "spring" });
    expect(window.location.search).toBe("?foo=bar");
  });

  it("keeps the utm parameters in the URL when storage is unavailable", () => {
    const setItem = vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("storage disabled");
    });

    setLocationSearch("utm_source=google");

    captureUtmParams();

    expect(window.location.search).toBe("?utm_source=google");

    setItem.mockRestore();
  });

  it("stores derived direct attribution when the URL has no campaign signal", () => {
    setLocationSearch("foo=bar");

    captureUtmParams();

    expect(getStoredUtmParams()).toEqual({ utm_source: "direct" });
  });

  it("overwrites an existing set (last-touch)", () => {
    setLocationSearch("utm_source=google");
    captureUtmParams();

    setLocationSearch("utm_source=bing&utm_medium=cpc");
    captureUtmParams();

    expect(getStoredUtmParams()).toEqual({ utm_source: "bing", utm_medium: "cpc" });
  });

  it("keeps the existing set when the URL has no utm parameters", () => {
    setLocationSearch("utm_source=google");
    captureUtmParams();

    setLocationSearch("foo=bar");
    captureUtmParams();

    expect(getStoredUtmParams()).toEqual({ utm_source: "google" });
  });

  it("treats an expired set as absent", () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2026-01-01"));

    setLocationSearch("utm_source=google");
    captureUtmParams();

    // 91 days later — beyond the 90-day TTL
    vi.setSystemTime(new Date("2026-04-02"));

    expect(getStoredUtmParams()).toBeUndefined();

    setLocationSearch("utm_source=bing");
    captureUtmParams();

    expect(getStoredUtmParams()).toEqual({ utm_source: "bing" });
  });

  it("stringifies parsed values and truncates long ones", () => {
    setLocationSearch(`utm_campaign=12345&utm_term=${"a".repeat(500)}`);

    captureUtmParams();

    const params = getStoredUtmParams();
    expect(params?.utm_campaign).toBe("12345");
    expect(params?.utm_term).toBe("a".repeat(255));
  });

  it("takes the first value of a repeated parameter", () => {
    setLocationSearch("utm_source=first&utm_source=second");

    captureUtmParams();

    expect(getStoredUtmParams()).toEqual({ utm_source: "first" });
  });

  it("clears the stored set", () => {
    setLocationSearch("utm_source=google");
    captureUtmParams();

    clearUtmParams();

    expect(getStoredUtmParams()).toBeUndefined();
  });

  it("returns undefined for a corrupted stored value", () => {
    localStorage.setItem(STORAGE_KEY, "not-json");

    expect(getStoredUtmParams()).toBeUndefined();
  });

  it("consumeUtmParams passes the stored set to the action and clears it on success", async () => {
    setLocationSearch("utm_source=google");
    captureUtmParams();

    const action = vi.fn().mockResolvedValue("done");

    await expect(consumeUtmParams(action)).resolves.toBe("done");

    expect(action).toHaveBeenCalledWith({ utm_source: "google" });
    expect(getStoredUtmParams()).toBeUndefined();
  });

  it("consumeUtmParams keeps the stored set when the action rejects", async () => {
    setLocationSearch("utm_source=google");
    captureUtmParams();

    await expect(consumeUtmParams(() => Promise.reject(new Error("registration failed")))).rejects.toThrow(
      "registration failed"
    );

    expect(getStoredUtmParams()).toEqual({ utm_source: "google" });
  });

  it("consumeUtmParams keeps the stored set when shouldClear returns false", async () => {
    setLocationSearch("utm_source=google");
    captureUtmParams();

    const result = await consumeUtmParams(() => Promise.resolve({ register: false }), {
      shouldClear: ({ register }) => register,
    });

    expect(result).toEqual({ register: false });
    expect(getStoredUtmParams()).toEqual({ utm_source: "google" });
  });

  it("consumeUtmParams passes undefined to the action when nothing is stored", async () => {
    const action = vi.fn().mockResolvedValue(null);

    await consumeUtmParams(action);

    expect(action).toHaveBeenCalledWith(undefined);
  });

  it("survives broken localStorage without throwing", () => {
    const getItem = vi.spyOn(Storage.prototype, "getItem").mockImplementation(() => {
      throw new Error("storage disabled");
    });
    const setItem = vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new Error("storage disabled");
    });
    const removeItem = vi.spyOn(Storage.prototype, "removeItem").mockImplementation(() => {
      throw new Error("storage disabled");
    });

    setLocationSearch("utm_source=google");

    expect(() => captureUtmParams()).not.toThrow();
    expect(getStoredUtmParams()).toBeUndefined();
    expect(() => clearUtmParams()).not.toThrow();

    getItem.mockRestore();
    setItem.mockRestore();
    removeItem.mockRestore();
  });

  describe("click IDs", () => {
    it("maps gclid to ads/google when no explicit utm is present", () => {
      setLocationSearch("gclid=EAIaIQobChMI_test");

      captureUtmParams();

      expect(getStoredUtmParams()).toEqual({ utm_source: "ads", utm_medium: "google" });
    });

    it("maps yclid to ads/yandex", () => {
      setLocationSearch("yclid=123456789");

      captureUtmParams();

      expect(getStoredUtmParams()).toEqual({ utm_source: "ads", utm_medium: "yandex" });
    });

    it("maps fbclid to ads/facebook", () => {
      setLocationSearch("fbclid=IwAR0abc");

      captureUtmParams();

      expect(getStoredUtmParams()).toEqual({ utm_source: "ads", utm_medium: "facebook" });
    });

    it("never includes utm_campaign, utm_term, or utm_content", () => {
      setLocationSearch("gclid=EAIaIQobChMI_test");

      captureUtmParams();

      const stored = getStoredUtmParams();
      expect(stored?.utm_campaign).toBeUndefined();
      expect(stored?.utm_term).toBeUndefined();
      expect(stored?.utm_content).toBeUndefined();
    });

    it("is not stripped from the URL, unlike utm_*", () => {
      setLocationSearch("gclid=EAIaIQobChMI_test");

      captureUtmParams();

      expect(window.location.search).toBe("?gclid=EAIaIQobChMI_test");
    });

    it("is ignored when an explicit utm parameter is also present", () => {
      setLocationSearch("utm_source=manual&gclid=EAIaIQobChMI_test");

      captureUtmParams();

      expect(getStoredUtmParams()).toEqual({ utm_source: "manual" });
    });

    it("overwrites a previously stored attribution (last-touch)", () => {
      setLocationSearch("utm_source=newsletter");
      captureUtmParams();

      setLocationSearch("gclid=EAIaIQobChMI_test");
      captureUtmParams();

      expect(getStoredUtmParams()).toEqual({ utm_source: "ads", utm_medium: "google" });
    });

    it("does not re-apply a click ID already captured, so it can't clobber a more recent touch", () => {
      setLocationSearch("gclid=EAIaIQobChMI_test");
      captureUtmParams();

      setLocationSearch("utm_source=newsletter");
      captureUtmParams();

      // The gclid is still in the address bar (deliberately never stripped) — a reload,
      // back button, or stale bookmark can bring the browser back to this exact URL
      setLocationSearch("gclid=EAIaIQobChMI_test");
      captureUtmParams();

      expect(getStoredUtmParams()).toEqual({ utm_source: "newsletter" });
    });

    it("does not let a stale click ID clobber a different, more recent click ID either", () => {
      setLocationSearch("gclid=EAIaIQobChMI_test");
      captureUtmParams();

      setLocationSearch("fbclid=IwAR0abc");
      captureUtmParams();

      setLocationSearch("gclid=EAIaIQobChMI_test");
      captureUtmParams();

      expect(getStoredUtmParams()).toEqual({ utm_source: "ads", utm_medium: "facebook" });
    });

    it("still applies a genuinely different click ID normally", () => {
      setLocationSearch("gclid=EAIaIQobChMI_first");
      captureUtmParams();

      setLocationSearch("gclid=EAIaIQobChMI_second");
      captureUtmParams();

      expect(getStoredUtmParams()).toEqual({ utm_source: "ads", utm_medium: "google" });
    });

    it("clears the seen-click-ID memory along with the stored attribution", () => {
      setLocationSearch("gclid=EAIaIQobChMI_test");
      captureUtmParams();

      clearUtmParams();

      setLocationSearch("utm_source=newsletter");
      captureUtmParams();

      // Without clearUtmParams resetting the memory too, this revisit would be silently
      // ignored as "already seen" instead of being credited normally
      setLocationSearch("gclid=EAIaIQobChMI_test");
      captureUtmParams();

      expect(getStoredUtmParams()).toEqual({ utm_source: "ads", utm_medium: "google" });
    });
  });

  describe("stored attribution priority", () => {
    it("does not recalculate a valid stored attribution on an untagged visit", () => {
      vi.useFakeTimers();
      vi.setSystemTime(new Date("2026-01-01"));

      setLocationSearch("utm_source=newsletter&utm_medium=email");
      captureUtmParams();
      const stored = localStorage.getItem(STORAGE_KEY);

      vi.setSystemTime(new Date("2026-01-02"));
      setLocationSearch("");
      captureUtmParams();

      expect(localStorage.getItem(STORAGE_KEY)).toBe(stored);
    });
  });

  describe("referrer-derived attribution", () => {
    const mockReferrer = (value: string) => vi.spyOn(document, "referrer", "get").mockReturnValue(value);

    it("stores direct attribution when there is no referrer", () => {
      mockReferrer("");

      captureUtmParams();

      expect(getStoredUtmParams()).toEqual({ utm_source: "direct" });
    });

    it("stores organic attribution for a recognized search engine referrer", () => {
      mockReferrer("https://www.google.com/search?q=optscale");

      captureUtmParams();

      expect(getStoredUtmParams()).toEqual({ utm_source: "google.com", utm_medium: "organic" });
    });

    it("stores referral attribution for any other external referrer", () => {
      mockReferrer("https://blog.example.org/post");

      captureUtmParams();

      expect(getStoredUtmParams()).toEqual({ utm_source: "blog.example.org", utm_medium: "referral" });
    });

    it("stores direct attribution for a same-hostname referrer", () => {
      mockReferrer(`https://${window.location.hostname}/some-page`);

      captureUtmParams();

      expect(getStoredUtmParams()).toEqual({ utm_source: "direct" });
    });
  });
});
