import React from "react";
import { Autocomplete, createFilterOptions } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Input from "components/Input";
import { useFormatOrganizationCurrency } from "hooks/useFormatOrganizationCurrency";
import { currencyCodes } from "utils/currency";

export const FIELD_NAME = "currency";

const OrganizationCurrencyField = () => {
  const intl = useIntl();

  const formatOrganizationCurrency = useFormatOrganizationCurrency();

  const {
    formState: { errors },
    control
  } = useFormContext();

  const stringifyCurrency = (currencyCode) => formatOrganizationCurrency(currencyCode);

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
        <Autocomplete
          freeSolo
          disableClearable
          clearOnEscape
          selectOnFocus
          value={value}
          options={currencyCodes}
          onInputChange={(event, selected) => {
            onChange(selected);
          }}
          filterOptions={createFilterOptions({
            matchFrom: "any",
            stringify: (option) => stringifyCurrency(option)
          })}
          renderOption={(props, option) => <li {...props}>{stringifyCurrency(option)}</li>}
          renderInput={(params) => (
            <Input
              {...params}
              inputProps={{
                ...params.inputProps,
                style: {
                  width: "100%"
                }
              }}
              margin="none"
              error={!!errors[FIELD_NAME]}
              helperText={errors[FIELD_NAME] && errors[FIELD_NAME].message}
              label={<FormattedMessage id="currency" />}
              required
            />
          )}
        />
      )}
    />
  );
};

export default OrganizationCurrencyField;
