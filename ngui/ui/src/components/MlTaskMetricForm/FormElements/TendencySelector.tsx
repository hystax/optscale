import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import Selector, { Item, ItemContent } from "components/Selector";
import { GOALS_FILTER_TYPES } from "utils/constants";

const FIELD_MESSAGE_ID = "tendency";

const TendencySelector = ({ name, isLoading = false }) => {
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
          id="tendency-selector"
          fullWidth
          required
          error={!!errors[name]}
          helperText={errors?.[name]?.message}
          labelMessageId={FIELD_MESSAGE_ID}
          isLoading={isLoading}
          {...field}
        >
          <Item value={GOALS_FILTER_TYPES.LESS_IS_BETTER}>
            <ItemContent>{intl.formatMessage({ id: "lessIsBetter" })}</ItemContent>
          </Item>
          <Item value={GOALS_FILTER_TYPES.MORE_IS_BETTER}>
            <ItemContent>{intl.formatMessage({ id: "moreIsBetter" })}</ItemContent>
          </Item>
        </Selector>
      )}
    />
  );
};

export default TendencySelector;
