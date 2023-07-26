import React from "react";
import Link from "@mui/material/Link";
import PropTypes from "prop-types";
import { Link as RouterLink } from "react-router-dom";
import Tooltip from "components/Tooltip";
import { getResourceUrl } from "urls";
import useStyles from "./CloudResourceId.styles";

const SHORTENED_CLOUD_RESOURCE_ID_PREFIX = ".../";

const CloudResourceIdString = ({ cloudResourceIdentifier, resourceId, resourceType, dataTestId, disableLink = false }) => {
  const {
    classes: { longNamesBreak }
  } = useStyles();

  if (resourceId && !disableLink) {
    return (
      <Link
        to={resourceType ? `${getResourceUrl(resourceId)}?resourceType=${resourceType}` : getResourceUrl(resourceId)}
        component={RouterLink}
        data-test-id={dataTestId}
        className={longNamesBreak}
      >
        {cloudResourceIdentifier}
      </Link>
    );
  }

  return (
    <span className={longNamesBreak} data-test-id={dataTestId}>
      {cloudResourceIdentifier}
    </span>
  );
};

const CloudResourceId = (props) => {
  const { cloudResourceIdentifier = "", separator = "/", disableFullNameTooltip = false } = props;

  // Additional check to handle cloudResourceIdentifier having 'null' or 'undefined' substring
  if (separator && cloudResourceIdentifier.includes(separator)) {
    const shortenedCloudResourceId = `${SHORTENED_CLOUD_RESOURCE_ID_PREFIX}${cloudResourceIdentifier.split(separator).pop()}`;

    return (
      <Tooltip title={disableFullNameTooltip ? undefined : cloudResourceIdentifier}>
        <span>
          <CloudResourceIdString {...props} cloudResourceIdentifier={shortenedCloudResourceId} />
        </span>
      </Tooltip>
    );
  }

  return <CloudResourceIdString {...props} />;
};

CloudResourceId.propTypes = {
  cloudResourceIdentifier: PropTypes.string.isRequired,
  resourceId: PropTypes.string,
  resourceType: PropTypes.string,
  separator: PropTypes.string,
  dataTestId: PropTypes.string,
  disableLink: PropTypes.bool,
  disableFullNameTooltip: PropTypes.bool
};

export default CloudResourceId;
