import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import Selector from "components/Selector";
import SelectorLoader from "components/SelectorLoader";
import { GOALS_FILTER_TYPES } from "utils/constants";

const buildSelectorData = ({ intl }) => ({
  items: [
    {
      name: intl.formatMessage({ id: "lessIsBetter" }),
      value: GOALS_FILTER_TYPES.LESS_IS_BETTER
    },
    {
      name: intl.formatMessage({ id: "moreIsBetter" }),
      value: GOALS_FILTER_TYPES.MORE_IS_BETTER
    }
  ]
});

const FIELD_MESSAGE_ID = "tendency";

const TendencySelector = ({ name, isLoading }) => {
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
          dataTestId="selector_tendency"
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

export default TendencySelector;
