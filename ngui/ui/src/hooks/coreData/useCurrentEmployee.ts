import { useCurrentEmployeeQuery } from "graphql/__generated__/hooks/restapi";
import { useOrganizationInfo } from "../useOrganizationInfo";

export const useCurrentEmployee = () => {
  const { organizationId } = useOrganizationInfo();

  const { data } = useCurrentEmployeeQuery({
    variables: {
      organizationId,
    },
    fetchPolicy: "cache-only",
  });

  // The current user is not always returned by the API in some corner test cases
  return data?.currentEmployee ?? {};
};
