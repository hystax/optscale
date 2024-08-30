import { useMemo } from "react";
import { Autocomplete, Box, Stack, createFilterOptions } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Chip from "components/Chip";
import InlineSeverityAlert from "components/InlineSeverityAlert";
import Input from "components/Input";
import MlModelVersionLabel from "components/MlModelVersionLabel";
import SlicedText from "components/SlicedText";
import { DEFAULT_MAX_INPUT_LENGTH } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import { notOnlyWhiteSpaces } from "utils/validation";
import { ALIAS_LENGTH_LIMIT, FIELD_NAMES } from "../constants";
import { AliasesFieldProps, ConflictingAliasesWarningProps, FormValues } from "../types";

const FIELD_NAME = FIELD_NAMES.ALIASES;

const filter = createFilterOptions();

const ConflictingAliasesWarning = ({ modelVersion, aliasToVersionMap }: ConflictingAliasesWarningProps) => {
  const { watch } = useFormContext<FormValues>();

  const aliases = watch(FIELD_NAME);

  const conflictingAliases = aliases.filter((alias) => {
    const version = aliasToVersionMap[alias];

    return version && version !== modelVersion.version;
  });

  return conflictingAliases.map((alias) => (
    <InlineSeverityAlert
      key={alias}
      messageId="conflictingAliasWarning"
      messageValues={{
        alias,
        version: aliasToVersionMap[alias],
        strong: (chunks) => <strong>{chunks}</strong>
      }}
      sx={{ width: "100%" }}
    />
  ));
};

export const isAliasValid = (alias: string) => {
  const isLengthValid = alias.length <= DEFAULT_MAX_INPUT_LENGTH;

  const containsNotOnlyWhiteSpaces = notOnlyWhiteSpaces(alias) === true;

  return isLengthValid && containsNotOnlyWhiteSpaces;
};

const AliasesField = ({ aliasToVersionMap, modelVersion }: AliasesFieldProps) => {
  const {
    formState: { errors },
    control
  } = useFormContext<FormValues>();

  const intl = useIntl();

  const options = useMemo(
    () =>
      Object.keys(aliasToVersionMap).map((alias) => ({
        title: alias
      })),
    [aliasToVersionMap]
  );

  return (
    <Stack spacing={SPACING_1}>
      <Controller
        name={FIELD_NAME}
        control={control}
        render={({ field: { value: aliasesValue, onChange } }) => (
          <Autocomplete
            value={aliasesValue.map((alias) => ({
              title: alias
            }))}
            onChange={(event, newValues) => {
              const values = newValues.map((value) => {
                // Typed in input
                if (typeof value === "string") {
                  return value;
                }
                // Created a new option by clicking "Add `xxx`"
                if (value && value.inputValue) {
                  return value.inputValue;
                }
                // Selected from the list
                return value.title;
              });

              const uniqueValues = [...new Set(values)];

              onChange(uniqueValues);
            }}
            filterOptions={(filterOptions, params) => {
              const filtered = filter(filterOptions, params);

              const { inputValue } = params;

              // Suggest creation of a new value
              const isExisting = filterOptions.some((option) => inputValue === option.title);
              if (inputValue !== "" && !isExisting) {
                filtered.push({
                  inputValue,
                  title: `${intl.formatMessage({ id: "add" })} ${inputValue}`
                });
              }

              return filtered;
            }}
            renderOption={(props, option) => {
              const version = aliasToVersionMap[option.title];

              return (
                <li {...props}>
                  <Box display="flex" justifyContent="space-between" width="100%">
                    <Box>
                      <SlicedText limit={ALIAS_LENGTH_LIMIT} text={option.title} />
                    </Box>
                    {version && (
                      <Box>
                        {modelVersion.version === version ? (
                          <FormattedMessage id="thisVersion" />
                        ) : (
                          <>
                            {`${intl.formatMessage({ id: "version" })}`}
                            &nbsp;
                            <MlModelVersionLabel version={version} />
                          </>
                        )}
                      </Box>
                    )}
                  </Box>
                </li>
              );
            }}
            getOptionLabel={(option) => {
              // "Add `xxx`" option created dynamically
              if (option.inputValue) {
                return option.inputValue;
              }

              return option.title;
            }}
            isOptionEqualToValue={(option, value) => option.title === value.title}
            options={options}
            freeSolo
            multiple
            renderTags={(value, getTagProps) =>
              value.map((option, index) => (
                <Chip
                  key={option.title}
                  variant="outlined"
                  color={isAliasValid(option.title) ? "info" : "error"}
                  label={option.title}
                  {...getTagProps({ index })}
                />
              ))
            }
            renderInput={(params) => (
              <Input
                {...params}
                dataTestId="input_aliases"
                autoFocus
                label={<FormattedMessage id="aliases" />}
                error={!!errors[FIELD_NAME]}
                helperText={errors[FIELD_NAME]?.message}
              />
            )}
            clearOnBlur
          />
        )}
      />
      <ConflictingAliasesWarning modelVersion={modelVersion} aliasToVersionMap={aliasToVersionMap} />
    </Stack>
  );
};

export default AliasesField;
