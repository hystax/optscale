import { useEffect, useState } from "react";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { useIsAllowed } from "hooks/useAllowedActions";
import OrganizationOptionsService from "services/OrganizationOptionsService";
import PoolsService from "services/PoolsService";
import { SETTINGS_TYPE_SUCCESS_MESSAGE } from "utils/constants";
import Exclusions from "./Exclusions";

const ExclusionsForm = ({ onSave, options, availablePools, isGetDataLoading, isChangeSettingsAllowed, isSaveDataLoading }) => {
  const { excluded_pools: excludedPools = {} } = options;

  const [selectedPoolIds, setSelectedPoolsIds] = useState([]);

  useEffect(() => {
    setSelectedPoolsIds(Object.keys(excludedPools));
  }, [excludedPools]);

  const onSubmit = () => {
    const newOptions = {
      ...options,
      excluded_pools: Object.fromEntries(selectedPoolIds.map((id) => [id, true]))
    };

    onSave(newOptions);
  };

  const onSelectedPoolIdsChange = (poolIds) => {
    setSelectedPoolsIds(poolIds);
  };

  return (
    <div>
      <Exclusions
        availablePools={availablePools}
        currentExcludedPools={excludedPools}
        isLoading={isGetDataLoading}
        isChangeSettingsAllowed={isChangeSettingsAllowed}
        selectedPoolIds={selectedPoolIds}
        onSelectedPoolIdsChange={onSelectedPoolIdsChange}
      />
      <FormButtonsWrapper withBottomMargin>
        <ButtonLoader
          messageId="save"
          variant="contained"
          color="primary"
          tooltip={{
            show: !isChangeSettingsAllowed,
            messageId: "youDoNotHaveEnoughPermissions"
          }}
          type="submit"
          onClick={onSubmit}
          isLoading={isGetDataLoading || isSaveDataLoading}
        />
      </FormButtonsWrapper>
    </div>
  );
};

const ExcludePoolsFromRecommendation = ({ recommendationType, onSuccess }) => {
  const { useGetRecommendationOptionsOnce, useUpdateRecommendationOptions } = OrganizationOptionsService();
  const { isLoading: isGetRecommendationOptionsLoading, options } = useGetRecommendationOptionsOnce(recommendationType);

  const { useGetAvailablePoolsOnce } = PoolsService();
  const { isLoading: isGetAvailablePoolsLoading, data: availablePools } = useGetAvailablePoolsOnce();

  const isGetDataLoading = isGetRecommendationOptionsLoading || isGetAvailablePoolsLoading;

  const { isLoading: isSaveDataLoading, updateRecommendationOptions } = useUpdateRecommendationOptions();

  const onSave = (newOptions) => {
    updateRecommendationOptions(
      recommendationType,
      {
        settingType: SETTINGS_TYPE_SUCCESS_MESSAGE.EXCLUSIONS,
        options: newOptions
      },
      onSuccess
    );
  };

  const isChangeSettingsAllowed = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });

  return (
    <>
      <ExclusionsForm
        options={options}
        onSave={onSave}
        availablePools={availablePools}
        isGetDataLoading={isGetDataLoading}
        isChangeSettingsAllowed={isChangeSettingsAllowed}
        isSaveDataLoading={isSaveDataLoading}
      />
    </>
  );
};

export default ExcludePoolsFromRecommendation;
