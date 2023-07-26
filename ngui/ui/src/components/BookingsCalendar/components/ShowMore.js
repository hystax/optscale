import React, { useState } from "react";
import { FormattedMessage } from "react-intl";
import useStyles from "../BookingsCalendar.styles";
import Event from "./Event";
import Popover from "./Popover";

const ShowMore = ({ count, events }) => {
  const { classes, cx } = useStyles();

  const [selectedEvent, setSelectedEvent] = useState("");

  return (
    <Popover
      popoverId="show-more-popover"
      onClose={() => setSelectedEvent("")}
      popoverContent={
        <div className={classes.showMoreEventsPopupWrapper}>
          {events.map((event) => (
            <div
              key={event.title}
              className={cx("rbc-event", event.title === selectedEvent ? classes.selectedEvent : "", classes.event)}
              onClick={() => {
                setSelectedEvent(event.title);
              }}
            >
              <Event event={event} />
            </div>
          ))}
        </div>
      }
    >
      <FormattedMessage id="countMore" values={{ count }} />
    </Popover>
  );
};

export default ShowMore;
