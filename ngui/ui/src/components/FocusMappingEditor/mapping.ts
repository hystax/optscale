import { MAPPING_FIELDS, MAPPING_SOURCE_TYPES, TAGS_MODES } from "./constants";
import type {
  ApiMapping,
  ApiMappingFieldRule,
  ApiMappingSource,
  FocusMappingFormValues,
  MappingFieldFormValues,
  MappingStepFormValues,
  TagsMode,
} from "./types";

export const getEmptyMappingStep = (): MappingStepFormValues => ({
  sourceType: MAPPING_SOURCE_TYPES.COLUMNS,
  columns: [],
  value: "",
  template: "",
});

const getDefaultFieldFormValues = (): MappingFieldFormValues => ({
  enabled: false,
  chain: [getEmptyMappingStep()],
  useDefaultAtEnd: false,
});

export const getDefaultFocusMappingFormValues = (): FocusMappingFormValues => ({
  cost: { ...getDefaultFieldFormValues(), decimalSeparator: null },
  startDate: getDefaultFieldFormValues(),
  endDate: getDefaultFieldFormValues(),
  resourceId: { ...getDefaultFieldFormValues(), normalize: null },
  resourceType: { ...getDefaultFieldFormValues(), rules: [] },
  name: getDefaultFieldFormValues(),
  region: getDefaultFieldFormValues(),
  serviceName: getDefaultFieldFormValues(),
  tags: { ...getDefaultFieldFormValues(), mode: null, prefix: "" },
});

// Form values -> API

const stepToApiSource = ({ sourceType, columns, value, template }: MappingStepFormValues): ApiMappingSource => {
  if (sourceType === MAPPING_SOURCE_TYPES.VALUE) {
    return { value };
  }
  if (sourceType === MAPPING_SOURCE_TYPES.TEMPLATE) {
    return { template };
  }
  return { columns };
};

// The first step is the field's own source, each next step is the previous step's fallback
const chainToApiSource = (chain: MappingStepFormValues[], useDefaultAtEnd: boolean): ApiMappingSource =>
  chain.reduceRight<ApiMappingSource | undefined>((fallback, step) => {
    const source = stepToApiSource(step);
    if (fallback) {
      return { ...source, fallback };
    }
    return useDefaultAtEnd ? { ...source, fallback: { default: true } } : source;
  }, undefined) ?? {};

// An unset mode is json
export const canTagsUseDefault = (mode: TagsMode | null) => mode === null || mode === TAGS_MODES.JSON;

const fieldToApiRule = (key: keyof FocusMappingFormValues, values: FocusMappingFormValues): ApiMappingFieldRule => {
  const field = values[key];

  if (key === "tags" && values.tags.mode === TAGS_MODES.PREFIXED_COLUMNS) {
    // Prefixed columns take no source and no default fallback
    return { mode: values.tags.mode, prefix: values.tags.prefix };
  }

  // The default fallback of the tags needs json mode (the tags of all default mappings are json)
  const useDefaultAtEnd = key === "tags" ? field.useDefaultAtEnd && canTagsUseDefault(values.tags.mode) : field.useDefaultAtEnd;

  const rule: ApiMappingFieldRule = chainToApiSource(field.chain, useDefaultAtEnd);

  if (key === "cost" && values.cost.decimalSeparator !== null) {
    rule.decimal_separator = values.cost.decimalSeparator;
  }
  if (key === "resourceId" && values.resourceId.normalize !== null) {
    rule.normalize = values.resourceId.normalize;
  }
  if (key === "resourceType" && values.resourceType.rules.length > 0) {
    rule.rules = values.resourceType.rules;
  }
  if (key === "tags" && values.tags.mode !== null) {
    rule.mode = values.tags.mode;
  }

  return rule;
};

// Fields left on defaults are omitted, so a mapping with no overridden field is {}
export const mappingFormValuesToApi = (values: FocusMappingFormValues): ApiMapping =>
  Object.fromEntries(
    MAPPING_FIELDS.filter(({ key }) => values[key].enabled).map(({ key, apiName }) => [apiName, fieldToApiRule(key, values)])
  );

export const isEmptyApiMapping = (mapping: ApiMapping | null | undefined) => Object.keys(mapping ?? {}).length === 0;

// API -> form values

const apiSourceToStep = (source: ApiMappingSource): MappingStepFormValues => {
  const step = getEmptyMappingStep();
  if (source.value !== undefined) {
    return { ...step, sourceType: MAPPING_SOURCE_TYPES.VALUE, value: source.value };
  }
  if (source.template !== undefined) {
    return { ...step, sourceType: MAPPING_SOURCE_TYPES.TEMPLATE, template: source.template };
  }
  return { ...step, sourceType: MAPPING_SOURCE_TYPES.COLUMNS, columns: source.columns ?? [] };
};

const isDefaultFallback = (fallback: ApiMappingSource["fallback"]) =>
  !!fallback && "default" in fallback && fallback.default === true;

const apiSourceToChain = (source: ApiMappingSource) => {
  const chain: MappingStepFormValues[] = [];
  let node: ApiMappingSource | undefined = source;
  let useDefaultAtEnd = false;

  while (node) {
    chain.push(apiSourceToStep(node));
    const { fallback }: ApiMappingSource = node;
    if (isDefaultFallback(fallback)) {
      useDefaultAtEnd = true;
      node = undefined;
    } else {
      node = fallback as ApiMappingSource | undefined;
    }
  }

  return { chain, useDefaultAtEnd };
};

const hasSource = (rule: ApiMappingFieldRule) =>
  rule.columns !== undefined || rule.value !== undefined || rule.template !== undefined;

export const mappingApiToFormValues = (mapping: ApiMapping | null | undefined): FocusMappingFormValues => {
  const values = getDefaultFocusMappingFormValues();

  MAPPING_FIELDS.forEach(({ key, apiName }) => {
    const rule = mapping?.[apiName];
    if (!rule) {
      return;
    }

    const field = values[key];
    field.enabled = true;

    // Tags in prefixed_columns mode have no source: keep the empty first step for a later switch to another mode
    if (hasSource(rule)) {
      const { chain, useDefaultAtEnd } = apiSourceToChain(rule);
      field.chain = chain;
      field.useDefaultAtEnd = useDefaultAtEnd;
    }
  });

  if (mapping?.cost?.decimal_separator !== undefined) {
    values.cost.decimalSeparator = mapping.cost.decimal_separator;
  }
  if (mapping?.resource_id?.normalize !== undefined) {
    values.resourceId.normalize = mapping.resource_id.normalize;
  }
  if (mapping?.resource_type?.rules !== undefined) {
    values.resourceType.rules = mapping.resource_type.rules;
  }
  if (mapping?.tags?.mode !== undefined) {
    values.tags.mode = mapping.tags.mode;
  }
  if (mapping?.tags?.prefix !== undefined) {
    values.tags.prefix = mapping.tags.prefix;
  }

  return values;
};
