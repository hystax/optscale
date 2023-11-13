import { useDispatch } from "react-redux";
import { GET_TOKEN } from "api/auth/actionTypes";
import { signOut } from "utils/api";
import { useApiData } from "./useApiData";

export const useSignOut = () => {
  const dispatch = useDispatch();

  const {
    apiData: { userEmail }
  } = useApiData(GET_TOKEN);

  return () =>
    signOut(dispatch, {
      userEmail
    });
};
