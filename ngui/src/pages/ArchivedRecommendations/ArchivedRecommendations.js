import React from "react";
import ArchivedRecommendationsMocked from "components/ArchivedRecommendations/ArchivedRecommendationsMocked";
import { MESSAGE_TYPES } from "components/ContentBackdrop";
import Mocked from "components/Mocked";
import ArchivedRecommendationsContainer from "containers/ArchivedRecommendationsContainer";

const ArchivedRecommendations = () => (
  <Mocked mock={<ArchivedRecommendationsMocked />} backdropMessageType={MESSAGE_TYPES.RECOMMENDATIONS}>
    <ArchivedRecommendationsContainer />
  </Mocked>
);

export default ArchivedRecommendations;
