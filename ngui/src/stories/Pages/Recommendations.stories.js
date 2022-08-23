import React from "react";
import { RelevantRecommendationsMocked } from "components/RelevantRecommendations";
import { KINDS } from "stories";

export default {
  title: `${KINDS.PAGES}/Recommendations`
};

export const basic = () => <RelevantRecommendationsMocked />;
