import { useEffect, useState } from "react";
import { useDispatch } from "react-redux";
import { connectSlackUser } from "api";
import { CONNECT_SLACK_USER } from "api/slacker/actionTypes";
import ConnectSlack from "components/ConnectSlack";
import { useApiState } from "hooks/useApiState";
import { isError } from "utils/api";

const ConnectSlackContainer = ({ secret }) => {
  const dispatch = useDispatch();
  const [hasError, setHasError] = useState(false);

  const { isLoading } = useApiState(CONNECT_SLACK_USER);

  useEffect(() => {
    dispatch((_, getState) => {
      dispatch(connectSlackUser(secret))
        .then(() => {
          if (isError(CONNECT_SLACK_USER, getState())) {
            return Promise.reject();
          }
          return undefined;
        })
        .catch(() => setHasError(true));
    });
  }, [dispatch, secret]);

  return <ConnectSlack isLoading={isLoading} isError={hasError} />;
};

export default ConnectSlackContainer;
