import { describe, expect, it } from "vitest";
import { getDefaultFocusMappingFormValues, mappingApiToFormValues, mappingFormValuesToApi } from "./mapping";
import type { ApiMapping, FocusMappingFormValues, MappingStepFormValues } from "./types";

const step = (overrides: Partial<MappingStepFormValues>): MappingStepFormValues => ({
  sourceType: "columns",
  columns: [],
  value: "",
  template: "",
  ...overrides,
});

describe("mappingFormValuesToApi", () => {
  it("returns an empty mapping when every field is left on defaults", () => {
    expect(mappingFormValuesToApi(getDefaultFocusMappingFormValues())).toEqual({});
  });

  it("sends an overridden field taken from a list of columns", () => {
    const values: FocusMappingFormValues = getDefaultFocusMappingFormValues();
    values.cost = { ...values.cost, enabled: true, chain: [step({ columns: ["EffectiveCost", "BilledCost"] })] };

    expect(mappingFormValuesToApi(values)).toEqual({ cost: { columns: ["EffectiveCost", "BilledCost"] } });
  });
});

describe("mappingFormValuesToApi chains", () => {
  it("sends a constant and a template", () => {
    const values = getDefaultFocusMappingFormValues();
    values.serviceName = { ...values.serviceName, enabled: true, chain: [step({ sourceType: "value", value: "Azure" })] };
    values.name = {
      ...values.name,
      enabled: true,
      chain: [step({ sourceType: "template", template: "{ServiceName}/{SkuId}", columns: ["Ignored"] })],
    };

    expect(mappingFormValuesToApi(values)).toEqual({
      service_name: { value: "Azure" },
      name: { template: "{ServiceName}/{SkuId}" },
    });
  });

  it("turns each next step into the fallback of the previous one and ends the chain with the default mapping", () => {
    const values = getDefaultFocusMappingFormValues();
    values.region = {
      ...values.region,
      enabled: true,
      chain: [
        step({ columns: ["x_SkuRegion"] }),
        step({ sourceType: "template", template: "{x_Zone}-region" }),
        step({ sourceType: "value", value: "global" }),
      ],
      useDefaultAtEnd: true,
    };

    expect(mappingFormValuesToApi(values)).toEqual({
      region: {
        columns: ["x_SkuRegion"],
        fallback: { template: "{x_Zone}-region", fallback: { value: "global", fallback: { default: true } } },
      },
    });
  });

  it("sends the decimal separator of the cost only when it is set", () => {
    const values = getDefaultFocusMappingFormValues();
    values.cost = { ...values.cost, enabled: true, chain: [step({ columns: ["x_Cost"] })], decimalSeparator: "," };
    expect(mappingFormValuesToApi(values)).toEqual({ cost: { columns: ["x_Cost"], decimal_separator: "," } });

    values.cost.decimalSeparator = null;
    expect(mappingFormValuesToApi(values)).toEqual({ cost: { columns: ["x_Cost"] } });
  });

  it("does not send a field that is not overridden even if it has steps", () => {
    const values = getDefaultFocusMappingFormValues();
    values.endDate = { ...values.endDate, enabled: false, chain: [step({ columns: ["x_End"] })], useDefaultAtEnd: true };

    expect(mappingFormValuesToApi(values)).toEqual({});
  });
});

describe("mappingApiToFormValues", () => {
  it("leaves every field on defaults for an empty mapping", () => {
    expect(mappingApiToFormValues(undefined)).toEqual(getDefaultFocusMappingFormValues());
    expect(mappingApiToFormValues(null)).toEqual(getDefaultFocusMappingFormValues());
    expect(mappingApiToFormValues({})).toEqual(getDefaultFocusMappingFormValues());
  });
});

const roundTrip = (mapping: ApiMapping) => mappingFormValuesToApi(mappingApiToFormValues(mapping));

