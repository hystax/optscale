import React, { useEffect, useState } from "react";
import { ERROR_HANDLER_TYPE_ALERT } from "api/constants";
import ApiErrorMessage from "components/ApiErrorMessage";
import SnackbarAlert from "components/SnackbarAlert";
import { useApiState } from "hooks/useApiState";
import { useApiStateData } from "hooks/useApiStateData";
import { useLastResult } from "hooks/useLastResult";
import { isEmpty } from "utils/objects";

const ApiErrorAlert = () => {
  const { apiStateData: latestErrorLabel } = useApiStateData("latestErrorLabel");

  const {
    lastResult: { errorHandlerType, response: { data: { error = {} } = {}, config: { url } = {} } = {} }
  } = useLastResult(latestErrorLabel);

  const { isLoading } = useApiState(latestErrorLabel);

  const [open, setOpen] = useState(false);

  useEffect(() => {
    setOpen(!isEmpty(error));
  }, [error]);

  const handleClose = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setOpen(false);
  };

  const errorMessage =
    errorHandlerType === ERROR_HANDLER_TYPE_ALERT && !isEmpty(error) ? (
      <ApiErrorMessage errorCode={error.error_code} reason={error.reason} url={url} params={error.params} />
    ) : null;

  return errorHandlerType === ERROR_HANDLER_TYPE_ALERT && errorMessage !== null && !isLoading ? (
    <SnackbarAlert
      severity="error"
      body={errorMessage}
      openState={open}
      handleClose={handleClose}
      dataTestIds={{
        snackbar: "alert_error"
      }}
    />
  ) : null;
};

export default ApiErrorAlert;
