import { ReactNode } from "react";
import DnsOutlinedIcon from "@mui/icons-material/DnsOutlined";
import GroupWorkOutlinedIcon from "@mui/icons-material/GroupWorkOutlined";
import { FormattedMessage } from "react-intl";
import Icon from "components/Icon";
import IconLabel from "components/IconLabel";

type ClusterIconProps = {
  dataTestId: string;
  hasRightMargin?: boolean;
};

type EnvironmentIconProps = {
  dataTestId: string;
  hasRightMargin?: boolean;
};

type DefaultLabelProps = {
  label: ReactNode;
};

type ClusterLabelProps = {
  label: ReactNode;
  iconDataTestId: string;
};

type EnvironmentLabelProps = {
  label: ReactNode;
  iconDataTestId: string;
};

type EnvironmentClusterLabelProps = {
  label: ReactNode;
  iconDataTestId: string;
};

type ResourceInfo = {
  isEnvironment: boolean;
  shareable: boolean;
  clusterTypeId: string;
  resourceType: string;
};

type ResourceTypeLabelProps = {
  resourceInfo: ResourceInfo;
  iconDataTestId: string;
};

const ClusterIcon = ({ dataTestId, hasRightMargin = false }: ClusterIconProps) => (
  <Icon
    icon={GroupWorkOutlinedIcon}
    dataTestId={dataTestId}
    hasRightMargin={hasRightMargin}
    tooltip={{
      show: true,
      messageId: "cluster",
    }}
  />
);

const EnvironmentIcon = ({ dataTestId, hasRightMargin = false }: EnvironmentIconProps) => (
  <Icon
    icon={DnsOutlinedIcon}
    dataTestId={dataTestId}
    hasRightMargin={hasRightMargin}
    tooltip={{
      show: true,
      messageId: "environment",
    }}
  />
);

const DefaultLabel = ({ label }: DefaultLabelProps) => label || null;

const ClusterLabel = ({ label, iconDataTestId }: ClusterLabelProps) => (
  <IconLabel
    icon={<ClusterIcon dataTestId={iconDataTestId} hasRightMargin />}
    label={
      <span>
        {label} (<FormattedMessage id="cluster" />)
      </span>
    }
  />
);

const EnvironmentLabel = ({ label, iconDataTestId }: EnvironmentLabelProps) => (
  <IconLabel
    icon={<EnvironmentIcon dataTestId={iconDataTestId} hasRightMargin />}
    label={
      <span>
        {label} (<FormattedMessage id="SharedEnvironment" />)
      </span>
    }
  />
);

const EnvironmentClusterLabel = ({ label, iconDataTestId }: EnvironmentClusterLabelProps) => (
  <IconLabel
    icon={
      <>
        <EnvironmentIcon key="environment" dataTestId={`environment_${iconDataTestId}`} hasRightMargin />
        <ClusterIcon key="cluster" dataTestId={`cluster_${iconDataTestId}`} hasRightMargin />
      </>
    }
    label={
      <span>
        {label} (<FormattedMessage id="SharedEnvironment" />, <FormattedMessage id="cluster" />)
      </span>
    }
  />
);

const getLabelComponent = (resourceInfo: ResourceInfo) => {
  if (resourceInfo.isEnvironment || resourceInfo.shareable) {
    return resourceInfo.clusterTypeId ? EnvironmentClusterLabel : EnvironmentLabel;
  }
  if (resourceInfo.clusterTypeId) {
    return ClusterLabel;
  }
  return DefaultLabel;
};

const ResourceTypeLabel = ({ resourceInfo, iconDataTestId }: ResourceTypeLabelProps) => {
  const LabelComponent = getLabelComponent(resourceInfo);
  return <LabelComponent label={resourceInfo.resourceType} iconDataTestId={iconDataTestId} />;
};

export default ResourceTypeLabel;
