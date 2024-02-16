import { useMemo } from "react";
import AddOutlinedIcon from "@mui/icons-material/AddOutlined";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import PowerSettingsNewOutlinedIcon from "@mui/icons-material/PowerSettingsNewOutlined";
import { FormattedMessage } from "react-intl";
import { useNavigate } from "react-router-dom";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import { DeletePowerScheduleModal } from "components/SideModalManager/SideModals";
import Table from "components/Table";
import TableCellActions from "components/TableCellActions";
import TableLoader from "components/TableLoader";
import TextWithDataTestId from "components/TextWithDataTestId";
import { useIsAllowed } from "hooks/useAllowedActions";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { type PowerScheduleResponse } from "services/PowerScheduleService";
import { CREATE_POWER_SCHEDULE } from "urls";
import { formattedTime, powerScheduleLastRun, powerScheduleName, powerScheduleValidityPeriod, text } from "utils/columns";

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
  isLoadingProps = {}
}: PowerSchedulesProps) => {
  const openSideModal = useOpenSideModal();
  const navigate = useNavigate();

  const isManagePowerScheduleAllowed = useIsAllowed({
    requiredActions: ["EDIT_PARTNER"]
  });

  const { isGetPowerSchedulesLoading, isUpdatePowerScheduleLoading } = isLoadingProps;

  const actionBarDefinition = {
    title: {
      messageId: "powerSchedulesTitle"
    },
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
        action: () => navigate(CREATE_POWER_SCHEDULE)
      }
    ]
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
          index
        }
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
                  action: () => onDeactivate(id)
                }
              : {
                  key: "activate",
                  messageId: "activate",
                  icon: <PowerSettingsNewOutlinedIcon />,
                  color: "success",
                  dataTestId: `btn_activate_${index}`,
                  isLoading: updatingEntityId === id && isUpdatePowerScheduleLoading,
                  action: () => onActivate(id)
                },
            {
              key: "deletePowerSchedule",
              messageId: "delete",
              icon: <DeleteOutlinedIcon />,
              color: "error",
              dataTestId: `btn_delete_power_schedule${index}`,
              action: () => {
                openSideModal(DeletePowerScheduleModal, { id, name });
              }
            }
          ]}
        />
      )
    });

    return [
      powerScheduleName({
        accessorKey: "name",
        headerDataTestId: "lbl_name",
        headerMessageId: "name",
        cellDataAccessors: {
          enabled: "enabled",
          id: "id"
        }
      }),
      powerScheduleLastRun({
        accessorKey: "last_run",
        headerDataTestId: "lbl_last_execution_time",
        headerMessageId: "lastExecution",
        cellDataAccessors: {
          lastRunError: "last_run_error"
        }
      }),
      text({
        headerMessageId: "resourcesOnSchedule",
        headerDataTestId: "lbl_number_of_resources_on_schedule",
        accessorKey: "resources_count"
      }),
      formattedTime({
        accessorKey: "power_on",
        headerMessageId: "instancePowerOn",
        headerDataTestId: "lbl_power_on",
        timeStringFormat: "HH:mm",
        parsedTimeStringFormat: "hh:mm a"
      }),
      formattedTime({
        accessorKey: "power_off",
        headerMessageId: "instancePowerOff",
        headerDataTestId: "lbl_power_off",
        timeStringFormat: "HH:mm",
        parsedTimeStringFormat: "hh:mm a"
      }),
      text({
        headerMessageId: "timeZone",
        headerDataTestId: "lbl_time_zone",
        accessorKey: "timezone"
      }),
      powerScheduleValidityPeriod({
        startDateAccessor: "start_date",
        endDateAccessor: "end_date"
      }),
      ...(isManagePowerScheduleAllowed ? [getActionsColumn()] : [])
    ];
  }, [isManagePowerScheduleAllowed, isUpdatePowerScheduleLoading, onActivate, onDeactivate, openSideModal, updatingEntityId]);

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        {isGetPowerSchedulesLoading ? <TableLoader /> : <Table withSearch data={tableData} columns={columns} pageSize={50} />}
      </PageContentWrapper>
    </>
  );
};

export default PowerSchedules;
