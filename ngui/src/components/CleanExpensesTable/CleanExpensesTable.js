import React, { useState, useMemo } from "react";
import AssignmentOutlinedIcon from "@mui/icons-material/AssignmentOutlined";
import CloudDownloadOutlinedIcon from "@mui/icons-material/CloudDownloadOutlined";
import DnsOutlinedIcon from "@mui/icons-material/DnsOutlined";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { useDispatch } from "react-redux";
import { markResourcesAsEnvironments } from "api";
import { MARK_RESOURCES_AS_ENVIRONMENTS } from "api/restapi/actionTypes";
import CaptionedCell from "components/CaptionedCell";
import CloudLabel from "components/CloudLabel";
import ExpenseCell from "components/ExpenseCell";
import ExpensesTableHeader from "components/ExpensesTableHeader";
import { IEC_UNITS, useFormatDigitalUnit } from "components/FormattedDigitalUnit";
import KeyValueLabel from "components/KeyValueLabel";
import PoolLabel from "components/PoolLabel";
import ResourceCell from "components/ResourceCell";
import ResourcePaidNetworkTrafficList from "components/ResourcePaidNetworkTrafficList";
import ResourceTypeLabel from "components/ResourceTypeLabel";
import { AssignResourcesModal } from "components/SideModalManager/SideModals";
import Table from "components/Table";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useApiState } from "hooks/useApiState";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import { intl } from "translations/react-intl-config";
import { getCreateAssignmentRuleUrl } from "urls";
import { getValuesByObjectKey } from "utils/arrays";
import {
  ASSIGNMENT_RULE_CONDITIONS_QUERY_PARAMETER,
  DOWNLOAD_FILE_FORMATS,
  CLEAN_EXPENSES_TABLE_QUERY_PARAM_PREFIX,
  METADATA_FIELDS
} from "utils/constants";
import { EN_FORMAT, format, secondsToMilliseconds } from "utils/datetime";
import { RESOURCE_ID_COLUMN_CELL_STYLE } from "utils/tables";
import CollapsableTableCell from "../CollapsableTableCell";

const LocationNodes = ({ region, service_name: serviceName, k8s_node: k8sNode, k8sNamespace }) => {
  const captionSettings = [
    { value: region, messageId: "region" },
    { value: serviceName, messageId: "service" },
    { value: k8sNode, messageId: "node" },
    { value: k8sNamespace, messageId: "namespace" }
  ].filter(({ value }) => Boolean(value));

  const toString = () => captionSettings.map(({ value, messageId }) => `${intl.formatMessage({ id: messageId })}: ${value}`);

  const getNodes = () =>
    captionSettings.map(({ value, messageId }) => ({
      key: value,
      node: <KeyValueLabel variant="caption" value={value} messageId={messageId} />
    }));

  return {
    toString,
    getNodes
  };
};

