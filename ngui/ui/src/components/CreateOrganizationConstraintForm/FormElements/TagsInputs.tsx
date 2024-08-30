import { useMemo } from "react";
import { Autocomplete, Box, Typography } from "@mui/material";
import { Controller, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import ButtonGroup from "components/ButtonGroup";
import Input from "components/Input";
import AvailableFiltersService from "services/AvailableFiltersService";
import { TAG_KEY_MAX_SIZE } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import { CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES } from "../constants";
import { filtersRangeFunction } from "./Filters";

const FIELD_NAME_BAR = CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.TAGS_BAR;
const FIELD_NAME_PROHIBITED_TAG = CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.PROHIBITED_TAG;
const FIELD_NAME_REQUIRED_TAG = CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.REQUIRED_TAG;
const FIELD_NAME_CORRELATION_TAG_1 = CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.CORRELATION_TAG_1;
const FIELD_NAME_CORRELATION_TAG_2 = CREATE_ORGANIZATION_CONSTRAINT_FORM_FIELD_NAMES.CORRELATION_TAG_2;

const ControllableButtonsGroup = ({ buttons, value, onChange }) => {
  const handledButtons = buttons.map((buttonDef) => ({ ...buttonDef, action: () => onChange(buttonDef.id) }));
  return (
    <Box sx={{ my: SPACING_1 }}>
      <ButtonGroup buttons={handledButtons} activeButtonId={value} onChange={onChange} />
    </Box>
  );
};

const AutocompleteInput = ({ labelMessageId, fieldName, tags, required = false }) => {
  const intl = useIntl();

  const {
    control,
    formState: { errors }
  } = useFormContext();

  const sortedTags = tags.toSorted();

  return (
    <Controller
      name={fieldName}
      control={control}
      rules={{
        required: {
          value: required,
          message: intl.formatMessage({ id: "thisFieldIsRequired" })
        },
        maxLength: {
          value: TAG_KEY_MAX_SIZE,
          message: intl.formatMessage(
            { id: "maxLength" },
            { inputName: intl.formatMessage({ id: "value" }), max: TAG_KEY_MAX_SIZE }
          )
        }
      }}
      render={({ field: { value: formFieldValue, onChange, ...rest } }) => (
        <Autocomplete
          freeSolo
          options={sortedTags}
          value={formFieldValue}
          onChange={(event, newValue) => {
            onChange(newValue);
          }}
          onInputChange={(event, newInputValue) => {
            onChange(newInputValue);
          }}
          renderInput={(autoCompleteParams) => (
            <Input
              required={required}
              label={<FormattedMessage id={labelMessageId} />}
              dataTestId={`input_${fieldName}`}
              error={!!errors[fieldName]}
              helperText={errors[fieldName]?.message}
              {...autoCompleteParams}
              {...rest}
            />
          )}
        />
      )}
    />
  );
};

export const TYPE_REQUIRED = "taggingPolicy.requiredTag";
export const TYPE_PROHIBITED = "taggingPolicy.prohibitedTag";
export const TYPE_CORRELATION = "taggingPolicy.tagsCorrelation";

const TagsInputs = () => {
  const { control, watch } = useFormContext();

  const typeSelected = watch(FIELD_NAME_BAR);

  const buttons = [TYPE_REQUIRED, TYPE_PROHIBITED, TYPE_CORRELATION].map((strategy) => ({
    id: strategy,
    messageId: strategy,
    dataTestId: `tags_strategy_${strategy}`
  }));

  const { useGet } = AvailableFiltersService();
  const params = useMemo(() => {
    const { startDate, endDate } = filtersRangeFunction();

    return {
      startDate,
      endDate
    };
  }, []);
  const {
    filters: { tag = [] }
  } = useGet(params);

  return (
    <>
      <Controller
        control={control}
        name={FIELD_NAME_BAR}
        render={({ field: { onChange, value } }) => (
          <ControllableButtonsGroup buttons={buttons} value={value} onChange={onChange} />
        )}
      />
      {typeSelected === TYPE_REQUIRED && (
        <>
          <AutocompleteInput tags={tag} labelMessageId="requiredTagField" fieldName={FIELD_NAME_REQUIRED_TAG} />
          <Typography variant="caption">
            <FormattedMessage id="taggingPolicy.anyTagHelpText" />
          </Typography>
        </>
      )}
      {typeSelected === TYPE_PROHIBITED && (
        <AutocompleteInput required tags={tag} labelMessageId="prohibitedTagField" fieldName={FIELD_NAME_PROHIBITED_TAG} />
      )}
      {typeSelected === TYPE_CORRELATION && (
        <>
          <AutocompleteInput
            required
            tags={tag}
            labelMessageId="tagsCorrelationPrimaryTag"
            fieldName={FIELD_NAME_CORRELATION_TAG_1}
          />
          <AutocompleteInput
            required
            tags={tag}
            labelMessageId="tagsCorrelationCorrelatedTag"
            fieldName={FIELD_NAME_CORRELATION_TAG_2}
          />
          <Typography variant="caption">
            <FormattedMessage id="taggingPolicy.tagsCorrelationHelpText" />
          </Typography>
        </>
      )}
    </>
  );
};

export default TagsInputs;
