import React from "react";
import PropTypes from "prop-types";
import Icon from "components/Icon";
import { useDataSources } from "hooks/useDataSources";

const CloudTypeIcon = ({ type, ...rest }) => {
  const { icon } = useDataSources(type);
  return icon ? <Icon {...rest} icon={icon} /> : null;
};

CloudTypeIcon.propTypes = {
  type: PropTypes.string,
  iconProps: PropTypes.object
};

export default CloudTypeIcon;
