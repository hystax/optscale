import React from "react";
import PropTypes from "prop-types";
import { useDispatch, useSelector } from "react-redux";
import { assignResources, sendAssignResourcesRequest } from "api";
import { ASSIGN_RESOURCES } from "api/restapi/actionTypes";
import SplitResources from "components/SplitResources";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { rejectOnError } from "utils/api";

const SplitResourcesAssignContainer = ({ data, closeSideModal }) => {
  const dispatch = useDispatch();
  const resourcesState = useSelector((state) => state.resources) || {};
  const { organizationId } = useOrganizationInfo();

  const assignResourcesOnSubmit = (splitGroup, resourceIds, toSomeoneElse) => {
    const { [splitGroup]: { poolId = "", ownerId: poolOwnerId = "" } = {} } = resourcesState;
    const ownerId = toSomeoneElse ? poolOwnerId : undefined;

    dispatch(assignResources(organizationId, { resourceIds, poolId, ownerId }))
      .then(rejectOnError(dispatch, ASSIGN_RESOURCES))
      .then(closeSideModal);
  };

  const assignResourcesRequestOnSubmit = (splitGroup, resourceIds) => {
    const { [splitGroup]: { employeeId = "" } = {} } = resourcesState;

    dispatch(sendAssignResourcesRequest(organizationId, { resourceIds, employeeId })).then(closeSideModal);
  };

  return (
    <SplitResources
      data={data}
      assignResourcesOnSubmit={assignResourcesOnSubmit}
      assignResourcesRequestOnSubmit={assignResourcesRequestOnSubmit}
    />
  );
};

SplitResourcesAssignContainer.propTypes = {
  data: PropTypes.object.isRequired,
  closeSideModal: PropTypes.func.isRequired
};

export default SplitResourcesAssignContainer;
