import { useState } from "react";
import { getQueryParams, updateQueryParams } from "utils/network";

export const useSyncQueryParamWithState = (queryParamName, defaultValue = "") => {
  const [state, setState] = useState(() => {
    const { [queryParamName]: queryParamValue = defaultValue } = getQueryParams();

    return queryParamValue;
  });

  const onChange = (newStateValue) => {
    setState(newStateValue);
    updateQueryParams({
      [queryParamName]: newStateValue
    });
  };

  return [state, onChange];
};
