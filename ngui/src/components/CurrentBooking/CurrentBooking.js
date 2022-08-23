import React from "react";
import PropTypes from "prop-types";
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

CurrentBooking.propTypes = {
  employeeName: PropTypes.string.isRequired,
  acquiredSince: PropTypes.number.isRequired,
  releasedAt: PropTypes.number.isRequired,
  jiraIssues: PropTypes.array
};

export default CurrentBooking;
