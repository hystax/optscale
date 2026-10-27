import { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import PowerSettingsNewOutlinedIcon from "@mui/icons-material/PowerSettingsNewOutlined";
import { Box, Typography } from "@mui/material";
import { FormattedMessage, useIntl } from "react-intl";
import { useNavigate } from "react-router-dom";
import ActionBar from "components/ActionBar";
import ExpandableList from "components/ExpandableList";
import HeaderHelperCell from "components/HeaderHelperCell";
import IconLabel from "components/IconLabel";
import PageContentWrapper from "components/PageContentWrapper";
import { DeletePowerScheduleModal } from "components/SideModalManager/SideModals";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";
import { type PowerScheduleResponse } from "services/PowerScheduleService";
import { CREATE_POWER_SCHEDULE } from "urls";
import { isEmptyArray } from "utils/arrays";
import { powerScheduleLastRun, powerScheduleName, powerScheduleValidityPeriod, text } from "utils/columns";
import { POWER_SCHEDULE_ACTIONS } from "utils/constants";
import { EN_TIME_FORMAT, EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM, formatTimeString, parse } from "utils/datetime";
import { CELL_EMPTY_VALUE } from "utils/tables";

type PowerSchedulesProps = {
  powerSchedules: PowerScheduleResponse[];
  onActivate: (id: string) => void;
  onDeactivate: (id: string) => void;
  updatingEntityId: string;
  isLoadingProps?: {
    isGetPowerSchedulesLoading?: boolean;
    isUpdatePowerScheduleLoading?: boolean;
  };
};

const PowerSchedules = ({
  powerSchedules,
  onActivate,
  onDeactivate,
  updatingEntityId,
  isLoadingProps = {},
}: PowerSchedulesProps) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  const openSideModal = useOpenSideModal();
  const navigate = useNavigate();
  const intl = useIntl();

  const isManagePowerScheduleAllowed = useIsAllowed({
    requiredActions: ["EDIT_PARTNER"],
  });

  const { isGetPowerSchedulesLoading, isUpdatePowerScheduleLoading } = isLoadingProps;

  const actionBarDefinition = {
    title: {
      messageId: "powerSchedulesTitle",
    },
  };

  const tableData = useMemo(() => powerSchedules, [powerSchedules]);

  const columns = useMemo(() => {
    const getActionsColumn = () => ({
      header: (
        <TextWithDataTestId dataTestId="lbl_actions">
          <FormattedMessage id="actions" />
        </TextWithDataTestId>
      ),
      id: "actions",
      cell: ({
        row: {
          original: { id, name, enabled },
          index,
        },
      }) => (
        <TableCellActions
          items={[
            enabled
              ? {
                  key: "deactivate",
                  messageId: "deactivate",
                  icon: <PowerSettingsNewOutlinedIcon />,
                  color: "error",
                  dataTestId: `btn_deactivate_${index}`,
                  isLoading: updatingEntityId === id && isUpdatePowerScheduleLoading,
                  action: () => onDeactivate(id),
                  disabled: isRestricted,
                  tooltip: {
                    show: isRestricted,
                    value: restrictionReasonMessage,
                  },
                }
              : {
                  key: "activate",
                  messageId: "activate",
                  icon: <PowerSettingsNewOutlinedIcon />,
                  color: "success",
                  dataTestId: `btn_activate_${index}`,
                  isLoading: updatingEntityId === id && isUpdatePowerScheduleLoading,
                  action: () => onActivate(id),
                  disabled: isRestricted,
                  tooltip: {
                    show: isRestricted,
                    value: restrictionReasonMessage,
                  },
                },
            {
              key: "deletePowerSchedule",
              messageId: "delete",
              icon: <DeleteOutlinedIcon />,
              color: "error",
              dataTestId: `btn_delete_power_schedule${index}`,
              action: () => {
                openSideModal(DeletePowerScheduleModal, { id, name });
              },
            },
          ]}
        />
      ),
    });

    return [
      powerScheduleName({
        accessorKey: "name",
        headerDataTestId: "lbl_name",
        headerMessageId: "name",
        cellDataAccessors: {
          enabled: "enabled",
          id: "id",
        },
      }),
      powerScheduleLastRun({
        accessorKey: "last_run",
        headerDataTestId: "lbl_last_execution_time",
        headerMessageId: "lastExecution",
        cellDataAccessors: {
          lastRunError: "last_run_error",
        },
      }),
      text({
        headerMessageId: "resourcesOnSchedule",
        headerDataTestId: "lbl_number_of_resources_on_schedule",
        accessorKey: "resources_count",
      }),
      {
        header: (
          <HeaderHelperCell
            titleMessageId="triggers"
            helperMessageId="triggersDescription"
            helperMessageValues={{ br: <br /> }}
          />
        ),
        id: "triggers",
        enableSorting: false,
        accessorFn: (originalRow) =>
          originalRow.triggers
            .map((trigger) => {
              const formattedTime = formatTimeString({
                timeString: trigger.time,
                timeStringFormat: EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM,
                parsedTimeStringFormat: EN_TIME_FORMAT,
              });

              const action =
                trigger.action === POWER_SCHEDULE_ACTIONS.POWER_ON
                  ? intl.formatMessage({ id: "on" })
                  : intl.formatMessage({ id: "off" });

              return `${formattedTime}: ${action}`;
            })
            .join(" "),
        cell: ({ row: { original } }) => {
          const { triggers } = original;

          return isEmptyArray(triggers) ? (
            CELL_EMPTY_VALUE
          ) : (
            <ExpandableList
              items={triggers.toSorted((triggerA, triggerB) => {
                const timeA = parse(triggerA.time, EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM, new Date());
                const timeB = parse(triggerB.time, EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM, new Date());

                return timeA.getTime() - timeB.getTime();
              })}
              render={({ time, action }) => {
                const formattedTime = formatTimeString({
                  timeString: time,
                  timeStringFormat: EN_TIME_FORMAT_24_HOURS_CLOCK_HH_MM,
                  parsedTimeStringFormat: EN_TIME_FORMAT,
                });

                const isOn = action === POWER_SCHEDULE_ACTIONS.POWER_ON;

                return (
                  <Box display="flex" alignItems="center" key={formattedTime}>
                    <Typography>
                      {formattedTime}
                      :&nbsp;{" "}
                    </Typography>
                    <IconLabel
                      icon={<PowerSettingsNewOutlinedIcon fontSize="small" color={isOn ? "success" : "error"} />}
                      label={
                        <Typography variant="body2" fontWeight="bold">
                          <FormattedMessage id={isOn ? "on" : "off"} />
                        </Typography>
                      }
                    />
                  </Box>
                );
              }}
              maxRows={5}
            />
          );
        },
      },
      text({
        headerMessageId: "timeZone",
        headerDataTestId: "lbl_time_zone",
        accessorKey: "timezone",
      }),
      powerScheduleValidityPeriod({
        startDateAccessor: "start_date",
        endDateAccessor: "end_date",
      }),
      ...(isManagePowerScheduleAllowed ? [getActionsColumn()] : []),
    ];
  }, [
    intl,
    isManagePowerScheduleAllowed,
    isRestricted,
    isUpdatePowerScheduleLoading,
    onActivate,
    onDeactivate,
    openSideModal,
    restrictionReasonMessage,
    updatingEntityId,
  ]);

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        {isGetPowerSchedulesLoading ? (
          <TableLoader />
        ) : (
          <Table
            withSearch
            data={tableData}
            columns={columns}
            actionBar={{
              show: true,
              definition: {
                items: [
                  {
                    key: "btn-add",
                    dataTestId: "btn_add",
                    icon: <AddOutlinedIcon fontSize="small" />,
                    messageId: "add",
                    color: "success",
                    variant: "contained",
                    type: "button",
                    requiredActions: ["EDIT_PARTNER"],
                    action: () => navigate(CREATE_POWER_SCHEDULE),
                  },
                ],
              },
            }}
            pageSize={50}
          />
        )}
      </PageContentWrapper>
    </>
  );
};

export default PowerSchedules;
