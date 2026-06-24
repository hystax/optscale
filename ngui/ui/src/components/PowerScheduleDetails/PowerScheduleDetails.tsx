import { useState } from "react";
import DeleteOutlinedIcon from "@mui/icons-material/DeleteOutlined";
import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import FlashOnOutlinedIcon from "@mui/icons-material/FlashOnOutlined";
import PlayCircleOutlineOutlinedIcon from "@mui/icons-material/PlayCircleOutlineOutlined";
import PowerSettingsNewOutlinedIcon from "@mui/icons-material/PowerSettingsNewOutlined";
import RefreshOutlinedIcon from "@mui/icons-material/RefreshOutlined";
import StopCircleOutlinedIcon from "@mui/icons-material/StopCircleOutlined";
import { Link, Stack } from "@mui/material";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogTitle from "@mui/material/DialogTitle";
import FormControlLabel from "@mui/material/FormControlLabel";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Typography from "@mui/material/Typography";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import ActionBar from "components/ActionBar";
import Button from "components/Button";
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
  onRefresh?: () => void;
  onRunNow?: (action: "power_on" | "power_off") => void;
  isLoadingProps?: {
    isGetPowerScheduleLoading?: boolean;
    isUpdatePowerScheduleLoading?: boolean;
    isRunNowLoading?: boolean;
  };
};

const TABS = Object.freeze({
  INSTANCES: "instances",
  TRIGGERS: "triggers",
});

const PowerScheduleDetails = ({
  powerSchedule,
  onActivate,
  onDeactivate,
  onRefresh,
  onRunNow,
  isLoadingProps = {},
}: PowerScheduleDetailsProps) => {
  const { isRestricted, restrictionReasonMessage } = useOrganizationActionRestrictions();

  const navigate = useNavigate();

  const { isGetPowerScheduleLoading = false, isUpdatePowerScheduleLoading = false, isRunNowLoading = false } = isLoadingProps;

  const [runDialogOpen, setRunDialogOpen] = useState(false);
  const [pendingAction, setPendingAction] = useState<"power_on" | "power_off">("power_on");

  const openSideModal = useOpenSideModal();

  const {
    id,
    name,
    enabled,
    start_date: startDate,
    end_date: endDate,
    last_run: lastRun,
    last_run_error: lastRunError,
    last_run_details: lastRunDetails,
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
        key: "runNow",
        icon: <FlashOnOutlinedIcon fontSize="small" />,
        messageId: "runNow",
        type: "button",
        dataTestId: "btn_run_now",
        isLoading: isGetPowerScheduleLoading || isRunNowLoading,
        action: () => setRunDialogOpen(true),
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
      {
        key: "refresh",
        icon: <RefreshOutlinedIcon fontSize="small" />,
        messageId: "refreshResources",
        type: "button",
        dataTestId: "btn_refresh_resources",
        isLoading: isGetPowerScheduleLoading,
        action: onRefresh ?? (() => {}),
      },
    ],
  };

  const tabs = [
    {
      title: TABS.INSTANCES,
      dataTestId: "tab_instances",
      node: <PowerScheduleInstances instances={instances} powerSchedule={powerSchedule} />,
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
      <Dialog open={runDialogOpen} onClose={() => setRunDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle>
          <FormattedMessage id="runNow" />
        </DialogTitle>
        <DialogContent>
          <RadioGroup value={pendingAction} onChange={(e) => setPendingAction(e.target.value as "power_on" | "power_off")}>
            <FormControlLabel value="power_on" control={<Radio />} label={<FormattedMessage id="powerOn" />} />
            <FormControlLabel value="power_off" control={<Radio />} label={<FormattedMessage id="powerOff" />} />
          </RadioGroup>
        </DialogContent>
        <DialogActions>
          <Button messageId="cancel" onClick={() => setRunDialogOpen(false)} />
          <Button
            messageId="run"
            variant="contained"
            color="primary"
            onClick={() => {
              setRunDialogOpen(false);
              onRunNow?.(pendingAction);
            }}
          />
        </DialogActions>
      </Dialog>
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
          {!isGetPowerScheduleLoading && lastRunDetails && lastRunDetails.length > 0 && (
            <div>
              <Typography variant="subtitle1" gutterBottom>
                <FormattedMessage id="lastRunDetails" />
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>
                        <FormattedMessage id="cloudResourceId" />
                      </TableCell>
                      <TableCell>
                        <FormattedMessage id="resourceType" />
                      </TableCell>
                      <TableCell>
                        <FormattedMessage id="action" />
                      </TableCell>
                      <TableCell>
                        <FormattedMessage id="error" />
                      </TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {lastRunDetails.map((detail, index) => (
                      // eslint-disable-next-line react/no-array-index-key
                      <TableRow key={index}>
                        <TableCell>{detail.cloud_resource_id}</TableCell>
                        <TableCell>{detail.resource_type}</TableCell>
                        <TableCell>{detail.action}</TableCell>
                        <TableCell sx={{ wordBreak: "break-word", maxWidth: 400 }}>{detail.error}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </div>
          )}
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
