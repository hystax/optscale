import React, { useState } from "react";
import { Divider } from "@mui/material";
import { Box } from "@mui/system";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import Button from "components/Button";
import Chip from "components/Chip";
import DashedTypography from "components/DashedTypography";
import DateRangePicker from "components/DateRangePicker";
import Popover from "components/Popover";
import { getMaxPickerDateSec, getMinPickerDateSec, secondsToMilliseconds } from "utils/datetime";

const AdHocDatesPickerContent = ({ defaultStartDate, defaultEndDate, isUtc, onApply, definedRanges = [] }) => {
  const [pickerDateRange, setPickerDateRange] = useState({
    startDate: defaultStartDate,
    endDate: defaultEndDate
  });

  return (
    <>
      <DateRangePicker
        open
        onChange={(rangeInMS) => setPickerDateRange(rangeInMS)}
        initialDateRange={{
          startDate: defaultStartDate,
          endDate: defaultEndDate
        }}
        minDate={secondsToMilliseconds(getMinPickerDateSec(isUtc))}
        maxDate={secondsToMilliseconds(getMaxPickerDateSec(isUtc))}
        isUtc={isUtc}
        definedRanges={definedRanges}
      />
      <Box display="flex" justifyContent="flex-end" p={0.5}>
        <Button variant="contained" messageId="apply" color="primary" onClick={() => onApply(pickerDateRange)} />
      </Box>
    </>
  );
};

const AdHocDates = ({ defaultStartDate, defaultEndDate, isUtc, onApply }) => (
  <Popover
    label={
      <DashedTypography>
        <FormattedMessage id="custom" />
      </DashedTypography>
    }
    renderMenu={({ closeHandler }) => (
      <AdHocDatesPickerContent
        defaultStartDate={defaultStartDate}
        defaultEndDate={defaultEndDate}
        isUtc={isUtc}
        onApply={(params) => {
          onApply(params);
          closeHandler();
        }}
      />
    )}
    rightLabelPosition
  />
);

const LinearDatePicker = ({ selectedRange, onSelectedRangeChange, ranges }) => (
  <Box
    sx={{
      display: "inline-flex",
      alignItems: "center",
      flexWrap: "wrap",
      gap: (theme) => theme.spacing(1),
      minHeight: "40px"
    }}
  >
    <Box>
      <Chip label={selectedRange.name} color="info" size="medium" variant="outlined" />
    </Box>
    <Divider style={{ marginLeft: "8px", marginRight: "8px", width: "2px" }} flexItem orientation="vertical" />
    {ranges.map((def) => {
      if (def.type === "custom") {
        return (
          <AdHocDates
            key={def.type}
            defaultStartDate={selectedRange.interval.startDate}
            defaultEndDate={selectedRange.interval.endDate}
            isUtc={def.isUtc}
            onApply={(pickerDateRange) => {
              onSelectedRangeChange({
                name: def.getName(pickerDateRange.startDate, pickerDateRange.endDate),
                interval: def.getInterval(pickerDateRange.startDate, pickerDateRange.endDate),
                searchParams: def.getSearchParams(pickerDateRange.startDate, pickerDateRange.endDate)
              });
            }}
          />
        );
      }

      return (
        <DashedTypography
          key={def.type}
          onClick={() => {
            onSelectedRangeChange({
              name: def.getName(),
              interval: def.getInterval(),
              searchParams: def.getSearchParams()
            });
          }}
        >
          {def.getName()}
        </DashedTypography>
      );
    })}
  </Box>
);

LinearDatePicker.propTypes = {
  selectedRange: PropTypes.object.isRequired,
  onSelectedRangeChange: PropTypes.func.isRequired,
  ranges: PropTypes.array.isRequired
};

export default LinearDatePicker;
