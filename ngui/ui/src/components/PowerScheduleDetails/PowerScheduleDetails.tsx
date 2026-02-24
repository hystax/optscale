import { useState } from "react";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import PlayCircleOutlineOutlinedIcon from "@mui/icons-material/PlayCircleOutlineOutlined";
import PowerSettingsNewOutlinedIcon from "@mui/icons-material/PowerSettingsNewOutlined";
import StopCircleOutlinedIcon from "@mui/icons-material/StopCircleOutlined";
import { Link, Stack } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import ActionBar from "components/ActionBar";
import IconLabel from "components/IconLabel";
import PageContentWrapper from "components/PageContentWrapper";
import PowerScheduleInstances from "components/PowerScheduleInstances";
import PowerScheduleSummaryCards from "components/PowerScheduleSummaryCards";
import PowerScheduleTriggersChart from "components/PowerScheduleTriggersChart";
import PowerScheduleTriggersTable from "components/PowerScheduleTriggersTable/PowerScheduleTriggersTable";
import { DeletePowerScheduleModal } from "components/SideModalManager/SideModals";
import TabsWrapper from "components/TabsWrapper";
import Tooltip from "components/Tooltip";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useOrganizationActionRestrictions } from "hooks/useOrganizationActionRestrictions";
import { PowerScheduleResponse } from "services/PowerScheduleService";
import { POWER_SCHEDULES, getEditPowerScheduleUrl } from "urls";
import { SPACING_4 } from "utils/layouts";

type PowerScheduleDetailsProps = {
  powerSchedule: PowerScheduleResponse;
  onActivate: () => void;
  onDeactivate: () => void;
  isLoadingProps?: {
    isGetPowerScheduleLoading?: boolean;
    isUpdatePowerScheduleLoading?: boolean;
  };
};

const TABS = Object.freeze({
  INSTANCES: "instances",
  TRIGGERS: "triggers",
});

const PowerScheduleDetails = ({ powerSchedule, onActivate, onDeactivate, isLoadingProps = {} }: PowerScheduleDetailsProps) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  const navigate = useNavigate();

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
    resources: instances = [],
    triggers = [],
    timezone: timeZone,
  } = powerSchedule;

  const actionBarDefinition = {
    breadcrumbs: [
      <Link key={1} to={POWER_SCHEDULES} component={RouterLink}>
        <FormattedMessage id="powerSchedulesTitle" />
      </Link>,
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
      isLoading: isGetPowerScheduleLoading,
    },
    items: [
      {
        key: "edit",
        icon: <EditOutlinedIcon fontSize="small" />,
        messageId: "edit",
        type: "button",
        dataTestId: "btn_edit_power_schedule",
        isLoading: isGetPowerScheduleLoading,
        action: () => navigate(getEditPowerScheduleUrl(id)),
        requiredActions: ["EDIT_PARTNER"],
      },
      enabled
        ? {
            key: "deactivate",
            messageId: "deactivate",
            icon: <PowerSettingsNewOutlinedIcon />,
            dataTestId: `btn_deactivate`,
            type: "button",
            action: onDeactivate,
            isLoading: isGetPowerScheduleLoading || isUpdatePowerScheduleLoading,
            requiredActions: ["EDIT_PARTNER"],
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
            dataTestId: `btn_activate`,
            type: "button",
            action: onActivate,
            isLoading: isGetPowerScheduleLoading || isUpdatePowerScheduleLoading,
            requiredActions: ["EDIT_PARTNER"],
            disabled: isRestricted,
            tooltip: {
              show: isRestricted,
              value: restrictionReasonMessage,
            },
          },
      {
        key: "delete",
        icon: <DeleteOutlinedIcon fontSize="small" />,
        messageId: "delete",
        type: "button",
        dataTestId: "btn_delete_power_schedule",
        isLoading: isGetPowerScheduleLoading,
        action: () => openSideModal(DeletePowerScheduleModal, { id, name }),
        requiredActions: ["EDIT_PARTNER"],
      },
    ],
  };

  const tabs = [
    {
      title: TABS.INSTANCES,
      dataTestId: "tab_instances",
      node: <PowerScheduleInstances instances={instances} />,
    },
    {
      title: TABS.TRIGGERS,
      dataTestId: "tab_triggers",
      node: <PowerScheduleTriggersTable triggers={triggers} />,
    },
  ];

  const [activeTab, setActiveTab] = useState();

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Stack spacing={SPACING_4}>
          <div>
            <PowerScheduleSummaryCards
              timeZone={timeZone}
              startDate={startDate}
              endDate={endDate}
              lastRun={lastRun}
              lastRunError={lastRunError}
              resourcesOnSchedule={resourcesOnSchedule}
              isLoading={isGetPowerScheduleLoading}
            />
          </div>
          <div>
            <PowerScheduleTriggersChart triggers={triggers} isLoading={isGetPowerScheduleLoading} />
          </div>
          <div>
            <TabsWrapper
              tabsProps={{
                tabs,
                defaultTab: TABS.INSTANCES,
                name: "power-schedule-details-tabs",
                isLoading: isGetPowerScheduleLoading,
                activeTab,
                handleChange: (event, value) => {
                  setActiveTab(value);
                },
              }}
            />
          </div>
        </Stack>
      </PageContentWrapper>
    </>
  );
};

export default PowerScheduleDetails;
