import React, { useEffect } from "react";
import Box from "@mui/material/Box";
import CircularProgress from "@mui/material/CircularProgress";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { splitResources } from "api";
import { GET_SPLIT_RESOURCES } from "api/restapi/actionTypes";
import SplitResourcesAssignContainer from "containers/SplitResourcesAssignContainer";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useInitialMount } from "hooks/useInitialMount";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { useShouldRenderLoader } from "hooks/useShouldRenderLoader";

const SplitResourcesContainer = ({ resourcesIds, closeSideModal }) => {
  const { organizationId } = useOrganizationInfo();

  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(splitResources(organizationId, resourcesIds));
  }, [dispatch, organizationId, resourcesIds]);

  const { isInitialMount, setIsInitialMount } = useInitialMount();

  useEffect(() => {
    if (isInitialMount) {
      setIsInitialMount(false);
    }
  }, [isInitialMount, setIsInitialMount]);

  const {
    apiData: { splitResources: data = {} }
  } = useApiData(GET_SPLIT_RESOURCES);

  const { isLoading: isSplitResourcesLoading } = useApiState(GET_SPLIT_RESOURCES);
  const isLoading = useShouldRenderLoader(isInitialMount, [isSplitResourcesLoading]);

  return isLoading ? (
    <Box margin="auto" width="fit-content">
      <CircularProgress />
    </Box>
  ) : (
    <SplitResourcesAssignContainer data={data} closeSideModal={closeSideModal} />
  );
};

SplitResourcesContainer.propTypes = {
  resourcesIds: PropTypes.array.isRequired,
  closeSideModal: PropTypes.func.isRequired
};

export default SplitResourcesContainer;
