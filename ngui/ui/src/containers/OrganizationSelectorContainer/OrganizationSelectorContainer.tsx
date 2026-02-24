import OrganizationSelector from "components/OrganizationSelector";
import { useOrganizationsQuery } from "graphql/__generated__/hooks/restapi";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { useUpdateScope } from "hooks/useUpdateScope";
import { HOME } from "urls";

const OrganizationSelectorContainer = ({ isLoading = false }) => {
  const { data: { organizations = [] } = {} } = useOrganizationsQuery({
    fetchPolicy: "cache-only",
  });

  const { organizationId } = useOrganizationInfo();

  const updateScope = useUpdateScope();

  const handleScopeChange = (scopeId: string) => {
    updateScope({
      newScopeId: scopeId,
      redirectTo: HOME,
    });
  };

  return (
    <OrganizationSelector
      organizations={organizations}
      organizationId={organizationId}
      onChange={handleScopeChange}
      isLoading={isLoading}
    />
  );
};

export default OrganizationSelectorContainer;
