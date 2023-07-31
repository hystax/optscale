import React, { useCallback, useEffect } from "react";
import { Controller, FormProvider, useForm } from "react-hook-form";
import { SETTINGS_TYPE_SUCCESS_MESSAGE, RIGHTSIZING_METRIC_LIMIT_TYPES } from "utils/constants";
import BaseSideModal from "../BaseSideModal";
import InformationWrapper from "./components/InformationWrapper";
import RightsizingStrategy, {
  STRATEGY_METRICS,
  STRATEGIES,
  thresholdValidationRules,
  NAME as RIGHTSIZING_FORM_FIELD_NAME_ROOT
} from "./components/RightsizingStrategy";
import SaveButton from "./components/SaveButton";
import { useCommonSettingsData } from "./hooks";

const RightsizingStrategyForm = ({ recommendationType, onSuccess }) => {
  const { options, isGetDataLoading, isChangeSettingsAllowed, isSaveDataLoading, save } = useCommonSettingsData(
    recommendationType,
    SETTINGS_TYPE_SUCCESS_MESSAGE.RIGHTSIZING_STRATEGY,
    onSuccess
  );
  const getFormValues = useCallback(
    (currentValues = {}) => {
      const getRightsizingMetricFormValue = () => {
        const { days_threshold: daysThreshold = 3 } = options;

        const metric = options.metric?.type
          ? { type: options.metric.type, limit: options.metric.limit }
          : { type: RIGHTSIZING_METRIC_LIMIT_TYPES.Q99, limit: 0 };

        const strategy = (() => {
          const predefinedStrategy = Object.entries(STRATEGY_METRICS).find(
            ([, { type, limit }]) => metric.type === type && metric.limit === limit
          )?.[0];

          return predefinedStrategy ?? STRATEGIES.CUSTOM;
        })();

        return {
          [RIGHTSIZING_FORM_FIELD_NAME_ROOT]: {
            metric,
            strategy,
            daysThreshold,
            // store metric copy in order to reset previously selected values when the "custom" strategy is selected
            customMetric: metric
          }
        };
      };

      return {
        ...currentValues,
        ...getRightsizingMetricFormValue()
      };
    },
    [options]
  );

  const methods = useForm({
    defaultValues: getFormValues()
  });

  const {
    getValues,
    control,
    handleSubmit,
    formState: { errors },
    reset
  } = methods;

  useEffect(() => {
    reset((formValues) => getFormValues(formValues));
  }, [reset, getFormValues]);

  const onSubmit = (formData) => {
    const { rightsizingStrategy } = formData;

    const newOptions = {
      ...options,
      metric: rightsizingStrategy.metric,
      days_threshold: rightsizingStrategy.daysThreshold
    };

    save(newOptions);
  };

  return (
    <FormProvider>
      <form onSubmit={handleSubmit(onSubmit)}>
        <Controller
          name={RIGHTSIZING_FORM_FIELD_NAME_ROOT}
          control={control}
          rules={{
            validate: thresholdValidationRules
          }}
          render={({ field: { onChange, value } }) => {
            const { strategy, metric, customMetric, daysThreshold } = value;

            const onStrategyChange = (newStrategy) => {
              const newVal = {
                ...value,
                strategy: newStrategy,
                metric:
                  newStrategy !== STRATEGIES.CUSTOM
                    ? STRATEGY_METRICS[newStrategy]
                    : getValues()[RIGHTSIZING_FORM_FIELD_NAME_ROOT].customMetric
              };

              onChange(newVal);
            };

            const onCustomMetricChange = (target, newValue) => {
              const newMetricValue = {
                ...value.metric,
                [target]: newValue
              };

              onChange({
                ...value,
                metric: newMetricValue,
                customMetric: newMetricValue
              });
            };

            const onDaysThresholdChange = (newValue) => {
              onChange({ ...value, daysThreshold: newValue });
            };

            return (
              <RightsizingStrategy
                daysThreshold={daysThreshold}
                strategy={strategy}
                metric={metric}
                customMetric={customMetric}
                onStrategyChange={onStrategyChange}
                onCustomMetricChange={onCustomMetricChange}
                onDaysThresholdChange={onDaysThresholdChange}
                isLoading={isGetDataLoading}
                error={errors.rightsizingStrategy}
              />
            );
          }}
        />
        <SaveButton
          isGetDataLoading={isGetDataLoading}
          isChangeSettingsAllowed={isChangeSettingsAllowed}
          isSaveDataLoading={isSaveDataLoading}
        />
      </form>
    </FormProvider>
  );
};

class RightsizingStrategyModal extends BaseSideModal {
  headerProps = {
    messageId: "rightsizingStrategy",
    dataTestIds: {
      title: "lbl_rightsizing_strategy_sidemodal_title",
      closeButton: "btn_close"
    }
  };

  dataTestId = "smodal_rightsizing_strategy";

  get content() {
    return (
      <InformationWrapper>
        <RightsizingStrategyForm recommendationType={this.payload?.recommendationType} onSuccess={this.closeSideModal} />
      </InformationWrapper>
    );
  }
}

export default RightsizingStrategyModal;
