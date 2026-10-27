import CreateResourcePerspectiveForm from "components/forms/CreateResourcePerspectiveForm";
import {
  OrganizationPerspectivesDocument,
  useUpdateOrganizationPerspectivesMutation,
} from "graphql/__generated__/hooks/restapi";
import { useOrganizationPerspectives } from "hooks/coreData/useOrganizationPerspectives";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const CreateResourcePerspectiveContainer = ({
  breakdownBy,
  breakdownData,
  onSuccess,
  onCancel,
  filterValues,
  appliedFilters,
}) => {
  const { organizationId } = useOrganizationInfo();

  const { allPerspectives } = useOrganizationPerspectives();

  const [updateOrganizationPerspectives, { loading }] = useUpdateOrganizationPerspectivesMutation({
    update: (cache, { data }) => {
      cache.writeQuery({
        query: OrganizationPerspectivesDocument,
        variables: { organizationId },
        data: {
          organizationPerspectives: data.updateOrganizationPerspectives,
        },
      });
    },
  });

  const onSubmit = (data) =>
    updateOrganizationPerspectives({
      variables: {
        organizationId,
        value: {
          ...allPerspectives,
          [data.name]: data.payload,
        },
      },
    }).then(onSuccess);

  return (
    <CreateResourcePerspectiveForm
      onSubmit={onSubmit}
      isLoading={loading}
      breakdownBy={breakdownBy}
      breakdownData={breakdownData}
      perspectiveNames={Object.keys(allPerspectives)}
      onCancel={onCancel}
      filterValues={filterValues}
      appliedFilters={appliedFilters}
    />
  );
};

export default CreateResourcePerspectiveContainer;
