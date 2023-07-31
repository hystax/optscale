import { useDispatch } from "react-redux";
import { signOut } from "utils/api";

export const useSignOut = () => {
  const dispatch = useDispatch();

  return () => signOut(dispatch);
};
