import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import { createClusterType } from "api";
import { CREATE_CLUSTER_TYPE } from "api/restapi/actionTypes";
import CreateClusterTypeForm from "components/forms/CreateClusterTypeForm";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { CLUSTER_TYPES } from "urls";
import { isError } from "utils/api";

const CreateClusterTypeFormContainer = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const { organizationId } = useOrganizationInfo();

  const { isLoading: isSubmitLoading } = useApiState(CREATE_CLUSTER_TYPE);

  const redirect = () => navigate(CLUSTER_TYPES);

  const onSubmit = (formData) => {
    dispatch((_, getState) => {
      dispatch(createClusterType(organizationId, formData))
        .then(() => {
          if (isError(CREATE_CLUSTER_TYPE, getState())) {
            return Promise.reject();
          }
          return Promise.resolve();
        })
        .then(() => redirect());
    });
  };

  const onCancel = () => redirect();

  return <CreateClusterTypeForm onSubmit={onSubmit} onCancel={onCancel} isSubmitLoading={isSubmitLoading} />;
};

export default CreateClusterTypeFormContainer;
