import React, { useEffect } from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { getDataSourceDetails } from "api";
import { GET_DATA_SOURCE_DETAILS } from "api/restapi/actionTypes";
import CloudAccountDetails from "components/CloudAccountDetails";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";

const CloudAccountDetailsContainer = ({ cloudAccountId }) => {
  const dispatch = useDispatch();

  const {
    apiData: { cloudAccountDetails = {} }
  } = useApiData(GET_DATA_SOURCE_DETAILS);

  const { isLoading, shouldInvoke, isDataReady } = useApiState(GET_DATA_SOURCE_DETAILS, cloudAccountId);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getDataSourceDetails(cloudAccountId, true));
    }
  }, [shouldInvoke, dispatch, cloudAccountId]);

  return <CloudAccountDetails data={cloudAccountDetails} isLoading={isLoading || !isDataReady} />;
};

CloudAccountDetailsContainer.propTypes = {
  cloudAccountId: PropTypes.string.isRequired
};

export default CloudAccountDetailsContainer;
