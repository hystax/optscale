import { useEffect, useState } from "react";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import { useIsAllowed } from "hooks/useAllowedActions";
import OrganizationOptionsService from "services/OrganizationOptionsService";
import PoolsService from "services/PoolsService";
import { SETTINGS_TYPE_SUCCESS_MESSAGE } from "utils/constants";
import ExcludedPoolsTable from "./ExcludedPoolsTable";

type SelectedPoolType = { [key: string]: [value: boolean] };

type ExcludePoolsFromRecommendationType = { recommendationType: string; onSuccess: () => void };

const ExcludePoolsFromRecommendation = ({ recommendationType, onSuccess }: ExcludePoolsFromRecommendationType) => {
  const isChangeSettingsAllowed = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });

  const { useGetRecommendationOptionsOnce, useUpdateRecommendationOptions } = OrganizationOptionsService();
  const { isLoading: isSaveDataLoading, updateRecommendationOptions } = useUpdateRecommendationOptions();
  const { isLoading: isGetRecommendationOptionsLoading, options } = useGetRecommendationOptionsOnce(recommendationType);

  const { useGetAvailablePools } = PoolsService();
  const { isLoading: isGetAvailablePoolsLoading, data: availablePools } = useGetAvailablePools();
  const isGetDataLoading = isGetRecommendationOptionsLoading || isGetAvailablePoolsLoading;

  const [selectedPools, setSelectedPools] = useState({});

  useEffect(() => {
    const { excluded_pools: excludedPools = {} } = options;
    setSelectedPools(excludedPools);
  }, [options]);

  const onSubmit = () => {
    const newOptions = {
      ...options,
      excluded_pools: selectedPools
    };

    updateRecommendationOptions(
      recommendationType,
      {
        settingType: SETTINGS_TYPE_SUCCESS_MESSAGE.EXCLUSIONS,
        options: newOptions
      },
      onSuccess
    );
  };

  const onSelectedPoolChange = (pools: SelectedPoolType) => {
    setSelectedPools(pools);
  };

  return (
    <>
      <Typography gutterBottom>
        <FormattedMessage id="exclusionsDescription" values={{ strong: (chunks) => <strong>{chunks}</strong> }} />
      </Typography>
      <ExcludedPoolsTable
        availablePools={availablePools}
        isLoading={isGetDataLoading}
        isChangeSettingsAllowed={isChangeSettingsAllowed}
        selectedPools={selectedPools}
        onSelectedPoolChange={onSelectedPoolChange}
      />
      <FormButtonsWrapper>
        <ButtonLoader
          messageId="save"
          variant="contained"
          color="primary"
          disabled={!isChangeSettingsAllowed}
          tooltip={{
            show: !isChangeSettingsAllowed,
            messageId: "youDoNotHaveEnoughPermissions"
          }}
          type="submit"
          onClick={onSubmit}
          isLoading={isGetDataLoading || isSaveDataLoading}
        />
      </FormButtonsWrapper>
    </>
  );
};

export default ExcludePoolsFromRecommendation;
