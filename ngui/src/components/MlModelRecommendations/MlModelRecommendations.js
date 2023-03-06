import React from "react";
import { Box } from "@mui/material";
import PropTypes from "prop-types";
import RecommendationCard from "components/RecommendationCard";
import { getRecommendationInstanceByModuleName } from "./Recommendations";

const MlModelRecommendations = ({ recommendations, isLoading }) => {
  const cards = Object.entries(recommendations)
    .sort(([, { items = [] }], [, { items: items2 = [] }]) => (items2.length === 0 && items.length !== 0 ? -1 : 0))
    .map(([recommendationType, { count, saving, items }]) => {
      const recommendationInstance = getRecommendationInstanceByModuleName(recommendationType);

      if (!recommendationInstance) {
        return null;
      }

      const buildedRecommendation = recommendationInstance.build(recommendations);

      return (
        <RecommendationCard
          key={recommendationType}
          items={items}
          saving={saving}
          count={count}
          isLoading={isLoading}
          recommendationInstance={recommendationInstance}
          buildedRecommendation={buildedRecommendation}
        />
      );
    });

  return (
    <Box
      sx={{
        display: "grid",
        gridTemplateColumns: {
          xs: "100%",
          sm: "repeat(auto-fit, minmax(380px, 1fr))"
        },
        gap: 1
      }}
    >
      {cards}
    </Box>
  );
};

MlModelRecommendations.propTypes = {
  recommendations: PropTypes.object,
  isLoading: PropTypes.bool
};

export default MlModelRecommendations;
