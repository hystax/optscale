import { useEffect, useMemo } from "react";
import { useForm, FormProvider } from "react-hook-form";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import WrapperCard from "components/WrapperCard";
import { useReactiveDefaultDateRange } from "hooks/useReactiveDefaultDateRange";
import { START_DATE_PICKER_NAME, END_DATE_PICKER_NAME, TTL_MODES, DATE_RANGE_TYPE } from "utils/constants";
import TtlAnalysisFormPoolSelector from "./Fields/TtlAnalysisFormPoolSelector";
import TtlAnalysisFormRangePicker from "./Fields/TtlAnalysisFormRangePicker";
import TtlAnalysisFormTtlField from "./Fields/TtlAnalysisFormTtlField";

const { PREDEFINED_TTL, CUSTOM_TTL } = TTL_MODES;

const getTtlPolicy = (pool) => pool?.policies?.find((p) => p.type === "ttl") ?? {};

const getPool = (pools = [], poolId) => pools.find((b) => b.id === poolId);

const TtlAnalysisForm = ({ pools, isLoading, isPoolSelectorReadOnly, onSubmit, defaultValues = {}, fieldNames }) => {
  const [startDateTimestamp, endDateTimestamp] = useReactiveDefaultDateRange(DATE_RANGE_TYPE.TTL_ANALYSIS);

  const { poolFieldName, ttlModeFieldName, customTtlFieldName, startDateFieldName, endDateFieldName } = fieldNames;

  const methods = useForm({
    defaultValues: {
      [poolFieldName]: "",
      [ttlModeFieldName]: "",
      [customTtlFieldName]: "",
      [startDateFieldName]: startDateTimestamp,
      [endDateFieldName]: endDateTimestamp,
      ...defaultValues
    }
  });

  const { handleSubmit: rhfHandleSubmit, setValue, getValues, watch, reset } = methods;

  useEffect(() => {
    reset((formValues) => ({
      ...formValues,
      ...defaultValues
    }));
  }, [defaultValues, reset]);

  const [watchPoolId, watchTtlMode] = watch([poolFieldName, ttlModeFieldName]);

  const ttlPolicy = useMemo(() => getTtlPolicy(getPool(pools, watchPoolId)), [pools, watchPoolId]);

  useEffect(() => {
    if (watchTtlMode === PREDEFINED_TTL) {
      setValue(ttlModeFieldName, `${ttlPolicy?.limit ? PREDEFINED_TTL : CUSTOM_TTL}`);
    }
  }, [getValues, setValue, ttlModeFieldName, watchTtlMode, ttlPolicy]);

  const handleSubmit = (formData) => {
    const poolId = formData[poolFieldName];
    const customTtl = formData[CUSTOM_TTL];

    const { name: poolName, purpose: poolType } = pools.find((pool) => pool.id === poolId) ?? {};

    const params = {
      ttl: watchTtlMode === PREDEFINED_TTL ? ttlPolicy.limit : Number(customTtl),
      customTtl,
      poolId,
      poolName,
      poolType,
      ttlMode: formData[ttlModeFieldName],
      startDateTimestamp: formData[START_DATE_PICKER_NAME],
      endDateTimestamp: formData[END_DATE_PICKER_NAME]
    };
    onSubmit(params);
  };

  return (
    <WrapperCard className="halfWidth">
      <FormProvider {...methods}>
        <form onSubmit={rhfHandleSubmit(handleSubmit)} noValidate>
          <TtlAnalysisFormPoolSelector
            isReadOnly={isPoolSelectorReadOnly}
            isLoading={isLoading}
            fullWidth
            name={poolFieldName}
            pools={pools}
          />
          <TtlAnalysisFormTtlField
            ttlFieldName={ttlModeFieldName}
            predefinedTtlRadioName={PREDEFINED_TTL}
            customTtlRadioName={CUSTOM_TTL}
            ttlInputName={customTtlFieldName}
            isLoading={isLoading}
            ttlPolicyLimit={ttlPolicy.limit}
            ttlMode={watchTtlMode}
          />
          <TtlAnalysisFormRangePicker
            startDatePickerName={startDateFieldName}
            endDatePickerName={endDateFieldName}
            formValuesGetter={getValues}
          />
          <FormButtonsWrapper>
            <ButtonLoader
              dataTestId="btn_generate"
              messageId="generateReport"
              color="primary"
              type="submit"
              isLoading={isLoading}
              variant="contained"
            />
          </FormButtonsWrapper>
        </form>
      </FormProvider>
    </WrapperCard>
  );
};

export default TtlAnalysisForm;
