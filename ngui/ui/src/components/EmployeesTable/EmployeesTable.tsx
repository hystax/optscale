import { useMemo } from "react";
import CloudDownloadOutlinedIcon from "@mui/icons-material/CloudDownloadOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import PersonAddOutlinedIcon from "@mui/icons-material/PersonAddOutlined";
import Box from "@mui/material/Box";
import { FormattedMessage, useIntl } from "react-intl";
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
import { useFormatIntervalTimeAgo } from "hooks/useFormatIntervalTimeAgo";
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
    name: employeeName,
    last_login: lastLogin
  } = rowOriginal;

  const formatTimeAgo = useFormatIntervalTimeAgo();

  const intl = useIntl();

  const caption = [
    { caption: employeeId, key: "employeeId" },
    lastLogin !== undefined && {
      caption: `${intl.formatMessage({ id: "lastLogin" })}: ${
        lastLogin === 0 ? intl.formatMessage({ id: "never" }).toLocaleLowerCase() : formatTimeAgo(lastLogin, 1)
      }`,
      key: "lastLogin"
    }
  ].filter(Boolean);

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
    <CaptionedCell caption={caption} enableTextCopy>
      <>
        {employeeName}
        {icons}
      </>
    </CaptionedCell>
  );
};

const renderRoles = ({ assignments = [], organizationName, rowId }, toStringsArray, intl) =>
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

    if (toStringsArray) {
      if (isOrganizationScope) {
        return intl.formatMessage({ id: assignmentPurposeMessageId });
      }
      const role = intl.formatMessage({ id: assignmentPurposeMessageId });
      const roleAt = intl.formatMessage({ id: "roleAt" }, { role });

      return `${roleAt} ${assignmentResourceName}`;
    }

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
  const intl = useIntl();

  const { name: organizationName, organizationId } = useOrganizationInfo();

  const data = useMemo(
    () =>
      employees.map((el) => ({
        ...el,
        assignmentsStringified: renderRoles({ assignments: el.assignments, organizationName, id: el.id }, true, intl).join(" ")
      })),
    [employees, organizationName, intl]
  );

  const columns = useMemo(
    () => [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_user">
            <FormattedMessage id="user" />
          </TextWithDataTestId>
        ),
        accessorKey: "name",
        defaultSort: "asc",
        cell: ({ row: { id, original } }) => <EmployeeCell rowId={id} rowOriginal={original} />
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_email">
            <FormattedMessage id="email" />
          </TextWithDataTestId>
        ),
        accessorKey: "user_email"
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_roles">
            <FormattedMessage id="roles" />
          </TextWithDataTestId>
        ),
        enableSorting: false,
        accessorKey: "assignmentsStringified",
        cell: ({ row: { id, original: { assignments } = {} } }) => renderRoles({ assignments, organizationName, id })
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_actions">
            <FormattedMessage id="actions" />
          </TextWithDataTestId>
        ),
        id: "actions",
        enableSorting: false,
        enableHiding: false,
        cell: ({ row: { original: { name: employeeName, id: employeeId } = {}, index } }) => (
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
        withSearch
        columns={columns}
        actionBar={{
          show: true,
          definition: {
            items: [
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
                key: "download",
                startIcon: <CloudDownloadOutlinedIcon />,
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

export default EmployeesTable;
