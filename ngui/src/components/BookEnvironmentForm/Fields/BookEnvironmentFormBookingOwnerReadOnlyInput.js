import React from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import Input from "components/Input";

const BookEnvironmentFormBookingOwnerReadOnlyInput = ({ value }) => (
  <Input
    required
    InputProps={{
      readOnly: true
    }}
    value={value}
    label={<FormattedMessage id="bookingOwner" />}
    type="text"
  />
);
BookEnvironmentFormBookingOwnerReadOnlyInput.propTypes = {
  value: PropTypes.string.isRequired
};

export default BookEnvironmentFormBookingOwnerReadOnlyInput;
