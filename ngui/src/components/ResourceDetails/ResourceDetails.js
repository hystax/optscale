import React, { useMemo } from "react";
import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import CloudLabel from "components/CloudLabel";
import CopyText from "components/CopyText";
import KeyValueLabel from "components/KeyValueLabel";
import PoolLabel from "components/PoolLabel";
import ResourceLabel from "components/ResourceLabel";
import ResourceLink from "components/ResourceLink";
import ResourceTypeLabel from "components/ResourceTypeLabel";
import SubTitle from "components/SubTitle";
import Table from "components/Table";
import { RESOURCE_PAGE_TABS } from "utils/constants";
import { formatUTC, EN_FULL_FORMAT } from "utils/datetime";
import { toKeyValueString, isEmpty } from "utils/objects";
import CollapsableTableCell from "../CollapsableTableCell";

const renderKeyValueLabels = (options) => options.map((opt) => <KeyValueLabel key={opt.messageId} {...opt} />);

const TagsTable = ({ tags }) => {
  const tableData = useMemo(() => [{ tags }], [tags]);
  const columns = useMemo(
    () => [
      {
        accessor: "tags",
        Cell: ({ cell: { value } }) => <CollapsableTableCell tags={value} limit={Infinity} />,
        style: {
          border: "none"
        }
      }
    ],
    []
  );
  return <Table withHeader={false} data={tableData} columns={columns} localization={{ emptyMessageId: "noTags" }} />;
};

const renderTagsTable = (tags) => (
  <>
    <KeyValueLabel dataTestIds={{ key: "lbl_tags" }} messageId="tags" placeholder={null} />
    <TagsTable tags={tags} />
  </>
);

const getIdLabelDefinition = ({ cloudResourceId, isActive }) => ({
  value: () => (
    <CopyText variant="inherit" text={cloudResourceId} dataTestIds={{ button: "btn_copy" }}>
      <ResourceLabel
        cloudResourceId={cloudResourceId}
        isActive={isActive}
        FigureLabelProps={{ textFirst: false }}
        separator={null}
      />
    </CopyText>
  ),
  messageId: "id",
  dataTestIds: {
    key: "lbl_id",
    value: "lbl_id_value"
  }
});

const getLabelDefinition = ({ value, messageId, dataTestIds }) => ({
  value,
  messageId,
  dataTestIds
});

const getNameLabelDefinition = (resourceName) =>
  getLabelDefinition({
    value: resourceName,
    messageId: "name",
    dataTestIds: {
      key: "lbl_name",
      value: "lbl_name_value"
    }
  });

const getSubResourcesLabelDefinition = (count) =>
  getLabelDefinition({
    value: count,
    messageId: "subResources",
    dataTestIds: {
      key: "lbl_sub_resources",
      value: "lbl_sub_resources_value"
    }
  });

const getCloudNameLabelDefinition = (cloudName, cloudAccountId, cloudType) =>
  getLabelDefinition({
    value: () => <CloudLabel id={cloudAccountId} name={cloudName} type={cloudType} />,
    messageId: "dataSource",
    dataTestIds: {
      key: "lbl_cloud",
      value: "lbl_cloud_value"
    }
  });

const getResourceTypeLabelDefinition = (value) =>
  getLabelDefinition({
    value,
    messageId: "type",
    dataTestIds: {
      key: "lbl_type",
      value: "lbl_type_value"
    }
  });

const getServiceNameLabelDefinition = (serviceName) =>
  getLabelDefinition({
    value: serviceName,
    messageId: "service",
    dataTestIds: {
      key: "lbl_service",
      value: "lbl_service_value"
    }
  });

const getRegionLabelDefinition = (region) =>
  getLabelDefinition({
    value: region,
    messageId: "region",
    dataTestIds: {
      key: "lbl_region",
      value: "lbl_region_value"
    }
  });

const getK8sNodeLabelDefinition = (node) =>
  getLabelDefinition({
    value: node,
    messageId: "node",
    dataTestIds: {
      key: "lbl_k8s_node",
      value: "lbl_k8s_node_value"
    }
  });

