import React from "react";
import { Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import UpcomingBooking from "components/UpcomingBooking";
import BookEnvironmentFormContainer from "containers/BookEnvironmentFormContainer";
import { isEmpty } from "utils/arrays";
import BaseSideModal from "./BaseSideModal";

class BookEnvironmentModal extends BaseSideModal {
  get headerProps() {
    const bookEnvironmentProps = this.payload;
    const environmentName = bookEnvironmentProps.resourceName ?? bookEnvironmentProps.cloudResourceId;

    return {
      messageId: "bookEnvironment",
      formattedMessageValues: {
        environmentName
      },
      dataTestIds: {
        title: "lbl_add_booking",
        closeButton: "bnt_close"
      }
    };
  }

  dataTestId = "smodal_add_booking";

  get content() {
    const bookEnvironmentProps = this.payload;
    return (
      <>
        <div style={{ marginBottom: 16 }}>
          <BookEnvironmentFormContainer
            resourceId={bookEnvironmentProps.id}
            allBookings={bookEnvironmentProps.allBookings}
            isEnvironmentAvailable={bookEnvironmentProps.isEnvironmentAvailable}
            onSuccess={this.closeSideModal}
            onCancel={this.closeSideModal}
            isSshRequired={bookEnvironmentProps.isSshRequired}
          />
        </div>
        {!isEmpty(bookEnvironmentProps.upcomingBookings) && (
          <>
            <Typography gutterBottom>
              <FormattedMessage id="upcomingBookings" />
            </Typography>
            {bookEnvironmentProps.upcomingBookings.map((upcomingBooking) => {
              const {
                acquired_by: { name } = {},
                id: bookingId,
                acquired_since: acquiredSince,
                released_at: releasedAt
              } = upcomingBooking;
              return (
                <div key={bookingId} style={{ marginBottom: 8 }}>
                  <UpcomingBooking employeeName={name} acquiredSince={acquiredSince} releasedAt={releasedAt} />
                </div>
              );
            })}
          </>
        )}
      </>
    );
  }
}

export default BookEnvironmentModal;
