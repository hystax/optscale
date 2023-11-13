import { useEffect, useRef, useState } from "react";
import { useLastResult } from "hooks/useLastResult";
import { UNKNOWN } from "utils/constants";

export const useApiSendState = (label, submitFunc) => {
  const componentJustMounted = useRef(true);
  const [sendState, setSendState] = useState(UNKNOWN);
  const { lastResult } = useLastResult(label);

  useEffect(() => {
    if (!componentJustMounted.current) {
      setSendState(lastResult.status);
    }
  }, [lastResult]);

  const onSubmit = (...args) => {
    submitFunc(...args);
    // We need to reset status back to UNKNOWN here. Probably a temporary solution.
    // Case:
    // 1) Successfully submit a form
    // 2) Get back to the same form and let the backend fail the submission(e.g., create an entity with the same name)
    // 3) The error will pop up, but a user will still be redirected to a successful callback page, because the status is still SUCCESS from the previous submission
    setSendState(UNKNOWN);
    componentJustMounted.current = false;
  };

  const onResend = () => {
    setSendState(UNKNOWN);
    componentJustMounted.current = true;
  };

  return {
    lastResult,
    sendState,
    onSubmit,
    onResend
  };
};
