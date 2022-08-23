import React, { useEffect, useState, useCallback } from "react";
import FiberManualRecordIcon from "@mui/icons-material/FiberManualRecord";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { Controller, useForm, FormProvider } from "react-hook-form";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import TabsWrapper from "components/TabsWrapper";
import WrapperCard from "components/WrapperCard";
import { RECOMMENDATIONS } from "urls";
import { RIGHTSIZING_METRIC_LIMIT_TYPES, TAB_QUERY_PARAM_NAME } from "utils/constants";
import { getQueryParams } from "utils/network";
import Exclusions from "./Exclusions";
import InsecurePorts from "./InsecurePorts";
import RightsizingStrategy, {
  STRATEGIES,
  STRATEGY_METRICS,
  thresholdValidationRules,
  NAME as RIGHTSIZING_FORM_FIELD_NAME_ROOT
} from "./RightsizingStrategy";
import Thresholds, { THRESHOLDS_FORM_FIELD_NAME_ROOT, THRESHOLD_INPUT_NAMES } from "./Thresholds";

const getExcludedPoolsIds = (selectedPools) => selectedPools.map(({ id }) => id);

const TAB_NAME = TAB_QUERY_PARAM_NAME;

const SETTINGS_TYPE = Object.freeze({
  THRESHOLDS: "thresholds",
  RIGHTSIZING_STRATEGY: "rightsizingStrategy",
  EXCLUSIONS: "exclusions",
  INSECURE_PORTS: "insecurePorts"
});

const SettingFormButtons = ({ isChangeSettingsAllowed, isGetDataLoading, isSaveDataLoading, isUnsaved, onSubmit }) => {
  const navigate = useNavigate();

  const isSubmitEnabled = isChangeSettingsAllowed && isUnsaved;

  return (
    <FormButtonsWrapper>
      <ButtonLoader
        messageId="save"
        variant="contained"
        color="primary"
        tooltip={{
          show: !isChangeSettingsAllowed,
          messageId: "youDoNotHaveEnoughPermissions"
        }}
        type="submit"
        disabled={!isSubmitEnabled}
        onClick={onSubmit}
        isLoading={isGetDataLoading || isSaveDataLoading}
      />
      <Button messageId="back" onClick={() => navigate(-1)} />
    </FormButtonsWrapper>
  );
};

