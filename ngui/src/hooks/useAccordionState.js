import { useState } from "react";
import { getQueryParams, updateQueryParams } from "utils/network";

export const useAccordionsState = (queryParameterName) => {
  const { [queryParameterName]: queryParamAccordionName = "" } = getQueryParams();

  const [expanded, setExpanded] = useState(queryParamAccordionName);

  const isExpanded = (accordionName) => expanded === accordionName;

  const toggleAccordionState = (accordionName) => {
    const isAccordionExpanded = isExpanded(accordionName);

    updateQueryParams({
      [queryParameterName]: isAccordionExpanded ? "" : accordionName
    });

    setExpanded(isAccordionExpanded ? "" : accordionName);
  };

  return {
    toggleAccordionState,
    isExpanded
  };
};
