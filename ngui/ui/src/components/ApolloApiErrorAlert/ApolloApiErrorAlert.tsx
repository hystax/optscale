import { useEffect, useState } from "react";
import { useReactiveVar } from "@apollo/client";
import ApiErrorMessage from "components/ApiErrorMessage";
import SnackbarAlert from "components/SnackbarAlert";
import { errorVar } from "graphql/reactiveVars";

const ApolloApiErrorAlert = () => {
  const error = useReactiveVar(errorVar);

  const { id, url, errorCode, errorReason, params, apolloErrorMessage } = error ?? {};

  const [open, setOpen] = useState(false);

  useEffect(() => {
    setOpen(!!id);
  }, [id]);

  const handleClose = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setOpen(false);
  };

  const getErrorMessage = () => {
    if (errorCode) {
      return <ApiErrorMessage errorCode={errorCode} reason={errorReason} url={url} params={params} />;
    }
    if (apolloErrorMessage) {
      return apolloErrorMessage;
    }
    return null;
  };

  const errorMessage = getErrorMessage();

  return (
    errorMessage !== null && (
      <SnackbarAlert
        severity="error"
        body={errorMessage}
        openState={open}
        handleClose={handleClose}
        dataTestIds={{
          snackbar: "alert_error",
        }}
      />
    )
  );
};

export default ApolloApiErrorAlert;
