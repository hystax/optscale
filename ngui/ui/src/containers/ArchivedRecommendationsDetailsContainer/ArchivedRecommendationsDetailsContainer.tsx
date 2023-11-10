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

  return accordionBreakdown.map(({ archived_at: archivedAt, reason, module, accordionName, count }, index) => (
    <ArchivedRecommendationAccordion
      dataTestId={`sp_archived_recommendation_${index}`}
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

export default ArchivedRecommendationsDetailsContainer;
