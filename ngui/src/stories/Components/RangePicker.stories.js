import React from "react";
import RangePicker from "components/RangePicker";
import { getCurrentUTCTimeInSec, addDays, millisecondsToSeconds } from "utils/datetime";
import { select, object } from "@storybook/addon-knobs";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/RangePicker`
};

const today = getCurrentUTCTimeInSec();
const nextWeek = millisecondsToSeconds(addDays(today, 7));

const orientationOptions = {
  horizontal: "horizontal",
  vertical: "vertical"
};

export const basic = () => (
  <RangePicker
    initialDateRange={{ startDate: today, endDate: nextWeek }}
    onChange={(dateRange) => {
      console.log("Start value: ", dateRange.startDate);
      console.log("End value: ", dateRange.endDate);
    }}
  />
);

export const withKnobs = () => (
  <RangePicker
    initialDateRange={{ startDate: today, endDate: nextWeek }}
    onChange={(dateRange) => {
      console.log("Start value: ", dateRange.startDate);
      console.log("End value: ", dateRange.endDate);
    }}
    validation={object("dateValidation", {
      error: false,
      helperText: ""
    })}
    position={select("position", ["default", "start"], "default")}
    orientation={select("orientation", orientationOptions, "horizontal")}
  />
);