// Design examples and the default mappings of tools/cloud_adapter/clouds/focus.py
const IDENTITY_FALLBACK = {
  template: "{ServiceName}/{SkuId}",
  fallback: { template: "{ChargeCategory}/{ServiceName}", fallback: { columns: ["ChargeCategory"] } },
};
const GENERIC_TYPE_RULES = [
  { column: "ResourceType", match: "(?i)snapshot", type: "Snapshot" },
  { column: "ResourceType", match: "(?i)virtual machine|instance", type: "Instance" },
  { column: "ResourceType", match: "(?i)disk|volume", type: "Volume" },
  { column: "ResourceType", match: "(?i)bucket|storage account", type: "Bucket" },
  { column: "ResourceType", match: "(?i)ip address", type: "IP Address" },
];
const GENERIC_MAPPING: ApiMapping = {
  cost: { columns: ["BilledCost"], decimal_separator: "." },
  start_date: { columns: ["ChargePeriodStart"] },
  end_date: { columns: ["ChargePeriodEnd"] },
  resource_id: { columns: ["ResourceId", "CommitmentDiscountId"], normalize: ["strip"], fallback: IDENTITY_FALLBACK },
  resource_type: { rules: GENERIC_TYPE_RULES, columns: ["ServiceName"], fallback: { columns: ["ChargeCategory"] } },
  name: { columns: ["ResourceName"] },
  region: { columns: ["RegionId", "RegionName"] },
  service_name: { columns: ["ServiceName"] },
  tags: { columns: ["Tags"], mode: "json" },
};
const AWS_MAPPING: ApiMapping = {
  ...GENERIC_MAPPING,
  resource_type: {
    rules: [
      { column: "x_Operation", match: "^RunInstances", type: "Instance" },
      { column: "x_Operation", match: "^CreateSnapshot", type: "Snapshot" },
      { column: "x_Operation", match: "^CreateVolume", type: "Volume" },
      { column: "x_ServiceCode", match: "^AmazonS3$", type: "Bucket" },
      { column: "x_Operation", match: "^AssociateAddress", type: "IP Address" },
    ],
    columns: ["ServiceName"],
    fallback: { columns: ["ChargeCategory"] },
  },
};
const AZURE_MAPPING: ApiMapping = {
  ...GENERIC_MAPPING,
  resource_id: { columns: ["ResourceId", "CommitmentDiscountId"], normalize: ["strip", "lower"], fallback: IDENTITY_FALLBACK },
  resource_type: {
    rules: [
      { column: "x_ResourceType", match: "(?i)^microsoft\\.compute/virtualmachines$", type: "Instance" },
      { column: "x_ResourceType", match: "(?i)^microsoft\\.compute/disks$", type: "Volume" },
      ...GENERIC_TYPE_RULES,
    ],
    columns: ["ServiceName"],
    fallback: { columns: ["ChargeCategory"] },
  },
};
const OCI_MAPPING: ApiMapping = {
  ...GENERIC_MAPPING,
  resource_id: { columns: ["ResourceId"], normalize: ["strip"], fallback: IDENTITY_FALLBACK },
  region: { columns: ["RegionId", "RegionName", "Region"] },
};

const pick = (mapping: ApiMapping, fields: (keyof ApiMapping)[]): ApiMapping =>
  Object.fromEntries(fields.filter((field) => mapping[field]).map((field) => [field, mapping[field]]));

const BASIC_FIELDS: (keyof ApiMapping)[] = ["cost", "start_date", "end_date", "name", "region", "service_name"];

describe("round-trip API mapping -> form values -> API mapping", () => {
  it.each([
    ["Generic", GENERIC_MAPPING],
    ["AWS", AWS_MAPPING],
    ["Azure", AZURE_MAPPING],
    ["OCI", OCI_MAPPING],
  ])("keeps the basic fields of the %s default mapping", (_, mapping) => {
    const basicMapping = pick(mapping, BASIC_FIELDS);
    expect(roundTrip(basicMapping)).toEqual(basicMapping);
  });

  it.each([
    ["Generic", GENERIC_MAPPING],
    ["AWS", AWS_MAPPING],
    ["Azure", AZURE_MAPPING],
    ["OCI", OCI_MAPPING],
  ])("keeps the whole %s default mapping", (_, mapping) => {
    expect(roundTrip(mapping)).toEqual(mapping);
  });

  it("keeps the design examples with nested fallbacks and the default mapping at the end", () => {
    const mapping: ApiMapping = {
      cost: { columns: ["x_Cost"], decimal_separator: ",", fallback: { default: true } },
      region: { columns: ["x_SkuRegion"], fallback: { value: "global" } },
      service_name: { value: "Azure" },
      name: { template: "{x_Project}/{ResourceName}", fallback: { columns: ["ResourceName"], fallback: { default: true } } },
      resource_id: { template: "{SubAccountId}/{ResourceId}", normalize: ["strip", "lower"] },
      resource_type: {
        rules: [{ column: "x_Kind", match: "^db$", type: "Database" }],
        columns: ["x_Kind"],
        fallback: { default: true },
      },
      tags: { mode: "prefixed_columns", prefix: "tag." },
    };

    expect(roundTrip(mapping)).toEqual(mapping);
  });

  it("keeps a numeric constant as a number", () => {
    const mapping: ApiMapping = { cost: { value: 0 }, start_date: { columns: ["A"], fallback: { value: 20240101 } } };

    expect(roundTrip(mapping)).toEqual(mapping);
  });

  it("keeps an unset field parameter unset and an empty normalization empty", () => {
    expect(roundTrip({ resource_id: { columns: ["Id"], fallback: { default: true } } })).toEqual({
      resource_id: { columns: ["Id"], fallback: { default: true } },
    });
    expect(roundTrip({ resource_id: { columns: ["Id"], normalize: [] } })).toEqual({
      resource_id: { columns: ["Id"], normalize: [] },
    });
    expect(roundTrip({ tags: { columns: ["Tags"], fallback: { default: true } } })).toEqual({
      tags: { columns: ["Tags"], fallback: { default: true } },
    });
    expect(roundTrip({ tags: { columns: ["x_Labels"], mode: "list" } })).toEqual({
      tags: { columns: ["x_Labels"], mode: "list" },
    });
  });
});

