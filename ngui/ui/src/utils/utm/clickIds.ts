import type { UtmParams } from "./types";

/**
 * Advertising click-ID query parameters, mapped to the UTM attribution they imply when
 * no explicit utm_* parameters are present. A click ID alone can only identify the
 * advertising platform, not a campaign/ad/keyword — utm_campaign, utm_term and
 * utm_content stay absent unless supplied as explicit UTM parameters.
 *
 * utm_source is always the constant "ads"; the specific platform goes in utm_medium.
 * Not exhaustive — e.g. Microsoft/Bing Ads' msclkid and LinkedIn Ads' li_fat_id are not
 * covered (not yet confirmed with Marketing).
 *
 * Order matters: a URL carrying more than one click ID resolves by this list's order
 * (gclid, then yclid, then fbclid).
 */
export const CLICK_ID_ATTRIBUTIONS: ReadonlyArray<{ param: string; utm: UtmParams }> = [
  { param: "gclid", utm: { utm_source: "ads", utm_medium: "google" } },
  { param: "yclid", utm: { utm_source: "ads", utm_medium: "yandex" } },
  { param: "fbclid", utm: { utm_source: "ads", utm_medium: "facebook" } },
];
