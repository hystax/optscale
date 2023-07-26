import React, { useEffect } from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";

import { getResourceLimitHits } from "api";
import { GET_RESOURCE_LIMIT_HITS } from "api/restapi/actionTypes";
import ResourceLimitHits from "components/ResourceLimitHits";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";

const ResourceLimitHitsContainer = ({ resourceId }) => {
  const dispatch = useDispatch();

  const {
    apiData: { limitHits = [] }
  } = useApiData(GET_RESOURCE_LIMIT_HITS);
  const { isLoading, shouldInvoke } = useApiState(GET_RESOURCE_LIMIT_HITS, { resourceId });

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getResourceLimitHits(resourceId));
    }
  }, [resourceId, shouldInvoke, dispatch]);

  return <ResourceLimitHits limitHits={limitHits} isLoading={isLoading} />;
};

ResourceLimitHitsContainer.propTypes = {
  resourceId: PropTypes.string.isRequired
};

export default ResourceLimitHitsContainer;
