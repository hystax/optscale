import JiraIssuesAttachments from "components/JiraIssuesAttachments";
import KeyValueLabel from "components/KeyValueLabel";
import { BookingTimeMeasure, getBookingTimeMeasuresDefinition } from "components/UpcomingBooking";
import { INFINITY_SIGN } from "utils/constants";

// TODO: generalize Current and Upcoming bookings
const CurrentBooking = ({ employeeName, acquiredSince, releasedAt, jiraIssues = [] }) => {
  const { remained } = getBookingTimeMeasuresDefinition({ releasedAt, acquiredSince });
  return (
    <>
      <KeyValueLabel noWrap messageId="user" value={employeeName} />
      {remained !== INFINITY_SIGN && <BookingTimeMeasure messageId="availableIn" measure={remained} />}
      {jiraIssues.length > 0 && <JiraIssuesAttachments issues={jiraIssues} />}
    </>
  );
};

export default CurrentBooking;
