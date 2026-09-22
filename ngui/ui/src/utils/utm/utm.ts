import { MILLISECONDS_IN_SECOND, SECONDS_IN_DAY } from "utils/datetime";
import { getSearchParams, updateSearchParams } from "utils/network";
import { isEmptyObject } from "utils/objects";
import { CLICK_ID_ATTRIBUTIONS } from "./clickIds";
import { getReferrerUtmParams } from "./referrer";
import { UTM_PARAMS } from "./types";
import type { SeenClickId, StoredUtmParams, UtmParams } from "./types";

const STORAGE_KEY = "utmParams";
const SEEN_CLICK_IDS_STORAGE_KEY = "utmSeenClickIds";

// Attribution window; an expired set is treated as absent. Built from the already-exported
const TTL_MS = 90 * SECONDS_IN_DAY * MILLISECONDS_IN_SECOND;

const MAX_VALUE_LENGTH = 255;

// getSearchParams parses numbers/booleans and turns repeated parameters into arrays.
// This is the single place that turns a raw query value into a trimmed, length-capped
// string — reused by sanitizeUtmParams for every attribution source, not just explicit
// utm_*.
const readFirstValue = (rawValue: unknown): string | undefined => {
  const value = Array.isArray(rawValue) ? rawValue[0] : rawValue;

  if (value === null || value === undefined) {
    return undefined;
  }

  const stringValue = String(value).trim().slice(0, MAX_VALUE_LENGTH);
  return stringValue === "" ? undefined : stringValue;
};

const sanitizeUtmParams = (rawParams: Record<string, unknown>): UtmParams => {
  const params: UtmParams = {};

  UTM_PARAMS.forEach((name) => {
    const value = readFirstValue(rawParams[name]);
    if (value !== undefined) {
      params[name] = value;
    }
  });

  return params;
};

const readStoredUtmParams = (): StoredUtmParams | undefined => {
  try {
    const rawStored = localStorage.getItem(STORAGE_KEY);
    if (!rawStored) {
      return undefined;
    }

    const stored: unknown = JSON.parse(rawStored);
    if (
      typeof stored !== "object" ||
      stored === null ||
      typeof (stored as StoredUtmParams).capturedAt !== "number" ||
      typeof (stored as StoredUtmParams).params !== "object" ||
      (stored as StoredUtmParams).params === null
    ) {
      return undefined;
    }

    const age = Date.now() - (stored as StoredUtmParams).capturedAt;
    if (age < 0 || age > TTL_MS) {
      return undefined;
    }

    return stored as StoredUtmParams;
  } catch {
    // UTM tracking must never break the app (e.g. blocked storage, corrupted value)
    return undefined;
  }
};

/**
 * Click-ID values already captured, within the same attribution window as everything
 * else. Kept so that revisiting a stale ad-click URL — it's deliberately never stripped
 * from the address bar, see captureUtmParams — doesn't re-assert itself over a more
 * recent touch (explicit or a different click ID) captured in between.
 */
const readSeenClickIds = (): SeenClickId[] => {
  try {
    const raw = localStorage.getItem(SEEN_CLICK_IDS_STORAGE_KEY);
    if (!raw) {
      return [];
    }

    const parsed: unknown = JSON.parse(raw);
    if (!Array.isArray(parsed)) {
      return [];
    }

    const now = Date.now();
    return parsed.filter(
      (entry): entry is SeenClickId =>
        typeof entry === "object" &&
        entry !== null &&
        typeof (entry as SeenClickId).value === "string" &&
        typeof (entry as SeenClickId).capturedAt === "number" &&
        now - (entry as SeenClickId).capturedAt >= 0 &&
        now - (entry as SeenClickId).capturedAt <= TTL_MS
    );
  } catch {
    return [];
  }
};

const MAX_SEEN_CLICK_IDS = 20;

const recordSeenClickId = (value: string) => {
  try {
    const seen = readSeenClickIds();
    if (seen.some((entry) => entry.value === value)) {
      return;
    }

    const updated = [...seen, { value, capturedAt: Date.now() } satisfies SeenClickId];
    localStorage.setItem(SEEN_CLICK_IDS_STORAGE_KEY, JSON.stringify(updated.slice(-MAX_SEEN_CLICK_IDS)));
  } catch {
    // UTM tracking must never break the app
  }
};