const MetadataNodes = ({
  first_seen: firstSeen,
  last_seen: lastSeen,
  meta: {
    attached,
    category,
    cpu_count: cpuCount,
    engine,
    engine_version: engineVersion,
    flavor,
    host_ip: hostIp,
    image_id: imageId,
    last_attached: lastAttached,
    last_used: lastUsed,
    os,
    pod_ip: podIp,
    preinstalled,
    size,
    snapshot_id: snapshotId,
    state,
    storage_type: storageType,
    volume_id: volumeId,
    volume_type: volumeType,
    vpc_id: vpcId,
    vpc_name: vpcName,
    zone_id: zoneId
  } = {}
}) => {
  const formatDigitalUnit = useFormatDigitalUnit();
  const dateTimeFields = [
    METADATA_FIELDS.FIRST_SEEN,
    METADATA_FIELDS.LAST_SEEN,
    METADATA_FIELDS.LAST_ATTACHED,
    METADATA_FIELDS.LAST_USED
  ];
  const captionSettings = [
    { value: firstSeen, messageId: METADATA_FIELDS.FIRST_SEEN },
    { value: lastSeen, messageId: METADATA_FIELDS.LAST_SEEN },
    { value: imageId, messageId: METADATA_FIELDS.IMAGE_ID },
    { value: os, messageId: METADATA_FIELDS.OS },
    { value: preinstalled, messageId: METADATA_FIELDS.PREINSTALLED },
    { value: flavor, messageId: METADATA_FIELDS.FLAVOR },
    { value: cpuCount, messageId: METADATA_FIELDS.CPU_COUNT },
    { value: state, messageId: METADATA_FIELDS.STATE },
    { value: zoneId, messageId: METADATA_FIELDS.ZONE_ID },
    { value: snapshotId, messageId: METADATA_FIELDS.SNAPSHOT_ID },
    { value: size, messageId: METADATA_FIELDS.SIZE },
    { value: volumeId, messageId: METADATA_FIELDS.VOLUME_ID },
    { value: engineVersion, messageId: METADATA_FIELDS.ENGINE_VERSION },
    { value: engine, messageId: METADATA_FIELDS.ENGINE },
    { value: volumeType, messageId: METADATA_FIELDS.VOLUME_TYPE },
    { value: storageType, messageId: METADATA_FIELDS.STORAGE_TYPE },
    { value: attached, messageId: METADATA_FIELDS.ATTACHED },
    { value: lastAttached, messageId: METADATA_FIELDS.LAST_ATTACHED },
    { value: lastUsed, messageId: METADATA_FIELDS.LAST_USED },
    { value: hostIp, messageId: METADATA_FIELDS.HOST_IP },
    { value: category, messageId: METADATA_FIELDS.CATEGORY },
    { value: podIp, messageId: METADATA_FIELDS.POD_IP },
    { value: vpcId, messageId: METADATA_FIELDS.VPC_ID },
    { value: vpcName, messageId: METADATA_FIELDS.VPC_NAME }
  ]
    .filter(({ value }) => value !== undefined)
    .map(({ value, messageId }) => {
      if (dateTimeFields.includes(messageId)) {
        return {
          value: value === 0 ? intl.formatMessage({ id: "never" }) : format(secondsToMilliseconds(value), EN_FORMAT),
          messageId
        };
      }
      if (messageId === METADATA_FIELDS.SIZE) {
        return { value: formatDigitalUnit({ value, baseUnit: IEC_UNITS.BYTE, maximumFractionDigits: 1 }), messageId };
      }
      return { value: String(value), messageId };
    });

  const getTags = () =>
    Object.fromEntries(captionSettings.map(({ messageId, value }) => [intl.formatMessage({ id: messageId }), value]));

  const toString = () => captionSettings.map(({ value, messageId }) => `${intl.formatMessage({ id: messageId })}: ${value}`);

  return {
    getTags,
    toString
  };
};

