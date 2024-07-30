import { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import { Autocomplete, Box, Typography, createFilterOptions } from "@mui/material";
import FormControl from "@mui/material/FormControl";
import { Controller, useFieldArray, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Button from "components/Button";
import { NumberInput } from "components/forms/common/fields";
import IconButton from "components/IconButton";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { ARRAY_FORM_FIELD_FLEX_BASIS_WIDTH } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import { FIELD_NAMES } from "../constants";
import { FormValues } from "../types";

const {
  DATASETS_COVERAGE_ARRAY_FIELD_NAMES: {
    NAME: FIELD_NAME,
    ARRAY_FIELD_NAMES: { DATASET_LABEL, LAST_DATASETS_COVERED }
  }
} = FIELD_NAMES;

const filter = createFilterOptions();

const MAX_DATASETS_COVERED = 100;

const LastDatasetsCoveredInput = ({ index }) => {
  const {
    formState: { isSubmitted },
    trigger
  } = useFormContext<FormValues>();

  return (
    <NumberInput
      name={`${FIELD_NAME}.${index}.${LAST_DATASETS_COVERED}`}
      label={<FormattedMessage id="lastDatasetsCovered" />}
      required
      onChange={() => {
        if (isSubmitted) {
          trigger(`${FIELD_NAME}.${index}.${LAST_DATASETS_COVERED}`);
        }
      }}
      max={MAX_DATASETS_COVERED}
      dataTestId={`restriction_max_${index}`}
    />
  );
};

const DatasetLabelSelect = ({ index, labels, selectorsCount }) => {
  const intl = useIntl();

  const {
    control,
    formState: { errors, isSubmitted },
    trigger
  } = useFormContext<FormValues>();

  const fieldName = `${FIELD_NAME}.${index}.${DATASET_LABEL}`;

  const options = useMemo(() => labels.map((label) => label), [labels]);

  return (
    <Controller
      name={fieldName}
      control={control}
      rules={{
        validate: {
          required: (value) => (value ? true : intl.formatMessage({ id: "thisFieldIsRequired" })),
          labelsShouldUnique: (value, formValues) => {
            const selectedLabels = formValues[FIELD_NAME].map(({ [DATASET_LABEL]: label }) => label);

            return selectedLabels.filter((label) => label === value).length <= 1
              ? true
              : intl.formatMessage({ id: "entitiesMustBeUnique" }, { name: intl.formatMessage({ id: "datasetLabels" }) });
          }
        }
      }}
      render={({ field: { value: datasetLabel, onChange } }) => (
        <Autocomplete
          value={datasetLabel}
          onChange={(event, newValue) => {
            if (newValue === null || typeof newValue === "string") {
              onChange(newValue ?? "");
            } else {
              onChange(newValue.inputValue);
            }
            if (isSubmitted) {
              [...Array(selectorsCount)].forEach((_, itemIndex) => {
                trigger(`${FIELD_NAME}.${itemIndex}.${DATASET_LABEL}`);
              });
            }
          }}
          filterOptions={(filterOptions, params) => {
            const filtered = filter(options, params);

            const { inputValue } = params;

            // Suggest creation of a new value
            const isExisting = filterOptions.some((option) => inputValue === option);
            if (inputValue !== "" && !isExisting) {
              filtered.push({
                inputValue,
                title: `${intl.formatMessage({ id: "add" })} ${inputValue}`
              });
            }

            return filtered;
          }}
          options={options}
          getOptionLabel={(option) => {
            if (typeof option === "string") {
              return option;
            }
            return option.inputValue;
          }}
          renderOption={(props, option) => <li {...props}>{typeof option === "string" ? option : option.title}</li>}
          freeSolo
          renderInput={(params) => (
            <Input
              {...params}
              label={<FormattedMessage id="datasetLabel" />}
              required
              error={!!errors[FIELD_NAME]?.[index]?.[DATASET_LABEL]}
              helperText={errors[FIELD_NAME]?.[index]?.[DATASET_LABEL] && errors[FIELD_NAME]?.[index]?.[DATASET_LABEL]?.message}
              dataTestId="input_dataset_label"
            />
          )}
          clearOnBlur
        />
      )}
    />
  );
};

const DatasetLabelsCoverageField = ({ labels = [], isLoading = false }) => {
  const { control } = useFormContext<FormValues>();

  const { fields, append, remove } = useFieldArray({
    control,
    name: FIELD_NAME
  });

  const onAppend = () =>
    append({
      [DATASET_LABEL]: "",
      [LAST_DATASETS_COVERED]: ""
    });

  return isLoading ? (
    <InputLoader fullWidth />
  ) : (
    <>
      {isEmptyArray(fields) ? (
        <Typography>
          <FormattedMessage id="noLabels" />
        </Typography>
      ) : (
        fields.map((item, index) => (
          <Box key={item.id} display="flex" gap={SPACING_1} flexWrap="wrap">
            <Box flexGrow={1} flexBasis={ARRAY_FORM_FIELD_FLEX_BASIS_WIDTH.MEDIUM}>
              <DatasetLabelSelect index={index} labels={labels} selectorsCount={fields.length} />
            </Box>
            <Box flexGrow={2} display="flex" flexBasis={ARRAY_FORM_FIELD_FLEX_BASIS_WIDTH.LARGE} gap={SPACING_1}>
              <Box flexGrow={1} display="flex" gap={SPACING_1}>
                <LastDatasetsCoveredInput index={index} />
              </Box>
              <Box>
                <FormControl>
                  <IconButton
                    color="error"
                    icon={<DeleteOutlinedIcon />}
                    onClick={() => remove(index)}
                    tooltip={{
                      show: true,
                      value: <FormattedMessage id="delete" />
                    }}
                    dataTestId={`btn_delete_restriction_${index}`}
                  />
                </FormControl>
              </Box>
            </Box>
          </Box>
        ))
      )}
      <FormControl fullWidth>
        <Button
          dashedBorder
          startIcon={<AddOutlinedIcon />}
          messageId="add"
          size="medium"
          color="primary"
          onClick={onAppend}
          dataTestId="btn_add_restriction"
        />
      </FormControl>
    </>
  );
};

export default DatasetLabelsCoverageField;
