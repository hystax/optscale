import React, { useCallback, useEffect, useMemo, useState } from "react";
import CloudCostComparison from "components/CloudCostComparison";
import { FIELD_NAMES, SUPPORTED_CLOUD_TYPES } from "components/CloudCostComparisonFiltersForm/FormElements";
import { REGIONS } from "components/CloudCostComparisonFiltersForm/FormElements/RegionField";
import { useIsNebiusConnectionEnabled } from "hooks/useIsNebiusConnectionEnabled";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import CloudCostComparisonService from "services/CloudCostComparisonService";
import { isEmpty } from "utils/arrays";
import { NEBIUS } from "utils/constants";
import { getQueryParams, updateQueryParams } from "utils/network";

const CloudCostComparisonContainer = () => {
  const { currency } = useOrganizationInfo();
  const isNebiusConnectionEnabled = useIsNebiusConnectionEnabled();
  const { useGet, useGetOnDemand } = CloudCostComparisonService();

  const { onGet } = useGetOnDemand();

  const defaultFormValues = () => {
    const queryParams = getQueryParams();

    const getCloudTypeValue = () => {
      const value = queryParams[FIELD_NAMES.CLOUD_TYPE_FIELD_NAME];

      if (value === undefined) {
        return [];
      }

      return Array.isArray(value) ? value : [value];
    };

    return {
      [FIELD_NAMES.CLOUD_TYPE_FIELD_NAME]: getCloudTypeValue(),
      [FIELD_NAMES.REGION_FIELD_NAME]: queryParams[FIELD_NAMES.REGION_FIELD_NAME] ?? REGIONS.EU,
      [FIELD_NAMES.CURRENCY_CODE_FIELD_NAME]: queryParams[FIELD_NAMES.CURRENCY_CODE_FIELD_NAME] ?? currency,
      [FIELD_NAMES.MIN_CPU_FIELD_NAME]: queryParams[FIELD_NAMES.MIN_CPU_FIELD_NAME] ?? "1",
      [FIELD_NAMES.MAX_CPU_FIELD_NAME]: queryParams[FIELD_NAMES.MAX_CPU_FIELD_NAME] ?? "416",
      [FIELD_NAMES.MIN_RAM_FIELD_NAME]: queryParams[FIELD_NAMES.MIN_RAM_FIELD_NAME] ?? "0",
      [FIELD_NAMES.MAX_RAM_FIELD_NAME]: queryParams[FIELD_NAMES.MAX_RAM_FIELD_NAME] ?? "18432"
    };
  };

  const getApiParams = useCallback(
    (params) => {
      const minCpu = params[FIELD_NAMES.MIN_CPU_FIELD_NAME] === "" ? undefined : params[FIELD_NAMES.MIN_CPU_FIELD_NAME].trim();
      const maxCpu = params[FIELD_NAMES.MAX_CPU_FIELD_NAME] === "" ? undefined : params[FIELD_NAMES.MAX_CPU_FIELD_NAME].trim();
      const minRam = params[FIELD_NAMES.MIN_RAM_FIELD_NAME] === "" ? undefined : params[FIELD_NAMES.MIN_RAM_FIELD_NAME].trim();
      const maxRam = params[FIELD_NAMES.MAX_RAM_FIELD_NAME] === "" ? undefined : params[FIELD_NAMES.MAX_RAM_FIELD_NAME].trim();

      const getCloudType = () => {
        const cloudTypes = SUPPORTED_CLOUD_TYPES.map(({ type }) => type);

        const allowedTypes = cloudTypes.filter((type) => {
          if (type === NEBIUS && !isNebiusConnectionEnabled) {
            return false;
          }
          return true;
        });

        if (isEmpty(params[FIELD_NAMES.CLOUD_TYPE_FIELD_NAME])) {
          return allowedTypes;
        }
        return allowedTypes.filter((type) => params[FIELD_NAMES.CLOUD_TYPE_FIELD_NAME].includes(type));
      };

      return {
        cloud_type: getCloudType(),
        min_cpu: minCpu,
        max_cpu: maxCpu,
        min_ram: minRam,
        max_ram: maxRam,
        region: params[FIELD_NAMES.REGION_FIELD_NAME],
        preferred_currency: params[FIELD_NAMES.CURRENCY_CODE_FIELD_NAME]
      };
    },
    [isNebiusConnectionEnabled]
  );

  const [params, setParams] = useState(() => defaultFormValues());

  const apiParams = useMemo(() => getApiParams(params), [getApiParams, params]);

  useEffect(() => {
    updateQueryParams(params, { allowEmptyString: true });
  }, [params]);

  const { isLoading, sizes, errors } = useGet(apiParams);

  return (
    <CloudCostComparison
      isLoading={isLoading}
      cloudProviders={params[FIELD_NAMES.CLOUD_TYPE_FIELD_NAME]}
      defaultFormValues={defaultFormValues()}
      onFiltersApply={(newParams) => {
        setParams(newParams);
        onGet(getApiParams(newParams));
      }}
      relevantSizes={sizes}
      errors={errors}
    />
  );
};

export default CloudCostComparisonContainer;
