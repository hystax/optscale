import type { ApiMappingFieldName, MappingFieldKey, MappingSourceType, TagsMode } from "./types";

// Path of the mapping form values (FocusMappingFormValues) in the Connect and Edit mapping forms
export const FOCUS_MAPPING_FIELD_NAME = "focusMapping";

export const MAPPING_SOURCE_TYPES = Object.freeze({
  COLUMNS: "columns",
  VALUE: "value",
  TEMPLATE: "template",
} as const satisfies Record<string, MappingSourceType>);

export const TAGS_MODES = Object.freeze({
  JSON: "json",
  LIST: "list",
  PREFIXED_COLUMNS: "prefixed_columns",
} as const satisfies Record<string, TagsMode>);

// Form keys of the mapping fields, in the order they are shown, with the API names and the label message ids
export const MAPPING_FIELDS: ReadonlyArray<{ key: MappingFieldKey; apiName: ApiMappingFieldName; messageId: string }> = [
  { key: "cost", apiName: "cost", messageId: "cost" },
  { key: "startDate", apiName: "start_date", messageId: "startDate" },
  { key: "endDate", apiName: "end_date", messageId: "endDate" },
  { key: "resourceId", apiName: "resource_id", messageId: "resourceId" },
  { key: "resourceType", apiName: "resource_type", messageId: "resourceType" },
  { key: "name", apiName: "name", messageId: "name" },
  { key: "region", apiName: "region", messageId: "region" },
  { key: "serviceName", apiName: "service_name", messageId: "service" },
  { key: "tags", apiName: "tags", messageId: "tags" },
];

// A {Column} placeholder of a template, the same expression as PLACEHOLDER_RE of the backend
export const TEMPLATE_PLACEHOLDER_REGEX = /\{[^{}]+\}/;

// Standard OptScale resource types suggested for a resource type rule; any other type can be typed
export const RESOURCE_TYPE_SUGGESTIONS = ["Instance", "Volume", "Snapshot", "Bucket", "IP Address"];
