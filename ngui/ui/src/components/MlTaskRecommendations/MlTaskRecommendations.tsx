import { useCallback } from "react";
import { Box, Typography } from "@mui/material";
import { FormattedMessage } from "react-intl";
import { RecommendationModal } from "components/SideModalManager/SideModals";
import Cards from "containers/RecommendationsOverviewContainer/Cards";
import RecommendationCard from "containers/RecommendationsOverviewContainer/RecommendationCard";
import { ALL_RECOMMENDATIONS } from "containers/RecommendationsOverviewContainer/recommendations/allRecommendations";
import { ACTIVE } from "containers/RecommendationsOverviewContainer/recommendations/BaseRecommendation";
import useStyles from "containers/RecommendationsOverviewContainer/RecommendationsOverview.styles";
import { useGetIsRecommendationsDownloadAvailable } from "hooks/useGetIsRecommendationsDownloadAvailable";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import OrganizationOptionsService from "services/OrganizationOptionsService";
import { RECOMMENDATIONS_LIMIT_FILTER } from "utils/constants";
import { isEmpty as isEmptyObject } from "utils/objects";

const MlTaskRecommendations = ({ taskId, recommendations, isLoading }) => {
  const { classes } = useStyles();
  const openSideModal = useOpenSideModal();

  const { useGetRecommendationsDownloadOptions } = OrganizationOptionsService();
  const { options: downloadOptions } = useGetRecommendationsDownloadOptions();
  const downloadLimit = downloadOptions?.limit ?? RECOMMENDATIONS_LIMIT_FILTER;
  const { isLoading: isGetIsDownloadAvailableLoading, isDownloadAvailable } = useGetIsRecommendationsDownloadAvailable();

  const onRecommendationClick = useCallback(
    (recommendation) => {
      openSideModal(RecommendationModal, {
        type: recommendation.type,
        titleMessageId: recommendation.title,
        limit: downloadLimit,
        mlTaskId: taskId
      });
    },
    [downloadLimit, openSideModal, taskId]
  );

  const getCards = () => {
    if (isLoading) {
      return [
        <RecommendationCard key={1} isLoading={isLoading} />,
        <RecommendationCard key={2} isLoading={isLoading} />,
        <RecommendationCard key={3} isLoading={isLoading} />
      ];
    }

    if (isEmptyObject(recommendations)) {
      return (
        <Typography>
          <FormattedMessage id="noRecommendations" />
        </Typography>
      );
    }

    if (!recommendations?.total_count) {
      return (
        <Typography>
          <FormattedMessage id="noActiveRecommendationsAvailable" />
        </Typography>
      );
    }

    const recommendationsInstances = Object.values(ALL_RECOMMENDATIONS)
      .map((RecommendationClass) => new RecommendationClass(ACTIVE, recommendations))
      .filter(({ count }) => count !== 0)
      .sort(({ count: countA }, { count: countB }) => countB - countA);

    // TODO: that should be unified with RecommendationsOverview

    return (
      <Cards
        recommendations={recommendationsInstances}
        isLoading={false}
        downloadLimit={downloadLimit}
        onRecommendationClick={onRecommendationClick}
        isDownloadAvailable={isDownloadAvailable}
        isGetIsDownloadAvailableLoading={isGetIsDownloadAvailableLoading}
        selectedDataSources={[]}
      />
    );
  };

  return <Box className={classes.cardsGrid}>{getCards()}</Box>;
};

export default MlTaskRecommendations;
