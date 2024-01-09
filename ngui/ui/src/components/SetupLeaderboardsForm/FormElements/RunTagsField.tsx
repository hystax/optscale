import { Autocomplete } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Chip from "components/Chip";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import QuestionMark from "components/QuestionMark";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { FIELD_NAMES } from "../constants";

const FIELD_NAME = FIELD_NAMES.RUN_TAGS_FIELD_NAME;

const RunTagsField = ({ runTags = [], isLoading }) => {
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
        validate: {
          required: (value) => (!isEmptyArray(value) ? true : intl.formatMessage({ id: "thisFieldIsRequired" }))
        }
      }}
      render={({ field: { name, value: formFieldValue, onChange, onBlur, ref } }) =>
        isLoading ? (
          <InputLoader fullWidth />
        ) : (
          <Autocomplete
            name={name}
            freeSolo
            value={formFieldValue}
            multiple
            onChange={(event, newValue) => {
              onChange(newValue);
            }}
            onBlur={onBlur}
            disableClearable
            clearOnBlur
            isOptionEqualToValue={(option, value) => option === value}
            options={runTags}
            getOptionLabel={(option) => option}
            renderTags={(autocompleteValue, getTagProps) =>
              autocompleteValue.map((option, index) => (
                <Chip key={option} variant="outlined" color="info" label={option} {...getTagProps({ index })} />
              ))
            }
            renderInput={(params) => (
              <Input
                {...params}
                dataTestId="input_group_runs_by_tags"
                label={<FormattedMessage id="tagsForGrouping" />}
                required
                error={!!errors[FIELD_NAME]}
                helperText={errors[FIELD_NAME]?.message}
                ref={ref}
                InputProps={{
                  ...params.InputProps,
                  endAdornment: <QuestionMark messageId="groupRunsByTagsHint" dataTestId="qmark_group_runs_by_tags" />
                }}
              />
            )}
          />
        )
      }
    />
  );
};

export default RunTagsField;
