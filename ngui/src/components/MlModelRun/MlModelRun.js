import React, { useState } from "react";
import { Link, Typography } from "@mui/material";
import Breadcrumbs from "@mui/material/Breadcrumbs";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { useParams, Link as RouterLink } from "react-router-dom";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import TabsWrapper from "components/TabsWrapper";
import { getMlDetailsUrl } from "urls";
import { Executors, Overview } from "./Components";

const TABS = Object.freeze({
  OVERVIEW: "overview",
  EXECUTION: "execution",
  EXECUTORS: "executors"
});

const Tabs = ({ run, isLoading = false }) => {
  const [activeTab, setActiveTab] = useState();

  const tabs = [
    {
      title: TABS.OVERVIEW,
      dataTestId: "tab_overview",
      node: (
        <Overview
          status={run.status}
          cost={run.cost}
          endedAt={run.finish}
          runData={run.data}
          duration={run.duration}
          dataRead={run.data_read}
          dataWritten={run.data_written}
          tasksCPU={run.task_cpu}
          cpuUptime={run.cpu_uptime}
          hostCPU={run.host_cpu}
          processCPU={run.process_cpu}
          hostRAM={run.host_ram}
          processRAM={run.process_ram}
          goals={run.goals}
          tags={run.tags}
          isLoading={isLoading}
          onSeeExecutorsClick={() => setActiveTab(TABS.EXECUTORS)}
        />
      )
    },
    {
      title: TABS.EXECUTORS,
      dataTestId: "tab_executors",
      node: <Executors />
    }
  ];

  return (
    <TabsWrapper
      tabsProps={{
        tabs,
        defaultTab: TABS.OVERVIEW,
        name: "ml-model-run-details",
        activeTab,
        handleChange: (event, value) => {
          setActiveTab(value);
        }
      }}
    />
  );
};

const MlModelRun = ({ run, isLoading = false }) => {
  const { application: { name: applicationName } = {}, name: runName } = run;
  const { modelId: applicationId } = useParams();

  const actionBarDefinition = {
    title: {
      isLoading,
      text: (
        <>
          <FormattedMessage id="runOverview" />
          <Breadcrumbs>
            <Link to={getMlDetailsUrl(applicationId)} component={RouterLink}>
              {applicationName}
            </Link>
            <Typography>{runName}</Typography>
          </Breadcrumbs>
        </>
      )
    }
  };

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Tabs run={run} isLoading={isLoading} />
      </PageContentWrapper>
    </>
  );
};

MlModelRun.propTypes = {
  run: PropTypes.object.isRequired,
  isLoading: PropTypes.bool
};

export default MlModelRun;