const getK8sNamespaceLabelDefinition = (namespace) =>
  getLabelDefinition({
    value: namespace,
    messageId: "namespace",
    dataTestIds: {
      key: "lbl_k8s_namespace",
      value: "lbl_k8s_namespace_value"
    }
  });

const getPoolNameLabelDefinition = (poolId, poolName, poolType) =>
  getLabelDefinition({
    value: poolName ? () => <PoolLabel id={poolId} name={poolName} type={poolType} /> : "",
    messageId: "pool",
    dataTestIds: {
      key: "lbl_pool",
      value: "lbl_pool_value"
    }
  });

const getOwnerNameLabelDefinition = (ownerName) =>
  getLabelDefinition({
    value: ownerName,
    messageId: "owner",
    dataTestIds: {
      key: "lbl_owner",
      value: "lbl_owner_value"
    }
  });

const getFirstSeenLabelDefinition = (firstSeen) =>
  getLabelDefinition({
    value: firstSeen ? `${formatUTC(firstSeen, EN_FULL_FORMAT)} UTC` : "",
    messageId: "firstSeenOn",
    dataTestIds: {
      key: "lbl_first_seen",
      value: "lbl_first_seen_value"
    }
  });

const getLastSeenLabelDefinition = (lastSeen) =>
  getLabelDefinition({
    value: lastSeen ? `${formatUTC(lastSeen, EN_FULL_FORMAT)} UTC` : "",
    messageId: "lastSeenOn",
    dataTestIds: {
      key: "lbl_last_seen",
      value: "lbl_last_seen_value"
    }
  });

const getTagsLabelDefinition = (tags) =>
  getLabelDefinition({
    value: toKeyValueString(tags),
    messageId: "tags",
    dataTestIds: {
      key: "lbl_tags",
      value: "lbl_tags_value"
    }
  });

const getVPCNameLabelDefinition = (vpcName) =>
  getLabelDefinition({
    value: vpcName,
    messageId: "metadata.vpcName",
    dataTestIds: {
      key: "lbl_vpc_name",
      value: "lbl_vpc_name_value"
    }
  });

const getVPCIdLabelDefinition = (vpcId) =>
  getLabelDefinition({
    value: vpcId,
    messageId: "metadata.vpcId",
    dataTestIds: {
      key: "lbl_vpc_id",
      value: "lbl_vpc_id_value"
    }
  });

const getCommonLabelsDefinition = ({
  cloudResourceId,
  isActive,
  clusterTypeId,
  poolId,
  poolName,
  poolType,
  ownerName,
  firstSeen,
  lastSeen,
  vpcName,
  vpcId,
  resourceType,
  tags,
  isEnvironment,
  shareable
}) => ({
  idLabelDefinition: getIdLabelDefinition({ cloudResourceId, isActive }),
  resourceTypeLabelDefinition: getResourceTypeLabelDefinition(
    <ResourceTypeLabel
      resourceInfo={{
        clusterTypeId,
        resourceType,
        isEnvironment,
        shareable
      }}
      iconDataTestId={clusterTypeId ? "img_type_cluster_logo" : ""}
    />
  ),
  poolNameLabelDefinition: getPoolNameLabelDefinition(poolId, poolName, poolType),
  ownerNameLabelDefinition: getOwnerNameLabelDefinition(ownerName),
  firstSeenLabelDefinition: getFirstSeenLabelDefinition(firstSeen),
  lastSeenLabelDefinition: getLastSeenLabelDefinition(lastSeen),
  vpcIdLabelDefinition: getVPCIdLabelDefinition(vpcId),
  vpcNameLabelDefinition: getVPCNameLabelDefinition(vpcName),
  tagsLabelDefinition: getTagsLabelDefinition(tags)
});

