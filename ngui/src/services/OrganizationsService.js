import { useDispatch } from "react-redux";
import { createOrganization, getOrganizations as getOrganizationsActionCreator, RESTAPI } from "api";
import { CREATE_ORGANIZATION, GET_ORGANIZATIONS } from "api/restapi/actionTypes";
import { useApiState } from "hooks/useApiState";
import { checkError } from "utils/api";

const useCreate = () => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(CREATE_ORGANIZATION);

  const onCreate = (name) =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(createOrganization(name))
          .then(() => checkError(CREATE_ORGANIZATION, getState()))
          .then(() => resolve(getState()[RESTAPI].CREATE_ORGANIZATION))
          .catch(() => reject());
      });
    });

  return { onCreate, isLoading };
};

const useGet = () => {
  const dispatch = useDispatch();

  const { isLoading } = useApiState(GET_ORGANIZATIONS);

  const getOrganizations = () =>
    new Promise((resolve, reject) => {
      dispatch((_, getState) => {
        dispatch(getOrganizationsActionCreator())
          .then(() => checkError(GET_ORGANIZATIONS, getState()))
          .then(() => resolve())
          .catch(() => reject());
      });
    });

  return { getOrganizations, isLoading };
};

function OrganizationsService() {
  return { useGet, useCreate };
}

export default OrganizationsService;
