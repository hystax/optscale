import React from "react";
import Link from "@mui/material/Link";
import PropTypes from "prop-types";
import { Link as RouterLink } from "react-router-dom";
import Tooltip from "components/Tooltip";
import { getResourceUrl } from "urls";

const SHORTENED_CLOUD_RESOURCE_ID_PREFIX = ".../";

const renderLink = ({ resourceId, cloudResourceIdentifier, resourceType, dataTestId }) => (
  <Link
    to={resourceType ? `${getResourceUrl(resourceId)}?resourceType=${resourceType}` : getResourceUrl(resourceId)}
    component={RouterLink}
    data-test-id={dataTestId}
  >
    {cloudResourceIdentifier}
  </Link>
);

const renderCloudResourceId = ({ cloudResourceIdentifier, resourceId, resourceType, dataTestId, disableLink = false }) =>
  resourceId && !disableLink ? (
    renderLink({ resourceId, cloudResourceIdentifier, resourceType, dataTestId })
  ) : (
    <span data-test-id={dataTestId}>{cloudResourceIdentifier}</span>
  );

const renderShortenedCloudResourceId = ({
  shortenedCloudResourceId,
  cloudResourceIdentifier,
  resourceId,
  resourceType,
  dataTestId,
  disableLink
}) => (
  <Tooltip title={cloudResourceIdentifier}>
    {renderCloudResourceId({
      cloudResourceIdentifier: shortenedCloudResourceId,
      resourceId,
      resourceType,
      dataTestId,
      disableLink
    })}
  </Tooltip>
);

const getShortenedCloudResourceId = (cloudResourceIdentifier, separator) => cloudResourceIdentifier.split(separator).pop();

const getCloudResourceIdWithPrefix = (id) => `${SHORTENED_CLOUD_RESOURCE_ID_PREFIX}${id}`;

const CloudResourceId = ({
  cloudResourceIdentifier = "",
  resourceId = "",
  resourceType = "",
  separator = "/",
  dataTestId,
  disableLink
}) => {
  // Additional check to handle cloudResourceIdentifier having 'null' or 'undefined' substring
  if (separator && cloudResourceIdentifier.includes(separator)) {
    const shortenedCloudResourceId = getShortenedCloudResourceId(cloudResourceIdentifier, separator);
    return renderShortenedCloudResourceId({
      shortenedCloudResourceId: getCloudResourceIdWithPrefix(shortenedCloudResourceId),
      cloudResourceIdentifier,
      resourceId,
      resourceType,
      dataTestId,
      disableLink
    });
  }

  return renderCloudResourceId({ cloudResourceIdentifier, resourceId, resourceType, dataTestId, disableLink });
};

CloudResourceId.propTypes = {
  cloudResourceIdentifier: PropTypes.string.isRequired,
  resourceId: PropTypes.string,
  resourceType: PropTypes.string,
  separator: PropTypes.string,
  dataTestId: PropTypes.string,
  disableLink: PropTypes.bool
};

export default CloudResourceId;
