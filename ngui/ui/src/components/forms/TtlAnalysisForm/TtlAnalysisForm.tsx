import { useEffect, useMemo } from "react";
import { useForm, FormProvider } from "react-hook-form";
import ButtonLoader from "components/ButtonLoader";
import FormButtonsWrapper from "components/FormButtonsWrapper";
import WrapperCard from "components/WrapperCard";
import { useReactiveDefaultDateRange } from "hooks/useReactiveDefaultDateRange";
import { TTL_MODES, DATE_RANGE_TYPE } from "utils/constants";
import { FIELD_NAMES } from "./constants";
import { PoolSelector, TtlField, TtlRangePicker } from "./FormElements";
import { FormValues } from "./types";

const { PREDEFINED_TTL, CUSTOM_TTL } = TTL_MODES;

const getTtlPolicy = (pool) => pool?.policies?.find((p) => p.type === "ttl") ?? {};

const getPool = (pools = [], poolId) => pools.find((b) => b.id === poolId);

const poolFieldName = FIELD_NAMES.POOL_ID;
const ttlModeFieldName = FIELD_NAMES.TTL_MODE;
const customTtlFieldName = FIELD_NAMES.CUSTOM_TTL;
const startDateFieldName = FIELD_NAMES.START_DATE_PICKER_NAME;
const endDateFieldName = FIELD_NAMES.END_DATE_PICKER_NAME;

const TtlAnalysisForm = ({ pools, isLoading, isPoolSelectorReadOnly, onSubmit, defaultValues = {} }) => {
  const [startDateTimestamp, endDateTimestamp] = useReactiveDefaultDateRange(DATE_RANGE_TYPE.TTL_ANALYSIS);

  const methods = useForm<FormValues>({
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
  }, [getValues, setValue, watchTtlMode, ttlPolicy]);

  const handleSubmit = rhfHandleSubmit((formData) => {
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
      startDateTimestamp: formData[startDateFieldName],
      endDateTimestamp: formData[endDateFieldName]
    };

    onSubmit(params);
  });

  return (
    <WrapperCard className="halfWidth">
      <FormProvider {...methods}>
        <form onSubmit={handleSubmit} noValidate>
          <PoolSelector isReadOnly={isPoolSelectorReadOnly} isLoading={isLoading} pools={pools} fullWidth />
          <TtlField isLoading={isLoading} ttlPolicyLimit={ttlPolicy.limit} ttlMode={watchTtlMode} />
          <TtlRangePicker formValuesGetter={getValues} />
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
