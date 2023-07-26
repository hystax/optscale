import React from "react";
import { GET_EVENTS_COUNT } from "api/keeper/actionTypes";
import LatestEvents from "components/LatestEvents";
import { useApiData } from "hooks/useApiData";

const LatestEventsContainer = () => {
  const {
    apiData: { count = 0 }
  } = useApiData(GET_EVENTS_COUNT);

  return <LatestEvents count={count} />;
};

export default LatestEventsContainer;
