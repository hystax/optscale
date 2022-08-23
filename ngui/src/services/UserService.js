import { useEffect } from "react";
import { useDispatch } from "react-redux";
import { getUser } from "api";
import { GET_USER } from "api/auth/actionTypes";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";

export const useGet = (userId) => {
  const dispatch = useDispatch();

  const { isLoading, isDataReady, shouldInvoke } = useApiState(GET_USER);

  useEffect(() => {
    if (userId && shouldInvoke) {
      dispatch(getUser(userId));
    }
  }, [dispatch, shouldInvoke, userId]);

  const { apiData: user } = useApiData(GET_USER);

  return { isLoading, isDataReady, user };
};

function UserService() {
  return { useGet };
}

export default UserService;
