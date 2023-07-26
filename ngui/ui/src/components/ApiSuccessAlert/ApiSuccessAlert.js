import React, { useEffect, useState } from "react";
import { SUCCESS_HANDLER_TYPE_ALERT } from "api/constants";
import { LATEST_SUCCESS_HANDLED_LABEL } from "api/reducer";
import ApiSuccessMessage from "components/ApiSuccessMessage";
import SnackbarAlert from "components/SnackbarAlert";
import { useApiState } from "hooks/useApiState";
import { useApiStateData } from "hooks/useApiStateData";
import { useLastResult } from "hooks/useLastResult";
import { isEmpty } from "utils/objects";

const ApiSuccessAlert = () => {
  const { apiStateData: latestSuccessHandledLabel } = useApiStateData(LATEST_SUCCESS_HANDLED_LABEL);

  const {
    lastResult: { successHandlerType, response: { data: { success = {} } = {} } = {} }
  } = useLastResult(latestSuccessHandledLabel);

  const { isLoading } = useApiState(latestSuccessHandledLabel);

  const [open, setOpen] = useState(false);

  useEffect(() => {
    setOpen(!isEmpty(success));
  }, [success]);

  const handleClose = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setOpen(false);
  };

  const successMessage =
    successHandlerType === SUCCESS_HANDLER_TYPE_ALERT && !isEmpty(success) ? (
      <ApiSuccessMessage successCode={success.code} reason={success.reason} params={success.messageParams} />
    ) : null;

  return successHandlerType === SUCCESS_HANDLER_TYPE_ALERT && successMessage !== null && !isLoading ? (
    <SnackbarAlert severity={success.alertSeverity} body={successMessage} openState={open} handleClose={handleClose} />
  ) : null;
};

export default ApiSuccessAlert;
