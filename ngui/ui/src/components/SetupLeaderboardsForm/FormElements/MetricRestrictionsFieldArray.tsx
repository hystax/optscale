import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import { Box, Typography } from "@mui/material";
import FormControl from "@mui/material/FormControl";
import { Controller, useFieldArray, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Button from "components/Button";
import { NumberInput } from "components/forms/common/fields";
import IconButton from "components/IconButton";
import InputLoader from "components/InputLoader";
import Selector, { Item, ItemContent } from "components/Selector";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { ARRAY_FORM_FIELD_FLEX_BASIS_WIDTH } from "utils/constants";
import { SPACING_1 } from "utils/layouts";
import { FIELD_NAMES } from "../constants";

const {
  METRIC_RESTRICTIONS_ARRAY_FIELD_NAMES: {
    NAME: FIELD_NAME,
    ARRAY_FIELD_NAMES: { METRIC, METRIC_MIN, METRIC_MAX }
  }
} = FIELD_NAMES;

const MinInput = ({ index }) => {
  const intl = useIntl();

  const {
    formState: { isSubmitted },
    trigger
  } = useFormContext();

  return (
    <NumberInput
      name={`${FIELD_NAME}.${index}.${METRIC_MIN}`}
      label={<FormattedMessage id="min" />}
      onChange={() => {
        if (isSubmitted) {
          trigger(`${FIELD_NAME}.${index}.${METRIC_MAX}`);
        }
      }}
      validate={{
        maxOrMinShouldBeDefined: (value, formValues) => {
          const max = formValues[FIELD_NAME]?.[index]?.[METRIC_MAX];

          return !max && !value ? intl.formatMessage({ id: "eitherMinOrMaxMustBeDefined" }) : true;
        },
        lessThanOrEqualToMax: (value, formValues) => {
          const max = formValues[FIELD_NAME]?.[index]?.[METRIC_MAX];

          if (!max || !value) {
            return true;
          }

          return Number(value) <= Number(max)
            ? true
            : intl.formatMessage(
                { id: "fieldLessThanOrEqualToField" },
                {
                  fieldName1: intl.formatMessage({ id: "min" }),
                  fieldName2: intl.formatMessage({ id: "max" })
                }
              );
        }
      }}
      dataTestId={`restriction_min_${index}`}
    />
  );
};

const MaxInput = ({ index }) => {
  const intl = useIntl();

  const {
    formState: { isSubmitted },
    trigger
  } = useFormContext();

  return (
    <NumberInput
      name={`${FIELD_NAME}.${index}.${METRIC_MAX}`}
      label={<FormattedMessage id="max" />}
      onChange={() => {
        if (isSubmitted) {
          trigger(`${FIELD_NAME}.${index}.${METRIC_MIN}`);
        }
      }}
      validate={{
        maxOrMinShouldBeDefined: (value, formValues) => {
          const min = formValues[FIELD_NAME]?.[index]?.[METRIC_MIN];

          return !min && !value ? intl.formatMessage({ id: "eitherMinOrMaxMustBeDefined" }) : true;
        },
        moreThatOrEqualToMin: (value, formValues) => {
          const min = formValues[FIELD_NAME]?.[index]?.[METRIC_MIN];

          if (!min || !value) {
            return true;
          }

          return Number(value) >= Number(min)
            ? true
            : intl.formatMessage(
                { id: "fieldMoreThanOrEqualToField" },
                {
                  fieldName1: intl.formatMessage({ id: "max" }),
                  fieldName2: intl.formatMessage({ id: "min" })
                }
              );
        }
      }}
      dataTestId={`restriction_max_${index}`}
    />
  );
};

const MetricSelect = ({ index, metrics, selectorsCount }) => {
  const intl = useIntl();

  const {
    control,
    formState: { errors, isSubmitted },
    trigger
  } = useFormContext();

  const fieldName = `${FIELD_NAME}.${index}.${METRIC}`;

  return (
    <Controller
      name={fieldName}
      control={control}
      rules={{
        validate: {
          required: (value) => (value ? true : intl.formatMessage({ id: "thisFieldIsRequired" })),
          metricShouldBeUnique: (value, formValues) => {
            const selectedMetrics = formValues[FIELD_NAME].map(({ [METRIC]: metricName }) => metricName);

            return selectedMetrics.filter((metricName) => metricName === value).length <= 1
              ? true
              : intl.formatMessage({ id: "entitiesMustBeUnique" }, { name: intl.formatMessage({ id: "metrics" }) });
          }
        }
      }}
      render={({ field: { onChange, ...rest } }) => (
        <Selector
          id={`metric-selector-${index}`}
          required
          labelMessageId="metric"
          onChange={(newValue) => {
            onChange(newValue);
            if (isSubmitted) {
              [...Array(selectorsCount)].forEach((_, itemIndex) => {
                trigger(`${FIELD_NAME}.${itemIndex}.${METRIC}`);
              });
            }
          }}
          error={!!errors[FIELD_NAME]?.[index]?.[METRIC]}
          helperText={errors[FIELD_NAME]?.[index]?.[METRIC] && errors[FIELD_NAME]?.[index]?.[METRIC]?.message}
          fullWidth
          {...rest}
        >
          {metrics.map(({ id: metricId, name: metricName }) => (
            <Item key={metricId} value={metricId}>
              <ItemContent>{metricName}</ItemContent>
            </Item>
          ))}
        </Selector>
      )}
    />
  );
};

const FieldArray = ({ metrics }) => {
  const { control } = useFormContext();

  const { fields, append, remove } = useFieldArray({
    control,
    name: FIELD_NAME
  });

  const onAppend = () =>
    append({
      [METRIC]: "",
      [METRIC_MIN]: "",
      [METRIC_MAX]: ""
    });

  return (
    <>
      {isEmptyArray(fields) ? (
        <Typography>
          <FormattedMessage id="noRestrictions" />
        </Typography>
      ) : (
        fields.map((item, index) => (
          <Box key={item.id} display="flex" gap={SPACING_1} flexWrap="wrap">
            <Box flexGrow={1} flexBasis={ARRAY_FORM_FIELD_FLEX_BASIS_WIDTH.MEDIUM}>
              <MetricSelect index={index} metrics={metrics} selectorsCount={fields.length} />
            </Box>
            <Box flexGrow={2} display="flex" flexBasis={ARRAY_FORM_FIELD_FLEX_BASIS_WIDTH.LARGE} gap={SPACING_1}>
              <Box flexGrow={1} display="flex" gap={SPACING_1}>
                <MinInput index={index} />
                <MaxInput index={index} />
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
      {fields.length < metrics.length && (
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
      )}
    </>
  );
};

const MetricRestrictionsFieldArray = ({ metrics = [], isLoading = false }) =>
  isLoading ? <InputLoader fullWidth /> : <FieldArray metrics={metrics} />;

export default MetricRestrictionsFieldArray;
