import React from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { updateOrganization } from "api";
import { UPDATE_ORGANIZATION } from "api/restapi/actionTypes";
import EditOrganizationForm from "components/EditOrganizationForm";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";

const EditOrganizationFormContainer = ({ onCancel }) => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(UPDATE_ORGANIZATION);

  const { name: currentOrganizationName, organizationId } = useOrganizationInfo();

  const onSubmit = (organizationName) => {
    // There is no need to handle edit mode close since organization will be re-requested after deletion
    // and backdrop loader for the entire page will be rendered => edit form will be automatically unmounted
    dispatch(updateOrganization(organizationId, { name: organizationName }));
  };

  return (
    <EditOrganizationForm
      currentOrganizationName={currentOrganizationName}
      onSubmit={onSubmit}
      onCancel={onCancel}
      isLoading={isLoading}
    />
  );
};

EditOrganizationFormContainer.propTypes = {
  onCancel: PropTypes.func.isRequired
};

export default EditOrganizationFormContainer;
