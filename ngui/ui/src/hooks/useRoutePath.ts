import { useContext } from "react";
import { RoutePathContext } from "contexts/RoutePathContext";

export const useRoutePath = () => {
  const path = useContext(RoutePathContext);

  return path;
};
