import Grid from "@mui/material/Grid";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import CloudLabel from "components/CloudLabel";
import CopyText from "components/CopyText";
import KeyValueLabel from "components/KeyValueLabel/KeyValueLabel";
import PoolLabel from "components/PoolLabel";
import ResourceLabel from "components/ResourceLabel";
import ResourceLink from "components/ResourceLink";
import ResourceTypeLabel from "components/ResourceTypeLabel";
import SubTitle from "components/SubTitle";
import { RESOURCE_PAGE_TABS } from "utils/constants";
import { formatUTC, EN_FULL_FORMAT } from "utils/datetime";
import { SPACING_2 } from "utils/layouts";
import { MetadataNodes } from "utils/metadata";
import { isEmpty } from "utils/objects";
import CollapsableTableCell from "../CollapsableTableCell";

const renderKeyValueLabels = (options) => options.map((opt) => <KeyValueLabel key={opt.messageId} {...opt} />);

const getIdLabelDefinition = ({ cloudResourceIdentifier, isActive }) => ({
  value: (
    <CopyText variant="inherit" text={cloudResourceIdentifier} dataTestIds={{ button: "btn_copy" }}>
      <ResourceLabel
        cloudResourceIdentifier={cloudResourceIdentifier}
        isActive={isActive}
        FigureLabelProps={{ textFirst: false }}
        separator={null}
      />
    </CopyText>
  ),
  keyMessageId: "id",
  dataTestIds: {
    key: "lbl_id",
    value: "lbl_id_value"
  }
});

const getLabelDefinition = ({ value, keyMessageId, dataTestIds }) => ({
  value,
  keyMessageId,
  dataTestIds
});

const getNameLabelDefinition = (resourceName) =>
  getLabelDefinition({
    value: resourceName,
    keyMessageId: "name",
    dataTestIds: {
      key: "lbl_name",
      value: "lbl_name_value"
    }
  });

const getSubResourcesLabelDefinition = (count) =>
  getLabelDefinition({
    value: count,
    keyMessageId: "subResources",
    dataTestIds: {
      key: "lbl_sub_resources",
      value: "lbl_sub_resources_value"
    }
  });

const getCloudNameLabelDefinition = (cloudName, cloudAccountId, cloudType) =>
  getLabelDefinition({
    value: <CloudLabel id={cloudAccountId} name={cloudName} type={cloudType} />,
    keyMessageId: "dataSource",
    dataTestIds: {
      key: "lbl_cloud",
      value: "lbl_cloud_value"
    }
  });

const getResourceTypeLabelDefinition = (value) =>
  getLabelDefinition({
    value,
    keyMessageId: "type",
    dataTestIds: {
      key: "lbl_type",
      value: "lbl_type_value"
    }
  });

const getServiceNameLabelDefinition = (serviceName) =>
  getLabelDefinition({
    value: serviceName,
    keyMessageId: "service",
    dataTestIds: {
      key: "lbl_service",
      value: "lbl_service_value"
    }
  });

const getRegionLabelDefinition = (region) =>
  getLabelDefinition({
    value: region,
    keyMessageId: "region",
    dataTestIds: {
      key: "lbl_region",
      value: "lbl_region_value"
    }
  });

const getK8sNodeLabelDefinition = (node) =>
  getLabelDefinition({
    value: node,
    keyMessageId: "node",
    dataTestIds: {
      key: "lbl_k8s_node",
      value: "lbl_k8s_node_value"
    }
  });

const getK8sNamespaceLabelDefinition = (namespace) =>
  getLabelDefinition({
    value: namespace,
    keyMessageId: "namespace",
    dataTestIds: {
      key: "lbl_k8s_namespace",
      value: "lbl_k8s_namespace_value"
    }
  });

const getPoolNameLabelDefinition = (poolId, poolName, poolType) =>
  getLabelDefinition({
    value: poolName ? <PoolLabel id={poolId} name={poolName} type={poolType} /> : "",
    keyMessageId: "pool",
    dataTestIds: {
      key: "lbl_pool",
      value: "lbl_pool_value"
    }
  });

const getOwnerNameLabelDefinition = (ownerName) =>
  getLabelDefinition({
    value: ownerName,
    keyMessageId: "owner",
    dataTestIds: {
      key: "lbl_owner",
      value: "lbl_owner_value"
    }
  });

