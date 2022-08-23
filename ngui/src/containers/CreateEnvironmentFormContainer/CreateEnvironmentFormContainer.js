import React from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { createEnvironment } from "api";
import { CREATE_ENVIRONMENT } from "api/restapi/actionTypes";
import CreateEnvironmentForm from "components/CreateEnvironmentForm";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { ENVIRONMENTS } from "urls";
import { isError } from "utils/api";

const CreateEnvironmentFormContainer = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const { organizationId } = useOrganizationInfo();

  const { isLoading: isSubmitLoading } = useApiState(CREATE_ENVIRONMENT);

  const redirect = () => navigate(ENVIRONMENTS);

  const onCancel = () => redirect();

  const onSubmit = (formData) => {
    dispatch((_, getState) => {
      dispatch(createEnvironment(organizationId, formData))
        .then(() => {
          if (isError(CREATE_ENVIRONMENT, getState())) {
            return Promise.reject();
          }
          return Promise.resolve();
        })
        .then(() => redirect());
    });
  };

  return <CreateEnvironmentForm onSubmit={onSubmit} onCancel={onCancel} isSubmitLoading={isSubmitLoading} />;
};

export default CreateEnvironmentFormContainer;
