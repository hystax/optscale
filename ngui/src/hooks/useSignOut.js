import { useDispatch } from "react-redux";
import { reset } from "reducers/route";
import requestManager from "utils/requestManager";

export const useSignOut = () => {
  const dispatch = useDispatch();
  const dispatchReset = () => dispatch(reset());
  const cancelAllPendingRequests = () => requestManager.cancelAllPendingRequests();

  return { dispatchReset, cancelAllPendingRequests };
};
