import { useSelector } from "react-redux";
import { ERROR, SUCCESS, UNKNOWN } from "utils/constants";

export const useLastResult = (targetAction) => {
  const status = useSelector((state) => state.api?.[targetAction]?.status ?? null);

  const lastResult = {};
  if (status === null) {
    lastResult.status = UNKNOWN;
  } else if (status.isError) {
    lastResult.status = ERROR;
    lastResult.response = status.response;
    lastResult.errorHandlerType = status.errorHandlerType;
  } else {
    lastResult.status = SUCCESS;
    lastResult.response = status.response;
    lastResult.successHandlerType = status.successHandlerType;
  }

  return { lastResult };
};
