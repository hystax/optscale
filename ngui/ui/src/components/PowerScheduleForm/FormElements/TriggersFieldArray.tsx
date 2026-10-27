import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import { Box, FormControl, FormLabel } from "@mui/material";
import { Controller, useFieldArray, useFormContext } from "react-hook-form";
import { FormattedMessage, useIntl } from "react-intl";
import Button from "components/Button";
import Day from "components/DateRangePicker/Day";
import { Selector } from "components/forms/common/fields";
import IconButton from "components/IconButton";
import InputLoader from "components/InputLoader";
import QuestionMark from "components/QuestionMark";
import { ItemContent } from "components/Selector";
import { POWER_SCHEDULE_ACTIONS } from "utils/constants";
import { MERIDIEM_NAMES } from "utils/datetime";
import { SPACING_1 } from "utils/layouts";
import { TIME_VALUES, FIELD_NAMES } from "../constants";
import { FormValues } from "../types";

const { FIELD_NAME } = FIELD_NAMES.TRIGGERS_FIELD_ARRAY;
const TIME_FIELD = FIELD_NAMES.TRIGGERS_FIELD_ARRAY.TIME;
const MERIDIEM_FIELD = FIELD_NAMES.TRIGGERS_FIELD_ARRAY.MERIDIEM;
const ACTION_FIELD = FIELD_NAMES.TRIGGERS_FIELD_ARRAY.ACTION;

const MAX_TRIGGERS = 8;

const TimeField = ({ index, timeFieldsCount }: { index: number; timeFieldsCount: number }) => {
  const {
    formState: { isSubmitted },
    trigger,
  } = useFormContext();

  const intl = useIntl();

  return (
    <Selector
      name={`${FIELD_NAME}.${index}.${TIME_FIELD}`}
      id={`trigger-time-${index}`}
      labelMessageId="time"
      required
      fullWidth
      onChange={() => {
        if (isSubmitted) {
          [...Array(timeFieldsCount)].forEach((_, itemIndex) => {
            trigger(`${FIELD_NAME}.${itemIndex}.${TIME_FIELD}`);
          });
        }
      }}
      validate={{
        unique: (value, formValues) => {
          const allFullValues = formValues[FIELD_NAME].map(
            ({ [TIME_FIELD]: time, [MERIDIEM_FIELD]: meridiem }) => `${time} ${meridiem}`
          );
          const currentFullValue = `${value} ${formValues[FIELD_NAME][index][MERIDIEM_FIELD]}`;

          const triggersWithSameTime = allFullValues.filter((time) => time === currentFullValue);

          const isTriggerUnique = triggersWithSameTime.length === 1;

          return (
            isTriggerUnique ||
            intl.formatMessage({ id: "entitiesMustBeUnique" }, { name: intl.formatMessage({ id: "triggerTimes" }) })
          );
        },
      }}
      items={TIME_VALUES.map((timeValue) => ({
        value: timeValue,
        content: <ItemContent>{timeValue}</ItemContent>,
      }))}
    />
  );
};

const MeridiemField = ({ index, timeFieldsCount }: { index: number; timeFieldsCount: number }) => {
  const {
    control,
    formState: { isSubmitted },
    trigger,
  } = useFormContext<FormValues>();

  return (
    <FormControl
      sx={{ display: "flex", alignItems: "center", flexDirection: "row", gap: 0, flexWrap: "nowrap", minWidth: "initial" }}
    >
      <Controller
        name={`${FIELD_NAME}.${index}.${MERIDIEM_FIELD}`}
        control={control}
        render={({ field: { onChange, value } }) => (
          <>
            {Object.values(MERIDIEM_NAMES).map((meridiemName) => (
              <Day
                key={meridiemName}
                outlined={value === meridiemName}
                filled={value === meridiemName}
                onClick={() => {
                  onChange(meridiemName);
                  if (isSubmitted) {
                    [...Array(timeFieldsCount)].forEach((_, itemIndex) => {
                      trigger(`${FIELD_NAME}.${itemIndex}.${TIME_FIELD}`);
                    });
                  }
                }}
                value={meridiemName}
              />
            ))}
          </>
        )}
      />
    </FormControl>
  );
};

const ActionField = ({ index }: { index: number }) => {
  const intl = useIntl();

  return (
    <Selector
      name={`${FIELD_NAME}.${index}.${ACTION_FIELD}`}
      id={`trigger-action-${index}`}
      labelMessageId="state"
      required
      fullWidth
      items={[
        {
          value: POWER_SCHEDULE_ACTIONS.POWER_ON,
          content: <ItemContent>{intl.formatMessage({ id: "on" })}</ItemContent>,
        },
        {
          value: POWER_SCHEDULE_ACTIONS.POWER_OFF,
          content: <ItemContent>{intl.formatMessage({ id: "off" })}</ItemContent>,
        },
      ]}
    />
  );
};

const FieldArray = () => {
  const { control } = useFormContext<FormValues>();

  const { fields, append, remove } = useFieldArray<FormValues>({
    control,
    name: FIELD_NAME,
  });

  const onAppend = () =>
    append({
      time: "",
      action: POWER_SCHEDULE_ACTIONS.POWER_ON,
      meridiem: MERIDIEM_NAMES.AM,
    });

  return (
    <>
      {fields.map((item, index) => (
        <Box key={item.id} display="flex" columnGap={2} flexWrap="wrap">
          <Box flexGrow={1} gap={1} flexBasis="150px" display="flex" alignItems="flex-start">
            <TimeField index={index} timeFieldsCount={fields.length} />
            <MeridiemField index={index} timeFieldsCount={fields.length} />
          </Box>
          <Box flexGrow={2} display="flex" flexBasis="200px" gap={SPACING_1}>
            <Box flexGrow={1}>
              <ActionField index={index} />
            </Box>
            <Box>
              <FormControl>
                <IconButton
                  dataTestId={`btn_delete_trigger_${index}`}
                  icon={<DeleteOutlinedIcon />}
                  onClick={() => (fields.length > 1 ? remove(index) : null)}
                  disabled={fields.length === 1}
                  tooltip={{
                    show: true,
                    value: <FormattedMessage id="delete" />,
                  }}
                  color="error"
                  type="button"
                  ref={null}
                />
              </FormControl>
            </Box>
          </Box>
        </Box>
      ))}
      {fields.length < MAX_TRIGGERS && (
        <FormControl fullWidth>
          <Button
            dataTestId="btn_add_trigger"
            messageId="addTrigger"
            size="large"
            color="primary"
            onClick={onAppend}
            variant="outlined"
            dashedBorder
            type="button"
            ref={null}
          />
        </FormControl>
      )}
    </>
  );
};

const TriggersFieldArray = ({ isLoading = false }) => (
  <>
    <Box display="flex" alignItems="center">
      <FormLabel component="p" required>
        <FormattedMessage id="triggers" />
      </FormLabel>
      <QuestionMark
        dataTestId="triggers_help"
        messageId="triggersDescription"
        messageValues={{ br: <br /> }}
        fontSize="small"
      />
    </Box>
    {isLoading ? <InputLoader fullWidth /> : <FieldArray />}
  </>
);

export default TriggersFieldArray;
