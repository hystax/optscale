import React from "react";
import ErrorOutlineOutlinedIcon from "@mui/icons-material/ErrorOutlineOutlined";
import { Box } from "@mui/material";
import Typography from "@mui/material/Typography";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import QuestionMark from "components/QuestionMark";
import { isEmpty } from "utils/arrays";
import Actions from "../Actions";
import RecommendationCard, { ServicesChipsGrid, TableContent, Header } from "../RecommendationCard";
import { usePinnedRecommendations } from "../redux/pinnedRecommendations/hooks";

const useOrderedRecommendations = (recommendations) => {
  const pinnedRecommendations = usePinnedRecommendations();

  const pinnedRecommendationInstances = pinnedRecommendations
    .map((pinnedRecommendationType) =>
      recommendations.find((recommendation) => recommendation.type === pinnedRecommendationType)
    )
    .filter((instance) => instance !== undefined);

  const unpinnedRecommendationInstances = recommendations.filter(
    (recommendation) => !pinnedRecommendations.includes(recommendation.type)
  );

  return [...pinnedRecommendationInstances, ...unpinnedRecommendationInstances];
};

const Cards = ({
  isLoading,
  downloadLimit,
  recommendations,
  onRecommendationClick,
  isDownloadAvailable,
  isGetIsDownloadAvailableLoading,
  selectedDataSources
}) => {
  const orderedRecommendations = useOrderedRecommendations(recommendations);

  if (isLoading) {
    return [
      <RecommendationCard isLoading key={1} />,
      <RecommendationCard isLoading key={2} />,
      <RecommendationCard isLoading key={3} />
    ];
  }

  if (isEmpty(orderedRecommendations)) {
    return (
      <Typography>
        <FormattedMessage id="noRecommendationsFound" />
      </Typography>
    );
  }

  return orderedRecommendations.map((r) => (
    <RecommendationCard
      key={r.type}
      color={r.color}
      header={
        <Header
          recommendationType={r.type}
          color={r.color}
          title={<FormattedMessage id={r.title} />}
          subtitle={<ServicesChipsGrid services={r.services} />}
          value={r.value}
          valueLabel={r.label}
        />
      }
      description={
        <>
          <Typography gutterBottom>
            <FormattedMessage
              id={r.descriptionMessageId}
              values={{ strong: (chunks) => <strong>{chunks}</strong>, ...r.descriptionMessageValues }}
            />
          </Typography>
          {r.hasError && (
            <Box display="flex" alignItems="center">
              <Typography color="error">
                <FormattedMessage id="recommendationError" />
              </Typography>
              <QuestionMark tooltipText={r.error} color="error" Icon={ErrorOutlineOutlinedIcon} />
            </Box>
          )}
        </>
      }
      cta={r.count > 0 && <FormattedMessage id="seeAllItems" values={{ value: r.count }} />}
      onCtaClick={() => onRecommendationClick(r)}
      menu={
        <Actions
          downloadLimit={downloadLimit}
          recommendation={r}
          withMenu
          isDownloadAvailable={isDownloadAvailable}
          isGetIsDownloadAvailableLoading={isGetIsDownloadAvailableLoading}
          selectedDataSources={selectedDataSources}
        />
      }
    >
      <TableContent data={r.previewItems} />
    </RecommendationCard>
  ));
};

Cards.propTypes = {
  isLoading: PropTypes.bool,
  downloadLimit: PropTypes.number,
  recommendations: PropTypes.array,
  onRecommendationClick: PropTypes.func.isRequired,
  isDownloadAvailable: PropTypes.bool,
  isGetIsDownloadAvailableLoading: PropTypes.bool,
  selectedDataSources: PropTypes.array
};

export default Cards;
