import { useEffect, useState } from "react";
import { useQuery } from "@apollo/client";
import ApiErrorMessage from "components/ApiErrorMessage";
import SnackbarAlert from "components/SnackbarAlert";
import { GET_ERROR } from "graphql/api/common";

// TODO: implement ERROR_HANDLER_TYPE_ALERT analogy for Apollo queries. https://www.apollographql.com/docs/react/v2/data/error-handling/
const ApolloApiErrorAlert = () => {
  const { data = {} } = useQuery(GET_ERROR);

  const { error: { id, error_code: errorCode, reason: errorReason, url, params } = {} } = data;

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

  const errorMessage = errorCode && <ApiErrorMessage errorCode={errorCode} reason={errorReason} url={url} params={params} />;

  return (
    errorMessage !== null && (
      <SnackbarAlert
        severity="error"
        body={errorMessage}
        openState={open}
        handleClose={handleClose}
        dataTestIds={{
          snackbar: "alert_error"
        }}
      />
    )
  );
};

export default ApolloApiErrorAlert;
