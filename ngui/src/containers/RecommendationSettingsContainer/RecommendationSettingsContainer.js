import React from "react";
import RecommendationSettings from "components/RecommendationSettings";
import { useIsAllowed } from "hooks/useAllowedActions";
import OrganizationOptionsService from "services/OrganizationOptionsService";
import PoolsService from "services/PoolsService";

const RecommendationSettingsContainer = ({
  backendRecommendationType,
  withExclusions,
  withThresholds,
  withRightsizingStrategy,
  withInsecurePorts
}) => {
  const { useGetRecommendationOptionsOnce, useUpdateRecommendationOptions } = OrganizationOptionsService();
  const { isLoading: isGetRecommendationOptionsLoading, options } = useGetRecommendationOptionsOnce(backendRecommendationType);

  const { useGetAvailablePoolsOnce } = PoolsService();
  const { isLoading: isGetAvailablePoolsLoading, data: availablePools } = useGetAvailablePoolsOnce();

  const isGetDataLoading = isGetRecommendationOptionsLoading || isGetAvailablePoolsLoading;

  const { isLoading: isSaveDataLoading, updateRecommendationOptions } = useUpdateRecommendationOptions();

  const onSave = (settingType, newOptions, onSuccess) => {
    updateRecommendationOptions(backendRecommendationType, { settingType, options: newOptions }, onSuccess);
  };

  const isChangeSettingsAllowed = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });

  return (
    <RecommendationSettings
      options={options}
      backendRecommendationType={backendRecommendationType}
      availablePools={availablePools}
      withExclusions={withExclusions}
      withThresholds={withThresholds}
      withRightsizingStrategy={withRightsizingStrategy}
      withInsecurePorts={withInsecurePorts}
      isLoading={isGetDataLoading}
      isGetDataLoading={isGetDataLoading}
      isSaveDataLoading={isSaveDataLoading}
      isChangeSettingsAllowed={isChangeSettingsAllowed}
      onSave={onSave}
    />
  );
};

export default RecommendationSettingsContainer;
