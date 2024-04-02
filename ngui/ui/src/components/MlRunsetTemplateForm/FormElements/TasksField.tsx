import { Autocomplete } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Chip from "components/Chip";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import { isEmpty as isEmptyArray } from "utils/arrays";

export const FIELD_NAME = "tasks";

const TasksField = ({ tasks, isLoading }) => {
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
      render={({ field: { value: formFieldValue, onChange } }) =>
        isLoading ? (
          <InputLoader fullWidth />
        ) : (
          <Autocomplete
            value={formFieldValue}
            multiple
            onChange={(event, newValue) => {
              onChange(newValue);
            }}
            disableClearable
            clearOnBlur
            isOptionEqualToValue={(option, value) => option.id === value.id}
            options={tasks.map((task) => ({
              name: task.name,
              id: task.id
            }))}
            getOptionLabel={(option) => option.name}
            renderTags={(autocompleteValue, getTagProps) =>
              autocompleteValue.map((option, index) => (
                <Chip key={option.name} variant="outlined" color="info" label={option.name} {...getTagProps({ index })} />
              ))
            }
            renderInput={(params) => (
              <Input
                {...params}
                dataTestId="input_tasks"
                label={<FormattedMessage id="tasks" />}
                required
                error={!!errors[FIELD_NAME]}
                helperText={errors[FIELD_NAME]?.message}
              />
            )}
          />
        )
      }
    />
  );
};

export default TasksField;
