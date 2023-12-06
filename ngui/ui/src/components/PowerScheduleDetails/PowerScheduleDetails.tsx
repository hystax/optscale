import { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import ErrorOutlineOutlinedIcon from "@mui/icons-material/ErrorOutlineOutlined";
import PlayCircleOutlineOutlinedIcon from "@mui/icons-material/PlayCircleOutlineOutlined";
import PowerSettingsNewOutlinedIcon from "@mui/icons-material/PowerSettingsNewOutlined";
import StopCircleOutlinedIcon from "@mui/icons-material/StopCircleOutlined";
import { Box, Link, Stack } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink, useParams } from "react-router-dom";
import ActionBar from "components/ActionBar";
import IconLabel from "components/IconLabel";
import IntervalTimeAgo from "components/IntervalTimeAgo";
import PageContentWrapper from "components/PageContentWrapper";
import PowerScheduleValidityPeriod from "components/PowerScheduleValidityPeriod";
import QuestionMark from "components/QuestionMark";
import {
  AddInstanceToScheduleModal,
  DeletePowerScheduleModal,
  RemoveInstancesFromScheduleModal
} from "components/SideModalManager/SideModals";
import SubTitle from "components/SubTitle";
import SummaryGrid from "components/SummaryGrid";
import Table from "components/Table";
import TableLoader from "components/TableLoader";
import Tooltip from "components/Tooltip";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { POWER_SCHEDULES } from "urls";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { powerScheduleInstance, resourceLocation, resourcePoolOwner, size, tags } from "utils/columns";
import { SUMMARY_VALUE_COMPONENT_TYPES } from "utils/constants";
import { formatTimeString } from "utils/datetime";
import { SPACING_4 } from "utils/layouts";

const Details = ({
  timeZone,
  startDate,
  endDate,
  lastRun,
  lastRunError,
  resourcesOnSchedule,
  powerOn,
  powerOff,
  isLoading
}) => (
  <SummaryGrid
    summaryData={[
      {
        key: "lastExecution",
        valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
        CustomValueComponent: () => {
          if (lastRun === 0) {
            return <FormattedMessage id="never" />;
          }

          if (lastRunError) {
            return (
              <Box display="flex" alignItems="center">
                <IntervalTimeAgo secondsTimestamp={lastRun} precision={1} />
                <QuestionMark color="error" tooltipText={lastRunError} Icon={ErrorOutlineOutlinedIcon} />
              </Box>
            );
          }

          return <IntervalTimeAgo secondsTimestamp={lastRun} precision={1} />;
        },
        captionMessageId: "lastExecution",
        color: lastRunError ? "error" : "primary",
        dataTestIds: {
          cardTestId: "card_last_execution_time"
        },
        isLoading,
        renderCondition: () => lastRun !== undefined || lastRunError !== undefined
      },
      {
        key: "resourcesOnSchedule",
        valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
        CustomValueComponent: () => resourcesOnSchedule,
        captionMessageId: "resourcesOnSchedule",
        dataTestIds: {
          cardTestId: "card_resources_on_schedule"
        },
        isLoading
      },
      {
        key: "instancePowerOn",
        valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
        CustomValueComponent: () =>
          formatTimeString({
            timeString: powerOn,
            timeStringFormat: "HH:mm",
            parsedTimeStringFormat: "hh:mm a"
          }),
        captionMessageId: "instancePowerOn",
        dataTestIds: {
          cardTestId: "card_instance_power_on"
        },
        isLoading,
        renderCondition: () => !!powerOn
      },
      {
        key: "instancePowerOff",
        valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
        CustomValueComponent: () =>
          formatTimeString({
            timeString: powerOff,
            timeStringFormat: "HH:mm",
            parsedTimeStringFormat: "hh:mm a"
          }),
        captionMessageId: "instancePowerOff",
        dataTestIds: {
          cardTestId: "card_instance_power_off"
        },
        isLoading,
        renderCondition: () => !!powerOff
      },
      {
        key: "timeZone",
        valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
        CustomValueComponent: () => timeZone,
        captionMessageId: "timeZone",
        dataTestIds: {
          cardTestId: "card_time_zone"
        },
        isLoading
      },
      {
        key: "validityPeriod",
        valueComponentType: SUMMARY_VALUE_COMPONENT_TYPES.Custom,
        CustomValueComponent: () => <PowerScheduleValidityPeriod startDate={startDate} endDate={endDate} />,
        captionMessageId: "validityPeriod",
        dataTestIds: {
          cardTestId: "card_time_zone"
        },
        isLoading,
        renderCondition: () => !!startDate || !!endDate
      }
    ]}
  />
);

