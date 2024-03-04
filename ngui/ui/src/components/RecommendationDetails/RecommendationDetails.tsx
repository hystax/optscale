import { useEffect } from "react";
import { Box, CircularProgress, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import TabsWrapper from "components/TabsWrapper";
import { ACTIVE, DISMISSED, EXCLUDED } from "containers/RecommendationsOverviewContainer/recommendations/BaseRecommendation";
import MlModelsService from "services/MlModelsService";
import { removeQueryParam } from "utils/network";
import Details from "./Details";
import RecommendationDetailsService from "./RecommendationDetailsService";
import SelectedCloudAccounts from "./SelectedCloudAccounts";

const QUERY_TAB_NAME = "recommendationDetailsTab";

const Recommendations = ({ isLoading, type, limit, data, status, dataSourceIds, withDownload }) => {
  if (isLoading) {
    return (
      <Box display="flex" justifyContent="center">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Details type={type} limit={limit} data={data} status={status} dataSourceIds={dataSourceIds} withDownload={withDownload} />
  );
};

const RecommendationsContainer = ({ type, limit, status, dataSourceIds }) => {
  const { useGetOptimizations } = RecommendationDetailsService();
  const { isLoading, data } = useGetOptimizations({ type, limit, status, cloudAccountIds: dataSourceIds });

  return (
    <Recommendations
      type={type}
      limit={limit}
      data={data}
      status={status}
      isLoading={isLoading}
      dataSourceIds={dataSourceIds}
      withDownload
    />
  );
};

const MlRecommendationsContainer = ({ taskId, type, limit, status }) => {
  const { useGetModelRecommendation } = MlModelsService();
  const { isLoading, data } = useGetModelRecommendation({ taskId, type, status });

  return <Recommendations type={type} limit={limit} data={data} status={status} isLoading={isLoading} />;
};

const RecommendationDetails = ({
  type,
  dataSourceIds = [],
  limit = 100,
  mlModelId,
  dismissable = false,
  withExclusions = false
}) => {
  useEffect(
    () => () => {
      removeQueryParam(QUERY_TAB_NAME);
    },
    []
  );

  const tabs = [ACTIVE, dismissable ? DISMISSED : false, withExclusions ? EXCLUDED : false].filter(Boolean).map((name) => ({
    title: name,
    node: mlModelId ? (
      <MlRecommendationsContainer type={type} limit={limit} status={name} taskId={mlModelId} />
    ) : (
      <RecommendationsContainer type={type} dataSourceIds={dataSourceIds} limit={limit} status={name} />
    )
  }));

  return (
    <>
      {dataSourceIds.length !== 0 && (
        <Typography>
          <FormattedMessage id="displayingRecommendationsFor" />
          <SelectedCloudAccounts cloudAccountIds={dataSourceIds} />
        </Typography>
      )}
      <TabsWrapper
        tabsProps={{
          queryTabName: QUERY_TAB_NAME,
          tabs,
          defaultTab: ACTIVE,
          name: "recommendations-data"
        }}
      />
    </>
  );
};

export default RecommendationDetails;