describe("mappingApiToFormValues prefill", () => {
  it("shows a stored chain as ordered steps with the default mapping at the end", () => {
    const values = mappingApiToFormValues({
      region: { columns: ["x_SkuRegion"], fallback: { template: "{x_Zone}", fallback: { default: true } } },
      cost: { value: "1,5", decimal_separator: "," },
    });

    expect(values.region).toEqual({
      enabled: true,
      chain: [step({ columns: ["x_SkuRegion"] }), step({ sourceType: "template", template: "{x_Zone}" })],
      useDefaultAtEnd: true,
    });
    expect(values.cost).toEqual({
      enabled: true,
      chain: [step({ sourceType: "value", value: "1,5" })],
      useDefaultAtEnd: false,
      decimalSeparator: ",",
    });
    expect(values.startDate.enabled).toBe(false);
  });
});

describe("mappingFormValuesToApi field parameters", () => {
  it("sends tags in each mode", () => {
    const values = getDefaultFocusMappingFormValues();
    values.tags = { ...values.tags, enabled: true, chain: [step({ columns: ["Tags"] })], useDefaultAtEnd: true };
    expect(mappingFormValuesToApi(values)).toEqual({ tags: { columns: ["Tags"], fallback: { default: true } } });

    values.tags.mode = "json";
    expect(mappingFormValuesToApi(values)).toEqual({
      tags: { columns: ["Tags"], fallback: { default: true }, mode: "json" },
    });

    // The default fallback needs json mode, so the flag left from json mode is not sent
    values.tags.mode = "list";
    expect(mappingFormValuesToApi(values)).toEqual({ tags: { columns: ["Tags"], mode: "list" } });

    values.tags = { ...values.tags, mode: "prefixed_columns", prefix: "tag." };
    expect(mappingFormValuesToApi(values)).toEqual({ tags: { mode: "prefixed_columns", prefix: "tag." } });
  });

  it("sends the normalization of the resource id", () => {
    const values = getDefaultFocusMappingFormValues();
    values.resourceId = { ...values.resourceId, enabled: true, chain: [step({ columns: ["ResourceId"] })] };
    expect(mappingFormValuesToApi(values)).toEqual({ resource_id: { columns: ["ResourceId"] } });

    values.resourceId.normalize = ["strip", "lower"];
    expect(mappingFormValuesToApi(values)).toEqual({ resource_id: { columns: ["ResourceId"], normalize: ["strip", "lower"] } });
  });

  it("keeps the order of the resource type rules", () => {
    const rules = [
      { column: "x_Kind", match: "^vm$", type: "Instance" },
      { column: "x_Kind", match: "(?i)^disk", type: "Volume" },
      { column: "ResourceType", match: ".*", type: "Database" },
    ];
    const values = getDefaultFocusMappingFormValues();
    values.resourceType = { ...values.resourceType, enabled: true, chain: [step({ columns: ["ServiceName"] })], rules };

    expect(mappingFormValuesToApi(values)).toEqual({ resource_type: { columns: ["ServiceName"], rules } });
    expect(mappingApiToFormValues({ resource_type: { columns: ["ServiceName"], rules } }).resourceType.rules).toEqual(rules);
  });
});
