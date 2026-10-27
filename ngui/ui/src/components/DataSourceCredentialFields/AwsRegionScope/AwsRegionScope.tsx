import { Autocomplete, Stack, Typography } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import ButtonGroup from "components/ButtonGroup";
import Chip from "components/Chip";
import Input from "components/Input";
import QuestionMark from "components/QuestionMark";
import { isEmptyArray } from "utils/arrays";
import { AWS_REGION_CODES, FIELD_NAMES, REGION_SCOPE_MODES } from "./constants";

const RegionsField = ({
  fieldName,
  labelMessageId,
  tooltipMessageId,
}: {
  fieldName: string;
  labelMessageId: string;
  tooltipMessageId: string;
}) => {
  const intl = useIntl();
  const {
    control,
    formState: { errors },
  } = useFormContext();

  return (
    <Controller
      name={fieldName}
      control={control}
      defaultValue={[]}
      rules={{
        validate: {
          required: (value) => (!isEmptyArray(value) ? true : intl.formatMessage({ id: "thisFieldIsRequired" })),
        },
      }}
      render={({ field: { name, value, onChange, onBlur, ref } }) => (
        <Autocomplete
          name={name}
          multiple
          freeSolo
          value={value ?? []}
          onChange={(_event, newValue: string[]) => {
            const normalized = Array.from(
              new Set(newValue.map((region) => region.trim().toLowerCase()).filter((region) => region !== ""))
            );
            onChange(normalized);
          }}
          onBlur={onBlur}
          disableCloseOnSelect
          options={AWS_REGION_CODES}
          getOptionLabel={(option) => option}
          renderTags={(autocompleteValue: string[], getTagProps) =>
            autocompleteValue.map((option, index) => (
              <Chip key={option} variant="outlined" color="info" label={option} {...getTagProps({ index })} />
            ))
          }
          renderInput={(params) => (
            <Input
              {...params}
              dataTestId="input_region_scope_regions"
              label={<FormattedMessage id={labelMessageId} />}
              required
              error={!!errors[fieldName]}
              helperText={errors[fieldName]?.message as string}
              ref={ref}
              InputProps={{
                ...params.InputProps,
                endAdornment: (
                  <>
                    <QuestionMark messageId={tooltipMessageId} dataTestId="qmark_region_scope_regions" />
                    {params.InputProps.endAdornment}
                  </>
                ),
              }}
            />
          )}
        />
      )}
    />
  );
};

const AwsRegionScope = () => {
  const { control } = useFormContext();

  return (
    <Controller
      name={FIELD_NAMES.MODE}
      control={control}
      defaultValue={REGION_SCOPE_MODES.ALL}
      render={({ field: { value: mode, onChange } }) => (
        <>
          <Stack direction="row" alignItems="center" spacing={2} mt={2} mb={2}>
            <Typography>
              <FormattedMessage id="regionScope" />
            </Typography>
            <ButtonGroup
              buttons={[
                {
                  id: REGION_SCOPE_MODES.ALL,
                  messageId: "regionScopeAll",
                  dataTestId: "btn_region_scope_all",
                  action: () => onChange(REGION_SCOPE_MODES.ALL),
                },
                {
                  id: REGION_SCOPE_MODES.INCLUDE,
                  messageId: "regionScopeInclude",
                  dataTestId: "btn_region_scope_include",
                  action: () => onChange(REGION_SCOPE_MODES.INCLUDE),
                },
                {
                  id: REGION_SCOPE_MODES.EXCLUDE,
                  messageId: "regionScopeExclude",
                  dataTestId: "btn_region_scope_exclude",
                  action: () => onChange(REGION_SCOPE_MODES.EXCLUDE),
                },
              ]}
              activeButtonId={mode}
              activeButtonIndex={undefined}
              fullWidth={false}
            />
          </Stack>
          {mode === REGION_SCOPE_MODES.INCLUDE && (
            <RegionsField
              fieldName={FIELD_NAMES.INCLUDED_REGIONS}
              labelMessageId="regionScopeInclude"
              tooltipMessageId="regionScopeIncludeTooltip"
            />
          )}
          {mode === REGION_SCOPE_MODES.EXCLUDE && (
            <RegionsField
              fieldName={FIELD_NAMES.EXCLUDED_REGIONS}
              labelMessageId="regionScopeExclude"
              tooltipMessageId="regionScopeExcludeTooltip"
            />
          )}
        </>
      )}
    />
  );
};

export default AwsRegionScope;
