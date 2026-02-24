import { useEffect } from "react";
import { Box, CircularProgress, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import TabsWrapper from "components/TabsWrapper";
import { STATUS } from "containers/RecommendationsOverviewContainer/recommendations/BaseRecommendation";
import MlTasksService from "services/MlTasksService";
import { removeSearchParam } from "utils/network";
import Details from "./Details";
import RecommendationDetailsService from "./RecommendationDetailsService";
import SelectedCloudAccounts from "./SelectedCloudAccounts";
import type {
  RecommendationsProps,
  RecommendationsContainerProps,
  MlRecommendationsContainerProps,
  RecommendationDetailsProps,
} from "./types";

const QUERY_TAB_NAME = "recommendationDetailsTab";

const Recommendations = ({ isLoading, type, limit, data, status, dataSourceIds, withDownload }: RecommendationsProps) => {
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

const RecommendationsContainer = ({ type, limit, status, dataSourceIds }: RecommendationsContainerProps) => {
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

const MlRecommendationsContainer = ({ taskId, type, limit, status }: MlRecommendationsContainerProps) => {
  const { useGetTaskRecommendation } = MlTasksService();
  const { isLoading, data } = useGetTaskRecommendation({ taskId, type, status });

  return <Recommendations type={type} limit={limit} data={data} status={status} isLoading={isLoading} />;
};

const RecommendationDetails = ({
  type,
  dataSourceIds = [],
  limit,
  mlTaskId,
  dismissible = false,
  withExclusions = false,
}: RecommendationDetailsProps) => {
  useEffect(
    () => () => {
      removeSearchParam(QUERY_TAB_NAME);
    },
    []
  );

  const tabs = [STATUS.ACTIVE, dismissible ? STATUS.DISMISSED : false, withExclusions ? STATUS.EXCLUDED : false]
    .filter(Boolean)
    .map((name) => ({
      title: name,
      node: mlTaskId ? (
        <MlRecommendationsContainer type={type} limit={limit} status={name} taskId={mlTaskId} />
      ) : (
        <RecommendationsContainer type={type} dataSourceIds={dataSourceIds} limit={limit} status={name} />
      ),
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
          defaultTab: STATUS.ACTIVE,
          name: "recommendations-data",
        }}
      />
    </>
  );
};

export default RecommendationDetails;