const CleanExpensesTable = ({
  expenses,
  disableColumnsSelection = false,
  downloadResources,
  isDownloadingResources = false,
  startDateTimestamp,
  endDateTimestamp,
  assignmentRuleCreationLinkParameters
}) => {
  const dispatch = useDispatch();
  const { organizationId } = useOrganizationInfo();
  const { isLoading: isMarkResourcesAsEnvironmentsLoading } = useApiState(MARK_RESOURCES_AS_ENVIRONMENTS);

  const columns = useMemo(
    () => [
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_resource_name">
            <FormattedMessage id="resource" />
          </TextWithDataTestId>
        ),
        accessor: "resource",
        style: RESOURCE_ID_COLUMN_CELL_STYLE,
        // if cells are strings just use Cell: ({ cell: { value } }) => <ComponentBasedOn value={value} />
        // useful props are ( {row, cell, column}  )
        Cell: ({ row: { original, id } }) => (
          <ResourceCell rowData={original} dataTestIds={{ labelIds: { label: `resource_name_${id}` } }} />
        ),
        isStatic: true
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_expenses">
            <ExpensesTableHeader startDateTimestamp={startDateTimestamp} endDateTimestamp={endDateTimestamp} />
          </TextWithDataTestId>
        ),
        accessor: "cost",
        Cell: ({ row: { original, id } }) => <ExpenseCell rowData={original} id={id} />,
        defaultSort: "desc",
        isStatic: true
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_paid_network_traffic">
            <FormattedMessage id="paidNetworkTraffic" />
          </TextWithDataTestId>
        ),
        columnsSelector: {
          messageId: "paidNetworkTraffic",
          dataTestId: "btn_toggle_paid_network_traffic"
        },
        accessor: "traffic_expenses",
        disableSortBy: true,
        style: {
          minWidth: 320
        },
        Cell: ({
          row: {
            original: { traffic_expenses: trafficExpenses = [] }
          }
        }) => <ResourcePaidNetworkTrafficList trafficExpenses={trafficExpenses} />
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_metadata">
            <FormattedMessage id="metadata" />
          </TextWithDataTestId>
        ),
        columnsSelector: {
          messageId: "metadata",
          dataTestId: "btn_toggle_column_metadata"
        },
        accessor: "metadataString",
        Cell: ({ row: { original } }) => {
          const metadataTags = MetadataNodes(original).getTags(intl);
          return <CollapsableTableCell maxRows={5} tags={metadataTags} sorted={false} limit={33} />;
        }
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_pool_owner">
            <FormattedMessage id="pool/owner" />
          </TextWithDataTestId>
        ),
        columnsSelector: {
          messageId: "pool/owner",
          dataTestId: "btn_toggle_column_pool_owner"
        },
        accessor: "pool/owner",
        style: {
          whiteSpace: "nowrap"
        },
        Cell: ({
          row: {
            original: { pool, owner },
            id
          }
        }) =>
          pool || owner ? (
            <CaptionedCell caption={owner ? owner.name : ""}>
              {pool && <PoolLabel dataTestId={`resource_pool_${id}`} id={pool.id} name={pool.name} type={pool.purpose} />}
            </CaptionedCell>
          ) : null
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_type">
            <FormattedMessage id="type" />
          </TextWithDataTestId>
        ),
        accessor: "resourceType",
        columnsSelector: {
          messageId: "type",
          dataTestId: "btn_toggle_column_type"
        },
        Cell: ({
          row: {
            original: { resource_type: resourceType, cluster_type_id: clusterTypeId, is_environment: isEnvironment, shareable }
          }
        }) => (
          <ResourceTypeLabel
            resourceInfo={{
              resourceType,
              clusterTypeId,
              isEnvironment,
              shareable
            }}
          />
        )
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_cloud">
            <FormattedMessage id="location" />
          </TextWithDataTestId>
        ),
        columnsSelector: {
          messageId: "location",
          dataTestId: "btn_toggle_column_location"
        },
        accessor: "locationString",
        style: {
          whiteSpace: "nowrap"
        },
        Cell: ({ row: { original, id } }) => {
          const { cloud_account_type: cloudType, cloud_account_id: cloudId, cloud_account_name: cloudName } = original;

          // Clusters do not have cloud type
          if (!cloudType) {
            return null;
          }

          const locationCaptionNodes = LocationNodes(original).getNodes();

          return (
            <CaptionedCell caption={locationCaptionNodes}>
              <CloudLabel dataTestId={`resource_location_${id}`} id={cloudId} name={cloudName} type={cloudType} />
            </CaptionedCell>
          );
        }
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_tags">
            <FormattedMessage id="tags" />
          </TextWithDataTestId>
        ),
        columnsSelector: {
          messageId: "tags",
          dataTestId: "btn_toggle_column_tags"
        },
        accessor: "tagsString",
        disableSortBy: true,
        Cell: ({
          row: {
            original: { tags = {} }
          }
        }) => <CollapsableTableCell maxRows={5} tags={tags} />
      }
    ],
    [endDateTimestamp, startDateTimestamp]
  );

  const [selectedRows, setSelectedRows] = useState([]);

  const tableData = useMemo(
    () =>
      expenses.map((e) => {
        const updatedExpense = { ...e };

        updatedExpense["pool/owner"] = `${e.pool ? e.pool.name : ""} ${e.owner ? e.owner.name : ""}`;

        // making props searchable
        updatedExpense.resource = `${e.cloud_resource_id} ${e.resource_name}`;
        updatedExpense.tagsString = Object.entries(e.tags || {}) // tags object array of entries
          .map(([key, val]) => `${key}: ${val}`) // making array of key: value strings
          .join(" "); // joining with space

        updatedExpense.metadataString = MetadataNodes(e).toString();
        updatedExpense.locationString = `${e.cloud_account_name} ${e.cloud_account_type} ${LocationNodes(e).toString()}`;

        updatedExpense.resourceType = e.cluster_type_id
          ? `${intl.formatMessage({ id: "cluster" })}: ${e.resource_type}`
          : e.resource_type;

        return updatedExpense;
      }),
    [expenses]
  );

  const openSideModal = useOpenSideModal();

  const getActionBarItems = () => {
    const resourceIds = getValuesByObjectKey(selectedRows, "resource_id");

    const actionBarItems = [
      {
        key: "assign",
        icon: <AssignmentOutlinedIcon fontSize="small" />,
        messageId: "assign",
        enableIfSelectedRows: true,
        type: "button",
        dataTestId: "btn_assign",
        action: () => openSideModal(AssignResourcesModal, { resourceIds })
      },
      {
        key: "markAsEnvironment",
        icon: <DnsOutlinedIcon fontSize="small" />,
        messageId: "markAsEnvironment",
        enableIfSelectedRows: true,
        type: "button",
        isLoading: isMarkResourcesAsEnvironmentsLoading,
        requiredActions: ["MANAGE_RESOURCES"],
        dataTestId: "btn_mark_as_environment",
        action: () => {
          dispatch(markResourcesAsEnvironments(organizationId, resourceIds));
        }
      }
    ];

    if (typeof downloadResources === "function") {
      actionBarItems.push({
        key: "download",
        icon: <CloudDownloadOutlinedIcon fontSize="small" />,
        messageId: "download",
        type: "dropdown",
        action: downloadResources,
        isLoading: isDownloadingResources,
        menu: {
          items: [
            {
              key: "xlsx",
              messageId: "xlsxFile",
              action: () => downloadResources(DOWNLOAD_FILE_FORMATS.XLSX),
              dataTestId: "btn_download_xlsx"
            },
            {
              key: "json",
              messageId: "jsonFile",
              action: () => downloadResources(DOWNLOAD_FILE_FORMATS.JSON),
              dataTestId: "btn_download_json"
            }
          ]
        },
        dataTestId: "btn_download"
      });
    }

    if (assignmentRuleCreationLinkParameters) {
      actionBarItems.push({
        key: "addAssignmentRule",
        messageId: "addAssignmentRuleShort",
        icon: <AssignmentOutlinedIcon fontSize="small" />,
        type: "button",
        link: getCreateAssignmentRuleUrl(assignmentRuleCreationLinkParameters)
      });
    }

    return actionBarItems;
  };

  return (
    <>
      <Table
        data={tableData}
        columns={columns}
        pageSize={50}
        setSelectedRows={setSelectedRows}
        addSelectionColumn
        actionBar={{
          show: true,
          definition: {
            items: getActionBarItems()
          }
        }}
        withSearch
        columnsSelectorUID={disableColumnsSelection ? "" : "cleanExpensesTable"}
        localization={{ emptyMessageId: "noResources" }}
        queryParamPrefix={CLEAN_EXPENSES_TABLE_QUERY_PARAM_PREFIX}
        counters={{ showCounters: true, hideTotal: true }}
        dataTestIds={{
          infoArea: {
            displayed: "counter_displayed",
            selected: "counter_selected"
          },
          searchInput: "input_search",
          searchButton: "btn_search",
          deleteSearchButton: "btn_delete_search",
          columnsSelector: {
            container: "list_columns",
            button: "btn_columns",
            clear: "btn_select_clear_all"
          }
        }}
      />
    </>
  );
};

CleanExpensesTable.propTypes = {
  expenses: PropTypes.array.isRequired,
  startDateTimestamp: PropTypes.number,
  endDateTimestamp: PropTypes.number,
  disableColumnsSelection: PropTypes.bool,
  downloadResources: PropTypes.func,
  isDownloadingResources: PropTypes.bool,
  assignmentRuleCreationLinkParameters: PropTypes.shape({
    [ASSIGNMENT_RULE_CONDITIONS_QUERY_PARAMETER]: PropTypes.arrayOf(
      PropTypes.shape({
        type: PropTypes.string.isRequired,
        value: PropTypes.oneOfType([
          PropTypes.shape({ tagKey: PropTypes.string.isRequired, tagValue: PropTypes.string.isRequired })
        ]).isRequired
      })
    )
  })
};

export default CleanExpensesTable;
