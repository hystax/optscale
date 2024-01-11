import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import { Box, Typography } from "@mui/material";
import FormControl from "@mui/material/FormControl";
import { Controller, useFieldArray, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Button from "components/Button";
import IconButton from "components/IconButton";
import Input from "components/Input";
import InputLoader from "components/InputLoader";
import Selector from "components/Selector";
import { isEmpty as isEmptyArray } from "utils/arrays";
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
    register,
    formState: { errors, isSubmitted },
    trigger
  } = useFormContext();

  const { onChange, ...restRegister } = register(`${FIELD_NAME}.${index}.${METRIC_MIN}`, {
    valueAsNumber: true,
    validate: {
      maxOrMinShouldBeDefined: (value, formValues) => {
        const max = formValues[FIELD_NAME]?.[index]?.[METRIC_MAX];

        return Number.isNaN(max) && Number.isNaN(value) ? intl.formatMessage({ id: "eitherMinOrMaxShouldBeDefined" }) : true;
      },
      lessThanOrEqualToMax: (value, formValues) => {
        const max = formValues[FIELD_NAME]?.[index]?.[METRIC_MAX];

        if (Number.isNaN(max) || Number.isNaN(value)) {
          return true;
        }

        return value <= max
          ? true
          : intl.formatMessage(
              { id: "fieldLessThanOrEqualToField" },
              {
                fieldName1: intl.formatMessage({ id: "min" }),
                fieldName2: intl.formatMessage({ id: "max" })
              }
            );
      }
    }
  });

  return (
    <Input
      label={<FormattedMessage id="min" />}
      type="number"
      error={!!errors[FIELD_NAME]?.[index]?.[METRIC_MIN]}
      helperText={errors[FIELD_NAME]?.[index]?.[METRIC_MIN] && errors[FIELD_NAME]?.[index]?.[METRIC_MIN]?.message}
      onChange={(event) => {
        onChange(event);
        if (isSubmitted) {
          trigger(`${FIELD_NAME}.${index}.${METRIC_MAX}`);
        }
      }}
      {...restRegister}
      dataTestId={`restriction_min_${index}`}
    />
  );
};

const MaxInput = ({ index }) => {
  const intl = useIntl();

  const {
    register,
    formState: { errors, isSubmitted },
    trigger
  } = useFormContext();

  const { onChange, ...restRegister } = register(`${FIELD_NAME}.${index}.${METRIC_MAX}`, {
    valueAsNumber: true,
    validate: {
      maxOrMinShouldBeDefined: (value, formValues) => {
        const min = formValues[FIELD_NAME]?.[index]?.[METRIC_MIN];

        return Number.isNaN(min) && Number.isNaN(value) ? intl.formatMessage({ id: "eitherMinOrMaxShouldBeDefined" }) : true;
      },
      moreThatOrEqualToMin: (value, formValues) => {
        const min = formValues[FIELD_NAME]?.[index]?.[METRIC_MIN];

        if (Number.isNaN(min) || Number.isNaN(value)) {
          return true;
        }

        return value >= min
          ? true
          : intl.formatMessage(
              { id: "fieldMoreThanOrEqualToField" },
              {
                fieldName1: intl.formatMessage({ id: "max" }),
                fieldName2: intl.formatMessage({ id: "min" })
              }
            );
      }
    }
  });

  return (
    <Input
      label={<FormattedMessage id="max" />}
      type="number"
      error={!!errors[FIELD_NAME]?.[index]?.[METRIC_MAX]}
      helperText={errors[FIELD_NAME]?.[index]?.[METRIC_MAX] && errors[FIELD_NAME]?.[index]?.[METRIC_MAX]?.message}
      onChange={(event) => {
        onChange(event);
        if (isSubmitted) {
          trigger(`${FIELD_NAME}.${index}.${METRIC_MIN}`);
        }
      }}
      {...restRegister}
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
              : intl.formatMessage({ id: "entitiesShouldBeUnique" }, { name: intl.formatMessage({ id: "metrics" }) });
          }
        }
      }}
      render={({ field: { onChange, ...rest } }) => (
        <Selector
          labelId="metric"
          data={{
            items: metrics.map(({ id: metricId, name: metricName }) => ({
              name: metricName,
              value: metricId
            }))
          }}
          onChange={(newValue) => {
            onChange(newValue);
            if (isSubmitted) {
              [...Array(selectorsCount)].forEach((_, itemIndex) => {
                trigger(`${FIELD_NAME}.${itemIndex}.${METRIC}`);
              });
            }
          }}
          required
          error={!!errors[FIELD_NAME]?.[index]?.[METRIC]}
          helperText={errors[FIELD_NAME]?.[index]?.[METRIC] && errors[FIELD_NAME]?.[index]?.[METRIC]?.message}
          dataTestId={`selector_metric_${index}`}
          fullWidth
          {...rest}
        />
      )}
    />
  );
};

const MetricRestrictionsField = ({ isLoading, metrics = [] }) => {
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

  return isLoading ? (
    <InputLoader fullWidth />
  ) : (
    <>
      {isEmptyArray(fields) ? (
        <Typography>
          <FormattedMessage id="noRestrictions" />
        </Typography>
      ) : (
        fields.map((item, index) => (
          <Box key={item.id} display="flex" gap={SPACING_1} flexWrap="wrap">
            <Box
              flexGrow={1}
              // TODO: Replace with ARRAY_FORM_FIELD_FLEX_BASIS_WIDTH.MEDIUM
              flexBasis="150px"
            >
              <MetricSelect index={index} metrics={metrics} selectorsCount={fields.length} />
            </Box>
            <Box
              flexGrow={2}
              display="flex"
              // TODO: Replace with ARRAY_FORM_FIELD_FLEX_BASIS_WIDTH.LARGE
              flexBasis="300px"
              gap={SPACING_1}
            >
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

export default MetricRestrictionsField;
