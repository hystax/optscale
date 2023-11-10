import { RESOURCE_FILTERS } from "components/Filters/constants";
import {
  CLEAN_EXPENSES_BREAKDOWN_TYPES,
  CLEAN_EXPENSES_BREAKDOWN_TYPES_LIST,
  CLEAN_EXPENSES_GROUP_TYPES_LIST,
  RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY_VALUES
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
  enum: CLEAN_EXPENSES_BREAKDOWN_TYPES_LIST
};

const breakdownDataSchema = {
  type: "object",
  additionalProperties: false,
  properties: {
    [CATEGORIZE_BY_PROPERTY]: {
      type: "string",
      enum: RESOURCES_EXPENSES_DAILY_BREAKDOWN_BY_VALUES
    },
    [GROUP_BY_PROPERTY]: {
      type: "object",
      additionalProperties: false,
      dependencies: {
        [GROUP_BY_GROUP_BY_PROPERTY]: [GROUP_BY_GROUP_TYPE_PROPERTY],
        [GROUP_BY_GROUP_TYPE_PROPERTY]: [GROUP_BY_GROUP_BY_PROPERTY]
      },
      properties: {
        [GROUP_BY_GROUP_BY_PROPERTY]: {
          type: "string"
        },
        [GROUP_BY_GROUP_TYPE_PROPERTY]: {
          type: "string",
          enum: CLEAN_EXPENSES_GROUP_TYPES_LIST
        }
      }
    }
  }
};

const filtersSchema = {
  type: "object",
  required: [FILTER_VALUES_PROPERTY, APPLIED_FILTERS_PROPERTY],
  additionalProperties: false,
  properties: {
    [FILTER_VALUES_PROPERTY]: {
      type: "object",
      properties: Object.fromEntries(
        RESOURCE_FILTERS.map((filter) => [
          filter.apiName,
          {
            type: "array",
            items: filter.filterItemSchema
          }
        ])
      )
    },
    [APPLIED_FILTERS_PROPERTY]: {
      type: "object",
      properties: Object.fromEntries(
        RESOURCE_FILTERS.map((filter) => [
          filter.filterName,
          {
            type: "array",
            items: filter.appliedFilterSchema
          }
        ])
      )
    }
  },
  allOf: RESOURCE_FILTERS.map(({ apiName, filterName }) => ({
    apiName,
    filterName
  }))
    .map((filter) => {
      const { apiName, filterName } = filter;

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
                    type: "array"
                  }
                }
              }
            }
          },
          then: {
            required: [APPLIED_FILTERS_PROPERTY],
            properties: {
              [APPLIED_FILTERS_PROPERTY]: {
                type: "object",
                required: [filterName],
                properties: {
                  [filterName]: {
                    type: "array"
                  }
                }
              }
            }
          }
        },
        {
          if: {
            required: [APPLIED_FILTERS_PROPERTY],
            properties: {
              [APPLIED_FILTERS_PROPERTY]: {
                type: "object",
                required: [filterName],
                properties: {
                  [filterName]: {
                    type: "array"
                  }
                }
              }
            }
          },
          then: {
            required: [FILTER_VALUES_PROPERTY],
            properties: {
              [FILTER_VALUES_PROPERTY]: {
                type: "object",
                required: [apiName],
                properties: {
                  [apiName]: {
                    type: "array"
                  }
                }
              }
            }
          }
        }
      ];
    })
    .flat()
};

const propertiesSchema = {
  [BREAKDOWN_BY_PROPERTY]: breakdownBySchema,
  [BREAKDOWN_DATA_PROPERTY]: breakdownDataSchema,
  [FILTERS_PROPERTY]: filtersSchema
};

const rootSchema = {
  type: "object",
  allOf: [
    {
      if: {
        properties: {
          [BREAKDOWN_BY_PROPERTY]: {
            const: CLEAN_EXPENSES_BREAKDOWN_TYPES.EXPENSES
          }
        }
      },
      then: {
        properties: {
          [BREAKDOWN_DATA_PROPERTY]: {
            type: "object",
            required: [GROUP_BY_PROPERTY]
          }
        }
      }
    }
  ],
  required: [FILTERS_PROPERTY, BREAKDOWN_BY_PROPERTY, BREAKDOWN_DATA_PROPERTY],
  additionalProperties: false,
  properties: propertiesSchema
};

export { breakdownBySchema, breakdownDataSchema, filtersSchema, propertiesSchema };

export default rootSchema;
