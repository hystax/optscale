import React from "react";
import Link from "@mui/material/Link";
import PropTypes from "prop-types";
import { Link as RouterLink } from "react-router-dom";
import Tooltip from "components/Tooltip";
import { getResourceUrl } from "urls";

const SHORTENED_CLOUD_RESOURCE_ID_PREFIX = ".../";

const renderLink = ({ resourceId, cloudResourceId, resourceType, dataTestId }) => (
  <Link
    to={resourceType ? `${getResourceUrl(resourceId)}?resourceType=${resourceType}` : getResourceUrl(resourceId)}
    component={RouterLink}
    data-test-id={dataTestId}
  >
    {cloudResourceId}
  </Link>
);

const renderCloudResourceId = ({ cloudResourceId, resourceId, resourceType, dataTestId }) =>
  resourceId ? (
    renderLink({ resourceId, cloudResourceId, resourceType, dataTestId })
  ) : (
    <span data-test-id={dataTestId}>{cloudResourceId}</span>
  );

const renderShortenedCloudResourceId = ({
  shortenedCloudResourceId,
  cloudResourceId,
  resourceId,
  resourceType,
  dataTestId
}) => (
  <Tooltip title={cloudResourceId}>
    {renderCloudResourceId({ cloudResourceId: shortenedCloudResourceId, resourceId, resourceType, dataTestId })}
  </Tooltip>
);

const getShortenedCloudResourceId = (cloudResourceId, separator) => cloudResourceId.split(separator).pop();

const getCloudResourceIdWithPrefix = (id) => `${SHORTENED_CLOUD_RESOURCE_ID_PREFIX}${id}`;

const CloudResourceId = ({ cloudResourceId, resourceId = "", resourceType = "", separator = "/", dataTestId }) => {
  // Additional check to handle cloudResourceId having 'null' or 'undefined' substring
  if (separator && cloudResourceId.includes(separator)) {
    const shortenedCloudResourceId = getShortenedCloudResourceId(cloudResourceId, separator);
    return renderShortenedCloudResourceId({
      shortenedCloudResourceId: getCloudResourceIdWithPrefix(shortenedCloudResourceId),
      cloudResourceId,
      resourceId,
      resourceType,
      dataTestId
    });
  }

  return renderCloudResourceId({ cloudResourceId, resourceId, resourceType, dataTestId });
};

CloudResourceId.propTypes = {
  cloudResourceId: PropTypes.string.isRequired,
  resourceId: PropTypes.string,
  resourceType: PropTypes.string,
  separator: PropTypes.string,
  dataTestId: PropTypes.string
};

export default CloudResourceId;
