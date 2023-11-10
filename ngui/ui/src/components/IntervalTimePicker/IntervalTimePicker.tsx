import { useMemo, useState, useEffect } from "react";
import EventOutlinedIcon from "@mui/icons-material/EventOutlined";
import { FormattedMessage, useIntl } from "react-intl";
import IconButton from "components/IconButton";
import OutlinedDiv from "components/OutlinedDiv";
import Popover from "components/Popover";
import QuickDatePickerValues from "components/QuickDatePickerValues";
import {
  EN_FULL_FORMAT,
  format as dateToString,
  addMinutes,
  addDays,
  roundTimeToInterval,
  AMOUNT_30_MINUTES
} from "utils/datetime";
import { capitalize } from "utils/strings";
import IntervalTimePopoverContent from "./IntervalTimePopoverContent";

const quickValuesItemsDefinition = [
  {
    key: "now",
    label: "now",
    getValue: () => undefined
  },
  {
    key: "3h",
    label: "valueHours",
    translateValues: {
      value: "3",
      symbol: "+"
    },
    getValue: (roundTo) => +addMinutes(roundTimeToInterval(+new Date(), roundTo), 180)
  },
  {
    key: "1d",
    label: "valueDays",
    translateValues: {
      value: "1",
      symbol: "+"
    },
    getValue: (roundTo) => +addDays(roundTimeToInterval(+new Date(), roundTo), 1)
  },
  {
    key: "3d",
    label: "valueDays",
    translateValues: {
      value: "3",
      symbol: "+"
    },
    getValue: (roundTo) => +addDays(roundTimeToInterval(+new Date(), roundTo), 3)
  },
  {
    key: "noLimit",
    label: "noLimit",
    getValue: () => null
  }
];

const QuickValues = ({ quickValues, orQuickValues, onApply, intervalMinutes, dataTestIds = {} }) => {
  const { item: itemDataTestId } = dataTestIds;

  const getItemsDefinition = (values) =>
    quickValuesItemsDefinition
      .filter(({ key }) => values.some((value) => value === key))
      .map((item) => ({
        ...item,
        dataTestId: `${itemDataTestId}_${item.key}`,
        onClick: () => onApply(item.getValue(intervalMinutes))
      }));

  const itemsDefinition = getItemsDefinition(quickValues);
  const orItemsDefinition = orQuickValues ? getItemsDefinition(orQuickValues) : [];

  return (
    <QuickDatePickerValues
      titleMessageId={quickValues.includes("now") ? "setTo" : "setToNow"}
      items={itemsDefinition}
      orItems={orItemsDefinition}
    />
  );
};

const Field = ({
  labelMessageId,
  validation,
  value,
  required,
  fullWidth,
  popoverContent,
  onApply,
  onClose,
  margin,
  dataTestIds = {}
}) => {
  const { input: inputDataTestId, iconButton: iconButtonDataTestId } = dataTestIds;

  return (
    <Popover
      label={
        <OutlinedDiv
          margin={margin}
          label={labelMessageId && <FormattedMessage id={labelMessageId} />}
          required={required}
          endAdornment={
            <IconButton
              icon={<EventOutlinedIcon />}
              size="small"
              edge="end"
              style={{ marginRight: "-11px" }}
              dataTestId={iconButtonDataTestId}
            />
          }
          helperText={validation.helperText}
          error={validation.error}
          fullWidth={fullWidth}
          dataTestId={inputDataTestId}
        >
          {value}
        </OutlinedDiv>
      }
      menu={popoverContent}
      buttons={[
        {
          messageId: "set",
          variant: "contained",
          onClick: onApply,
          closable: true
        }
      ]}
      handleClose={onClose}
    />
  );
};

const IntervalTimePicker = ({
  value,
  onApply,
  validation = {},
  minDate,
  maxDate,
  format = EN_FULL_FORMAT,
  notSetMessageId = "datesNotSet",
  fullWidth = false,
  margin = "none",
  labelMessageId,
  required = false,
  quickValues,
  intervalMinutes = AMOUNT_30_MINUTES,
  dataTestIds = {}
}) => {
  const intl = useIntl();

  const { field: fieldDataTestIds = {}, quickValues: quickValuesDataTestIds = {} } = dataTestIds;

  const [intermediateValue, setIntermediateValue] = useState(value);

  useEffect(() => {
    setIntermediateValue(value);
  }, [value]);

  const displayedValue = intermediateValue
    ? dateToString(intermediateValue, format)
    : capitalize(intl.formatMessage({ id: notSetMessageId }));

  const popoverContent = useMemo(
    () => (
      <IntervalTimePopoverContent
        open
        onDayClick={(newDate) => {
          setIntermediateValue(newDate);
        }}
        initialDate={value}
        minDate={minDate}
        maxDate={maxDate}
        intervalMinutes={intervalMinutes}
      />
    ),
    [value, setIntermediateValue, minDate, maxDate, intervalMinutes]
  );

  const onApplyHandler = () => {
    if (typeof onApply === "function") {
      onApply(intermediateValue);
    }
  };

  const onClose = () => {
    setIntermediateValue(value);
  };

  return (
    <div
      style={{
        display: "grid"
      }}
    >
      <Field
        labelMessageId={labelMessageId}
        validation={validation}
        value={displayedValue}
        margin={margin}
        required={required}
        fullWidth={fullWidth}
        popoverContent={popoverContent}
        onApply={onApplyHandler}
        onClose={onClose}
        dataTestIds={fieldDataTestIds}
      />
      {quickValues && (
        <QuickValues
          quickValues={quickValues.values}
          orQuickValues={quickValues.orValues}
          onApply={onApply}
          intervalMinutes={intervalMinutes}
          dataTestIds={quickValuesDataTestIds}
        />
      )}
    </div>
  );
};

export default IntervalTimePicker;
