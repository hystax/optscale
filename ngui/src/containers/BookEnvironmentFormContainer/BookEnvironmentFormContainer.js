import React, { useEffect, useMemo } from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { bookEnvironment, getSshKeys, createSshKey, RESTAPI } from "api";
import { BOOK_ENVIRONMENT, GET_CURRENT_EMPLOYEE, GET_SSH_KEYS, CREATE_SSH_KEY } from "api/restapi/actionTypes";
import BookEnvironmentForm from "components/BookEnvironmentForm";
import { KEY_NAME_FIELD_ID } from "components/CreateSshKeyNameField";
import { KEY_VALUE_FIELD_ID } from "components/CreateSshKeyValueField";
import { SELECTED_KEY_FIELD_ID } from "components/EnvironmentSshKey";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import AuthorizedEmployeesService from "services/AuthorizedEmployeesService";
import { isError } from "utils/api";
import { SCOPE_TYPES } from "utils/constants";

const getDefaultOwner = (employees, currentEmployee) => employees.find(({ id }) => id === currentEmployee?.id);

const BookEnvironmentFormContainer = ({
  resourceId,
  allBookings = [],
  isEnvironmentAvailable,
  onSuccess,
  onCancel,
  isSshRequired
}) => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();
  const { isLoading: isBookEnvironmentLoading } = useApiState(BOOK_ENVIRONMENT);
  const { isLoading: isCreateSshKeyLoading } = useApiState(CREATE_SSH_KEY);

  const {
    apiData: { currentEmployee = {} }
  } = useApiData(GET_CURRENT_EMPLOYEE);

  const requestParams = useMemo(
    () => ({
      objectType: "cloud_resource", // todo: create constant with all possible types for authorized_employees api
      objectId: resourceId,
      permission: ["BOOK_ENVIRONMENTS"]
    }),
    [resourceId]
  );

  const { useGet } = AuthorizedEmployeesService();

  const { employees, isGetAuthorizedEmployeesLoading } = useGet(requestParams);

  const defaultOwner = getDefaultOwner(employees, currentEmployee);

  const canSetBookingOwner = useIsAllowed({
    entityType: SCOPE_TYPES.RESOURCE,
    entityId: resourceId,
    requiredActions: ["MANAGE_RESOURCES"]
  });

  const dispatchBookEnvironment = ({ bookedBy, bookSince, bookUntil, sshKeyId }) =>
    dispatch((_, getState) => {
      dispatch(
        bookEnvironment(organizationId, {
          resourceId,
          bookedBy,
          bookSince,
          bookUntil,
          sshKeyId
        })
      ).then(() => {
        if (typeof onSuccess === "function" && !isError(BOOK_ENVIRONMENT, getState())) {
          onSuccess();
        }
      });
    });

  const onSubmit = ({
    bookingOwnerId,
    bookSince,
    bookUntil,
    [SELECTED_KEY_FIELD_ID]: selectedSshKey,
    [KEY_NAME_FIELD_ID]: newSshKeyTitle,
    [KEY_VALUE_FIELD_ID]: newSshKeyValue
  }) => {
    const bookedBy = canSetBookingOwner ? bookingOwnerId : currentEmployee?.id;

    const dispatchBookEnvironmentWithKey = (sshKeyId) =>
      dispatchBookEnvironment({
        bookedBy,
        bookSince,
        bookUntil,
        sshKeyId
      });

    // no ssh required — just booking, without keys etc
    if (!isSshRequired) {
      return dispatchBookEnvironmentWithKey(null);
    }

    // ssh required and user selected one of saved keys or booking for another user
    if (!newSshKeyTitle) {
      // we can compute ssh key id
      let sshKeyId = selectedSshKey;
      if (!selectedSshKey) {
        // booking for another user, should find users default_ssh_key_id
        sshKeyId = employees.find(({ id }) => id === bookedBy)?.default_ssh_key_id;
      }

      return dispatchBookEnvironmentWithKey(sshKeyId);
    }

    // user entered new key: we should create it and only after that book environment
    return dispatch((_, getState) => {
      dispatch(
        createSshKey(currentEmployee?.id, { [KEY_NAME_FIELD_ID]: newSshKeyTitle, [KEY_VALUE_FIELD_ID]: newSshKeyValue })
      ).then(() => {
        if (!isError(CREATE_SSH_KEY, getState())) {
          // last element from keys array is the key just created by user
          const allSshKeys = getState()?.[RESTAPI]?.[GET_SSH_KEYS] || [];
          const createdKeyId = allSshKeys.length ? allSshKeys[allSshKeys.length - 1].id : null;
          dispatchBookEnvironmentWithKey(createdKeyId);
        }
      });
    });
  };

  const { apiData: currentEmployeeSshKeys } = useApiData(GET_SSH_KEYS, []);
  const { isDataReady: isGetSshKeysReady, shouldInvoke: shouldInvokeGetSshKeys } = useApiState(GET_SSH_KEYS);

  // get ssh keys for current employee, if environment is ssh_only
  useEffect(() => {
    if (isSshRequired && shouldInvokeGetSshKeys) {
      dispatch(getSshKeys(currentEmployee.id));
    }
  }, [currentEmployee.id, dispatch, isSshRequired, shouldInvokeGetSshKeys]);

  return (
    <BookEnvironmentForm
      resourceId={resourceId}
      onSubmit={onSubmit}
      onCancel={onCancel}
      isLoadingProps={{ isBookEnvironmentLoading, isGetAuthorizedEmployeesLoading, isCreateSshKeyLoading }}
      allBookings={allBookings}
      isEnvironmentAvailable={isEnvironmentAvailable}
      owners={employees}
      defaultBookingOwner={defaultOwner}
      canSetBookingOwner={canSetBookingOwner}
      isSshRequired={isSshRequired}
      currentEmployeeSshKeys={currentEmployeeSshKeys}
      isGetSshKeysReady={isGetSshKeysReady}
    />
  );
};

BookEnvironmentFormContainer.propTypes = {
  resourceId: PropTypes.string.isRequired,
  allBookings: PropTypes.array.isRequired,
  isEnvironmentAvailable: PropTypes.bool.isRequired,
  onSuccess: PropTypes.func,
  onCancel: PropTypes.func,
  isSshRequired: PropTypes.bool
};

export default BookEnvironmentFormContainer;
