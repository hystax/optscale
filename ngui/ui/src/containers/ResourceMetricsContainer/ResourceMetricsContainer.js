import React, { useEffect, useState } from "react";
import { Grid } from "@mui/material";
import PropTypes from "prop-types";
import { useDispatch } from "react-redux";
import { getResourceMetrics } from "api";
import { GET_RESOURCE_METRICS } from "api/restapi/actionTypes";
import { getBasicRangesSet } from "components/DateRangePicker/defaults";
import ResourceMetrics from "components/ResourceMetrics";
import RangePickerFormContainer from "containers/RangePickerFormContainer";
import { useApiData } from "hooks/useApiData";
import { useApiState } from "hooks/useApiState";
import { useResourceDetailsDefaultDateRange } from "hooks/useResourceDetailsDefaultDateRange";
import { DATE_RANGE_TYPE } from "utils/constants";
import {
  getTime,
  startOfDay,
  endOfDay,
  secondsToMilliseconds,
  millisecondsToSeconds,
  performDateTimeFunction
} from "utils/datetime";
import { updateQueryParams } from "utils/network";

const ResourceMetricsContainer = ({ resourceId, lastSeen, firstSeen }) => {
  const dispatch = useDispatch();

  const { apiData: metrics } = useApiData(GET_RESOURCE_METRICS);

  const firstSeenStartOfDay = millisecondsToSeconds(
    performDateTimeFunction(startOfDay, true, secondsToMilliseconds(firstSeen))
  );
  const lastSeenEndOfDay = millisecondsToSeconds(performDateTimeFunction(endOfDay, true, secondsToMilliseconds(lastSeen)));

  const [startDateTimestamp, endDateTimestamp] = useResourceDetailsDefaultDateRange({
    lastSeenEndOfDay,
    firstSeenStartOfDay
  });

  const [requestParams, setRequestParams] = useState({
    startDate: startDateTimestamp,
    endDate: endDateTimestamp
  });

  const { shouldInvoke, isLoading } = useApiState(GET_RESOURCE_METRICS, { ...requestParams, resourceId });

  useEffect(() => {
    updateQueryParams({
      startDate: requestParams.startDate,
      endDate: requestParams.endDate
    });
  }, [requestParams.startDate, requestParams.endDate]);

  const applyFilter = ({ startDate, endDate }) => {
    const params = {
      ...requestParams,
      startDate,
      endDate
    };
    setRequestParams(params);
  };

  useEffect(() => {
    if (shouldInvoke) {
      dispatch(getResourceMetrics(resourceId, requestParams));
    }
  }, [dispatch, shouldInvoke, resourceId, requestParams]);

  return (
    <Grid container spacing={2}>
      <Grid item xs={12}>
        <RangePickerFormContainer
          initialStartDateValue={startDateTimestamp}
          initialEndDateValue={endDateTimestamp}
          onApply={applyFilter}
          definedRanges={getBasicRangesSet()}
          rangeType={DATE_RANGE_TYPE.RESOURCES}
          maxDate={getTime(endOfDay(secondsToMilliseconds(lastSeen)))}
        />
      </Grid>
      <Grid item xs={12}>
        <ResourceMetrics isLoading={isLoading} metrics={metrics} />
      </Grid>
    </Grid>
  );
};

ResourceMetricsContainer.propTypes = {
  resourceId: PropTypes.string.isRequired,
  firstSeen: PropTypes.number,
  lastSeen: PropTypes.number
};

export default ResourceMetricsContainer;
