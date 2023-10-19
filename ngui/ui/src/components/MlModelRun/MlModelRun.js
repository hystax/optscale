import React, { useState } from "react";
import RefreshOutlinedIcon from "@mui/icons-material/RefreshOutlined";
import { Link, Typography } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import { GET_ML_EXECUTORS, GET_ML_RUN_DETAILS, GET_ML_RUN_DETAILS_BREAKDOWN } from "api/restapi/actionTypes";
import ActionBar from "components/ActionBar";
import PageContentWrapper from "components/PageContentWrapper";
import TabsWrapper from "components/TabsWrapper";
import { useRefetchApis } from "hooks/useRefetchApis";
import { ML_MODELS, getMlModelDetailsUrl } from "urls";
import { formatRunFullName } from "utils/ml";
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
          duration={run.duration}
          cost={run.cost}
          reachedGoals={run.reached_goals}
          tags={run.tags}
          isLoading={isLoading}
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
  const { application: { id: modelId, name: modelName } = {}, name: runName, number } = run;

  const refetch = useRefetchApis();

  const actionBarDefinition = {
    breadcrumbs: [
      <Link key={1} to={ML_MODELS} component={RouterLink}>
        <FormattedMessage id="models" />
      </Link>,
      <Link key={2} to={getMlModelDetailsUrl(modelId)} component={RouterLink}>
        {modelName}
      </Link>,
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
        action: () => refetch([GET_ML_RUN_DETAILS, GET_ML_EXECUTORS, GET_ML_RUN_DETAILS_BREAKDOWN])
      }
    ]
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
