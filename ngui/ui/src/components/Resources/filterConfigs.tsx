import AppsOutlinedIcon from "@mui/icons-material/AppsOutlined";
import BlockOutlinedIcon from "@mui/icons-material/BlockOutlined";
import CategoryOutlinedIcon from "@mui/icons-material/CategoryOutlined";
import CloudOutlinedIcon from "@mui/icons-material/CloudOutlined";
import DescriptionOutlinedIcon from "@mui/icons-material/DescriptionOutlined";
import DnsOutlinedIcon from "@mui/icons-material/DnsOutlined";
import ErrorOutlineOutlinedIcon from "@mui/icons-material/ErrorOutlineOutlined";
import FolderCopyOutlinedIcon from "@mui/icons-material/FolderCopyOutlined";
import FolderOutlinedIcon from "@mui/icons-material/FolderOutlined";
import LocalOfferOutlinedIcon from "@mui/icons-material/LocalOfferOutlined";
import LocationOnOutlinedIcon from "@mui/icons-material/LocationOnOutlined";
import MiscellaneousServicesOutlinedIcon from "@mui/icons-material/MiscellaneousServicesOutlined";
import PersonOutlineOutlinedIcon from "@mui/icons-material/PersonOutlineOutlined";
import RecommendOutlinedIcon from "@mui/icons-material/RecommendOutlined";
import SwapHorizOutlinedIcon from "@mui/icons-material/SwapHorizOutlined";
import ToggleOnOutlinedIcon from "@mui/icons-material/ToggleOnOutlined";
import { FormattedMessage } from "react-intl";
import CloudLabel from "components/CloudLabel";
import PoolLabel from "components/PoolLabel";
import ResourceTypeLabel from "components/ResourceTypeLabel";
import { intl } from "translations/react-intl-config";
import { isPoolIdWithSubPools } from "urls";
import { isEmptyArray } from "utils/arrays";
import {
  EMPTY_UUID,
  OPTSCALE_RESOURCE_TYPES,
  ANY_NETWORK_TRAFFIC_LOCATION,
  CLOUD_ACCOUNT_TYPES_LIST,
  POOL_TYPES_LIST,
} from "utils/constants";
import { EN_FORMAT, formatUTC, millisecondsToSeconds, moveDateToUTC, secondsToMilliseconds } from "utils/datetime";
import { getMetaFormattedName } from "utils/metadata";
import { getSearchParams } from "utils/network";
import { isNumber } from "utils/validation";

const getSelectionAppliedValuesFromSearchParams = (parameterName) => {
  const { [parameterName]: value } = getSearchParams();

  if ([null, undefined].includes(value)) {
    return [];
  }

  if (Array.isArray(value)) {
    return value;
  }

  return [value];
};

const getRangeAppliedFilterValuesFromSearchParams = (fromParameterName, toParameterName) => {
  const { [fromParameterName]: from, [toParameterName]: to } = getSearchParams();

  const range = {
    from: Number(from),
    to: Number(to),
  };

  return {
    from: isNumber(range.from) ? secondsToMilliseconds(range.from) : undefined,
    to: isNumber(range.to) ? secondsToMilliseconds(range.to) : undefined,
  };
};