const ResourcesOnSchedule = ({ resources, isLoading = false }) => {
  const { powerScheduleId } = useParams();

  const openSideModal = useOpenSideModal();

  const tableData = useMemo(
    () =>
      resources.map((resource) => ({
        id: resource.id,
        cloud_resource_id: resource.cloud_resource_id,
        name: resource.name,
        owner_name: resource.details?.owner_name,
        pool_id: resource.pool_id,
        pool_name: resource.details?.pool_name,
        pool_purpose: resource.details?.pool_purpose,
        region: resource.details?.region,
        cloud_account_id: resource.cloud_account_id,
        cloud_account_name: resource.details?.cloud_name,
        cloud_type: resource.details?.cloud_type,
        size: resource.meta?.flavor,
        tags: resource.tags
      })),
    [resources]
  );

  const columns = useMemo(
    () => [
      powerScheduleInstance({
        idAccessor: "id",
        nameAccessor: "name",
        headerDataTestId: "lbl_instance",
        titleMessageId: "instance"
      }),
      resourcePoolOwner({
        id: "pool/owner",
        accessorFn: (rowOriginal) => {
          const { owner_name: ownerName } = rowOriginal;
          const { pool_name: poolName } = rowOriginal;

          return [poolName, ownerName].filter((str) => str !== "").join(" ");
        },
        getOwner: (rowOriginal) => {
          const { owner_name: ownerName } = rowOriginal;

          return {
            name: ownerName
          };
        },
        getPool: (rowOriginal) => {
          const { pool_id: poolId, pool_name: poolName, pool_purpose: poolPurpose } = rowOriginal;

          return poolId
            ? {
                id: poolId,
                name: poolName,
                purpose: poolPurpose
              }
            : undefined;
        }
      }),
      resourceLocation({
        idAccessor: "cloud_account_id",
        typeAccessor: "cloud_type",
        locationAccessors: {
          region: "region"
        },
        accessorKey: "cloud_account_name",
        headerDataTestId: "lbl_location"
      }),
      size({
        id: "size",
        accessorKey: "size",
        headerDataTestId: "lbl_size"
      }),
      tags({
        id: "tags",
        accessorFn: (originalRow) =>
          Object.entries(originalRow.tags ?? {})
            .map(([key, val]) => `${key}: ${val}`)
            .join(" "),
        getTags: (rowOriginal) => rowOriginal.tags ?? {}
      })
    ],
    []
  );

  const actionBar = {
    show: true,
    definition: {
      items: [
        {
          key: "addInstancesToSchedule",
          icon: <AddOutlinedIcon fontSize="small" />,
          messageId: "addInstancesToSchedule",
          variant: "text",
          type: "button",
          dataTestId: "btn_add_instances_to_schedule",
          requiredActions: ["EDIT_PARTNER"],
          action: () => openSideModal(AddInstanceToScheduleModal, { powerScheduleId })
        },
        (tableContext) => {
          const { rows: selectedRows } = tableContext.getFilteredSelectedRowModel();

          return {
            key: "removeInstancesFromSchedule",
            icon: <DeleteOutlinedIcon fontSize="small" />,
            messageId: "removeInstancesFromSchedule",
            type: "button",
            dataTestId: "btn_delete_instances_from_schedule",
            disabled: isEmptyArray(selectedRows),
            requiredActions: ["EDIT_PARTNER"],
            action: () =>
              openSideModal(RemoveInstancesFromScheduleModal, {
                powerScheduleId,
                selectedInstances: selectedRows.map(({ original }) => original)
              })
          };
        }
      ]
    }
  };

  return (
    <>
      <SubTitle>
        <FormattedMessage id="resourcesOnSchedule" />
      </SubTitle>
      {isLoading ? (
        <TableLoader />
      ) : (
        <Table
          withSelection
          withSearch
          pageSize={50}
          data={tableData}
          columns={columns}
          actionBar={actionBar}
          localization={{
            emptyMessageId: "noInstances"
          }}
        />
      )}
    </>
  );
};

