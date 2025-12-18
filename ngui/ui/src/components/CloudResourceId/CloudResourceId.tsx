import Link from "@mui/material/Link";
import { Link as RouterLink } from "react-router-dom";
import Tooltip from "components/Tooltip";
import { getResourceUrl } from "urls";
import useStyles from "./CloudResourceId.styles";

const SHORTENED_CLOUD_RESOURCE_ID_PREFIX = ".../";

const CloudResourceIdString = ({
  cloudResourceIdentifier,
  resourceId,
  resourceType,
  dataTestId,
  disableLink = false,
  tooltip
}) => {
  const {
    classes: { longNamesBreak }
  } = useStyles();

  const content =
    resourceId && !disableLink ? (
      <Link
        to={resourceType ? `${getResourceUrl(resourceId)}?resourceType=${resourceType}` : getResourceUrl(resourceId)}
        component={RouterLink}
        data-test-id={dataTestId}
        className={longNamesBreak}
      >
        {cloudResourceIdentifier}
      </Link>
    ) : (
      <span className={longNamesBreak} data-test-id={dataTestId}>
        {cloudResourceIdentifier}
      </span>
    );

  if (tooltip) {
    return <Tooltip title={tooltip}>{content}</Tooltip>;
  }

  return content;
};

const CloudResourceId = (props) => {
  const { cloudResourceIdentifier = "", separator = "/", disableFullNameTooltip = false } = props;

  // Additional check to handle cloudResourceIdentifier having 'null' or 'undefined' substring
  if (separator && cloudResourceIdentifier.includes(separator)) {
    const shortenedCloudResourceId = `${SHORTENED_CLOUD_RESOURCE_ID_PREFIX}${cloudResourceIdentifier.split(separator).pop()}`;

    return (
      <CloudResourceIdString
        {...props}
        cloudResourceIdentifier={shortenedCloudResourceId}
        tooltip={disableFullNameTooltip ? undefined : cloudResourceIdentifier}
      />
    );
  }

  return <CloudResourceIdString {...props} />;
};

export default CloudResourceId;
