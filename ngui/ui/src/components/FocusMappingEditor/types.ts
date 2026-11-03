// FOCUS field mapping, as stored by the API (config.mapping) and passed as the top-level `mapping` parameter.
// The backend schema lives in tools/cloud_adapter/clouds/focus.py (validate_mapping).

export type ApiMappingFieldName =
  | "cost"
  | "start_date"
  | "end_date"
  | "resource_id"
  | "resource_type"
  | "name"
  | "region"
  | "service_name"
  | "tags";

export type DecimalSeparator = "." | ",";

export type NormalizeOption = "strip" | "lower";

export type TagsMode = "json" | "list" | "prefixed_columns";

export type ResourceTypeRule = {
  column: string;
  match: string;
  type: string;
};

// The last fallback of a chain may be {"default": true}: "then use the default mapping"
export type ApiDefaultFallback = { default: true };

// A source (exactly one of columns, value, template) with an optional fallback
export type ApiMappingSource = {
  columns?: string[];
  value?: string | number;
  template?: string;
  fallback?: ApiMappingSource | ApiDefaultFallback;
};

// A field rule: a source chain and the field-level parameters (only at the top level of a field)
export type ApiMappingFieldRule = ApiMappingSource & {
  decimal_separator?: DecimalSeparator;
  normalize?: NormalizeOption[];
  rules?: ResourceTypeRule[];
  mode?: TagsMode;
  prefix?: string;
};

export type ApiMapping = Partial<Record<ApiMappingFieldName, ApiMappingFieldRule>>;

// Form model

export type MappingSourceType = "columns" | "value" | "template";

// One step of a field's chain. The first step is the field's own source, each next step is the previous step's fallback.
// Values of the source types that are not selected are kept while the user switches between them, but are not submitted.
export type MappingStepFormValues = {
  sourceType: MappingSourceType;
  columns: string[];
  // A number is kept as is when it comes from the API, so that the mapping round-trips losslessly
  value: string | number;
  template: string;
};

export type MappingFieldFormValues = {
  // false: the field is left on the default mapping and is not sent
  enabled: boolean;
  chain: MappingStepFormValues[];
  // Appends {"default": true} as the last fallback
  useDefaultAtEnd: boolean;
};

export type CostMappingFormValues = MappingFieldFormValues & {
  // null: not set (the API uses ".")
  decimalSeparator: DecimalSeparator | null;
};

export type ResourceIdMappingFormValues = MappingFieldFormValues & {
  // null: not set (with the default fallback the normalization of the default mapping is used, otherwise none)
  normalize: NormalizeOption[] | null;
};

export type ResourceTypeMappingFormValues = MappingFieldFormValues & {
  // An empty list is not sent (the API treats a missing list and an empty one the same way)
  rules: ResourceTypeRule[];
};

export type TagsMappingFormValues = MappingFieldFormValues & {
  // null: not set (the API uses "json"). In "prefixed_columns" mode the chain and useDefaultAtEnd are not sent.
  mode: TagsMode | null;
  // Sent only in "prefixed_columns" mode
  prefix: string;
};

export type FocusMappingFormValues = {
  cost: CostMappingFormValues;
  startDate: MappingFieldFormValues;
  endDate: MappingFieldFormValues;
  resourceId: ResourceIdMappingFormValues;
  resourceType: ResourceTypeMappingFormValues;
  name: MappingFieldFormValues;
  region: MappingFieldFormValues;
  serviceName: MappingFieldFormValues;
  tags: TagsMappingFormValues;
};

export type MappingFieldKey = keyof FocusMappingFormValues;
