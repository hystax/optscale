import React, { useCallback } from "react";
import { Box, Typography, Link } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { RecommendationModal } from "components/SideModalManager/SideModals";
import RecommendationCard, { Header } from "containers/RecommendationsOverviewContainer/RecommendationCard";
import { ALL_RECOMMENDATIONS } from "containers/RecommendationsOverviewContainer/recommendations/allRecommendations";
import { ACTIVE } from "containers/RecommendationsOverviewContainer/recommendations/BaseRecommendation";
import useStyles from "containers/RecommendationsOverviewContainer/RecommendationsOverview.styles";
import { useOpenSideModal } from "hooks/useOpenSideModal";
import OrganizationOptionsService from "services/OrganizationOptionsService";
import { RECOMMENDATIONS_LIMIT_FILTER } from "utils/constants";
import { isEmpty as isEmptyObject } from "utils/objects";

const MlModelRecommendations = ({ modelId, recommendations, isLoading }) => {
  const { classes } = useStyles();
  const openSideModal = useOpenSideModal();

  const { useGetRecommendationsDownloadOptions } = OrganizationOptionsService();
  const { options: downloadOptions } = useGetRecommendationsDownloadOptions();
  const downloadLimit = downloadOptions?.limit ?? RECOMMENDATIONS_LIMIT_FILTER;

  const onRecommendationClick = useCallback(
    (recommendation) => {
      openSideModal(RecommendationModal, {
        type: recommendation.type,
        titleMessageId: recommendation.title,
        limit: downloadLimit,
        mlModelId: modelId
      });
    },
    [downloadLimit, openSideModal, modelId]
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
    return Object.values(ALL_RECOMMENDATIONS)
      .map((RecommendationClass) => new RecommendationClass(ACTIVE, recommendations))
      .filter(({ count }) => count !== 0)
      .sort(({ count: countA }, { count: countB }) => countB - countA)
      .map((r) => (
        <RecommendationCard
          key={r.type}
          color={r.color}
          header={
            <Header
              recommendationType={r.type}
              color={r.color}
              title={<FormattedMessage id={r.title} />}
              value={r.value}
              valueLabel={r.label}
              subtitle={
                <Link component="button" variant="body2" onClick={() => onRecommendationClick(r)}>
                  {r.count > 0 && <FormattedMessage id="seeAllItems" values={{ value: r.count }} />}
                </Link>
              }
            />
          }
        />
      ));
  };

  return <Box className={classes.cardsGrid}>{getCards()}</Box>;
};

MlModelRecommendations.propTypes = {
  recommendations: PropTypes.object,
  isLoading: PropTypes.bool,
  modelId: PropTypes.string
};

export default MlModelRecommendations;
