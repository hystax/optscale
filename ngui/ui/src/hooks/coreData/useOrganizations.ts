import { useOrganizationsQuery } from "graphql/__generated__/hooks/restapi";

export const useOrganizations = () => {
  const { data: { organizations = [] } = {} } = useOrganizationsQuery({
    fetchPolicy: "cache-only",
  });

  return organizations;
};
