import React from "react";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { useDispatch } from "react-redux";
import { deleteBooking } from "api";
import { DELETE_BOOKING } from "api/restapi/actionTypes";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import { useApiState } from "hooks/useApiState";
import { isError } from "utils/api";

const DeleteBookingContainer = ({ bookingId, onSuccess, onCancel }) => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(DELETE_BOOKING);

  const onSubmit = () =>
    dispatch((_, getState) => {
      dispatch(deleteBooking(bookingId)).then(() => {
        if (typeof onSuccess === "function" && !isError(DELETE_BOOKING, getState())) {
          onSuccess();
        }
      });
    });

  return (
    <>
      <Box mb={2}>
        <Typography>
          <FormattedMessage id="deleteBookingInformation" />
        </Typography>
      </Box>
      <Box display="flex">
        <ButtonLoader color="error" messageId="delete" variant="contained" onClick={onSubmit} isLoading={isLoading} />
        <Button messageId="cancel" variant="outlined" onClick={onCancel} />
      </Box>
    </>
  );
};

DeleteBookingContainer.propTypes = {
  bookingId: PropTypes.string.isRequired,
  onSuccess: PropTypes.func,
  onCancel: PropTypes.func
};

export default DeleteBookingContainer;
