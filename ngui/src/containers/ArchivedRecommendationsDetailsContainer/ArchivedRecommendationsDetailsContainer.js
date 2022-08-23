import React from "react";
import PropTypes from "prop-types";
import ArchivedRecommendationAccordion from "components/ArchivedRecommendationAccordion";
import { useAccordionsState } from "hooks/useAccordionState";

const ARCHIVED_RECOMMENDATIONS = "archivedRecommendation";

const ArchivedRecommendationsDetailsContainer = ({ archivedRecommendationsBreakdown = [] }) => {
  const accordionBreakdown = archivedRecommendationsBreakdown.map((data) => ({
    ...data,
    accordionName: `${data.module}-${data.reason}-${data.archived_at}`
  }));

  const { toggleAccordionState, isExpanded } = useAccordionsState(ARCHIVED_RECOMMENDATIONS);

  const handleAccordionsChange = (accordionName) => () => {
    toggleAccordionState(accordionName);
  };

  return accordionBreakdown.map(({ archived_at: archivedAt, reason, module, accordionName, count }) => (
    <ArchivedRecommendationAccordion
      key={accordionName}
      recommendationType={module}
      reason={reason}
      count={count}
      archivedAt={archivedAt}
      isExpanded={isExpanded(accordionName)}
      onChange={handleAccordionsChange(accordionName)}
    />
  ));
};

ArchivedRecommendationsDetailsContainer.propTypes = {
  archivedRecommendationsBreakdown: PropTypes.array
};

export default ArchivedRecommendationsDetailsContainer;
