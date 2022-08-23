import React from "react";
import EventsFilter from "components/EventsFilter";
import { KINDS } from "stories";

export default {
  title: `${KINDS.COMPONENTS}/EventsFilter`
};

export const basic = () => (
  <EventsFilter open handleDrawer={() => console.log("Handle drawer")} applyFilter={(data) => console.log(data)} />
);
