import React from "react";
import { KINDS } from "stories";
import MlRunHistoryChart from "components/MlRunHistoryChart";
import { GOALS_FILTER_TYPES } from "utils/constants";

export default {
  title: `${KINDS.COMPONENTS}/MlRunHistoryChart`,
  argTypes: {
    debug: {
      name: "Debug",
      control: "boolean"
    },
    history: {
      name: "History",
      control: "object",
      defaultValue: [10, 12, 11, 20, 9, 8, 7, 10, 20, 21, 19]
    },
    tendency: {
      name: "Tendency",
      options: [GOALS_FILTER_TYPES.MORE_IS_BETTER, GOALS_FILTER_TYPES.LESS_IS_BETTER],
      control: { type: "select" },
      defaultValue: GOALS_FILTER_TYPES.MORE_IS_BETTER
    },
    targetValue: {
      name: "Target value",
      control: { type: "range", min: -100, max: 100, step: 1 },
      defaultValue: 15
    }
  }
};

export const basic = (args) => {
  return (
    <MlRunHistoryChart
      history={args.history}
      targetValue={args.targetValue}
      width={500}
      height={200}
      tendency={args.tendency}
      debug={args.debug}
    />
  );
};
