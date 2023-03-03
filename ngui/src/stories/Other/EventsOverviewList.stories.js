import React from "react";
import EventsOverviewList from "components/EventsOverviewList";
import { KINDS } from "stories";

const events = [
  {
    id: 1,
    description:
      "Machine memcached1, rhel7.2_oracledb, IIS_Acura-Demo, memcached2, memcached3 for customer Snowdrop LLC went to status ERROR",
    time: 1578214058,
    level: "ERROR"
  },
  {
    id: 2,
    description: "Initial replication completed for device AD_SERVER (833eadfa-77e2-4551-9b0c-626eb2481aad)",
    time: 1574680457,
    level: "SUCCESS"
  },
  {
    id: 3,
    description: "Machine rhel7.2_oracledb for customer Snowdrop LLC went to status WARNED",
    time: 1577229048,
    level: "WARNING"
  }
];

export default {
  title: `${KINDS.OTHER}/EventsOverviewList`,
  argTypes: {
    events: { name: "Event", control: "object", defaultValue: events }
  }
};

export const basic = (args) => <EventsOverviewList isLoading={false} events={args.events} />;

export const loading = () => <EventsOverviewList isLoading={true} events={[]} />;

export const empty = () => <EventsOverviewList isLoading={false} events={[]} />;
