import { useOrganizationFeaturesQuery } from "graphql/__generated__/hooks/restapi";
import { useOrganizationInfo } from "../useOrganizationInfo";

export const useOrganizationFeatures = () => {
  const { organizationId } = useOrganizationInfo();

  const { data: { organizationFeatures = {} } = {} } = useOrganizationFeaturesQuery({
    fetchPolicy: "cache-only",
    variables: {
      organizationId,
    },
  });

  return organizationFeatures;
};
