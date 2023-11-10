import { useDispatch } from "react-redux";
import { resetTtl } from "api";

export const useRefetchApis = () => {
  const dispatch = useDispatch();

  return (labels) => {
    labels.forEach((label) => {
      dispatch(resetTtl(label));
    });
  };
};
