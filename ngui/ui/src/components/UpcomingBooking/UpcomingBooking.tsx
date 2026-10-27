import { FormattedMessage } from "react-intl";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import { EN_FULL_FORMAT, format, secondsToMilliseconds, intervalToDuration } from "utils/datetime";
import Duration from "./Duration";

type UpcomingBookingProps = {
  employeeName: string;
  acquiredSince: number;
  releasedAt: number;
};

const getInfiniteBookingTimeMeasuresDefinition = (acquiredSince: number) =>
  ({
    duration: Infinity,
    remained: Infinity,
    bookedUntil: Infinity,
    // TODO: generalize getBookedSince in InfiniteBookingTimeMeasures and FiniteBookingTimeMeasures
    bookedSince: format(secondsToMilliseconds(acquiredSince), EN_FULL_FORMAT),
  }) as const;

const getFiniteBookingTimeMeasuresDefinition = (acquiredSince: number, releasedAt: number) => {
  const acquiredSinceInMilliseconds = secondsToMilliseconds(acquiredSince);
  const releasedAtInMilliseconds = secondsToMilliseconds(releasedAt);

  return {
    duration: intervalToDuration({
      start: acquiredSinceInMilliseconds,
      end: releasedAtInMilliseconds,
    }),
    remained: intervalToDuration({
      start: Date.now(),
      end: releasedAtInMilliseconds,
    }),
    bookedUntil: format(releasedAtInMilliseconds, EN_FULL_FORMAT),
    bookedSince: format(acquiredSinceInMilliseconds, EN_FULL_FORMAT),
  };
};

export const getBookingTimeMeasuresDefinition = ({
  releasedAt,
  acquiredSince,
}: {
  releasedAt: number;
  acquiredSince: number;
}) => {
  const timeMeasuresDefinition =
    releasedAt === 0
      ? getInfiniteBookingTimeMeasuresDefinition(acquiredSince)
      : getFiniteBookingTimeMeasuresDefinition(acquiredSince, releasedAt);
  return timeMeasuresDefinition;
};

const UpcomingBooking = ({ employeeName, acquiredSince, releasedAt }: UpcomingBookingProps) => {
  const { bookedSince, bookedUntil, duration } = getBookingTimeMeasuresDefinition({ releasedAt, acquiredSince });

  return (
    <>
      <KeyValueLabel keyMessageId="user" value={employeeName} />
      <KeyValueLabel keyMessageId="since" value={bookedSince} />
      <KeyValueLabel keyMessageId="until" value={bookedUntil === Infinity ? <FormattedMessage id="infinite" /> : bookedUntil} />
      {bookedUntil !== Infinity && <Duration duration={duration} />}
    </>
  );
};

export default UpcomingBooking;
