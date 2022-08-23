import React, { useState } from "react";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import { GET_CLOUD_ACCOUNTS } from "api/restapi/actionTypes";
import Filters from "components/Filters";
import { RECOMMENDATION_FILTERS } from "components/Filters/constants";
import LinearSelector from "components/LinearSelector";
import { useApiData } from "hooks/useApiData";
import { CLOUD_ACCOUNT_BE_FILTER, CLOUD_ACCOUNT_ID_FILTER } from "utils/constants";
import { updateQueryParams, getQueryParams } from "utils/network";

const RecommendationFilters = ({ applyFilterCallback }) => {
  // TODO: Discuss usage dataSourceId[]=
  const { dataSourceId: queryParamsDataSourceId = [] } = getQueryParams();
  const [appliedFilters, setAppliedFilters] = useState({
    [CLOUD_ACCOUNT_ID_FILTER]: Array.isArray(queryParamsDataSourceId) ? queryParamsDataSourceId : [queryParamsDataSourceId]
  });
  const {
    apiData: { cloudAccounts = [] }
  } = useApiData(GET_CLOUD_ACCOUNTS);

  const recommendationFilters = new Filters({
    filters: RECOMMENDATION_FILTERS,
    filterValues: {
      [CLOUD_ACCOUNT_BE_FILTER]: cloudAccounts.map(({ type, name, id }) => ({ type, name, id }))
    },
    appliedFilters
  });

  const update = (data) => {
    updateQueryParams({ dataSourceId: data });
    applyFilterCallback(data);
  };

  return (
    <LinearSelector
      label={<FormattedMessage id="filters" />}
      value={recommendationFilters.getAppliedValues()}
      items={recommendationFilters.getFilterSelectors()}
      onClear={({ filterValue: value }) => {
        setAppliedFilters((prevState) => {
          const multiCloudAccountId = prevState[CLOUD_ACCOUNT_ID_FILTER].filter((el) => el !== value);
          update(multiCloudAccountId);
          return {
            ...prevState,
            [CLOUD_ACCOUNT_ID_FILTER]: multiCloudAccountId
          };
        });
      }}
      onApply={({ name, value }) => {
        setAppliedFilters((prevState) => {
          update(value);
          return {
            ...prevState,
            [name]: value
          };
        });
      }}
      onClearAll={() => {
        setAppliedFilters((prevState) => {
          update([]);
          return {
            ...prevState,
            [CLOUD_ACCOUNT_ID_FILTER]: []
          };
        });
      }}
    />
  );
};

RecommendationFilters.propTypes = {
  applyFilterCallback: PropTypes.func
};

export default RecommendationFilters;