export const FILTER_CONFIGS = {
  cloudAccountId: {
    id: "cloudAccountId",
    apiName: "cloud_account",
    type: "selection",
    label: <FormattedMessage id="dataSource" />,
    labelString: intl.formatMessage({ id: "dataSource" }),
    icon: <CloudOutlinedIcon />,
    renderItem: (item) => <CloudLabel id={item.id} name={item.name} type={item.type} disableLink />,
    renderSelectedItem: (item) => item.name,
    renderPerspectiveItem: (appliedValue, filterValues, { stringify = false } = {}) => {
      const item = filterValues.find((filterValue) => filterValue.id === appliedValue);

      if (!item) {
        return appliedValue;
      }

      return stringify ? item.name : <CloudLabel id={item.id} name={item.name} type={item.type} />;
    },
    searchPredicate: (item, query) => item.name.toLowerCase().includes(query.toLowerCase()),
    getValuesFromSearchParams: () => ({
      values: getSelectionAppliedValuesFromSearchParams("cloudAccountId"),
    }),
    getDefaultValue: () => ({
      values: [],
    }),
    isApplied: (appliedFilter) => !isEmptyArray(appliedFilter.values),
    transformers: {
      getItems: (availableDataSources) =>
        availableDataSources
          ?.filter((item) => item !== null)
          .map((item) => ({
            ...item,
            value: item.id,
          })) ?? [],
      getValue: (item) => item.id,
      toApi: (appliedFilter) => ({
        cloudAccountId: appliedFilter.values,
      }),
      filterFilterValuesByAppliedFilters: (filterValues, appliedFilters) =>
        filterValues.filter((filterValue) => {
          if (filterValue === null) {
            return appliedFilters.includes(EMPTY_UUID);
          }

          return appliedFilters.includes(filterValue.id);
        }),
    },
    schema: {
      filterValues: {
        cloud_account: {
          type: "array",
          items: {
            type: "object",
            required: ["id", "name", "type"],
            nullable: true,
            additionalProperties: false,
            properties: {
              id: {
                type: "string",
              },
              name: {
                type: "string",
              },
              type: {
                type: "string",
                enum: CLOUD_ACCOUNT_TYPES_LIST,
              },
              account_id: {
                type: "string",
                nullable: true,
              },
            },
          },
        },
      },
      appliedFilter: {
        cloudAccountId: {
          type: "array",
          items: {
            type: "string",
          },
        },
      },
    },
  },
  poolId: {
    id: "poolId",
    apiName: "pool",
    type: "selection",
    label: <FormattedMessage id="pool" />,
    labelString: intl.formatMessage({ id: "pool" }),
    icon: <FolderOutlinedIcon />,
    renderItem: (item) => <PoolLabel name={item.name} type={item.purpose} disableLink id={item.id} label={item.name} />,
    renderSelectedItem: (item) => item.name,
    searchPredicate: (item, query) => item.name.toLowerCase().includes(query.toLowerCase()),
    renderPerspectiveItem: (appliedValue, filterValues, { stringify = false } = {}) => {
      const withSubpools = isPoolIdWithSubPools(appliedValue);

      const item = filterValues.find(
        (filterValue) => filterValue.id === (withSubpools ? appliedValue.slice(0, -1) : appliedValue)
      );

      if (!item) {
        if (withSubpools) {
          return `${appliedValue.slice(0, -1)} ${intl.formatMessage({ id: "(withSubPools)" })}`;
        }

        return appliedValue;
      }

      if (stringify) {
        return `${item.name}${withSubpools ? ` ${intl.formatMessage({ id: "(withSubPools)" })}` : ""}`;
      }

      return <PoolLabel name={item.name} type={item.purpose} id={item.id} withSubpools={withSubpools} />;
    },
    getValuesFromSearchParams: () => {
      const values = getSelectionAppliedValuesFromSearchParams("poolId");

      const withSubPools = values.some((value) => isPoolIdWithSubPools(value));

      if (withSubPools) {
        return {
          values: values.filter((value) => isPoolIdWithSubPools(value)).map((value) => value.slice(0, -1)),
          settings: {
            withSubpools: true,
          },
        };
      }

      return {
        values: values,
        settings: {
          withSubpools: false,
        },
      };
    },
    getDefaultValue: () => ({
      values: [],
      settings: {
        withSubpools: false,
      },
    }),
    isApplied: (appliedFilter) => !isEmptyArray(appliedFilter.values),
    transformers: {
      getItems: (pools) =>
        pools?.map((item) => ({
          ...item,
          value: item.id,
        })) ?? [],
      getValue: (item) => item.id,
      toApi: (appliedFilter) => ({
        poolId: appliedFilter.settings?.withSubpools
          ? appliedFilter.values.map((poolId) => `${poolId}+`)
          : appliedFilter.values,
      }),
      filterFilterValuesByAppliedFilters: (filterValues, appliedFilters) =>
        filterValues.filter((filterValue) => appliedFilters.includes(filterValue.id)),
    },
    settings: [
      {
        name: "withSubpools",
        label: <FormattedMessage id="withSubPools" />,
      },
    ],
    schema: {
      filterValues: {
        pool: {
          type: "array",
          items: {
            type: "object",
            required: ["id", "name", "purpose"],
            additionalProperties: false,
            properties: {
              id: {
                type: "string",
              },
              name: {
                type: "string",
              },
              purpose: {
                type: "string",
                enum: POOL_TYPES_LIST,
              },
            },
          },
        },
      },
      appliedFilter: {
        poolId: {
          type: "array",
          items: {
            type: "string",
          },
        },
      },
    },
  },
  ownerId: {
    id: "ownerId",
    apiName: "owner",
    type: "selection",
    label: <FormattedMessage id="owner" />,
    labelString: intl.formatMessage({ id: "owner" }),
    icon: <PersonOutlineOutlinedIcon />,
    renderItem: (item) => item.name,
    renderSelectedItem: (item) => item.name,
    searchPredicate: (item, query) => item.name.toLowerCase().includes(query.toLowerCase()),
    renderPerspectiveItem: (appliedValue, filterValues) => {
      const item = filterValues.find((filterValue) => filterValue.id === appliedValue);

      if (!item) {
        return appliedValue;
      }

      return item.name;
    },
    getValuesFromSearchParams: () => ({
      values: getSelectionAppliedValuesFromSearchParams("ownerId"),
    }),
    getDefaultValue: () => ({
      values: [],
    }),
    isApplied: (appliedFilter) => !isEmptyArray(appliedFilter.values),
    transformers: {
      getItems: (owners) =>
        owners?.map((item) => ({
          ...item,
          value: item.id,
        })) ?? [],
      getValue: (item) => item.id,
      toApi: (appliedFilter) => ({
        ownerId: appliedFilter.values,
      }),
      filterFilterValuesByAppliedFilters: (filterValues, appliedFilters) =>
        filterValues.filter((filterValue) => appliedFilters.includes(filterValue.id)),
    },
    schema: {
      filterValues: {
        owner: {
          type: "array",
          items: {
            type: "object",
            required: ["id", "name"],
            additionalProperties: false,
            properties: {
              id: {
                type: "string",
              },
              name: {
                type: "string",
              },
            },
          },
        },
      },
      appliedFilter: {
        ownerId: {
          type: "array",
          items: {
            type: "string",
          },
        },
      },
    },
  },
  region: {
    id: "region",
    apiName: "region",
    type: "selection",
    label: <FormattedMessage id="region" />,
    labelString: intl.formatMessage({ id: "region" }),
    icon: <LocationOnOutlinedIcon />,
    renderItem: (item) => {
      if (item.value === EMPTY_UUID) {
        return item.name;
      }
      return <CloudLabel name={item.name} type={item.cloud_type} disableLink />;
    },
    renderSelectedItem: (item) => item.name,
    searchPredicate: (item, query) => item.name.toLowerCase().includes(query.toLowerCase()),
    renderPerspectiveItem: (appliedValue, filterValues, { stringify = false } = {}) => {
      const item = filterValues.find((filterValue) => {
        if (filterValue === null) {
          return appliedValue === EMPTY_UUID;
        }

        return filterValue.name === appliedValue;
      });

      if (item === undefined) {
        return appliedValue;
      }

      if (item === null) {
        return intl.formatMessage({ id: "notSet" });
      }

      return stringify ? item.name : <CloudLabel name={item.name} type={item.cloud_type} disableLink />;
    },
    getValuesFromSearchParams: () => ({
      values: getSelectionAppliedValuesFromSearchParams("region"),
    }),
    getDefaultValue: () => ({
      values: [],
    }),
    isApplied: (appliedFilter) => !isEmptyArray(appliedFilter.values),
    transformers: {
      getItems: (regions) =>
        regions?.map((item) => {
          if (item === null) {
            return {
              name: intl.formatMessage({ id: "notSet" }),
              value: EMPTY_UUID,
            };
          }
          return {
            ...item,
            value: item.name,
          };
        }) ?? [],
      getValue: (item) => (item === null ? EMPTY_UUID : item.name),
      toApi: (appliedFilter) => ({
        region: appliedFilter.values,
      }),
      filterFilterValuesByAppliedFilters: (filterValues, appliedFilters) =>
        filterValues.filter((filterValue) => {
          if (filterValue === null) {
            return appliedFilters.includes(EMPTY_UUID);
          }

          return appliedFilters.includes(filterValue.name);
        }),
    },
    schema: {
      filterValues: {
        region: {
          type: "array",
          items: {
            type: "object",
            nullable: true,
            required: ["name", "cloud_type"],
            additionalProperties: false,
            properties: {
              name: {
                type: "string",
              },
              cloud_type: {
                type: "string",
                enum: CLOUD_ACCOUNT_TYPES_LIST,
              },
            },
          },
        },
      },
      appliedFilter: {
        region: {
          type: "array",
          items: {
            type: "string",
          },
        },
      },
    },
  },
  serviceName: {
    id: "serviceName",
    apiName: "service_name",
    type: "selection",
    label: <FormattedMessage id="service" />,
    labelString: intl.formatMessage({ id: "service" }),
    icon: <MiscellaneousServicesOutlinedIcon />,
    renderItem: (item) => {
      if (item.value === EMPTY_UUID) {
        return item.name;
      }
      return <CloudLabel name={item.name} type={item.cloud_type} disableLink />;
    },
    renderSelectedItem: (item) => item.name,
    searchPredicate: (item, query) => item.name.toLowerCase().includes(query.toLowerCase()),
    renderPerspectiveItem: (appliedValue, filterValues, { stringify = false } = {}) => {
      const item = filterValues.find((filterValue) => {
        if (filterValue === null) {
          return appliedValue === EMPTY_UUID;
        }

        return filterValue.name === appliedValue;
      });

      if (item === undefined) {
        return appliedValue;
      }

      if (item === null) {
        return intl.formatMessage({ id: "notSet" });
      }

      return stringify ? item.name : <CloudLabel name={item.name} type={item.cloud_type} disableLink />;
    },
    getValuesFromSearchParams: () => ({
      values: getSelectionAppliedValuesFromSearchParams("serviceName"),
    }),
    getDefaultValue: () => ({
      values: [],
    }),
    isApplied: (appliedFilter) => !isEmptyArray(appliedFilter.values),
    transformers: {
      getItems: (services) =>
        services?.map((item) => {
          if (item === null) {
            return {
              name: intl.formatMessage({ id: "notSet" }),
              value: EMPTY_UUID,
            };
          }
          return {
            ...item,
            value: item.name,
          };
        }) ?? [],
      getValue: (item) => (item === null ? EMPTY_UUID : item.name),
      toApi: (appliedFilter) => ({
        serviceName: appliedFilter.values,
      }),
      filterFilterValuesByAppliedFilters: (filterValues, appliedFilters) =>
        filterValues.filter((filterValue) => {
          if (filterValue === null) {
            return appliedFilters.includes(EMPTY_UUID);
          }

          return appliedFilters.includes(filterValue.name);
        }),
    },
    schema: {
      filterValues: {
        service_name: {
          type: "array",
          items: {
            type: "object",
            nullable: true,
            required: ["name", "cloud_type"],
            additionalProperties: false,
            properties: {
              name: {
                type: "string",
              },
              cloud_type: {
                type: "string",
                enum: CLOUD_ACCOUNT_TYPES_LIST,
              },
            },
          },
        },
      },
      appliedFilter: {
        serviceName: {
          type: "array",
          items: {
            type: "string",
          },
        },
      },
    },
  },
  resourceType: {
    id: "resourceType",
    apiName: "resource_type",
    type: "selection",
    label: <FormattedMessage id="resourceType" />,
    labelString: intl.formatMessage({ id: "resourceType" }),
    icon: <CategoryOutlinedIcon />,
    renderItem: (item) => (
      <ResourceTypeLabel
        resourceInfo={{
          resourceType: item.name,
          clusterTypeId: item.type === OPTSCALE_RESOURCE_TYPES.CLUSTER,
          isEnvironment: item.type === OPTSCALE_RESOURCE_TYPES.ENVIRONMENT,
        }}
      />
    ),
    renderSelectedItem: (item) => item.name,
    searchPredicate: (item, query) => item.name.toLowerCase().includes(query.toLowerCase()),
    renderPerspectiveItem: (appliedValue, filterValues, { stringify = false } = {}) => {
      const item = filterValues.find((filterValue) => `${filterValue.name}:${filterValue.type}` === appliedValue);

      if (!item) {
        return appliedValue;
      }

      if (stringify) {
        return item.name;
      }

      return (
        <ResourceTypeLabel
          resourceInfo={{
            resourceType: item.name,
            clusterTypeId: item.type === OPTSCALE_RESOURCE_TYPES.CLUSTER,
            isEnvironment: item.type === OPTSCALE_RESOURCE_TYPES.ENVIRONMENT,
          }}
        />
      );
    },
    getValuesFromSearchParams: () => ({
      values: getSelectionAppliedValuesFromSearchParams("resourceType"),
    }),
    isApplied: (appliedFilter) => !isEmptyArray(appliedFilter.values),
    transformers: {
      getItems: (resourceTypes) =>
        resourceTypes?.map((item) => ({
          ...item,
          value: `${item.name}:${item.type}`,
        })) ?? [],
      getValue: (item) => `${item.name}:${item.type}`,
      toApi: (appliedFilter) => ({
        resourceType: appliedFilter.values,
      }),
      filterFilterValuesByAppliedFilters: (filterValues, appliedFilters) =>
        filterValues.filter((filterValue) => appliedFilters.includes(`${filterValue.name}:${filterValue.type}`)),
    },
    getDefaultValue: () => ({
      values: [],
    }),
    schema: {
      filterValues: {
        resource_type: {
          type: "array",
          items: {
            type: "object",
            required: ["name", "type"],
            additionalProperties: false,
            properties: {
              name: {
                type: "string",
              },
              type: {
                type: "string",
                enum: Object.values(OPTSCALE_RESOURCE_TYPES),
              },
            },
          },
        },
      },
      appliedFilter: {
        resourceType: {
          type: "array",
          items: {
            type: "string",
          },
        },
      },
    },
  },
  active: {
    id: "active",
    apiName: "active",
    type: "selection",
    label: <FormattedMessage id="activity" />,
    labelString: intl.formatMessage({ id: "activity" }),
    icon: <ToggleOnOutlinedIcon />,
    renderItem: (item) => item.name,
    renderSelectedItem: (item) => item.name,
    searchPredicate: (item, query) => item.name.toLowerCase().includes(query.toLowerCase()),
    renderPerspectiveItem: (appliedValue, filterValues) => {
      const item = filterValues.find((filterValue) => filterValue === appliedValue);

      if (item === undefined) {
        return appliedValue;
      }

      return item ? intl.formatMessage({ id: "active" }) : intl.formatMessage({ id: "billingOnly" });
    },
    getValuesFromSearchParams: () => ({
      values: getSelectionAppliedValuesFromSearchParams("active"),
    }),
    getDefaultValue: () => ({
      values: [],
    }),
    isApplied: (appliedFilter) => !isEmptyArray(appliedFilter.values),
    transformers: {
      getItems: (active) =>
        active?.map((value) => ({
          name: value ? intl.formatMessage({ id: "active" }) : intl.formatMessage({ id: "billingOnly" }),
          value: value,
        })) ?? [],
      getValue: (item) => item,
      toApi: (appliedFilter) => ({
        active: appliedFilter.values,
      }),
      filterFilterValuesByAppliedFilters: (filterValues, appliedFilters) =>
        filterValues.filter((filterValue) => appliedFilters.includes(filterValue)),
    },
    schema: {
      filterValues: {
        active: {
          type: "array",
          items: {
            type: "boolean",
          },
        },
      },
      appliedFilter: {
        active: {
          type: "array",
          items: {
            type: "boolean",
          },
        },
      },
    },
  },
  recommendations: {
    id: "recommendations",
    apiName: "recommendations",
    type: "selection",
    label: <FormattedMessage id="recommendations" />,
    labelString: intl.formatMessage({ id: "recommendations" }),
    icon: <RecommendOutlinedIcon />,
    renderItem: (item) => item.name,
    renderSelectedItem: (item) => item.name,
    searchPredicate: (item, query) => item.name.toLowerCase().includes(query.toLowerCase()),
    renderPerspectiveItem: (appliedValue, filterValues) => {
      const item = filterValues.find((filterValue) => filterValue === appliedValue);

      if (item === undefined) {
        return appliedValue;
      }

      return item ? intl.formatMessage({ id: "withRecommendations" }) : intl.formatMessage({ id: "withoutRecommendations" });
    },
    getValuesFromSearchParams: () => ({
      values: getSelectionAppliedValuesFromSearchParams("recommendations"),
    }),
    getDefaultValue: () => ({
      values: [],
    }),
    transformers: {
      getItems: (recommendations) =>
        recommendations?.map((value) => ({
          name: value
            ? intl.formatMessage({ id: "withRecommendations" })
            : intl.formatMessage({ id: "withoutRecommendations" }),
          value: value,
        })) ?? [],
      getValue: (item) => item,
      toApi: (appliedFilter) => ({
        recommendations: appliedFilter.values,
      }),
      filterFilterValuesByAppliedFilters: (filterValues, appliedFilters) =>
        filterValues.filter((filterValue) => appliedFilters.includes(filterValue)),
    },
    isApplied: (appliedFilter) => !isEmptyArray(appliedFilter.values),
    schema: {
      filterValues: {
        recommendations: {
          type: "array",
          items: {
            type: "boolean",
          },
        },
      },
      appliedFilter: {
        recommendations: {
          type: "array",
          items: {
            type: "boolean",
          },
        },
      },
    },
  },
  constraintViolated: {
    id: "constraintViolated",
    apiName: "constraint_violated",
    type: "selection",
    label: <FormattedMessage id="constraintViolations" />,
    labelString: intl.formatMessage({ id: "constraintViolations" }),
    icon: <ErrorOutlineOutlinedIcon />,
    renderItem: (item) => item.name,
    renderSelectedItem: (item) => item.name,
    searchPredicate: (item, query) => item.name.toLowerCase().includes(query.toLowerCase()),
    renderPerspectiveItem: (appliedValue, filterValues) => {
      const item = filterValues.find((filterValue) => filterValue === appliedValue);

      if (item === undefined) {
        return appliedValue;
      }

      return item ? intl.formatMessage({ id: "violated" }) : intl.formatMessage({ id: "notViolated" });
    },
    getValuesFromSearchParams: () => ({
      values: getSelectionAppliedValuesFromSearchParams("constraintViolated"),
    }),
    getDefaultValue: () => ({
      values: [],
    }),
    isApplied: (appliedFilter) => !isEmptyArray(appliedFilter.values),
    transformers: {
      getItems: (constraintViolated) =>
        constraintViolated?.map((value) => ({
          name: value ? intl.formatMessage({ id: "violated" }) : intl.formatMessage({ id: "notViolated" }),
          value: value,
        })) ?? [],
      getValue: (item) => item,
      toApi: (appliedFilter) => ({
        constraintViolated: appliedFilter.values,
      }),
      filterFilterValuesByAppliedFilters: (filterValues, appliedFilters) =>
        filterValues.filter((filterValue) => appliedFilters.includes(filterValue)),
    },
    schema: {
      filterValues: {
        constraint_violated: {
          type: "array",
          items: {
            type: "boolean",
          },
        },
      },
      appliedFilter: {
        constraintViolated: {
          type: "array",
          items: {
            type: "boolean",
          },
        },
      },
    },
  },
  firstSeen: {
    id: "firstSeen",
    apiName: "first_seen",
    fromName: "firstSeenFrom",
    fromApiName: "first_seen_gte",
    toName: "firstSeenTo",
    toApiName: "first_seen_lte",
    type: "range",
    label: <FormattedMessage id="firstSeen" />,
    labelString: intl.formatMessage({ id: "firstSeen" }),
    renderPerspectiveItem: (appliedValue) => {
      const { from, to } = appliedValue;

      if (from && to) {
        return `${formatUTC(from, EN_FORMAT)} - ${formatUTC(to, EN_FORMAT)}`;
      }

      if (from) {
        return `${intl.formatMessage({ id: "from" }).toLocaleLowerCase()} ${formatUTC(from, EN_FORMAT)}`;
      }

      if (to) {
        return `${intl.formatMessage({ id: "to" }).toLocaleLowerCase()} ${formatUTC(to, EN_FORMAT)}`;
      }
    },
    getValuesFromSearchParams: () => getRangeAppliedFilterValuesFromSearchParams("firstSeenFrom", "firstSeenTo"),
    getDefaultValue: () => ({
      from: undefined,
      to: undefined,
    }),
    isApplied: (appliedFilter) => !!(appliedFilter.from || appliedFilter.to),
    transformers: {
      getAppliedRange: (range) => ({
        from: range.from ? moveDateToUTC(range.from) : undefined,
        to: range.to ? moveDateToUTC(range.to) : undefined,
      }),
      getValue: (item) => ({
        from: item.from,
        to: item.to,
      }),
      toApi: (appliedFilter) => ({
        firstSeenFrom: appliedFilter.from ? millisecondsToSeconds(appliedFilter.from) : undefined,
        firstSeenTo: appliedFilter.to ? millisecondsToSeconds(appliedFilter.to) : undefined,
      }),
    },
    schema: {
      appliedFilter: {
        firstSeenFrom: {
          type: "number",
        },
        firstSeenTo: {
          type: "number",
        },
      },
    },
  },
  lastSeen: {
    id: "lastSeen",
    apiName: "last_seen",
    fromName: "lastSeenFrom",
    fromApiName: "last_seen_gte",
    toName: "lastSeenTo",
    toApiName: "last_seen_lte",
    type: "range",
    label: <FormattedMessage id="lastSeen" />,
    labelString: intl.formatMessage({ id: "lastSeen" }),
    renderPerspectiveItem: (appliedValue) => {
      const { from, to } = appliedValue;

      if (from && to) {
        return `${formatUTC(from, EN_FORMAT)} - ${formatUTC(to, EN_FORMAT)}`;
      }

      if (from) {
        return `${intl.formatMessage({ id: "from" }).toLocaleLowerCase()} ${formatUTC(from, EN_FORMAT)}`;
      }

      if (to) {
        return `${intl.formatMessage({ id: "to" }).toLocaleLowerCase()} ${formatUTC(to, EN_FORMAT)}`;
      }
    },
    getValuesFromSearchParams: () => getRangeAppliedFilterValuesFromSearchParams("lastSeenFrom", "lastSeenTo"),
    getDefaultValue: () => ({
      from: undefined,
      to: undefined,
    }),
    isApplied: (appliedFilter) => !!(appliedFilter.from || appliedFilter.to),
    transformers: {
      getAppliedRange: (range) => ({
        from: range.from ? moveDateToUTC(range.from) : undefined,
        to: range.to ? moveDateToUTC(range.to) : undefined,
      }),
      getValue: (item) => ({
        from: item.from,
        to: item.to,
      }),
      toApi: (appliedFilter) => ({
        lastSeenFrom: appliedFilter.from ? millisecondsToSeconds(appliedFilter.from) : undefined,
        lastSeenTo: appliedFilter.to ? millisecondsToSeconds(appliedFilter.to) : undefined,
      }),
    },
    schema: {
      appliedFilter: {
        lastSeenFrom: {
          type: "number",
        },
        lastSeenTo: {
          type: "number",
        },
      },
    },
  },
  tag: {
    id: "tag",
    apiName: "tag",
    type: "selection",
    label: <FormattedMessage id="tag" />,
    labelString: intl.formatMessage({ id: "tag" }),
    icon: <LocalOfferOutlinedIcon />,
    renderItem: (item) => item.name,
    renderSelectedItem: (item) => item.name,
    searchPredicate: (item, query) => item.name.toLowerCase().includes(query.toLowerCase()),
    renderPerspectiveItem: (appliedValue, filterValues) => {
      const item = filterValues.find((filterValue) => filterValue === appliedValue);

      if (item === undefined) {
        return appliedValue;
      }

      return item;
    },
    getValuesFromSearchParams: () => ({
      values: getSelectionAppliedValuesFromSearchParams("tag"),
    }),
    getDefaultValue: () => ({
      values: [],
    }),
    isApplied: (appliedFilter) => !isEmptyArray(appliedFilter.values),
    transformers: {
      getItems: (tags) =>
        tags?.map((tag) => ({
          name: tag,
          value: tag,
        })) ?? [],
      getValue: (item) => item,
      toApi: (appliedFilter) => ({
        tag: appliedFilter.values,
      }),
      filterFilterValuesByAppliedFilters: (filterValues, appliedFilters) =>
        filterValues.filter((filterValue) => appliedFilters.includes(filterValue)),
    },
    schema: {
      filterValues: {
        tag: {
          type: "array",
          items: {
            type: "string",
          },
        },
      },
      appliedFilter: {
        tag: {
          type: "array",
          items: {
            type: "string",
          },
        },
      },
    },
  },
  meta: {
    id: "meta",
    apiName: "meta",
    type: "selection",
    label: <FormattedMessage id="meta" />,
    labelString: intl.formatMessage({ id: "meta" }),
    icon: <DescriptionOutlinedIcon />,
    renderItem: (item) => getMetaFormattedName(item.name),
    renderSelectedItem: (item) => getMetaFormattedName(item.name),
    searchPredicate: (item, query) => getMetaFormattedName(item.name).toLowerCase().includes(query.toLowerCase()),
    renderPerspectiveItem: (appliedValue, filterValues) => {
      const item = filterValues.find((filterValue) => filterValue === appliedValue);

      if (item === undefined) {
        return appliedValue;
      }

      return getMetaFormattedName(item);
    },
    getValuesFromSearchParams: () => ({
      values: getSelectionAppliedValuesFromSearchParams("meta"),
    }),
    getDefaultValue: () => ({
      values: [],
    }),
    isApplied: (appliedFilter) => !isEmptyArray(appliedFilter.values),
    transformers: {
      getItems: (metaKeys) =>
        metaKeys?.map((meta) => ({
          name: meta,
          value: meta,
        })) ?? [],
      getValue: (item) => item,
      toApi: (appliedFilter) => ({
        meta: appliedFilter.values,
      }),
      filterFilterValuesByAppliedFilters: (filterValues, appliedFilters) =>
        filterValues.filter((filterValue) => appliedFilters.includes(filterValue)),
    },
    schema: {
      filterValues: {
        meta: {
          type: "array",
          items: {
            type: "string",
          },
        },
      },
      appliedFilter: {
        meta: {
          type: "array",
          items: {
            type: "string",
          },
        },
      },
    },
  },
  withoutTag: {
    id: "withoutTag",
    apiName: "without_tag",
    type: "selection",
    label: <FormattedMessage id="withoutTag" />,
    labelString: intl.formatMessage({ id: "withoutTag" }),
    icon: <BlockOutlinedIcon />,
    renderItem: (item) => item.name,
    renderSelectedItem: (item) => item.name,
    searchPredicate: (item, query) => item.name.toLowerCase().includes(query.toLowerCase()),
    renderPerspectiveItem: (appliedValue, filterValues) => {
      const item = filterValues.find((filterValue) => filterValue === appliedValue);

      if (item === undefined) {
        return appliedValue;
      }

      return item;
    },
    getValuesFromSearchParams: () => ({
      values: getSelectionAppliedValuesFromSearchParams("withoutTag"),
    }),
    getDefaultValue: () => ({
      values: [],
    }),
    isApplied: (appliedFilter) => !isEmptyArray(appliedFilter.values),
    transformers: {
      getItems: (withoutTags) =>
        withoutTags?.map((tag) => ({
          name: tag,
          value: tag,
        })) ?? [],
      getValue: (item) => item,
      toApi: (appliedFilter) => ({
        withoutTag: appliedFilter.values,
      }),
      filterFilterValuesByAppliedFilters: (filterValues, appliedFilters) =>
        filterValues.filter((filterValue) => appliedFilters.includes(filterValue)),
    },
    schema: {
      filterValues: {
        without_tag: {
          type: "array",
          items: {
            type: "string",
          },
        },
      },
      appliedFilter: {
        withoutTag: {
          type: "array",
          items: {
            type: "string",
          },
        },
      },
    },
  },
  networkTrafficFrom: {
    id: "networkTrafficFrom",
    apiName: "traffic_from",
    type: "selection",
    label: <FormattedMessage id="paidNetworkTrafficFrom" />,
    labelString: intl.formatMessage({ id: "paidNetworkTrafficFrom" }),
    icon: <SwapHorizOutlinedIcon />,
    renderItem: (item) => {
      if (item.value === ANY_NETWORK_TRAFFIC_LOCATION) {
        return item.name;
      }
      return <CloudLabel name={item.name} type={item.cloud_type} disableLink />;
    },
    renderSelectedItem: (item) => item.name,
    searchPredicate: (item, query) => item.name.toLowerCase().includes(query.toLowerCase()),
    renderPerspectiveItem: (appliedValue, filterValues, { stringify = false } = {}) => {
      const item = filterValues.find((filterValue) => {
        if (filterValue === ANY_NETWORK_TRAFFIC_LOCATION) {
          return appliedValue === ANY_NETWORK_TRAFFIC_LOCATION;
        }

        return `${filterValue.name}:${filterValue.cloud_type}` === appliedValue;
      });

      if (item === undefined) {
        return appliedValue;
      }

      if (item === ANY_NETWORK_TRAFFIC_LOCATION) {
        return intl.formatMessage({ id: "any" });
      }

      if (stringify) {
        return item.name;
      }

      return <CloudLabel name={item.name} type={item.cloud_type} disableLink />;
    },
    getValuesFromSearchParams: () => ({
      values: getSelectionAppliedValuesFromSearchParams("networkTrafficFrom"),
    }),
    getDefaultValue: () => ({
      values: [],
    }),
    isApplied: (appliedFilter) => !isEmptyArray(appliedFilter.values),
    transformers: {
      getItems: (networkTrafficFrom) =>
        networkTrafficFrom?.map((item) => {
          if (item === ANY_NETWORK_TRAFFIC_LOCATION) {
            return {
              name: intl.formatMessage({ id: "any" }),
              value: item,
            };
          }

          return {
            name: item.name,
            value: `${item.name}:${item.cloud_type}`,
            cloud_type: item.cloud_type,
          };
        }) ?? [],
      getValue: (item) => `${item.name}:${item.cloud_type}`,
      toApi: (appliedFilter) => ({
        networkTrafficFrom: appliedFilter.values,
      }),
      filterFilterValuesByAppliedFilters: (filterValues, appliedFilters) =>
        filterValues.filter((filterValue) => {
          if (filterValue === ANY_NETWORK_TRAFFIC_LOCATION) {
            return appliedFilters.includes(ANY_NETWORK_TRAFFIC_LOCATION);
          }

          return appliedFilters.includes(`${filterValue.name}:${filterValue.cloud_type}`);
        }),
    },
    schema: {
      filterValues: {
        traffic_from: {
          type: "array",
          items: {
            oneOf: [
              {
                type: "object",
                required: ["name", "cloud_type"],
                additionalProperties: false,
                properties: {
                  name: {
                    type: "string",
                  },
                  cloud_type: {
                    type: "string",
                    enum: CLOUD_ACCOUNT_TYPES_LIST,
                  },
                },
              },
              {
                type: "string",
                const: "ANY",
              },
            ],
          },
        },
      },
      appliedFilter: {
        networkTrafficFrom: {
          type: "array",
          items: {
            type: "string",
          },
        },
      },
    },
  },
  networkTrafficTo: {
    id: "networkTrafficTo",
    apiName: "traffic_to",
    type: "selection",
    label: <FormattedMessage id="paidNetworkTrafficTo" />,
    labelString: intl.formatMessage({ id: "paidNetworkTrafficTo" }),
    icon: <SwapHorizOutlinedIcon />,
    renderItem: (item) => {
      if (item.value === ANY_NETWORK_TRAFFIC_LOCATION) {
        return item.name;
      }
      return <CloudLabel name={item.name} type={item.cloud_type} disableLink />;
    },
    renderSelectedItem: (item) => item.name,
    searchPredicate: (item, query) => item.name.toLowerCase().includes(query.toLowerCase()),
    renderPerspectiveItem: (appliedValue, filterValues, { stringify = false } = {}) => {
      const item = filterValues.find((filterValue) => {
        if (filterValue === ANY_NETWORK_TRAFFIC_LOCATION) {
          return appliedValue === ANY_NETWORK_TRAFFIC_LOCATION;
        }

        return `${filterValue.name}:${filterValue.cloud_type}` === appliedValue;
      });

      if (item === undefined) {
        return appliedValue;
      }

      if (item === ANY_NETWORK_TRAFFIC_LOCATION) {
        return intl.formatMessage({ id: "any" });
      }

      if (stringify) {
        return item.name;
      }

      return <CloudLabel name={item.name} type={item.cloud_type} disableLink />;
    },
    getValuesFromSearchParams: () => ({
      values: getSelectionAppliedValuesFromSearchParams("networkTrafficTo"),
    }),
    getDefaultValue: () => ({
      values: [],
    }),
    isApplied: (appliedFilter) => !isEmptyArray(appliedFilter.values),
    transformers: {
      getItems: (networkTrafficTo) =>
        networkTrafficTo?.map((item) => {
          if (item === ANY_NETWORK_TRAFFIC_LOCATION) {
            return {
              name: intl.formatMessage({ id: "any" }),
              value: item,
            };
          }
          return {
            name: item.name,
            value: `${item.name}:${item.cloud_type}`,
            cloud_type: item.cloud_type,
          };
        }) ?? [],
      getValue: (item) => `${item.name}:${item.cloud_type}`,
      toApi: (appliedFilter) => ({
        networkTrafficTo: appliedFilter.values,
      }),
      filterFilterValuesByAppliedFilters: (filterValues, appliedFilters) =>
        filterValues.filter((filterValue) => {
          if (filterValue === ANY_NETWORK_TRAFFIC_LOCATION) {
            return appliedFilters.includes(ANY_NETWORK_TRAFFIC_LOCATION);
          }

          return appliedFilters.includes(`${filterValue.name}:${filterValue.cloud_type}`);
        }),
    },
    schema: {
      filterValues: {
        traffic_to: {
          type: "array",
          items: {
            oneOf: [
              {
                type: "object",
                required: ["name", "cloud_type"],
                additionalProperties: false,
                properties: {
                  name: {
                    type: "string",
                  },
                  cloud_type: {
                    type: "string",
                    enum: CLOUD_ACCOUNT_TYPES_LIST,
                  },
                },
              },
              {
                type: "string",
                const: "ANY",
              },
            ],
          },
        },
      },
      appliedFilter: {
        networkTrafficTo: {
          type: "array",
          items: {
            type: "string",
          },
        },
      },
    },
  },
  k8sNode: {
    id: "k8sNode",
    apiName: "k8s_node",
    type: "selection",
    label: <FormattedMessage id="k8sNode" />,
    labelString: intl.formatMessage({ id: "k8sNode" }),
    icon: <DnsOutlinedIcon />,
    renderItem: (item) => <CloudLabel name={item.name} type={item.cloud_type} disableLink />,
    renderSelectedItem: (item) => item.name,
    searchPredicate: (item, query) => item.name.toLowerCase().includes(query.toLowerCase()),
    renderPerspectiveItem: (appliedValue, filterValues, { stringify = false } = {}) => {
      const item = filterValues.find((filterValue) => {
        if (filterValue === null) {
          return appliedValue === EMPTY_UUID;
        }

        return filterValue.name === appliedValue;
      });

      if (item === undefined) {
        return appliedValue;
      }

      if (item === null) {
        return intl.formatMessage({ id: "notSet" });
      }

      if (stringify) {
        return item.name;
      }

      return <CloudLabel name={item.name} type={item.cloud_type} disableLink />;
    },
    getValuesFromSearchParams: () => ({
      values: getSelectionAppliedValuesFromSearchParams("k8sNode"),
    }),
    getDefaultValue: () => ({
      values: [],
    }),
    isApplied: (appliedFilter) => !isEmptyArray(appliedFilter.values),
    transformers: {
      getItems: (k8sNodes) =>
        k8sNodes?.map((item) => {
          if (item === null) {
            return {
              name: intl.formatMessage({ id: "notSet" }),
              value: EMPTY_UUID,
            };
          }
          return {
            name: item.name,
            value: item.name,
            cloud_type: item.cloud_type,
          };
        }) ?? [],
      getValue: (item) => (item === null ? EMPTY_UUID : item.name),
      toApi: (appliedFilter) => ({
        k8sNode: appliedFilter.values,
      }),
      filterFilterValuesByAppliedFilters: (filterValues, appliedFilters) =>
        filterValues.filter((filterValue) => {
          if (filterValue === null) {
            return appliedFilters.includes(EMPTY_UUID);
          }

          return appliedFilters.includes(filterValue.name);
        }),
    },
    schema: {
      filterValues: {
        k8s_node: {
          type: "array",
          items: {
            type: "object",
            nullable: true,
            required: ["name", "cloud_type"],
            additionalProperties: false,
            properties: {
              name: {
                type: "string",
              },
              cloud_type: {
                type: "string",
                enum: CLOUD_ACCOUNT_TYPES_LIST,
              },
            },
          },
        },
      },
      appliedFilter: {
        k8sNode: {
          type: "array",
          items: {
            type: "string",
          },
        },
      },
    },
  },
  k8sService: {
    id: "k8sService",
    apiName: "k8s_service",
    type: "selection",
    label: <FormattedMessage id="k8sService" />,
    labelString: intl.formatMessage({ id: "k8sService" }),
    icon: <AppsOutlinedIcon />,
    renderItem: (item) => <CloudLabel name={item.name} type={item.cloud_type} disableLink />,
    renderSelectedItem: (item) => item.name,
    searchPredicate: (item, query) => item.name.toLowerCase().includes(query.toLowerCase()),
    renderPerspectiveItem: (appliedValue, filterValues, { stringify = false } = {}) => {
      const item = filterValues.find((filterValue) => {
        if (filterValue === null) {
          return appliedValue === EMPTY_UUID;
        }

        return filterValue.name === appliedValue;
      });

      if (item === undefined) {
        return appliedValue;
      }

      if (item === null) {
        return intl.formatMessage({ id: "notSet" });
      }

      if (stringify) {
        return item.name;
      }

      return <CloudLabel name={item.name} type={item.cloud_type} disableLink />;
    },
    getValuesFromSearchParams: () => ({
      values: getSelectionAppliedValuesFromSearchParams("k8sService"),
    }),
    getDefaultValue: () => ({
      values: [],
    }),
    isApplied: (appliedFilter) => !isEmptyArray(appliedFilter.values),
    transformers: {
      getItems: (k8sServices) =>
        k8sServices?.map((item) => {
          if (item === null) {
            return {
              name: intl.formatMessage({ id: "notSet" }),
              value: EMPTY_UUID,
            };
          }
          return {
            name: item.name,
            value: item.name,
            cloud_type: item.cloud_type,
          };
        }) ?? [],
      getValue: (item) => (item === null ? EMPTY_UUID : item.name),
      toApi: (appliedFilter) => ({
        k8sService: appliedFilter.values,
      }),
      filterFilterValuesByAppliedFilters: (filterValues, appliedFilters) =>
        filterValues.filter((filterValue) => {
          if (filterValue === null) {
            return appliedFilters.includes(EMPTY_UUID);
          }

          return appliedFilters.includes(filterValue.name);
        }),
    },
    schema: {
      filterValues: {
        k8s_service: {
          type: "array",
          items: {
            type: "object",
            nullable: true,
            required: ["name", "cloud_type"],
            additionalProperties: false,
            properties: {
              name: {
                type: "string",
              },
              cloud_type: {
                type: "string",
                enum: CLOUD_ACCOUNT_TYPES_LIST,
              },
            },
          },
        },
      },
      appliedFilter: {
        k8sService: {
          type: "array",
          items: {
            type: "string",
          },
        },
      },
    },
  },
  k8sNamespace: {
    id: "k8sNamespace",
    apiName: "k8s_namespace",
    type: "selection",
    label: <FormattedMessage id="k8sNamespace" />,
    labelString: intl.formatMessage({ id: "k8sNamespace" }),
    icon: <FolderCopyOutlinedIcon />,
    renderItem: (item) => <CloudLabel name={item.name} type={item.cloud_type} disableLink />,
    renderSelectedItem: (item) => item.name,
    searchPredicate: (item, query) => item.name.toLowerCase().includes(query.toLowerCase()),
    renderPerspectiveItem: (appliedValue, filterValues, { stringify = false } = {}) => {
      const item = filterValues.find((filterValue) => {
        if (filterValue === null) {
          return appliedValue === EMPTY_UUID;
        }

        return filterValue.name === appliedValue;
      });

      if (item === undefined) {
        return appliedValue;
      }

      if (item === null) {
        return intl.formatMessage({ id: "notSet" });
      }

      if (stringify) {
        return item.name;
      }

      return <CloudLabel name={item.name} type={item.cloud_type} disableLink />;
    },
    getValuesFromSearchParams: () => ({
      values: getSelectionAppliedValuesFromSearchParams("k8sNamespace"),
    }),
    getDefaultValue: () => ({
      values: [],
    }),
    isApplied: (appliedFilter) => !isEmptyArray(appliedFilter.values),
    transformers: {
      getItems: (k8sNamespaces) =>
        k8sNamespaces?.map((item) => {
          if (item === null) {
            return {
              name: intl.formatMessage({ id: "notSet" }),
              value: EMPTY_UUID,
            };
          }
          return {
            name: item.name,
            value: item.name,
            cloud_type: item.cloud_type,
          };
        }) ?? [],
      getValue: (item) => (item === null ? EMPTY_UUID : item.name),
      toApi: (appliedFilter) => ({
        k8sNamespace: appliedFilter.values,
      }),
      filterFilterValuesByAppliedFilters: (filterValues, appliedFilters) =>
        filterValues.filter((filterValue) => {
          if (filterValue === null) {
            return appliedFilters.includes(EMPTY_UUID);
          }

          return appliedFilters.includes(filterValue.name);
        }),
    },
    schema: {
      filterValues: {
        k8s_namespace: {
          type: "array",
          items: {
            type: "object",
            nullable: true,
            required: ["name", "cloud_type"],
            additionalProperties: false,
            properties: {
              name: {
                type: "string",
              },
              cloud_type: {
                type: "string",
                enum: CLOUD_ACCOUNT_TYPES_LIST,
              },
            },
          },
        },
      },
      appliedFilter: {
        k8sNamespace: {
          type: "array",
          items: {
            type: "string",
          },
        },
      },
    },
  },
};
