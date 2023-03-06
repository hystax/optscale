import React from "react";
import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import { AGGREGATE_FUNCTION, AGGREGATE_FUNCTION_MESSAGE_ID } from "components/AggregateFunctionFormattedMessage";
import Selector from "components/Selector";
import SelectorLoader from "components/SelectorLoader";

const buildSelectorData = ({ intl }) => ({
  items: Object.values(AGGREGATE_FUNCTION).map((aggregateFunction) => ({
    name: intl.formatMessage({ id: AGGREGATE_FUNCTION_MESSAGE_ID[aggregateFunction] }),
    value: aggregateFunction
  }))
});

const FIELD_MESSAGE_ID = "aggregateFunction";

const MlApplicationParameterFormAggregateFunctionSelector = ({ name, isLoading }) => {
  const {
    control,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return isLoading ? (
    <SelectorLoader fullWidth labelId={FIELD_MESSAGE_ID} isRequired readOnly />
  ) : (
    <Controller
      name={name}
      control={control}
      rules={{
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        }
      }}
      render={({ field: { onChange, ...rest } }) => (
        <Selector
          dataTestId="selector_function"
          fullWidth
          required
          error={!!errors[name]}
          helperText={errors?.[name]?.message}
          data={buildSelectorData({ intl })}
          labelId={FIELD_MESSAGE_ID}
          onChange={(id) => {
            onChange(id);
          }}
          {...rest}
        />
      )}
    />
  );
};

export default MlApplicationParameterFormAggregateFunctionSelector;
