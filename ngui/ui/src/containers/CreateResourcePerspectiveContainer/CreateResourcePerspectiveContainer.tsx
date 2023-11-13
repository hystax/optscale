import CreateResourcePerspectiveForm from "components/CreateResourcePerspectiveForm";
import { useOrganizationPerspectives } from "hooks/useOrganizationPerspectives";
import OrganizationOptionsService from "services/OrganizationOptionsService";

const CreateResourcePerspectiveContainer = ({ filters, breakdownBy, breakdownData, onSuccess, onCancel }) => {
  const { allPerspectives } = useOrganizationPerspectives();

  const { useUpdateOrganizationPerspectives } = OrganizationOptionsService();

  const { update, isLoading } = useUpdateOrganizationPerspectives();

  const onSubmit = (data) => {
    update(
      {
        ...allPerspectives,
        [data.name]: data.payload
      },
      onSuccess
    );
  };

  return (
    <CreateResourcePerspectiveForm
      onSubmit={onSubmit}
      isLoading={isLoading}
      breakdownBy={breakdownBy}
      breakdownData={breakdownData}
      filters={filters}
      onCancel={onCancel}
    />
  );
};

export default CreateResourcePerspectiveContainer;
