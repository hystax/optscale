import { useMemo, Fragment } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import LockOpenOutlinedIcon from "@mui/icons-material/LockOpenOutlined";
import PowerSettingsNewOutlinedIcon from "@mui/icons-material/PowerSettingsNewOutlined";
import ScheduleOutlinedIcon from "@mui/icons-material/ScheduleOutlined";
import VpnKeyOutlinedIcon from "@mui/icons-material/VpnKeyOutlined";
import { Box, Stack } from "@mui/material";
import { FormattedMessage } from "react-intl";
import CaptionedCell from "components/CaptionedCell";
import Chip from "components/Chip";
import CloudResourceId from "components/CloudResourceId";
import CurrentBooking from "components/CurrentBooking";
import Icon from "components/Icon";
import Markdown from "components/Markdown";
import PoolLabel from "components/PoolLabel";
import ResourceLink from "components/ResourceLink";
import {
  BookEnvironmentModal,
  DeleteEnvironmentBookingModal,
  DeleteEnvironmentModal,
  ReleaseEnvironmentModal
} from "components/SideModalManager/SideModals";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { ENVIRONMENTS_TOUR_IDS } from "components/Tour";
import UpcomingBooking from "components/UpcomingBooking";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { ENVIRONMENTS_TABLE } from "reducers/columns";
import { ENVIRONMENT_CREATE } from "urls";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { SCOPE_TYPES, RESOURCE_PAGE_TABS, ENVIRONMENT_TOUR_IDS_BY_DYNAMIC_FIELDS } from "utils/constants";
import { millisecondsToSeconds } from "utils/datetime";
import { SPACING_1 } from "utils/layouts";
import { getCloudResourceIdentifier, getResourceDisplayedName } from "utils/resources";
import { CELL_EMPTY_VALUE } from "utils/tables";

const NAME_COLUMN_ACCESSOR = "displayedName";

const renderEnvironmentCell = ({ resource, index }) => {
  const { id, name, resource_type: resourceType, ssh_only: requireSshKey } = resource;

  return (
    <CaptionedCell caption={resourceType}>
      {name ? (
        <ResourceLink tabName={RESOURCE_PAGE_TABS.DETAILS} resourceId={id} dataTestId={`environment_name_${index}`}>
          {name}
        </ResourceLink>
      ) : (
        <CloudResourceId
          cloudResourceIdentifier={getCloudResourceIdentifier(resource)}
          resourceId={id}
          dataTestId={`environment_name_${index}`}
        />
      )}
      {requireSshKey && (
        <Icon icon={VpnKeyOutlinedIcon} hasLeftMargin tooltip={{ show: true, messageId: "sshKeyRequired" }} fontSize="small" />
      )}
    </CaptionedCell>
  );
};

// TODO: seems like we don't need resourceId to get active and upcoming bookings
// since «allBookings» already includes bookings only for a particular resource
const getActiveBooking = (allBookings, resourceId) => {
  const nowSecondsTimestamp = millisecondsToSeconds(Date.now());

  const activeBooking = allBookings.find(
    (booking) =>
      booking.resource_id === resourceId &&
      booking.acquired_since < nowSecondsTimestamp &&
      (nowSecondsTimestamp < booking.released_at || booking.released_at === 0)
  );

  return activeBooking || null;
};

const getUpcomingBookings = (allBookings, id) =>
  allBookings
    .filter((booking) => booking.resource_id === id && booking.acquired_since > millisecondsToSeconds(Date.now()))
    .sort((a, b) => a.acquired_since - b.acquired_since);

const getTableData = (data) => {
  const patchedWithDisplayedName = data.map((obj) => ({
    ...obj,
    // used for sorting
    [NAME_COLUMN_ACCESSOR]: obj.name || obj.cloud_resource_id || obj.cloud_resource_hash
  }));
  return patchedWithDisplayedName;
};

const getUniqueSortedEnvironmentProperties = (data) => {
  const allEnvironmentProperties = data.flatMap(({ env_properties: envProperties = {} }) => Object.keys(envProperties));
  return [...new Set(allEnvironmentProperties)].sort();
};

const getProductTourIdForDynamicField = (field) => ENVIRONMENT_TOUR_IDS_BY_DYNAMIC_FIELDS[field] || undefined;