const ThresholdsForm = ({
  options,
  backendRecommendationType,
  onSave,
  isGetDataLoading,
  onFormFieldChange,
  onSuccess,
  renderFormButtons
}) => {
  const getFormValues = useCallback(
    (currentValues = {}) => {
      const {
        days_threshold: currentDaysThreshold,
        cpu_percent_threshold: currentCpuPercentThreshold,
        network_bps_threshold: currentNetworkBpsThreshold,
        data_size_threshold: currentDataSizeThreshold,
        tier_1_request_quantity_threshold: currentTier1RequestsQuantityThreshold,
        tier_2_request_quantity_threshold: currentTier2RequestsQuantityThreshold
      } = options;

      return {
        ...currentValues,
        [THRESHOLDS_FORM_FIELD_NAME_ROOT]: {
          ...currentValues[THRESHOLDS_FORM_FIELD_NAME_ROOT],
          [THRESHOLD_INPUT_NAMES.DAYS_THRESHOLD]: currentDaysThreshold,
          [THRESHOLD_INPUT_NAMES.CPU_PERCENT_THRESHOLD]: currentCpuPercentThreshold,
          [THRESHOLD_INPUT_NAMES.NETWORK_BPS_THRESHOLD]: currentNetworkBpsThreshold,
          [THRESHOLD_INPUT_NAMES.DATA_SIZE_THRESHOLD]: currentDataSizeThreshold,
          [THRESHOLD_INPUT_NAMES.TIER_1_REQUESTS_QUANTITY_THRESHOLD]: currentTier1RequestsQuantityThreshold,
          [THRESHOLD_INPUT_NAMES.TIER_2_REQUESTS_QUANTITY_THRESHOLD]: currentTier2RequestsQuantityThreshold
        }
      };
    },
    [options]
  );

  const methods = useForm({
    defaultValues: getFormValues()
  });

  const { getValues, handleSubmit, reset } = methods;

  useEffect(() => {
    reset(getFormValues(getValues()));
  }, [reset, getValues, getFormValues]);

  const onSubmit = (formData) => {
    const { thresholds } = formData;

    const newOptions = {
      ...options,
      ...{
        days_threshold: thresholds[THRESHOLD_INPUT_NAMES.DAYS_THRESHOLD],
        cpu_percent_threshold: thresholds[THRESHOLD_INPUT_NAMES.CPU_PERCENT_THRESHOLD],
        network_bps_threshold: thresholds[THRESHOLD_INPUT_NAMES.NETWORK_BPS_THRESHOLD],
        data_size_threshold: thresholds[THRESHOLD_INPUT_NAMES.DATA_SIZE_THRESHOLD],
        tier_1_request_quantity_threshold: thresholds[THRESHOLD_INPUT_NAMES.TIER_1_REQUESTS_QUANTITY_THRESHOLD],
        tier_2_request_quantity_threshold: thresholds[THRESHOLD_INPUT_NAMES.TIER_2_REQUESTS_QUANTITY_THRESHOLD]
      }
    };

    onSave(SETTINGS_TYPE.THRESHOLDS, newOptions, onSuccess);
  };

  return (
    <FormProvider {...methods}>
      <form onSubmit={handleSubmit(onSubmit)}>
        <Thresholds
          formFieldNameRoot={THRESHOLDS_FORM_FIELD_NAME_ROOT}
          backendRecommendationType={backendRecommendationType}
          isLoading={isGetDataLoading}
          onChange={onFormFieldChange}
        />
        {renderFormButtons()}
      </form>
    </FormProvider>
  );
};

const RightsizingStrategyForm = ({ options, isGetDataLoading, onSave, onSuccess, onFormFieldChange, renderFormButtons }) => {
  const getFormValues = useCallback(
    (currentValues = {}) => {
      const getRightsizingMetricFormValue = () => {
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
    reset(getFormValues(getValues()));
  }, [reset, getValues, getFormValues]);

  const onSubmit = (formData) => {
    const { rightsizingStrategy } = formData;

    const newOptions = {
      ...options,
      metric: rightsizingStrategy.metric
    };

    onSave(SETTINGS_TYPE.RIGHTSIZING_STRATEGY, newOptions, onSuccess);
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
            const { strategy, metric, customMetric } = value;

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
              onFormFieldChange();
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
              onFormFieldChange();
            };

            return (
              <RightsizingStrategy
                strategy={strategy}
                metric={metric}
                customMetric={customMetric}
                onStrategyChange={onStrategyChange}
                onCustomMetricChange={onCustomMetricChange}
                isLoading={isGetDataLoading}
                error={errors.rightsizingStrategy}
              />
            );
          }}
        />
        {renderFormButtons()}
      </form>
    </FormProvider>
  );
};

const ExclusionsForm = ({
  onSave,
  options,
  availablePools,
  isGetDataLoading,
  isChangeSettingsAllowed,
  onSuccess,
  onFormFieldChange,
  renderFormButtons
}) => {
  const { excluded_pools: excludedPools = {} } = options;

  const [selectedPools, setSelectedPools] = useState([]);

  const onSubmit = () => {
    const newOptions = {
      ...options,
      excluded_pools: Object.fromEntries(getExcludedPoolsIds(selectedPools).map((id) => [id, true]))
    };

    onSave(SETTINGS_TYPE.EXCLUSIONS, newOptions, onSuccess);
  };

  return (
    <div>
      <Exclusions
        availablePools={availablePools}
        currentExcludedPools={excludedPools}
        setSelectedPools={setSelectedPools}
        isLoading={isGetDataLoading}
        isChangeSettingsAllowed={isChangeSettingsAllowed}
        onSelectionChange={onFormFieldChange}
      />
      {renderFormButtons(onSubmit)}
    </div>
  );
};

