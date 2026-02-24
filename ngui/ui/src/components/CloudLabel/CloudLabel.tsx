import { Box } from "@mui/material";
import Link from "@mui/material/Link";
import { Link as RouterLink } from "react-router-dom";
import CloudTypeIcon from "components/CloudTypeIcon";
import IconLabel from "components/IconLabel";
import { getCloudAccountUrl } from "urls";

const CloudLink = ({ id, name, dataTestId }) => (
  <Link data-test-id={dataTestId} color="primary" to={getCloudAccountUrl(id)} component={RouterLink}>
    {name}
  </Link>
);

const renderLabel = ({ disableLink, name, id, dataTestId }) =>
  disableLink ? <span data-test-id={dataTestId}>{name}</span> : <CloudLink name={name} id={id} dataTestId={dataTestId} />;

const CloudLabel = ({
  type = null,
  name,
  id,
  dataTestId,
  label,
  startAdornment = null,
  endAdornment = null,
  iconProps = {},
  disableLink = false,
  whiteSpace = "nowrap",
  display = "flex",
}) => {
  const hasAdornment = startAdornment || endAdornment;

  const renderIconLabel = ({ display: iconLabelDisplay } = {}) => (
    <IconLabel
      display={iconLabelDisplay}
      icon={<CloudTypeIcon type={type} hasRightMargin {...iconProps} />}
      label={label ? <span data-test-id={dataTestId}>{label}</span> : renderLabel({ disableLink, name, id, dataTestId })}
    />
  );

  if (hasAdornment) {
    return (
      <Box display={display} alignItems="center" whiteSpace={whiteSpace}>
        {startAdornment}
        {renderIconLabel()}
        {endAdornment}
      </Box>
    );
  }

  return renderIconLabel({
    display,
  });
};

export default CloudLabel;
