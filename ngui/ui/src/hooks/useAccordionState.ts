import { useState } from "react";
import { getSearchParams, updateSearchParams } from "utils/network";

export const useAccordionsState = (queryParameterName) => {
  const { [queryParameterName]: queryParamAccordionName = "" } = getSearchParams();

  const [expanded, setExpanded] = useState(queryParamAccordionName);

  const isExpanded = (accordionName) => expanded === accordionName;

  const toggleAccordionState = (accordionName) => {
    const isAccordionExpanded = isExpanded(accordionName);

    updateSearchParams({
      [queryParameterName]: isAccordionExpanded ? "" : accordionName,
    });

    setExpanded(isAccordionExpanded ? "" : accordionName);
  };

  return {
    toggleAccordionState,
    isExpanded,
  };
};
