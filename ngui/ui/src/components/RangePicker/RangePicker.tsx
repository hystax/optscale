import { useRef, useMemo, useState } from "react";
import EventOutlinedIcon from "@mui/icons-material/EventOutlined";
import { FormattedMessage, useIntl } from "react-intl";
import DateRangePicker from "components/DateRangePicker";
import IconButton from "components/IconButton";
import OutlinedDiv from "components/OutlinedDiv";
import Popover from "components/Popover";
import {
  getMaxPickerDateSec,
  getMinPickerDateSec,
  fitRangeIntoInterval,
  formatRangeToShortNotation,
  millisecondsToSeconds,
  secondsToMilliseconds
} from "utils/datetime";
import { objectMap } from "utils/objects";

const RangePicker = ({
  validation = {},
  initialDateRange,
  definedRanges,
  onChange,
  onApply,
  notSetMessageId = "datesNotSet",
  fullWidth = false,
  isUtc = true,
  minTimestamp = getMinPickerDateSec(isUtc),
  maxTimestamp = getMaxPickerDateSec(isUtc)
}) => {
  const intl = useIntl();

  const minDateDayStartMS = secondsToMilliseconds(minTimestamp);
  const maxDateDayEndMS = secondsToMilliseconds(maxTimestamp);

  // dates across the app transfered in utc timestamps
  const [dateRangeMS, setDateRangeMS] = useState(() =>
    fitRangeIntoInterval(
      { minDate: minDateDayStartMS, maxDate: maxDateDayEndMS },
      objectMap(initialDateRange, secondsToMilliseconds)
    )
  );
  // changing it's value only after apply hit. It helps to revert dates value back after popover is closed without apply
  const lastAppliedRangeMS = useRef(dateRangeMS);

  // date range picker same for both fields
  const popoverContent = useMemo(
    () => (
      <DateRangePicker
        open
        onChange={(rangeInMS) => {
          setDateRangeMS(rangeInMS);
          onChange(objectMap(rangeInMS, millisecondsToSeconds));
        }}
        initialDateRange={dateRangeMS}
        minDate={minDateDayStartMS}
        maxDate={maxDateDayEndMS}
        definedRanges={definedRanges}
        isUtc={isUtc}
      />
    ),
    [dateRangeMS, onChange, minDateDayStartMS, maxDateDayEndMS, definedRanges, isUtc]
  );

  const onApplyWrapper = () => {
    lastAppliedRangeMS.current = dateRangeMS;
    if (typeof onApply === "function") {
      onApply();
    }
  };

  const onClose = () => {
    setDateRangeMS(lastAppliedRangeMS.current);
    onChange(objectMap(lastAppliedRangeMS.current, millisecondsToSeconds));
  };

  const dateAsText = dateRangeMS.startDate
    ? formatRangeToShortNotation(
        millisecondsToSeconds(dateRangeMS.startDate),
        millisecondsToSeconds(dateRangeMS.endDate),
        isUtc
      )
    : intl.formatMessage({ id: notSetMessageId });

  return (
    <Popover
      label={
        <OutlinedDiv
          label={<FormattedMessage id={isUtc ? "dateRangeUTC" : "dateRange"} />}
          endAdornment={
            <IconButton
              icon={<EventOutlinedIcon />}
              size="small"
              edge="end"
              style={{ marginRight: "-11px" }}
              dataTestId={"btn_select_date"}
            />
          }
          helperText={validation.helperText}
          fullWidth={fullWidth}
          dataTestId={"text_selected_dates"}
          style={{ minWidth: "130px" }}
        >
          {dateAsText}
        </OutlinedDiv>
      }
      menu={popoverContent}
      buttons={[
        {
          messageId: "apply",
          variant: "contained",
          onClick: onApplyWrapper,
          closable: true,
          dataTestId: "btn_apply_date"
        }
      ]}
      handleClose={onClose}
      rightLabelPosition
      dataTestIds={{ popover: "window_date_range" }}
    />
  );
};

export default RangePicker;
