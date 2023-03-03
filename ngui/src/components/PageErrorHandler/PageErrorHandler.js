import React, { useEffect, useState } from "react";
import PropTypes from "prop-types";
import { useLocation } from "react-router-dom";
import { useApiStateData } from "hooks/useApiStateData";
import { useLastResult } from "hooks/useLastResult";
import Error from "pages/Error";

const isNotFound = (status) => status === 404;

const getErrorMessage = (status) => {
  if (isNotFound(status)) {
    return "notFound";
  }

  return "somethingWentWrong";
};

// Currently only 404 error is handled, due to page-wide approach. Corresponding issue is created.
const PageErrorHandler = ({ children }) => {
  const { apiStateData: latestErrorLabel } = useApiStateData("latestErrorLabel");

  const {
    lastResult: { response: { status } = {} }
  } = useLastResult(latestErrorLabel);

  const [isError, setIsError] = useState(false);

  const { pathname } = useLocation();

  useEffect(() => {
    setIsError(false);
  }, [pathname]);

  useEffect(() => {
    setIsError(isNotFound(status));
  }, [status]);

  if (isError) {
    return <Error context={{ messageId: getErrorMessage(status) }} />;
  }

  return children;
};

PageErrorHandler.propTypes = {
  children: PropTypes.node
};

export default PageErrorHandler;