const PowerScheduleDetails = ({ powerSchedule, onActivate, onDeactivate, isLoadingProps = {} }) => {
  const { isGetPowerScheduleLoading = false, isUpdatePowerScheduleLoading = false } = isLoadingProps;

  const openSideModal = useOpenSideModal();

  const {
    id,
    name,
    enabled,
    start_date: startDate,
    end_date: endDate,
    last_run: lastRun,
    last_run_error: lastRunError,
    resources_count: resourcesOnSchedule,
    resources = [],
    power_on: powerOn,
    power_off: powerOff,
    timezone: timeZone
  } = powerSchedule;

  const actionBarDefinition = {
    breadcrumbs: [
      <Link key={1} to={POWER_SCHEDULES} component={RouterLink}>
        <FormattedMessage id="powerSchedulesTitle" />
      </Link>
    ],
    title: {
      text: name ? (
        <IconLabel
          icon={
            <Tooltip title={<FormattedMessage id={enabled ? "active" : "inactive"} />}>
              {enabled ? (
                <PlayCircleOutlineOutlinedIcon fontSize="small" color="success" />
              ) : (
                <StopCircleOutlinedIcon fontSize="small" color="error" />
              )}
            </Tooltip>
          }
          label={name}
        />
      ) : (
        "-"
      ),
      dataTestId: "lbl_power_schedule_details",
      isLoading: isGetPowerScheduleLoading
    },
    items: [
      enabled
        ? {
            key: "deactivate",
            messageId: "deactivate",
            icon: <PowerSettingsNewOutlinedIcon />,
            dataTestId: `btn_deactivate`,
            type: "button",
            action: onActivate,
            isLoading: isGetPowerScheduleLoading || isUpdatePowerScheduleLoading
          }
        : {
            key: "activate",
            messageId: "activate",
            icon: <PowerSettingsNewOutlinedIcon />,
            dataTestId: `btn_activate`,
            type: "button",
            action: onDeactivate,
            isLoading: isGetPowerScheduleLoading || isUpdatePowerScheduleLoading
          },
      {
        key: "delete",
        icon: <DeleteOutlinedIcon fontSize="small" />,
        messageId: "delete",
        type: "button",
        dataTestId: "btn_delete_power_schedule",
        isLoading: isGetPowerScheduleLoading,
        action: () => openSideModal(DeletePowerScheduleModal, { id, name })
      }
    ]
  };

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Stack spacing={SPACING_4}>
          <div>
            <Details
              timeZone={timeZone}
              startDate={startDate}
              endDate={endDate}
              lastRun={lastRun}
              lastRunError={lastRunError}
              resourcesOnSchedule={resourcesOnSchedule}
              powerOn={powerOn}
              powerOff={powerOff}
              isLoading={isGetPowerScheduleLoading}
            />
          </div>
          <div>
            <ResourcesOnSchedule resources={resources} isLoading={isGetPowerScheduleLoading} />
          </div>
        </Stack>
      </PageContentWrapper>
    </>
  );
};

export default PowerScheduleDetails;
