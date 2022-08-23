import React from "react";
import { text, number, select } from "@storybook/addon-knobs";
import {
  TASK_INCOMING_ASSIGNMENT_REQUESTS,
  TASK_OUTGOING_ASSIGNMENT_REQUESTS,
  TASK_EXCEEDED_POOLS,
  TASK_EXCEEDED_POOL_FORECASTS
} from "utils/constants";
import TasksOverviewListItem from "components/TasksOverviewListItem";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/TasksOverviewListItem`
};

const options = {
  "Incoming assignment requests": TASK_INCOMING_ASSIGNMENT_REQUESTS,
  "Outgoing assignment requests": TASK_OUTGOING_ASSIGNMENT_REQUESTS,
  "Exceeded pools": TASK_EXCEEDED_POOLS,
  "Exceeded pool forecasts": TASK_EXCEEDED_POOL_FORECASTS
};
const defaultValue = TASK_EXCEEDED_POOLS;

export const basic = () => <TasksOverviewListItem count={5} type={TASK_EXCEEDED_POOLS} />;

export const withKnobs = () => (
  <TasksOverviewListItem
    count={number("count", 5)}
    type={select("type", options, defaultValue)}
    text={text("text", "test text")}
  />
);
