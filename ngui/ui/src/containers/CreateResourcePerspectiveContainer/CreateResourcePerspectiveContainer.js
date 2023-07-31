import React from "react";
import PropTypes from "prop-types";
import CreateResourcePerspectiveForm from "components/CreateResourcePerspectiveForm";
import Filters from "components/Filters";
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

CreateResourcePerspectiveContainer.propTypes = {
  onSuccess: PropTypes.func.isRequired,
  breakdownBy: PropTypes.string.isRequired,
  breakdownData: PropTypes.object.isRequired,
  filters: PropTypes.instanceOf(Filters).isRequired,
  onCancel: PropTypes.func.isRequired
};

export default CreateResourcePerspectiveContainer;