const EnvironmentsTable = ({ data, onUpdateActivity, entityId, isLoadingProps = {} }) => {
  const memoizedData = useMemo(() => getTableData(data), [data]);
  const openSideModal = useOpenSideModal();

  const {
    isGetEnvironmentsLoading = false,
    isUpdateEnvironmentLoading = false,
    isGetResourceAllowedActionsLoading = false
  } = isLoadingProps;

  const columns = useMemo(() => {
    const getDeleteAction = ({ id, name }, index) => ({
      key: "delete",
      messageId: "delete",
      icon: <DeleteOutlinedIcon />,
      color: "error",
      requiredActions: ["MANAGE_RESOURCES"],
      dataTestId: `btn_delete_${index}`,
      action: () => openSideModal(DeleteEnvironmentModal, { id, name })
    });

    const getActivityAction = ({ id, isActive }, index) => {
      const { key, messageId, dataTestId, color } = isActive
        ? {
            key: "deactivate",
            messageId: "deactivate",
            dataTestId: "btn_deactivate",
            color: "error"
          }
        : {
            key: "activate",
            messageId: "activate",
            dataTestId: "btn_activate",
            color: "success"
          };
      return {
        key,
        messageId,
        icon: <PowerSettingsNewOutlinedIcon />,
        action: () => {
          onUpdateActivity(id, !isActive);
        },
        isLoading: (isUpdateEnvironmentLoading && id === entityId) || isGetResourceAllowedActionsLoading,
        color,
        requiredActions: ["MANAGE_RESOURCES"],
        dataTestId: `${dataTestId}_${index}`
      };
    };

    const getManuallyCreatedEnvironmentActions = ({ id, name, isActive }, index) => {
      const activityAction = getActivityAction({ id, isActive }, index);
      const deleteAction = getDeleteAction({ id, name }, index);

      return [activityAction, deleteAction];
    };

    // TODO: combine actions in a single array ???
    const getBookingAction = ({
      id,
      resourceName,
      resourceDisplayedName,
      upcomingBookings,
      allBookings,
      index,
      isSshRequired,
      isEnvironmentAvailable
    }) => ({
      key: "book",
      messageId: "book",
      icon: <ScheduleOutlinedIcon />,
      action: () => {
        openSideModal(BookEnvironmentModal, {
          id,
          resourceName,
          resourceDisplayedName,
          upcomingBookings,
          allBookings,
          isSshRequired,
          isEnvironmentAvailable
        });
      },
      dataTestId: `btn_book_${index}`
      // requiredActions: ["BOOK_ENVIRONMENTS"]
    });

    const getReleaseAction = (activeBooking, index) => ({
      key: "release",
      messageId: "release",
      icon: <LockOpenOutlinedIcon />,
      action: () =>
        openSideModal(ReleaseEnvironmentModal, {
          bookingId: activeBooking.id,
          bookedSince: activeBooking.acquired_since
        }),
      dataTestId: `btn_release_${index}`,
      requiredActions: ["MANAGE_RESOURCES", "MANAGE_OWN_RESOURCES"]
    });

    const getDeleteBookingAction = (id, index) => ({
      key: "deleteBooking",
      messageId: "delete",
      icon: <DeleteOutlinedIcon />,
      color: "error",
      action: () => openSideModal(DeleteEnvironmentBookingModal, { bookingId: id }),
      dataTestId: `btn_delete_booking_${index}`,
      requiredActions: ["MANAGE_RESOURCES", "MANAGE_OWN_RESOURCES"]
    });

    const defaultColumns = [
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_environment">
            <FormattedMessage id="environment" />
          </TextWithDataTestId>
        ),
        accessorKey: NAME_COLUMN_ACCESSOR,
        enableHiding: false,
        cell: ({ row: { original, index } }) =>
          renderEnvironmentCell({
            resource: original,
            index
          }),
        defaultSort: "asc"
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_pool">
            <FormattedMessage id="pool" />
          </TextWithDataTestId>
        ),
        accessorKey: "pool_name",
        enableHiding: false,
        cell: ({ row: { original, index } }) => (
          <PoolLabel
            dataTestId={`environment_pool_${index}`}
            id={original.pool_id}
            name={original.pool_name}
            type={original.pool_purpose}
          />
        )
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_status">
            <FormattedMessage id="status" />
          </TextWithDataTestId>
        ),
        id: "currentBookings",
        accessorKey: "shareable_bookings",
        enableHiding: false,
        dataProductTourId: ENVIRONMENTS_TOUR_IDS.STATUS_CELL,
        enableSorting: false,
        cell: ({ cell, row: { original = {}, index: rowIndex } }) => {
          const shareableBookings = cell.getValue() ?? [];

          const { active: isActive, id, name: resourceName, ssh_only: isSshRequired } = original;

          const activeBooking = getActiveBooking(shareableBookings, id);
          const issues = activeBooking?.jira_issue_attachments ?? [];

          const renderCurrentBooking = () => {
            const { acquired_by: { name } = {}, acquired_since: acquiredSince, released_at: releasedAt } = activeBooking;
            return (
              <CurrentBooking employeeName={name} acquiredSince={acquiredSince} releasedAt={releasedAt} jiraIssues={issues} />
            );
          };

          const getTableCellActionsItems = () => {
            const bookingAction = isActive
              ? getBookingAction({
                  id,
                  resourceName,
                  resourceDisplayedName: getResourceDisplayedName(original),
                  upcomingBookings: getUpcomingBookings(shareableBookings, id),
                  index: rowIndex,
                  allBookings: shareableBookings,
                  isSshRequired,
                  isEnvironmentAvailable: !activeBooking
                })
              : null;

            const releaseAction = activeBooking ? getReleaseAction(activeBooking, rowIndex) : null;

            return [bookingAction, releaseAction].filter(Boolean);
          };

          const actionItems = getTableCellActionsItems();

          const getChip = () =>
            activeBooking ? (
              <Chip variant="outlined" uppercase color="warning" label={<FormattedMessage id="inUse" />} />
            ) : (
              <Chip variant="outlined" uppercase color="success" label={<FormattedMessage id="available" />} />
            );

          return (
            <Fragment key={id}>
              {isActive ? (
                <>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Box>{getChip()}</Box>
                    <Box>
                      <TableCellActions entityType={SCOPE_TYPES.RESOURCE} entityId={id} items={actionItems} />
                    </Box>
                  </Box>
                  {activeBooking && renderCurrentBooking()}
                </>
              ) : (
                <Chip variant="outlined" uppercase color="error" label={<FormattedMessage id="unavailable" />} />
              )}
            </Fragment>
          );
        }
      },
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_upcoming_bookings">
            <FormattedMessage id="upcomingBookings" />
          </TextWithDataTestId>
        ),
        id: "upcomingBookings",
        accessorKey: "shareable_bookings",
        enableHiding: false,
        enableSorting: false,
        style: {
          minWidth: "200px"
        },
        cell: ({
          cell,
          row: {
            original: { id }
          }
        }) => {
          const value = cell.getValue() ?? [];

          const upcomingBookings = getUpcomingBookings(value, id);

          if (isEmptyArray(upcomingBookings)) {
            return CELL_EMPTY_VALUE;
          }

          return (
            <Stack spacing={SPACING_1}>
              {upcomingBookings.map((upcomingBooking, index) => {
                const {
                  acquired_by: { name } = {},
                  id: bookingId,
                  acquired_since: acquiredSince,
                  released_at: releasedAt,
                  resource_id: resourceId
                } = upcomingBooking;
                return (
                  <Box key={bookingId} display="flex" justifyContent="flex-start" alignItems="center">
                    <Box mr={SPACING_1}>
                      <UpcomingBooking employeeName={name} acquiredSince={acquiredSince} releasedAt={releasedAt} />
                    </Box>
                    <Box>
                      <TableCellActions
                        entityType={SCOPE_TYPES.RESOURCE}
                        entityId={resourceId}
                        items={[getDeleteBookingAction(bookingId, index)]}
                      />
                    </Box>
                  </Box>
                );
              })}
            </Stack>
          );
        }
      }
    ];

    const envPropertiesColumns = getUniqueSortedEnvironmentProperties(memoizedData).map((field) => ({
      header: <TextWithDataTestId dataTestId={`lbl_environment_property_${field}`}>{field}</TextWithDataTestId>,
      accessorFn: (originalRow) => originalRow.env_properties?.[field],
      id: `env_properties.${field}`,
      columnSelector: {
        accessor: `env_properties.${field}`,
        title: field,
        dataTestId: `btn_toggle_column_${field}`
      },
      dataProductTourId: getProductTourIdForDynamicField(field),
      style: {
        minWidth: 200,
        /**
         * The maximum width is set to prevent the table from becoming too wide when the content is long
         * The value of 550 is selected to match the maximum width based on the environment property name length, which is limited to 64 characters
         */
        maxWidth: 550
      },
      cell: ({ cell }) => (
        <Box overflow="auto">
          <Markdown>{cell.getValue()}</Markdown>
        </Box>
      )
    }));

    return [
      ...defaultColumns,
      ...envPropertiesColumns,
      {
        header: (
          <TextWithDataTestId dataTestId="lbl_actions">
            <FormattedMessage id="actions" />
          </TextWithDataTestId>
        ),
        id: "actions",
        enableSorting: false,
        enableHiding: false,
        cell: ({ row: { original: { active: isActive, id, name, is_environment: isEnvironment } = {}, index } }) => (
          <TableCellActions
            entityType={SCOPE_TYPES.RESOURCE}
            entityId={id}
            items={[...(isEnvironment ? getManuallyCreatedEnvironmentActions({ id, name, isActive }, index) : [])]}
          />
        )
      }
    ];
  }, [isUpdateEnvironmentLoading, entityId, isGetResourceAllowedActionsLoading, onUpdateActivity, memoizedData, openSideModal]);

  return isGetEnvironmentsLoading ? (
    <TableLoader columnsCounter={5} showHeader />
  ) : (
    <Table
      actionBar={{
        show: true,
        definition: {
          items: [
            {
              key: "add",
              icon: <AddOutlinedIcon fontSize="small" />,
              messageId: "add",
              color: "success",
              variant: "contained",
              type: "button",
              link: ENVIRONMENT_CREATE,
              dataTestId: "btn_add",
              dataProductTourId: ENVIRONMENTS_TOUR_IDS.ADD_BUTTON,
              requiredActions: ["MANAGE_RESOURCES"],
              isLoading: isGetResourceAllowedActionsLoading
            }
          ]
        }
      }}
      data={memoizedData}
      columns={columns}
      withSearch
      pageSize={50}
      columnsSelectorUID={ENVIRONMENTS_TABLE}
      dataTestIds={{
        searchInput: "input_search",
        searchButton: "btn_search",
        deleteSearchButton: "btn_delete_search"
      }}
      localization={{ emptyMessageId: "noEnvironments" }}
    />
  );
};

export default EnvironmentsTable;
