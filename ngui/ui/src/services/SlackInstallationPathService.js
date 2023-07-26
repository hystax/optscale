import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getSlackInstallationPath } from "api";
import { GET_SLACK_INSTALLATION_PATH } from "api/slacker/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";

export const useGet = () => {
  const dispatch = useDispatch();
  const { shouldInvoke, isLoading } = useApiState(GET_SLACK_INSTALLATION_PATH);

  const {
    apiData: { url = "" }
  } = useApiData(GET_SLACK_INSTALLATION_PATH);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getSlackInstallationPath());
    }
  }, [dispatch, shouldInvoke]);

  return { isLoading, url };
};

function SlackInstallationPathService() {
  return { useGet };
}

export default SlackInstallationPathService;
