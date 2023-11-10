import { useCallback, useEffect } from "react";
import { useForm } from "react-hook-form";
import { useIsAllowed } from "hooks/useAllowedActions";
import OrganizationOptionsService from "services/OrganizationOptionsService";
import { objectMap } from "utils/objects";

export const useCommonSettingsData = (recommendationType, settingType, onSuccess) => {
  const { useGetRecommendationOptionsOnce, useUpdateRecommendationOptions } = OrganizationOptionsService();
  const { isLoading: isGetRecommendationOptionsLoading, options } = useGetRecommendationOptionsOnce(recommendationType);

  const isGetDataLoading = isGetRecommendationOptionsLoading;

  const { isLoading: isSaveDataLoading, updateRecommendationOptions } = useUpdateRecommendationOptions();

  const isChangeSettingsAllowed = useIsAllowed({ requiredActions: ["EDIT_PARTNER"] });

  const save = useCallback(
    (newOptions) => {
      updateRecommendationOptions(recommendationType, { settingType, options: newOptions }, onSuccess);
    },
    [onSuccess, recommendationType, settingType, updateRecommendationOptions]
  );

  return { options, isGetDataLoading, isChangeSettingsAllowed, save, isSaveDataLoading, updateRecommendationOptions };
};

// valueKeys is object to map form data to options object, sample:
// {
//   [THRESHOLD_INPUT_NAMES.DAYS_THRESHOLD]: "days_threshold",
//   [THRESHOLD_INPUT_NAMES.CPU_PERCENT_THRESHOLD]: "cpu_percent_threshold",
//   [THRESHOLD_INPUT_NAMES.NETWORK_BPS_THRESHOLD]: "network_bps_threshold"
// }
export const useFormWithValuesFromOptions = (options, onSave, valueKeys) => {
  const getFormValues = useCallback(
    (currentValues = {}) => ({
      ...currentValues,
      ...objectMap(valueKeys, (optionsKey) => options[optionsKey])
    }),
    [options, valueKeys]
  );

  const methods = useForm({
    defaultValues: getFormValues()
  });

  const { handleSubmit, reset } = methods;

  useEffect(() => {
    reset((formValues) => getFormValues(formValues));
  }, [reset, getFormValues]);

  const onSubmit = (formData) => {
    const revertedKeys = Object.fromEntries(Object.entries(valueKeys).map(([key, value]) => [value, key]));

    const newOptions = {
      ...options,
      ...objectMap(revertedKeys, (thresholdsKey) => formData[thresholdsKey])
    };

    onSave(newOptions);
  };

  return { submitHandler: handleSubmit(onSubmit), methods };
};
