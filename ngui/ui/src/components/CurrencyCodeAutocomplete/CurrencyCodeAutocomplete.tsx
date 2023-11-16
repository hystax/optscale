import { forwardRef } from "react";
import { Autocomplete, createFilterOptions } from "@mui/material";
import { FormattedMessage } from "react-intl";
import Input from "components/Input";
import { useFormatOrganizationCurrency } from "hooks/useFormatOrganizationCurrency";
import { currencyCodes } from "utils/currency";

const CurrencyCodeAutocomplete = forwardRef(({ name, onBlur, value, onChange, error, helperText, InputProps }, ref) => {
  const formatOrganizationCurrency = useFormatOrganizationCurrency();
  const stringifyCurrency = (currencyCode) => formatOrganizationCurrency(currencyCode);

  return (
    <Autocomplete
      name={name}
      freeSolo
      disableClearable
      clearOnEscape
      selectOnFocus
      value={value}
      options={currencyCodes}
      onInputChange={(event, selected) => {
        onChange(selected);
      }}
      onBlur={onBlur}
      filterOptions={createFilterOptions({
        matchFrom: "any",
        stringify: (option) => stringifyCurrency(option)
      })}
      renderOption={(props, option) => <li {...props}>{stringifyCurrency(option)}</li>}
      renderInput={(params) => (
        <Input
          {...params}
          ref={ref}
          InputProps={{ ...params.InputProps, ...InputProps }}
          margin="none"
          error={error}
          helperText={helperText}
          label={<FormattedMessage id="currency" />}
          required
        />
      )}
    />
  );
});

export default CurrencyCodeAutocomplete;