// Setting a parameter to undefined removes it from the URL (nullish values are skipped on stringify)
const removeUtmParamsFromUrl = () => {
  updateSearchParams(Object.fromEntries(UTM_PARAMS.map((name) => [name, undefined])));
};

/**
 * Sanitizes and persists an attribution set, replacing whatever was stored before.
 * Returns whether anything was actually written — sanitizeUtmParams can drop every
 * field, and callers must not act as if a write succeeded when the result would have
 * been empty.
 */
const storeUtmParams = (params: Record<string, unknown>): boolean => {
  const sanitized = sanitizeUtmParams(params);
  if (isEmptyObject(sanitized)) {
    return false;
  }

  localStorage.setItem(STORAGE_KEY, JSON.stringify({ params: sanitized, capturedAt: Date.now() } satisfies StoredUtmParams));

  return true;
};

/**
 * The first recognized advertising click ID present in the URL, with the UTM
 * attribution it implies (see clickIds.ts) and its raw value — needed by the caller to
 * check against readSeenClickIds. Only consulted when no explicit utm_* is present.
 */
const getClickIdMatch = (rawParams: Record<string, unknown>): { value: string; utm: UtmParams } | undefined => {
  for (const { param, utm } of CLICK_ID_ATTRIBUTIONS) {
    const value = readFirstValue(rawParams[param]);
    if (value !== undefined) {
      return { value, utm };
    }
  }

  return undefined;
};

export const getStoredUtmParams = (): UtmParams | undefined => {
  const stored = readStoredUtmParams();
  if (!stored) {
    return undefined;
  }

  const params = sanitizeUtmParams(stored.params);

  return isEmptyObject(params) ? undefined : params;
};

/**
 * Restores this visit's attribution by priority:
 * 1. explicit utm_* in the URL  — last-touch, replaces anything stored
 * 2. a recognized ad click ID   — treated as an explicit campaign touch, also replaces
 * 3. a valid stored attribution — left untouched, not recalculated
 * 4. document.referrer          — direct / organic / referral, only when nothing else applies
 *
 * Click IDs are deliberately not stripped from the URL (unlike utm_*, cleaned below) —
 * gtag / Meta Pixel / Яндекс.Метрика read them asynchronously for their own ad-conversion
 * tracking, and removing the parameter here would break that. Because it lingers, the
 * same click ID can resurface on a later, unrelated page load (reload, back button, a
 * stale bookmark) — readSeenClickIds skips re-applying one already captured, so it
 * can't clobber a more recent touch.
 */
export const captureUtmParams = () => {
  try {
    const searchParams = getSearchParams();

    if (storeUtmParams(searchParams)) {
      // Clean the URL only once the set is persisted — a failed capture keeps the parameters visible
      removeUtmParamsFromUrl();
      return;
    }

    const clickIdMatch = getClickIdMatch(searchParams);
    if (clickIdMatch !== undefined) {
      const alreadySeen = readSeenClickIds().some((seen) => seen.value === clickIdMatch.value);
      if (!alreadySeen) {
        storeUtmParams(clickIdMatch.utm);
        recordSeenClickId(clickIdMatch.value);
      }
      return;
    }

    if (getStoredUtmParams()) {
      return;
    }

    storeUtmParams(getReferrerUtmParams(document.referrer, window.location.hostname));
  } catch {
    // UTM tracking must never break the app
  }
};

/**
 * Removes the stored UTM parameters and the seen-click-ID memory. Should only be called
 * after a successful registration — the stored set must survive plain sign-ins and live
 * demo sessions.
 */
export const clearUtmParams = () => {
  try {
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(SEEN_CLICK_IDS_STORAGE_KEY);
  } catch {
    // UTM tracking must never break the app
  }
};

/**
 * Runs an action with the stored UTM parameters and clears them once the attribution
 * has been delivered to the backend: after the action resolves and `shouldClear`
 * (checked against its result) agrees. A rejected action keeps the stored set,
 * so a retry is still attributed.
 */
export const consumeUtmParams = async <T>(
  action: (utm: UtmParams | undefined) => T | Promise<T>,
  { shouldClear = () => true }: { shouldClear?: (result: Awaited<T>) => boolean } = {}
): Promise<Awaited<T>> => {
  const result = await action(getStoredUtmParams());

  if (shouldClear(result)) {
    clearUtmParams();
  }

  return result;
};
