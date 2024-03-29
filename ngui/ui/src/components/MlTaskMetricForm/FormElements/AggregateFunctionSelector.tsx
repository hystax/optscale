import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import { AGGREGATE_FUNCTION, AGGREGATE_FUNCTION_MESSAGE_ID } from "components/AggregateFunctionFormattedMessage";
import Selector, { Item, ItemContent } from "components/Selector";

const FIELD_MESSAGE_ID = "aggregateFunction";

const AggregateFunctionSelector = ({ name, isLoading = false }) => {
  const {
    control,
    formState: { errors }
  } = useFormContext();

  const intl = useIntl();

  return (
    <Controller
      name={name}
      control={control}
      rules={{
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        }
      }}
      render={({ field }) => (
        <Selector
          id="aggregate-function-selector"
          fullWidth
          required
          error={!!errors[name]}
          helperText={errors?.[name]?.message}
          labelMessageId={FIELD_MESSAGE_ID}
          isLoading={isLoading}
          {...field}
        >
          {Object.values(AGGREGATE_FUNCTION).map((aggregateFunction) => (
            <Item key={aggregateFunction} value={aggregateFunction}>
              <ItemContent>{intl.formatMessage({ id: AGGREGATE_FUNCTION_MESSAGE_ID[aggregateFunction] })}</ItemContent>
            </Item>
          ))}
        </Selector>
      )}
    />
  );
};

export default AggregateFunctionSelector;