const InsecurePortsForm = ({
  options,
  isGetDataLoading,
  isChangeSettingsAllowed,
  onSave,
  onFormFieldChange,
  onSuccess,
  renderFormButtons
}) => {
  const getFormValues = useCallback(
    (currentValues = {}) => ({
      ...currentValues,
      insecurePorts: options.insecure_ports ?? []
    }),
    [options.insecure_ports]
  );

  const methods = useForm({
    defaultValues: getFormValues()
  });

  const { control, getValues, handleSubmit, reset } = methods;

  useEffect(() => {
    reset(getFormValues(getValues()));
  }, [reset, getValues, getFormValues]);

  const onSubmit = (formData) => {
    const { insecurePorts } = formData;

    const newOptions = {
      ...options,
      insecure_ports: insecurePorts
    };

    onSave(SETTINGS_TYPE.INSECURE_PORTS, newOptions, onSuccess);
  };

  return (
    <FormProvider {...methods}>
      <form noValidate onSubmit={handleSubmit(onSubmit)}>
        <Controller
          name="insecurePorts"
          control={control}
          render={({ field: { onChange, value } }) => (
            <InsecurePorts
              insecurePorts={value}
              setData={(ports) => {
                onChange(ports);
                onFormFieldChange();
              }}
              isLoading={isGetDataLoading}
              isChangeSettingsAllowed={isChangeSettingsAllowed}
            />
          )}
        />
        {renderFormButtons()}
      </form>
    </FormProvider>
  );
};

