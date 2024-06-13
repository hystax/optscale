import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import CurrencyCodeAutocomplete from "components/CurrencyCodeAutocomplete";
import { currencyCodes } from "utils/currency";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.CURRENCY;

const CurrencyField = () => {
  const intl = useIntl();

  const {
    formState: { errors },
    control
  } = useFormContext();

  return (
    <Controller
      name={FIELD_NAME}
      control={control}
      rules={{
        required: {
          value: true,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        validate: {
          isAllowedCurrency: (value) =>
            currencyCodes.includes(value) ? true : intl.formatMessage({ id: "invalidCurrencyCode" })
        }
      }}
      render={({ field: { value, onChange } }) => (
        <CurrencyCodeAutocomplete
          value={value}
          onChange={onChange}
          error={!!errors[FIELD_NAME]}
          helperText={errors[FIELD_NAME] && errors[FIELD_NAME].message}
        />
      )}
    />
  );
};

export default CurrencyField;