const getFirstSeenLabelDefinition = (firstSeen) =>
  getLabelDefinition({
    value: firstSeen ? `${formatUTC(firstSeen, EN_FULL_FORMAT)} UTC` : "",
    keyMessageId: "firstSeenOn",
    dataTestIds: {
      key: "lbl_first_seen",
      value: "lbl_first_seen_value"
    }
  });

const getLastSeenLabelDefinition = (lastSeen) =>
  getLabelDefinition({
    value: lastSeen ? `${formatUTC(lastSeen, EN_FULL_FORMAT)} UTC` : "",
    keyMessageId: "lastSeenOn",
    dataTestIds: {
      key: "lbl_last_seen",
      value: "lbl_last_seen_value"
    }
  });

const getCommonLabelsDefinition = ({
  cloudResourceIdentifier,
  isActive,
  clusterTypeId,
  poolId,
  poolName,
  poolType,
  ownerName,
  firstSeen,
  lastSeen,
  resourceType,
  isEnvironment,
  shareable
}) => ({
  idLabelDefinition: getIdLabelDefinition({ cloudResourceIdentifier, isActive }),
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
  lastSeenLabelDefinition: getLastSeenLabelDefinition(lastSeen)
});

const ClusterDetails = ({ commonLabels, resourceDetails }) => {
  const { subResources = [] } = resourceDetails;

  const {
    idLabelDefinition,
    resourceTypeLabelDefinition,
    poolNameLabelDefinition,
    ownerNameLabelDefinition,
    firstSeenLabelDefinition,
    lastSeenLabelDefinition
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
            lastSeenLabelDefinition
          ].filter(Boolean)
        )}
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
    vpcIdLabelDefinition
  } = commonLabels;

  const { name, cloudName, serviceName, region, k8sService, k8sNode, k8sNamespace, cloudAccountId, cloudType } =
    resourceDetails;

  return (
    <Grid container spacing={2}>
      <Grid item xs={12}>
        {renderKeyValueLabels(
          [
            idLabelDefinition,
            getNameLabelDefinition(name),
            getCloudNameLabelDefinition(cloudName, cloudAccountId, cloudType),
            resourceTypeLabelDefinition,
            getServiceNameLabelDefinition(serviceName || k8sService),
            region ? getRegionLabelDefinition(region) : null,
            k8sNode ? getK8sNodeLabelDefinition(k8sNode) : null,
            k8sNamespace ? getK8sNamespaceLabelDefinition(k8sNamespace) : null,
            poolNameLabelDefinition,
            ownerNameLabelDefinition,
            firstSeenLabelDefinition,
            lastSeenLabelDefinition,
            vpcIdLabelDefinition,
            vpcNameLabelDefinition
          ].filter(Boolean)
        )}
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

const getColumnSize = (shouldRenderTagsTable, shouldRenderMetadata) => {
  if (shouldRenderTagsTable && shouldRenderMetadata) {
    return 4;
  }
  if (shouldRenderTagsTable || shouldRenderMetadata) {
    return 6;
  }
  return 12;
};

const ResourceDetails = (props) => {
  const metadataTags = MetadataNodes(props).getTags();
  const resourceProperties = getResourceProperties(props);
  const { tags } = props;

  const shouldRenderTagsTable = !isEmpty(tags) && Object.values(tags).filter(Boolean);
  const shouldRenderMetadata = !isEmpty(metadataTags) && Object.values(metadataTags).filter(Boolean);

  const columnSize = getColumnSize(shouldRenderTagsTable, shouldRenderMetadata);

  return (
    <Grid container spacing={SPACING_2}>
      <Grid item xs={12} sm={columnSize}>
        <SubTitle>
          <FormattedMessage id="resourceProperties" />
        </SubTitle>
        {resourceProperties}
      </Grid>
      {shouldRenderMetadata && (
        <Grid item xs={12} sm={columnSize}>
          <SubTitle>
            <FormattedMessage id="resourceMetadata" />
          </SubTitle>
          <CollapsableTableCell maxRows={10} tags={metadataTags} sorted={false} />
        </Grid>
      )}
      {shouldRenderTagsTable && (
        <Grid item xs={12} sm={columnSize}>
          <SubTitle>
            <FormattedMessage id="tags" />
          </SubTitle>
          <CollapsableTableCell tags={tags} />
        </Grid>
      )}
    </Grid>
  );
};

export default ResourceDetails;