const RecommendationSettings = ({
  options,
  backendRecommendationType,
  availablePools,
  onSave,
  isGetDataLoading = false,
  isSaveDataLoading = false,
  isChangeSettingsAllowed = false,
  withExclusions = false,
  withThresholds = false,
  withRightsizingStrategy = false,
  withInsecurePorts = false
}) => {
  const [activeTab, setActiveTab] = useState(getQueryParams()[TAB_NAME]);

  const [isUnsaved, setIsUnsaved] = useState(() => ({
    ...(withExclusions
      ? {
          [SETTINGS_TYPE.EXCLUSIONS]: false
        }
      : {}),
    ...(withThresholds
      ? {
          [SETTINGS_TYPE.THRESHOLDS]: false
        }
      : {}),
    ...(withRightsizingStrategy
      ? {
          [SETTINGS_TYPE.RIGHTSIZING_STRATEGY]: false
        }
      : {}),
    ...(withInsecurePorts
      ? {
          [SETTINGS_TYPE.INSECURE_PORTS]: false
        }
      : {})
  }));

  const updateUnsaved = useCallback((settingType, unsaved) => {
    setIsUnsaved((currentUnsavedState) => {
      if (currentUnsavedState[settingType] !== unsaved) {
        return {
          ...currentUnsavedState,
          [settingType]: unsaved
        };
      }
      return currentUnsavedState;
    });
  }, []);

  const getUnsavedState = (settingType) =>
    isUnsaved[settingType]
      ? {
          icon: <FiberManualRecordIcon fontSize="inherit" />,
          iconPosition: "end"
        }
      : {};

  const renderFormButtons = (settingType) => (onSubmit) =>
    (
      <SettingFormButtons
        isChangeSettingsAllowed={isChangeSettingsAllowed}
        isGetDataLoading={isGetDataLoading}
        isSaveDataLoading={isSaveDataLoading}
        isUnsaved={isUnsaved[settingType]}
        type="submit"
        onSubmit={onSubmit}
      />
    );

  const tabs = [
    withInsecurePorts && {
      title: "insecurePorts",
      ...getUnsavedState(SETTINGS_TYPE.INSECURE_PORTS),
      node: (
        <InsecurePortsForm
          options={options}
          isGetDataLoading={isGetDataLoading}
          isChangeSettingsAllowed={isChangeSettingsAllowed}
          onSave={onSave}
          onFormFieldChange={() => updateUnsaved(SETTINGS_TYPE.INSECURE_PORTS, true)}
          onSuccess={() => updateUnsaved(SETTINGS_TYPE.INSECURE_PORTS, false)}
          renderFormButtons={renderFormButtons(SETTINGS_TYPE.INSECURE_PORTS)}
        />
      )
    },
    withRightsizingStrategy && {
      title: RIGHTSIZING_FORM_FIELD_NAME_ROOT,
      ...getUnsavedState(SETTINGS_TYPE.RIGHTSIZING_STRATEGY),
      node: (
        <RightsizingStrategyForm
          options={options}
          isGetDataLoading={isGetDataLoading}
          onSave={onSave}
          onFormFieldChange={() => updateUnsaved(SETTINGS_TYPE.RIGHTSIZING_STRATEGY, true)}
          onSuccess={() => updateUnsaved(SETTINGS_TYPE.RIGHTSIZING_STRATEGY, false)}
          renderFormButtons={renderFormButtons(SETTINGS_TYPE.RIGHTSIZING_STRATEGY)}
        />
      )
    },
    withThresholds && {
      title: THRESHOLDS_FORM_FIELD_NAME_ROOT,
      ...getUnsavedState(SETTINGS_TYPE.THRESHOLDS),
      node: (
        <ThresholdsForm
          options={options}
          backendRecommendationType={backendRecommendationType}
          onSave={onSave}
          onFormFieldChange={() => updateUnsaved(SETTINGS_TYPE.THRESHOLDS, true)}
          onSuccess={() => updateUnsaved(SETTINGS_TYPE.THRESHOLDS, false)}
          isGetDataLoading={isGetDataLoading}
          renderFormButtons={renderFormButtons(SETTINGS_TYPE.THRESHOLDS)}
        />
      )
    },
    withExclusions && {
      title: "exclusions",
      ...getUnsavedState(SETTINGS_TYPE.EXCLUSIONS),
      node: (
        <ExclusionsForm
          options={options}
          onSave={onSave}
          availablePools={availablePools}
          isGetDataLoading={isGetDataLoading}
          isChangeSettingsAllowed={isChangeSettingsAllowed}
          onSuccess={() => updateUnsaved(SETTINGS_TYPE.EXCLUSIONS, false)}
          onFormFieldChange={() => updateUnsaved(SETTINGS_TYPE.EXCLUSIONS, true)}
          renderFormButtons={renderFormButtons(SETTINGS_TYPE.EXCLUSIONS)}
        />
      )
    }
  ].filter(Boolean);

  return (
    <WrapperCard>
      <Typography paragraph>
        <FormattedMessage
          id="recommendationSettingsDescription"
          values={{
            strong: (chunks) => <strong>{chunks}</strong>,
            link: (chunks) => (
              <Link to={RECOMMENDATIONS} component={RouterLink}>
                {chunks}
              </Link>
            )
          }}
        />
      </Typography>
      <TabsWrapper
        withWrapperCard={false}
        tabsProps={{
          tabs,
          defaultTab: tabs[0]?.title,
          name: "recommendationSettings",
          activeTab,
          handleChange: (event, value) => setActiveTab(value),
          queryTabName: TAB_NAME,
          keepTabContentMounted: true
        }}
      />
    </WrapperCard>
  );
};

RecommendationSettings.propTypes = {
  options: PropTypes.object.isRequired,
  backendRecommendationType: PropTypes.string.isRequired,
  availablePools: PropTypes.array.isRequired,
  onSave: PropTypes.func,
  isGetDataLoading: PropTypes.bool,
  isSaveDataLoading: PropTypes.bool,
  isChangeSettingsAllowed: PropTypes.bool,
  withExclusions: PropTypes.bool,
  withThresholds: PropTypes.bool,
  withRightsizingStrategy: PropTypes.bool,
  withInsecurePorts: PropTypes.bool
};

export default RecommendationSettings;
