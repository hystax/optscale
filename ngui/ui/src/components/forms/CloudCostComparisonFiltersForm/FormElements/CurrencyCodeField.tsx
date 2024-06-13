import { FormControl } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { useIntl } from "react-intl";
import CurrencyCodeAutocomplete from "components/CurrencyCodeAutocomplete";
import QuestionMark from "components/QuestionMark";
import { currencyCodes } from "utils/currency";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.CURRENCY_CODE;

const CurrencyCodeField = () => {
  const intl = useIntl();

  const {
    control,
    formState: { errors }
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
      render={({ field }) => (
        <FormControl fullWidth>
          <CurrencyCodeAutocomplete
            error={!!errors[FIELD_NAME]}
            helperText={errors[FIELD_NAME] && errors[FIELD_NAME].message}
            InputProps={{
              endAdornment: <QuestionMark messageId="cloudCostComparisonCurrencyDescription" />
            }}
            {...field}
          />
        </FormControl>
      )}
    />
  );
};

export default CurrencyCodeField;
