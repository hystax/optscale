import { useSelector, shallowEqual } from "react-redux";

export const useShallowEqualSelector = (selector) => useSelector(selector, shallowEqual);
