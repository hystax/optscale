export const UTM_PARAMS = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"] as const;

export type UtmParams = Partial<Record<(typeof UTM_PARAMS)[number], string>>;

export type StoredUtmParams = {
  params: UtmParams;
  capturedAt: number;
};

export type SeenClickId = {
  value: string;
  capturedAt: number;
};
