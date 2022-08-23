import { useIsAllowed } from "hooks/useAllowedActions";

export const useIsAllowedToCUDEnvironmentProperties = () => {
  const isAllowed = useIsAllowed({ requiredActions: ["MANAGE_RESOURCES"] });

  return isAllowed;
};
