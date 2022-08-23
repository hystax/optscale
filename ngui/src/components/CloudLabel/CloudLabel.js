import React from "react";
import { Box } from "@mui/material";
import Link from "@mui/material/Link";
import PropTypes from "prop-types";
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
  disableLink = false
}) => (
  <Box display="flex" alignItems="center">
    {startAdornment}
    <IconLabel
      icon={<CloudTypeIcon type={type} hasRightMargin {...iconProps} />}
      label={label ? <span data-test-id={dataTestId}>{label}</span> : renderLabel({ disableLink, name, id, dataTestId })}
    />
    {endAdornment}
  </Box>
);

CloudLink.propTypes = {
  name: PropTypes.string.isRequired,
  id: PropTypes.string.isRequired,
  dataTestId: PropTypes.string,
  disableLink: PropTypes.bool
};

const labelOrNameAndIdValidator = (props, propName, componentName) => {
  if (!props.label && !props.name) {
    return new Error(`${componentName}: component must have label or name`);
  }
  if (props.label && props.name) {
    return new Error(`${componentName}: label and name properties should not be applied together`);
  }
  if (props.name && !props.disableLink && !props.id) {
    return new Error(`${componentName}: need an id to create a link`);
  }
  if (props.id && !(typeof props.id === "string" || props.id instanceof String)) {
    return new Error(`${componentName}: id should be a string`);
  }
  if (props.name && !(typeof props.name === "string" || props.name instanceof String)) {
    return new Error(`${componentName}: name should be a string`);
  }
  return null;
};

CloudLabel.propTypes = {
  type: PropTypes.string,
  name: labelOrNameAndIdValidator,
  id: labelOrNameAndIdValidator,
  label: labelOrNameAndIdValidator,
  dataTestId: PropTypes.string,
  disableLink: PropTypes.bool,
  startAdornment: PropTypes.any,
  endAdornment: PropTypes.any,
  iconProps: PropTypes.object
};

export default CloudLabel;