const ClusterDetails = ({ commonLabels, resourceDetails }) => {
  const { subResources = [], tags } = resourceDetails;

  const shouldRenderTagsTable = !isEmpty(tags);
  const {
    idLabelDefinition,
    resourceTypeLabelDefinition,
    poolNameLabelDefinition,
    ownerNameLabelDefinition,
    firstSeenLabelDefinition,
    lastSeenLabelDefinition,
    tagsLabelDefinition
  } = commonLabels;

  return (
    <Grid container spacing={2}>
      <Grid item xs={12}>
        {renderKeyValueLabels(
          [
            idLabelDefinition,
            getSubResourcesLabelDefinition(subResources.length),
            resourceTypeLabelDefinition,
            poolNameLabelDefinition,
            ownerNameLabelDefinition,
            firstSeenLabelDefinition,
            lastSeenLabelDefinition,
            !shouldRenderTagsTable && tagsLabelDefinition
          ].filter(Boolean)
        )}
        {shouldRenderTagsTable && renderTagsTable(tags)}
      </Grid>
    </Grid>
  );
};

const SimpleResourceDetails = ({ commonLabels, resourceDetails }) => {
  const {
    idLabelDefinition,
    resourceTypeLabelDefinition,
    poolNameLabelDefinition,
    ownerNameLabelDefinition,
    firstSeenLabelDefinition,
    lastSeenLabelDefinition,
    vpcNameLabelDefinition,
    vpcIdLabelDefinition,
    tagsLabelDefinition
  } = commonLabels;

  const { name, cloudName, serviceName, region, k8sNode, k8sNamespace, tags, cloudAccountId, cloudType } = resourceDetails;

  const shouldRenderTagsTable = !isEmpty(tags);

  return (
    <Grid container spacing={2}>
      <Grid item xs={12}>
        {renderKeyValueLabels(
          [
            idLabelDefinition,
            getNameLabelDefinition(name),
            getCloudNameLabelDefinition(cloudName, cloudAccountId, cloudType),
            resourceTypeLabelDefinition,
            getServiceNameLabelDefinition(serviceName),
            region ? getRegionLabelDefinition(region) : null,
            k8sNode ? getK8sNodeLabelDefinition(k8sNode) : null,
            k8sNamespace ? getK8sNamespaceLabelDefinition(k8sNamespace) : null,
            poolNameLabelDefinition,
            ownerNameLabelDefinition,
            firstSeenLabelDefinition,
            lastSeenLabelDefinition,
            vpcIdLabelDefinition,
            vpcNameLabelDefinition,
            !shouldRenderTagsTable && tagsLabelDefinition
          ].filter(Boolean)
        )}
        {shouldRenderTagsTable && renderTagsTable(tags)}
      </Grid>
    </Grid>
  );
};

const getResourceProperties = (props) => {
  const commonLabels = getCommonLabelsDefinition(props);

  if (props.clusterTypeId) {
    return <ClusterDetails resourceDetails={props} commonLabels={commonLabels} />;
  }

  const simpleResourceDetails = <SimpleResourceDetails commonLabels={commonLabels} resourceDetails={props} />;

  if (props.clusterId) {
    return (
      <>
        <Typography gutterBottom data-test-id="p_cluster_part">
          <FormattedMessage
            id="resourceIsPartOfCluster"
            values={{
              link: (chunks) => (
                <ResourceLink resourceId={props.clusterId} tabName={RESOURCE_PAGE_TABS.DETAILS} dataTestId="link_cluster">
                  {chunks}
                </ResourceLink>
              )
            }}
          />
        </Typography>
        {simpleResourceDetails}
      </>
    );
  }
  return simpleResourceDetails;
};

const ResourceDetails = (props) => {
  const resourceProperties = getResourceProperties(props);

  return (
    <>
      <SubTitle>
        <FormattedMessage id="resourceProperties" />
      </SubTitle>
      {resourceProperties}
    </>
  );
};

ClusterDetails.propTypes = {
  commonLabels: PropTypes.object.isRequired,
  resourceDetails: PropTypes.object.isRequired
};

SimpleResourceDetails.propTypes = {
  commonLabels: PropTypes.object.isRequired,
  resourceDetails: PropTypes.object.isRequired
};

ResourceDetails.propTypes = {
  clusterTypeId: PropTypes.string,
  clusterId: PropTypes.string
};

TagsTable.propTypes = {
  tags: PropTypes.object.isRequired
};

export default ResourceDetails;
