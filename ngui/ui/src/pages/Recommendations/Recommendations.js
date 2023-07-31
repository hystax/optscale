import React from "react";
import CachedOutlinedIcon from "@mui/icons-material/CachedOutlined";
import RestoreOutlinedIcon from "@mui/icons-material/RestoreOutlined";
import Stack from "@mui/material/Stack";
import { GET_DATA_SOURCES } from "api/restapi/actionTypes";
import ActionBar from "components/ActionBar";
import DataSourceMultiSelect from "components/DataSourceMultiSelect";
import Mocked, { MESSAGE_TYPES } from "components/Mocked";
import PageContentWrapper from "components/PageContentWrapper";
import RecommendationsOverviewContainer from "containers/RecommendationsOverviewContainer";
import RecommendationsOverviewContainerMocked from "containers/RecommendationsOverviewContainer/RecommendationsOverviewContainerMocked";
import RecommendationsOverviewService from "containers/RecommendationsOverviewContainer/RecommendationsOverviewService";
import { useApiData } from "hooks/useApiData";
import { useSyncQueryParamWithState } from "hooks/useSyncQueryParamWithState";
import { ARCHIVED_RECOMMENDATIONS } from "urls";
import { AWS_CNR, AZURE_CNR, ALIBABA_CNR, GCP_CNR } from "utils/constants";
import { SPACING_2 } from "utils/layouts";

const DATA_SOURCES_QUERY_NAME = "dataSourceId";
const getActionBar = ({ forceCheck, isForceCheckAvailable }) => ({
  title: {
    messageId: "recommendations",
    dataTestId: "lbl_recommendations"
  },
  items: [
    {
      key: "archive",
      dataTestId: "btn_archive",
      icon: <RestoreOutlinedIcon />,
      messageId: "archive",
      type: "button",
      link: ARCHIVED_RECOMMENDATIONS
    },
    {
      key: "forceCheck",
      type: "button",
      show: isForceCheckAvailable,
      icon: <CachedOutlinedIcon />,
      action: forceCheck,
      dataTestId: "btn_force_check",
      messageId: "forceCheck"
    }
  ]
});

const RECOMMENDABLE_DATA_SOURCES = [AWS_CNR, AZURE_CNR, ALIBABA_CNR, GCP_CNR];

const RecommendationsPage = ({ isMock }) => {
  const {
    apiData: { cloudAccounts = [] }
  } = useApiData(GET_DATA_SOURCES);

  const [selectedDataSources, setSelectedDataSources] = useSyncQueryParamWithState({
    queryParamName: DATA_SOURCES_QUERY_NAME,
    defaultValue: [],
    parameterIsArray: true
  });

  const { forceCheck, isForceCheckAvailable } = RecommendationsOverviewService().useForceCheck();
  const recommendationsActionBar = getActionBar({ forceCheck, isForceCheckAvailable });

  return (
    <>
      <ActionBar data={recommendationsActionBar} />
      <PageContentWrapper>
        <Stack spacing={SPACING_2} sx={{ minHeight: "100%" }}>
          <div>
            <DataSourceMultiSelect
              allDataSources={cloudAccounts.filter((cloudAccount) => RECOMMENDABLE_DATA_SOURCES.includes(cloudAccount.type))}
              dataSourceIds={selectedDataSources}
              onChange={setSelectedDataSources}
            />
          </div>
          <div style={{ minHeight: "100%" }}>
            {isMock ? (
              <RecommendationsOverviewContainerMocked />
            ) : (
              <RecommendationsOverviewContainer isMock={isMock} selectedDataSources={selectedDataSources} />
            )}
          </div>
        </Stack>
      </PageContentWrapper>
    </>
  );
};

const Recommendations = () => (
  <Mocked backdropMessageType={MESSAGE_TYPES.RECOMMENDATIONS} mock={<RecommendationsPage isMock />}>
    <RecommendationsPage />
  </Mocked>
);

export default Recommendations;
