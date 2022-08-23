import React, { useEffect } from "react";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { getCloudAccountDetails } from "api";
import { GET_CLOUD_ACCOUNT_DETAILS } from "api/restapi/actionTypes";
import CloudAccountDetails from "components/CloudAccountDetails";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";

const CloudAccountDetailsContainer = ({ cloudAccountId }) => {
  const dispatch = useDispatch();

  const {
    apiData: { cloudAccountDetails = {} }
  } = useApiData(GET_CLOUD_ACCOUNT_DETAILS);

  const { isLoading, shouldInvoke } = useApiState(GET_CLOUD_ACCOUNT_DETAILS, cloudAccountId);

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getCloudAccountDetails(cloudAccountId, true));
    }
  }, [shouldInvoke, dispatch, cloudAccountId]);

  return <CloudAccountDetails data={cloudAccountDetails} isLoading={isLoading} />;
};

CloudAccountDetailsContainer.propTypes = {
  cloudAccountId: PropTypes.string.isRequired
};

export default CloudAccountDetailsContainer;
