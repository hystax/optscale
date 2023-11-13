import { FormattedMessage } from "react-intl";
import DashedTypography from "components/DashedTypography";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useToggle } from "hooks/useToggle";
import { formatNumericDayAndHour, convertToLocalNumericDayAndHour, ABBREVIATED_WEEK_DAYS } from "utils/datetime";

const renderItems = (value, limit = value.length) =>
  value
    .map((datePoint) => ({
      start: convertToLocalNumericDayAndHour(datePoint.start.hour, datePoint.start.day_of_week),
      end: convertToLocalNumericDayAndHour(datePoint.end.hour, datePoint.end.day_of_week)
    }))
    .sort((a, b) => a.start.dayOfWeek - b.start.dayOfWeek || a.start.hour - b.start.hour)
    .slice(0, limit)
    .map((period) => {
      const startDay = formatNumericDayAndHour(period.start.hour, period.start.dayOfWeek, {
        weekDaysFormat: ABBREVIATED_WEEK_DAYS
      });
      const endDay = formatNumericDayAndHour(period.end.hour, period.end.dayOfWeek, {
        isBeginningOfHour: false,
        weekDaysFormat: ABBREVIATED_WEEK_DAYS
      });

      return <div key={JSON.stringify(period)}>{`${startDay} - ${endDay}`}</div>;
    });

const PossibleShutdownPeriods = ({ value, limit }) => {
  const [isExpanded, toggleExpanded] = useToggle(false);

  return isExpanded ? (
    <>
      {renderItems(value)}
      <DashedTypography onClick={() => toggleExpanded()}>
        <FormattedMessage id="showLess" />
      </DashedTypography>
    </>
  ) : (
    <>
      {renderItems(value, limit)}
      {value.length > limit && (
        <DashedTypography onClick={() => toggleExpanded()}>
          <FormattedMessage id="showMore" />
        </DashedTypography>
      )}
    </>
  );
};

const possibleShutdownPeriods = ({ headerDataTestId, accessorKey = "inactivity_periods" }) => ({
  header: (
    <TextWithDataTestId dataTestId={headerDataTestId}>
      <FormattedMessage id="possibleShutdownPeriods" />
    </TextWithDataTestId>
  ),
  accessorKey,
  cell: ({ cell }) => <PossibleShutdownPeriods value={cell.getValue()} limit={10} />
});

export default possibleShutdownPeriods;
