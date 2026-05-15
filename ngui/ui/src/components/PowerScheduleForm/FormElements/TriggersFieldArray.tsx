import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import {
  Box,
  FormControl,
  FormLabel,
  Typography,
} from "@mui/material";
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
import { DAY_OF_WEEK_LABELS, TIME_VALUES, FIELD_NAMES } from "../constants";
import { FormValues } from "../types";

const { FIELD_NAME } = FIELD_NAMES.TRIGGERS_FIELD_ARRAY;
const TIME_FIELD = FIELD_NAMES.TRIGGERS_FIELD_ARRAY.TIME;
const MERIDIEM_FIELD = FIELD_NAMES.TRIGGERS_FIELD_ARRAY.MERIDIEM;
const ACTION_FIELD = FIELD_NAMES.TRIGGERS_FIELD_ARRAY.ACTION;
const DAYS_OF_WEEK_FIELD = FIELD_NAMES.TRIGGERS_FIELD_ARRAY.DAYS_OF_WEEK;

const MAX_TRIGGERS = 8;

const TimeField = ({ index, timeFieldsCount }: { index: number; timeFieldsCount: number }) => {
  const { formState: { isSubmitted }, trigger } = useFormContext();
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
          [...Array(timeFieldsCount)].forEach((_, i) => trigger(`${FIELD_NAME}.${i}.${TIME_FIELD}`));
        }
      }}
      validate={{
        unique: (value, formValues) => {
          const allFull = formValues[FIELD_NAME].map(
            ({ [TIME_FIELD]: t, [MERIDIEM_FIELD]: m }) => `${t} ${m}`
          );
          const current = `${value} ${formValues[FIELD_NAME][index][MERIDIEM_FIELD]}`;
          return (
            allFull.filter((v) => v === current).length === 1 ||
            intl.formatMessage({ id: "entitiesMustBeUnique" }, { name: intl.formatMessage({ id: "triggerTimes" }) })
          );
        },
      }}
      items={TIME_VALUES.map((v) => ({ value: v, content: <ItemContent>{v}</ItemContent> }))}
    />
  );
};

const MeridiemField = ({ index, timeFieldsCount }: { index: number; timeFieldsCount: number }) => {
  const { control, formState: { isSubmitted }, trigger } = useFormContext<FormValues>();
  return (
    <FormControl sx={{ display: "flex", alignItems: "center", flexDirection: "row", gap: 0, flexWrap: "nowrap", minWidth: "initial" }}>
      <Controller
        name={`${FIELD_NAME}.${index}.${MERIDIEM_FIELD}`}
        control={control}
        render={({ field: { onChange, value } }) => (
          <>
            {Object.values(MERIDIEM_NAMES).map((m) => (
              <Day
                key={m}
                outlined={value === m}
                filled={value === m}
                onClick={() => {
                  onChange(m);
                  if (isSubmitted) {
                    [...Array(timeFieldsCount)].forEach((_, i) => trigger(`${FIELD_NAME}.${i}.${TIME_FIELD}`));
                  }
                }}
                value={m}
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
        { value: POWER_SCHEDULE_ACTIONS.POWER_ON, content: <ItemContent>{intl.formatMessage({ id: "on" })}</ItemContent> },
        { value: POWER_SCHEDULE_ACTIONS.POWER_OFF, content: <ItemContent>{intl.formatMessage({ id: "off" })}</ItemContent> },
      ]}
    />
  );
};

const DaysOfWeekField = ({ index }: { index: number }) => {
  const { control } = useFormContext<FormValues>();
  return (
    <Controller
      name={`${FIELD_NAME}.${index}.${DAYS_OF_WEEK_FIELD}`}
      control={control}
      render={({ field: { value, onChange } }) => {
        const selected: number[] = value ?? [];
        return (
          <Box display="flex" alignItems="center" flexWrap="wrap" gap={0.25}>
            {DAY_OF_WEEK_LABELS.map((label, d) => (
              <Day
                key={d}
                value={label}
                filled={selected.includes(d)}
                outlined={selected.includes(d)}
                onClick={() => {
                  const next = selected.includes(d) ? selected.filter((x) => x !== d) : [...selected, d].sort();
                  onChange(next);
                }}
              />
            ))}
            {selected.length === 0 && (
              <Typography variant="caption" color="text.secondary" sx={{ ml: 0.5 }}>
                <FormattedMessage id="everyDay" />
              </Typography>
            )}
          </Box>
        );
      }}
    />
  );
};

const TriggerRow = ({ index, fieldCount, onRemove }: { index: number; fieldCount: number; onRemove: () => void }) => (
  <Box
    display="flex"
    flexDirection="column"
    gap={1}
    sx={{ border: "1px solid", borderColor: "divider", borderRadius: 1, p: 1.5 }}
  >
    <Box display="flex" columnGap={2} flexWrap="wrap" alignItems="flex-start">
      <Box flexGrow={1} gap={1} flexBasis="150px" display="flex" alignItems="flex-start">
        <TimeField index={index} timeFieldsCount={fieldCount} />
        <MeridiemField index={index} timeFieldsCount={fieldCount} />
      </Box>
      <Box flexGrow={1} display="flex" flexBasis="200px" gap={SPACING_1}>
        <Box flexGrow={1}>
          <ActionField index={index} />
        </Box>
        <Box>
          <FormControl>
            <IconButton
              dataTestId={`btn_delete_trigger_${index}`}
              icon={<DeleteOutlinedIcon />}
              onClick={onRemove}
              disabled={fieldCount === 1}
              tooltip={{ show: true, value: <FormattedMessage id="delete" /> }}
              color="error"
              type="button"
              ref={null}
            />
          </FormControl>
        </Box>
      </Box>
    </Box>
    <Box>
      <DaysOfWeekField index={index} />
    </Box>
  </Box>
);

const FieldArray = () => {
  const { control } = useFormContext<FormValues>();
  const { fields, append, remove } = useFieldArray<FormValues>({ control, name: FIELD_NAME });

  const onAppend = () =>
    append({
      time: "",
      action: POWER_SCHEDULE_ACTIONS.POWER_ON,
      meridiem: MERIDIEM_NAMES.AM,
      daysOfWeek: [],
    });

  return (
    <Box display="flex" flexDirection="column" gap={2}>
      {fields.map((item, index) => (
        <TriggerRow
          key={item.id}
          index={index}
          fieldCount={fields.length}
          onRemove={() => (fields.length > 1 ? remove(index) : null)}
        />
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
    </Box>
  );
};

const TriggersFieldArray = ({ isLoading = false }) => (
  <>
    <Box display="flex" alignItems="center" mb={1}>
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
