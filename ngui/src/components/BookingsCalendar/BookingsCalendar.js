import React, { useState } from "react";
import getDay from "date-fns/getDay";
import enUsLocale from "date-fns/locale/en-US";
import parse from "date-fns/parse";
import startOfWeek from "date-fns/startOfWeek";
import PropTypes from "prop-types";
import { Calendar, dateFnsLocalizer, Views } from "react-big-calendar";
import "react-big-calendar/lib/css/react-big-calendar.css";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { format, secondsToMilliseconds, MAX_UTC_DATE_TIMESTAMP } from "utils/datetime";
import { getResourceDisplayedName } from "utils/resources";
import useStyles from "./BookingsCalendar.styles";
import BookingsCalendarLoader from "./BookingsCalendarLoader";
import Event from "./components/Event";
import ShowMore from "./components/ShowMore";
import Toolbar from "./components/Toolbar";

const locales = {
  "en-US": enUsLocale
};

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek,
  getDay,
  locales
});

const getBookingEvents = (environments, eventProps) =>
  environments
    .filter(({ shareable_bookings: shareableBookings }) => !isEmptyArray(shareableBookings))
    .flatMap((environmentWithBookings) => {
      const { shareable_bookings: shareableBookings } = environmentWithBookings;

      return shareableBookings.map((booking) => {
        const { acquired_since: bookedSince, released_at: bookedUntil } = booking;

        return {
          title: getResourceDisplayedName(environmentWithBookings),
          start: new Date(secondsToMilliseconds(bookedSince)),
          end: bookedUntil === 0 ? new Date(MAX_UTC_DATE_TIMESTAMP) : new Date(secondsToMilliseconds(bookedUntil)),
          environment: environmentWithBookings,
          booking,
          props: eventProps
        };
      });
    });

const BookingsCalendar = ({ environments, isLoadingProps = {}, eventProps = {} }) => {
  const { classes } = useStyles();

  const bookingEvents = getBookingEvents(environments, eventProps);

  const [showMoreEvents, setShowMoreEvents] = useState([]);

  const { isGetEnvironmentsLoading = false } = isLoadingProps;

  const calendar = (
    <Calendar
      className={classes.calendar}
      localizer={localizer}
      defaultView={Views.MONTH}
      views={[Views.MONTH, Views.WEEK, Views.DAY]}
      events={bookingEvents}
      toolbar
      popup={false}
      doShowMoreDrillDown={false}
      onShowMore={(events) => setShowMoreEvents(events)}
      scrollToTime={new Date()}
      eventPropGetter={() => ({
        className: classes.event
      })}
      messages={{
        showMore: (count) => <ShowMore count={count} events={showMoreEvents} />
      }}
      components={{
        event: Event,
        toolbar: Toolbar
      }}
    />
  );

  return isGetEnvironmentsLoading ? <BookingsCalendarLoader>{calendar}</BookingsCalendarLoader> : calendar;
};

BookingsCalendar.propTypes = {
  environments: PropTypes.array.isRequired,
  isLoadingProps: PropTypes.shape({
    isGetEnvironmentsLoading: PropTypes.bool
  }),
  eventProps: PropTypes.shape({
    linkedTitle: PropTypes.bool
  })
};

export default BookingsCalendar;
