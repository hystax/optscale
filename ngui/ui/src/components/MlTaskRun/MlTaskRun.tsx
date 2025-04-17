import { Fragment } from "react";
import RefreshOutlinedIcon from "@mui/icons-material/RefreshOutlined";
import ShareOutlinedIcon from "@mui/icons-material/ShareOutlined";
import { Link, Stack, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import { GET_ML_ARTIFACTS, GET_ML_EXECUTORS, GET_ML_RUN_DETAILS, GET_ML_RUN_DETAILS_BREAKDOWN } from "api/restapi/actionTypes";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import { ShareRunLinkModal } from "components/SideModalManager/SideModals";
import RunArtifactsContainer from "containers/RunArtifactsContainer";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import { useRefetchApis } from "hooks/useRefetchApis";
import { ML_TASKS, getMlTaskDetailsUrl } from "urls";
import { SPACING_2 } from "utils/layouts";
import { formatRunFullName } from "utils/ml";
import { Charts, Executors, Overview, Status, Tabs } from "./Components";

const MlTaskRun = ({
  run,
  organizationId,
  arceeToken,
  isFinOpsEnabled = false,
  isPublicRun = false,
  isLoading = false,
  isDataReady = false
}) => {
  const { task: { id: taskId, name: taskName } = {}, name: runName, number } = run;

  const refetch = useRefetchApis();

  const openSideModal = useOpenSideModal();

  const actionBarDefinition = {
    breadcrumbs: [
      <Fragment key={1}>
        {isPublicRun ? (
          <span>
            <FormattedMessage id="tasks" />
          </span>
        ) : (
          <Link to={ML_TASKS} component={RouterLink}>
            <FormattedMessage id="tasks" />
          </Link>
        )}
      </Fragment>,
      <Fragment key={2}>
        {isPublicRun ? (
          <span>{taskName}</span>
        ) : (
          <Link to={getMlTaskDetailsUrl(taskId)} component={RouterLink}>
            {taskName}
          </Link>
        )}
      </Fragment>,
      <FormattedMessage key={3} id="runs" />
    ],
    title: {
      isLoading,
      text: <Typography>{formatRunFullName(number, runName)}</Typography>
    },
    items: [
      {
        key: "btn-refresh",
        icon: <RefreshOutlinedIcon fontSize="small" />,
        messageId: "refresh",
        dataTestId: "btn_refresh",
        type: "button",
        action: () => refetch([GET_ML_RUN_DETAILS, GET_ML_EXECUTORS, GET_ML_RUN_DETAILS_BREAKDOWN, GET_ML_ARTIFACTS])
      },
      ...(isPublicRun
        ? []
        : [
            {
              key: "btn-share",
              icon: <ShareOutlinedIcon fontSize="small" />,
              messageId: "share",
              dataTestId: "btn_share",
              type: "button",
              isLoading,
              action: () => {
                openSideModal(ShareRunLinkModal, {
                  runId: run.id
                });
              }
            }
          ])
    ]
  };

  const overviewTab = <Overview run={run} isLoading={isLoading} />;

  const chartsTab = (
    <Charts
      run={run}
      organizationId={organizationId}
      arceeToken={arceeToken}
      isPublicRun={isPublicRun}
      isTaskRunLoading={isLoading}
      isTaskRunDataReady={isDataReady}
    />
  );

  const artifactsTab = <RunArtifactsContainer organizationId={organizationId} arceeToken={arceeToken} />;

  const executorsTab = (
    <Executors
      arceeToken={arceeToken}
      organizationId={organizationId}
      withExpenses={isFinOpsEnabled}
      isPublicRun={isPublicRun}
    />
  );

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Stack spacing={SPACING_2}>
          <div>
            <Status
              status={run.status}
              duration={run.duration}
              cost={run.cost}
              withCost={isFinOpsEnabled}
              isLoading={isLoading}
            />
          </div>
          <div>
            <Tabs overviewTab={overviewTab} chartsTab={chartsTab} artifactsTab={artifactsTab} executorsTab={executorsTab} />
          </div>
        </Stack>
      </PageContentWrapper>
    </>
  );
};

export default MlTaskRun;
