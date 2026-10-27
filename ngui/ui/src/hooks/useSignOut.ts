import { useDispatch } from "react-redux";
import { signOut } from "utils/api";
import { useGetToken } from "./useGetToken";

export const useSignOut = () => {
  const dispatch = useDispatch();

  const { userEmail } = useGetToken();

  return () =>
    signOut(dispatch, {
      userEmail,
    });
};
