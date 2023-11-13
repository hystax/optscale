import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import { useDispatch } from "react-redux";
import { updateBooking } from "api";
import { UPDATE_BOOKING } from "api/restapi/actionTypes";
import Button from "components/Button";
import ButtonLoader from "components/ButtonLoader";
import { useApiState } from "hooks/useApiState";
import { isError } from "utils/api";
import { getCurrentUTCTimeInSec } from "utils/datetime";

const ReleaseBookingContainer = ({ bookingId, onSuccess, onCancel }) => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(UPDATE_BOOKING);

  const onSubmit = () =>
    dispatch((_, getState) => {
      dispatch(updateBooking(bookingId, { releasedAt: getCurrentUTCTimeInSec() })).then(() => {
        if (typeof onSuccess === "function" && !isError(UPDATE_BOOKING, getState())) {
          onSuccess();
        }
      });
    });

  return (
    <>
      <Box mb={2}>
        <Typography>
          <FormattedMessage id="releaseBookingInformation" />
        </Typography>
      </Box>
      <Box display="flex">
        <ButtonLoader
          dataTestId="btn_release"
          color="primary"
          messageId="release"
          variant="contained"
          onClick={onSubmit}
          isLoading={isLoading}
        />
        <Button dataTestId="btn_cancel" messageId="cancel" variant="outlined" onClick={onCancel} />
      </Box>
    </>
  );
};

export default ReleaseBookingContainer;
