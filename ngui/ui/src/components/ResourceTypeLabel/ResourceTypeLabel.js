import React from "react";
import DnsOutlinedIcon from "@mui/icons-material/DnsOutlined";
import GroupWorkOutlinedIcon from "@mui/icons-material/GroupWorkOutlined";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import Icon from "components/Icon";
import IconLabel from "components/IconLabel";

const DefaultLabel = ({ label }) => label || null;

const ClusterLabel = ({ label, iconDataTestId }) => (
  <IconLabel
    icon={<Icon icon={GroupWorkOutlinedIcon} dataTestId={iconDataTestId} hasRightMargin />}
    label={
      <span>
        {label} (<FormattedMessage id="cluster" />)
      </span>
    }
  />
);

const EnvironmentLabel = ({ label, iconDataTestId }) => (
  <IconLabel
    icon={<Icon icon={DnsOutlinedIcon} dataTestId={iconDataTestId} hasRightMargin />}
    label={
      <span>
        {label} (<FormattedMessage id="ItEnvironment" />)
      </span>
    }
  />
);

const EnvironmentClusterLabel = ({ label, iconDataTestId }) => (
  <IconLabel
    icon={
      <>
        <Icon key="environment" icon={DnsOutlinedIcon} dataTestId={`environment_${iconDataTestId}`} hasRightMargin />
        <Icon key="cluster" icon={GroupWorkOutlinedIcon} dataTestId={`cluster_${iconDataTestId}`} hasRightMargin />
      </>
    }
    label={
      <span>
        {label} (<FormattedMessage id="ItEnvironment" />, <FormattedMessage id="cluster" />)
      </span>
    }
  />
);

const getLabelComponent = (resourceInfo) => {
  if (resourceInfo.isEnvironment || resourceInfo.shareable) {
    return resourceInfo.clusterTypeId ? EnvironmentClusterLabel : EnvironmentLabel;
  }
  if (resourceInfo.clusterTypeId) {
    return ClusterLabel;
  }
  return DefaultLabel;
};

const ResourceTypeLabel = ({ resourceInfo, iconDataTestId }) => {
  const LabelComponent = getLabelComponent(resourceInfo);
  return <LabelComponent label={resourceInfo.resourceType} iconDataTestId={iconDataTestId} />;
};

ClusterLabel.propTypes = {
  label: PropTypes.node.isRequired,
  iconDataTestId: PropTypes.string
};

DefaultLabel.propTypes = {
  label: PropTypes.node.isRequired
};

ResourceTypeLabel.propTypes = {
  resourceInfo: PropTypes.shape({
    resourceType: PropTypes.string,
    clusterTypeId: PropTypes.oneOfType([PropTypes.string, PropTypes.bool]),
    isEnvironment: PropTypes.bool
  }).isRequired,
  iconDataTestId: PropTypes.string
};

export default ResourceTypeLabel;
