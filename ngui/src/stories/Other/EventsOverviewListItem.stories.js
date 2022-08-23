import React from "react";
import { text, select, number } from "@storybook/addon-knobs";
import EventsOverviewListItem from "components/EventsOverviewListItem";
import { KINDS } from "stories";

export default {
  title: `${KINDS.OTHER}/EventsOverviewListItem`
};

export const basic = () => <EventsOverviewListItem title="Title" description="Description" level="info" time={1578214058} />;

export const withKnobs = () => {
  const options = {
    warning: "warning",
    success: "success",
    info: "info",
    error: "error"
  };
  return (
    <EventsOverviewListItem
      title={text("title", "Initial warning")}
      description={text("description", "Something went wrong!")}
      level={select("level", options, options.error)}
      time={number("time", 1578214058)}
    />
  );
};
