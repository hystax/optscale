import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import { INFINITY_SIGN } from "utils/constants";
import { EN_FULL_FORMAT, format, secondsToMilliseconds, intervalToDuration } from "utils/datetime";
import BookingTimeMeasure from "./BookingTimeMeasure";

const getInfiniteBookingTimeMeasuresDefinition = (acquiredSince) => ({
  duration: INFINITY_SIGN,
  remained: INFINITY_SIGN,
  bookedUntil: INFINITY_SIGN,
  // TODO: generalize getBookedSince in InfiniteBookingTimeMeasures and FiniteBookingTimeMeasures
  bookedSince: format(secondsToMilliseconds(acquiredSince), EN_FULL_FORMAT)
});

const getFiniteBookingTimeMeasuresDefinition = (acquiredSince, releasedAt) => {
  const acquiredSinceInMilliseconds = secondsToMilliseconds(acquiredSince);
  const releasedAtInMilliseconds = secondsToMilliseconds(releasedAt);

  return {
    duration: intervalToDuration({
      start: acquiredSinceInMilliseconds,
      end: releasedAtInMilliseconds
    }),
    remained: intervalToDuration({
      start: Date.now(),
      end: releasedAtInMilliseconds
    }),
    bookedUntil: format(releasedAtInMilliseconds, EN_FULL_FORMAT),
    bookedSince: format(acquiredSinceInMilliseconds, EN_FULL_FORMAT)
  };
};

export const getBookingTimeMeasuresDefinition = ({ releasedAt, acquiredSince }) => {
  const timeMeasuresDefinition =
    releasedAt === 0
      ? getInfiniteBookingTimeMeasuresDefinition(acquiredSince)
      : getFiniteBookingTimeMeasuresDefinition(acquiredSince, releasedAt);
  return timeMeasuresDefinition;
};

const UpcomingBooking = ({ employeeName, acquiredSince, releasedAt }) => {
  const { bookedSince, bookedUntil, duration } = getBookingTimeMeasuresDefinition({ releasedAt, acquiredSince });

  return (
    <>
      <KeyValueLabel keyMessageId="user" value={employeeName} />
      <KeyValueLabel keyMessageId="since" valueWhiteSpace="nowrap" value={bookedSince} />
      <KeyValueLabel keyMessageId="until" valueWhiteSpace="nowrap" value={bookedUntil} />
      <BookingTimeMeasure messageId="duration" measure={duration} />
    </>
  );
};

export default UpcomingBooking;
