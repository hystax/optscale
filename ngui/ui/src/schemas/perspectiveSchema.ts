import { FILTER_CONFIGS } from "components/Resources/filterConfigs";
import {
  CLEAN_EXPENSES_BREAKDOWN_TYPES,
  CLEAN_EXPENSES_BREAKDOWN_TYPES_LIST,
  CLEAN_EXPENSES_GROUP_TYPES_LIST,
} from "utils/constants";

const BREAKDOWN_BY_PROPERTY = "breakdownBy";
const CATEGORIZE_BY_PROPERTY = "breakdownBy";
const BREAKDOWN_DATA_PROPERTY = "breakdownData";
const GROUP_BY_PROPERTY = "groupBy";
const GROUP_BY_GROUP_BY_PROPERTY = "groupBy";
const GROUP_BY_GROUP_TYPE_PROPERTY = "groupType";
const FILTERS_PROPERTY = "filters";
const FILTER_VALUES_PROPERTY = "filterValues";
const APPLIED_FILTERS_PROPERTY = "appliedFilters";

const breakdownBySchema = {
  type: "string",
  enum: CLEAN_EXPENSES_BREAKDOWN_TYPES_LIST,
};

const breakdownDataSchema = {
  type: "object",
  additionalProperties: false,
  properties: {
    [CATEGORIZE_BY_PROPERTY]: {
      type: "string",
    },
    [GROUP_BY_PROPERTY]: {
      type: "object",
      additionalProperties: false,
      dependencies: {
        [GROUP_BY_GROUP_BY_PROPERTY]: [GROUP_BY_GROUP_TYPE_PROPERTY],
        [GROUP_BY_GROUP_TYPE_PROPERTY]: [GROUP_BY_GROUP_BY_PROPERTY],
      },
      properties: {
        [GROUP_BY_GROUP_BY_PROPERTY]: {
          type: "string",
        },
        [GROUP_BY_GROUP_TYPE_PROPERTY]: {
          type: "string",
          enum: CLEAN_EXPENSES_GROUP_TYPES_LIST,
        },
      },
    },
  },
};

const filtersSchema = {
  type: "object",
  required: [FILTER_VALUES_PROPERTY, APPLIED_FILTERS_PROPERTY],
  additionalProperties: false,
  properties: {
    [FILTER_VALUES_PROPERTY]: {
      type: "object",
      additionalProperties: false,
      properties: Object.values(FILTER_CONFIGS).reduce(
        (properties, filter) => ({
          ...properties,
          ...(filter.schema.filterValues ?? {}),
        }),
        {}
      ),
    },
    [APPLIED_FILTERS_PROPERTY]: {
      type: "object",
      additionalProperties: false,
      properties: Object.values(FILTER_CONFIGS).reduce(
        (properties, filter) => ({
          ...properties,
          ...(filter.schema.appliedFilter ?? {}),
        }),
        {}
      ),
    },
  },
  allOf: Object.values(FILTER_CONFIGS)
    .map((filter) => {
      const { id, apiName } = filter;

      return [
        {
          if: {
            required: [FILTER_VALUES_PROPERTY],
            properties: {
              [FILTER_VALUES_PROPERTY]: {
                type: "object",
                required: [apiName],
                properties: {
                  [apiName]: {
                    type: "array",
                  },
                },
              },
            },
          },
          then: {
            required: [APPLIED_FILTERS_PROPERTY],
            properties: {
              [APPLIED_FILTERS_PROPERTY]: {
                type: "object",
                required: [id],
                properties: {
                  [id]: {
                    type: "array",
                  },
                },
              },
            },
          },
        },
        {
          if: {
            required: [APPLIED_FILTERS_PROPERTY],
            properties: {
              [APPLIED_FILTERS_PROPERTY]: {
                type: "object",
                required: [id],
                properties: {
                  [id]: {
                    type: "array",
                  },
                },
              },
            },
          },
          then: {
            required: [FILTER_VALUES_PROPERTY],
            properties: {
              [FILTER_VALUES_PROPERTY]: {
                type: "object",
                required: [apiName],
                properties: {
                  [apiName]: {
                    type: "array",
                  },
                },
              },
            },
          },
        },
      ];
    })
    .flat(),
};

const propertiesSchema = {
  [BREAKDOWN_BY_PROPERTY]: breakdownBySchema,
  [BREAKDOWN_DATA_PROPERTY]: breakdownDataSchema,
  [FILTERS_PROPERTY]: filtersSchema,
};

const rootSchema = {
  type: "object",
  allOf: [
    {
      if: {
        properties: {
          [BREAKDOWN_BY_PROPERTY]: {
            const: CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES,
          },
        },
      },
      then: {
        properties: {
          [BREAKDOWN_DATA_PROPERTY]: {
            type: "object",
            required: [GROUP_BY_PROPERTY],
          },
        },
      },
    },
  ],
  required: [FILTERS_PROPERTY, BREAKDOWN_BY_PROPERTY, BREAKDOWN_DATA_PROPERTY],
  additionalProperties: false,
  properties: propertiesSchema,
};

export { breakdownBySchema, breakdownDataSchema, filtersSchema, propertiesSchema };

export default rootSchema;
