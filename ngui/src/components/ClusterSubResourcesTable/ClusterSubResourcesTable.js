import React, { useMemo } from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import CloudLabel from "components/CloudLabel";
import KeyValueLabel from "components/KeyValueLabel";
import ResourceCell from "components/ResourceCell";
import Table from "components/Table";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useIsAllowed } from "hooks/useAllowedActions";
import { RESOURCE_ID_COLUMN_CELL_STYLE } from "utils/tables";
import CollapsableTableCell from "../CollapsableTableCell";

const ClusterSubResourcesTable = ({ data = [] }) => {
  const getCaptionText = (value, messageId) => <KeyValueLabel variant="caption" value={value} messageId={messageId} />;
  const tableData = useMemo(
    () =>
      data.map((subResource) => {
        const getLocationCaptionNodes = () =>
          [
            { value: subResource.region, messageId: "region" },
            { value: subResource.details?.service_name, messageId: "service" },
            { value: subResource.details?.k8s_node, messageId: "node" },
            { value: subResource.details?.k8s_namespace, messageId: "namespace" }
          ]
            .filter(({ value }) => Boolean(value))
            .map(({ value, messageId }) => ({
              key: value,
              node: getCaptionText(value, messageId)
            }));

        return {
          ...subResource,
          resource: `${subResource.cloud_resource_id} ${subResource.name}`,
          tagsString: Object.entries(subResource.tags || {})
            .map(([key, val]) => `${key}: ${val}`)
            .join(" "),
          locationString: `${subResource.details?.cloud_name} ${subResource.region} ${subResource.details?.cloud_type} ${subResource.details?.service_name} ${subResource.details?.k8s_node} ${subResource.details?.k8s_namespace}`,
          locationCaptionNodes: getLocationCaptionNodes()
        };
      }),
    [data]
  );

  const isManageCloudCredentialsAllowed = useIsAllowed({ requiredActions: ["MANAGE_CLOUD_CREDENTIALS"] });

  const columns = useMemo(
    () => [
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_tb_resources">
            <FormattedMessage id="resource" />
          </TextWithDataTestId>
        ),
        accessor: "resource",
        style: RESOURCE_ID_COLUMN_CELL_STYLE,
        Cell: ({ row: { original } }) => (
          <ResourceCell
            rowData={{
              resource_name: original.name,
              cloud_resource_id: original.cloud_resource_id,
              resource_id: original.id,
              active: original.active
            }}
          />
        )
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_tb_type">
            <FormattedMessage id="type" />
          </TextWithDataTestId>
        ),
        accessor: "resource_type"
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_tb_location">
            <FormattedMessage id="location" />
          </TextWithDataTestId>
        ),
        accessor: "locationString",
        style: {
          whiteSpace: "nowrap"
        },
        Cell: ({ row: { original } }) => (
          <CaptionedCell caption={original.locationCaptionNodes}>
            <CloudLabel
              enableLink={isManageCloudCredentialsAllowed}
              id={original.cloud_account_id}
              name={original.details?.cloud_name}
              type={original.details?.cloud_type}
            />
          </CaptionedCell>
        )
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_tb_tags">
            <FormattedMessage id="tags" />
          </TextWithDataTestId>
        ),
        accessor: "tagsString",
        disableSortBy: true,
        Cell: ({ row: { original } }) => <CollapsableTableCell maxRows={5} tags={original.tags} />
      }
    ],
    [isManageCloudCredentialsAllowed]
  );

  return (
    <Table
      data={tableData}
      columns={columns}
      withSearch
      localization={{
        emptyMessageId: "noSubResources"
      }}
      pageSize={50}
      counters={{ showCounters: true, hideTotal: false }}
    />
  );
};

ClusterSubResourcesTable.propTypes = {
  data: PropTypes.array
};

export default ClusterSubResourcesTable;
