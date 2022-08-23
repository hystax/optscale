import React, { useMemo } from "react";
import CloudDownloadOutlinedIcon from "@mui/icons-material/CloudDownloadOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import PersonAddOutlinedIcon from "@mui/icons-material/PersonAddOutlined";
import Box from "@mui/material/Box";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { REST_API_URL } from "api";
import CaptionedCell from "components/CaptionedCell";
import Icon from "components/Icon";
import { JIRA } from "components/Integrations/Jira/Jira";
import KeyValueLabel from "components/KeyValueLabel";
import PoolLabel from "components/PoolLabel";
import { DeleteEmployeeModal, SlackIntegrationModal } from "components/SideModalManager/SideModals";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useFetchAndDownload } from "hooks/useFetchAndDownload";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useOrganizationInfo } from "hooks/useOrganizationInfo";
import JiraIcon from "icons/JiraIcon";
import SlackIcon from "icons/SlackIcon";
import { EMPLOYEES_INVITE, getIntegrationsUrl } from "urls";
import { ROLE_PURPOSES, MEMBER, ORGANIZATION_ROLE_PURPOSES, SCOPE_TYPES, DOWNLOAD_FILE_FORMATS } from "utils/constants";

const EmployeeCell = ({ rowId, rowOriginal }) => {
  const {
    id: employeeId,
    slack_connected: isConnectedToSlack,
    jira_connected: itConnectedToJira,
    name: employeeName
  } = rowOriginal;

  const icons = [
    isConnectedToSlack && (
      <Icon
        key="slack-icon"
        icon={SlackIcon}
        hasLeftMargin
        tooltip={{ show: true, messageId: "connectedToSlack" }}
        dataTestId={`logo_slack_connected_${rowId}`}
        fontSize="small"
      />
    ),
    itConnectedToJira && (
      <Icon
        icon={JiraIcon}
        key="jira-icon"
        hasLeftMargin
        tooltip={{ show: true, messageId: "connectedToJira" }}
        dataTestId={`logo_jira_connected_${rowId}`}
        fontSize="small"
      />
    )
  ].filter(Boolean);

  return (
    <CaptionedCell caption={employeeId} enableTextCopy>
      <>
        {employeeName}
        {icons}
      </>
    </CaptionedCell>
  );
};

const renderRoles = (assignments = [], organizationName, rowId) =>
  [
    {
      purpose: MEMBER,
      assignment_id: organizationName,
      assignment_resource_name: organizationName,
      assignment_resource_type: SCOPE_TYPES.ORGANIZATION
    },
    ...assignments
  ].map((assignment, assignmentIndex) => {
    const {
      purpose,
      assignment_id: assignmentId,
      assignment_resource_id: assignmentResourceId,
      assignment_resource_purpose: assignmentResourcePurpose,
      assignment_resource_name: assignmentResourceName,
      assignment_resource_type: assignmentResourceType
    } = assignment;

    const isOrganizationScope = assignmentResourceType === SCOPE_TYPES.ORGANIZATION;
    const assignmentPurposeMessageId = isOrganizationScope ? ORGANIZATION_ROLE_PURPOSES[purpose] : ROLE_PURPOSES[purpose];

    return (
      <Box key={assignmentId}>
        {isOrganizationScope ? (
          <FormattedMessage id={assignmentPurposeMessageId} />
        ) : (
          <KeyValueLabel
            renderKey={() => (
              <FormattedMessage id="roleAt" values={{ role: <FormattedMessage id={assignmentPurposeMessageId} /> }} />
            )}
            value={
              <PoolLabel
                dataTestId={`link_pool_${rowId}_${assignmentIndex}`}
                name={assignmentResourceName}
                type={assignmentResourcePurpose}
                id={assignmentResourceId}
              />
            }
            separator="space"
          />
        )}
      </Box>
    );
  });

const EmployeesTable = ({ isLoading = false, employees }) => {
  const openSideModal = useOpenSideModal();

  const { name: organizationName, organizationId } = useOrganizationInfo();

  const data = useMemo(() => employees, [employees]);

  const columns = useMemo(
    () => [
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_user">
            <FormattedMessage id="user" />
          </TextWithDataTestId>
        ),
        accessor: "name",
        defaultSort: "asc",
        Cell: ({ row: { id, original } }) => <EmployeeCell rowId={id} rowOriginal={original} />
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_email">
            <FormattedMessage id="email" />
          </TextWithDataTestId>
        ),
        accessor: "user_email"
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_roles">
            <FormattedMessage id="roles" />
          </TextWithDataTestId>
        ),
        disableSortBy: true,
        accessor: "assignments",
        Cell: ({ row: { id, original: { assignments } = {} } }) => renderRoles(assignments, organizationName, id)
      },
      {
        Header: (
          <TextWithDataTestId dataTestId="lbl_actions">
            <FormattedMessage id="actions" />
          </TextWithDataTestId>
        ),
        id: "actions",
        disableSortBy: true,
        isStatic: true,
        Cell: ({ row: { original: { name: employeeName, id: employeeId } = {}, index } }) => (
          <TableCellActions
            items={[
              {
                key: "delete",
                messageId: "delete",
                icon: <DeleteOutlinedIcon />,
                color: "error",
                requiredActions: ["EDIT_PARTNER"],
                dataTestId: `btn_delete_${index}`,
                action: () =>
                  openSideModal(DeleteEmployeeModal, { entityToBeDeleted: { employeeName, employeeId }, employees: data })
              }
            ]}
          />
        )
      }
    ],
    [organizationName, openSideModal, data]
  );

  const { isFileDownloading, fetchAndDownload } = useFetchAndDownload();
  const downloadEmployees = (format) => {
    fetchAndDownload({
      url: `${REST_API_URL}/organizations/${organizationId}/employees?format=${format}`,
      fallbackFilename: `employees.${format}`,
      format
    });
  };

  return isLoading ? (
    <TableLoader columnsCounter={columns.length} showHeader />
  ) : (
    <>
      <Table
        data={data}
        localization={{
          emptyMessageId: "noUsers"
        }}
        counters={{
          showCounters: true,
          hideDisplayed: true
        }}
        columns={columns}
        actionBar={{
          show: true,
          definition: {
            items: [
              {
                key: "download",
                icon: <CloudDownloadOutlinedIcon fontSize="small" />,
                messageId: "download",
                type: "dropdown",
                isLoading: isFileDownloading,
                menu: {
                  items: [
                    {
                      key: "xlsx",
                      messageId: "xlsxFile",
                      action: () => downloadEmployees(DOWNLOAD_FILE_FORMATS.XLSX),
                      dataTestId: "btn_download_xlsx"
                    },
                    {
                      key: "json",
                      messageId: "jsonFile",
                      action: () => downloadEmployees(DOWNLOAD_FILE_FORMATS.JSON),
                      dataTestId: "btn_download_json"
                    }
                  ]
                },
                dataTestId: "btn_download"
              },
              {
                key: "slack",
                icon: <SlackIcon />,
                messageId: "slack",
                action: () => openSideModal(SlackIntegrationModal),
                type: "button",
                dataTestId: "btn_slack"
              },
              {
                key: "jira",
                icon: <JiraIcon />,
                messageId: "jira",
                link: getIntegrationsUrl(JIRA),
                type: "button",
                dataTestId: "btn_jira"
              },
              {
                key: "invite",
                icon: <PersonAddOutlinedIcon fontSize="small" />,
                messageId: "invite",
                link: EMPLOYEES_INVITE,
                type: "button",
                color: "success",
                variant: "contained",
                dataTestId: "btn_invite",
                requiredActions: ["MANAGE_INVITES"]
              }
            ]
          }
        }}
        dataTestIds={{
          container: "table_employees"
        }}
      />
    </>
  );
};

EmployeesTable.propTypes = {
  employees: PropTypes.array.isRequired,
  isLoading: PropTypes.bool
};

export default EmployeesTable;
