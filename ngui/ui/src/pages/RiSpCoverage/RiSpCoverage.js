import React from "react";
import { Link } from "@mui/material";
import FormControl from "@mui/material/FormControl";
import Stack from "@mui/material/Stack";
import { FormattedMessage } from "react-intl";
import { Link as RouterLink } from "react-router-dom";
import { GET_DATA_SOURCES } from "api/restapi/actionTypes";
import ActionBar from "components/ActionBar";
import DataSourceMultiSelect from "components/DataSourceMultiSelect";
import { getBasicRangesSet } from "components/DateRangePicker/defaults";
import PageContentWrapper from "components/PageContentWrapper";
import RangePickerFormContainer from "containers/RangePickerFormContainer";
import RiSpCoverageContainer from "containers/RiSpCoverageContainer";
import { useApiData } from "hooks/useApiData";
import { useReactiveDefaultDateRange } from "hooks/useReactiveDefaultDateRange";
import { useSyncQueryParamWithState } from "hooks/useSyncQueryParamWithState";
import { RECOMMENDATIONS, RI_SP_QUERY_PARAMETERS } from "urls";
import { AWS_CNR, DATE_RANGE_TYPE } from "utils/constants";
import { SPACING_2 } from "utils/layouts";

const actionBarDefinition = {
  breadcrumbs: [
    <Link key={1} to={RECOMMENDATIONS} component={RouterLink}>
      <FormattedMessage id="recommendations" />
    </Link>
  ],
  title: {
    messageId: "riSpCoverageTitle"
  }
};
const TARGET_DATA_SOURCES_TYPES = [AWS_CNR];

const RiSpCoverage = () => {
  const {
    apiData: { cloudAccounts = [] }
  } = useApiData(GET_DATA_SOURCES);

  const [selectedDataSourceIds, setSelectedDataSources] = useSyncQueryParamWithState({
    queryParamName: RI_SP_QUERY_PARAMETERS.DATA_SOURCE_ID,
    defaultValue: [],
    parameterIsArray: true
  });

  const [startDateTimestamp, endDateTimestamp] = useReactiveDefaultDateRange(DATE_RANGE_TYPE.EXPENSES);

  const [selectedStartDate, setSelectedStartDate] = useSyncQueryParamWithState({
    queryParamName: RI_SP_QUERY_PARAMETERS.START_DATE,
    defaultValue: startDateTimestamp
  });

  const [selectedEndDate, setSelectedEndDate] = useSyncQueryParamWithState({
    queryParamName: RI_SP_QUERY_PARAMETERS.END_DATE,
    defaultValue: endDateTimestamp
  });

  const onApply = ({ startDate, endDate }) => {
    setSelectedStartDate(startDate);
    setSelectedEndDate(endDate);
  };

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Stack spacing={SPACING_2}>
          <Stack direction="row" spacing={SPACING_2}>
            <div>
              <DataSourceMultiSelect
                allDataSources={cloudAccounts.filter((cloudAccount) => TARGET_DATA_SOURCES_TYPES.includes(cloudAccount.type))}
                dataSourceIds={selectedDataSourceIds}
                onChange={setSelectedDataSources}
              />
            </div>
            <div>
              {/* TODO: migrate FormControl into RangePickerFormContainer to avoid misalignment and additional styles */}
              <FormControl>
                <RangePickerFormContainer
                  onApply={onApply}
                  initialStartDateValue={selectedStartDate}
                  initialEndDateValue={selectedEndDate}
                  rangeType="expenses"
                  selectedEndDate
                  definedRanges={getBasicRangesSet()}
                />
              </FormControl>
            </div>
          </Stack>
          <div>
            <RiSpCoverageContainer
              startDate={selectedStartDate}
              endDate={selectedEndDate}
              dataSourceIds={selectedDataSourceIds}
            />
          </div>
        </Stack>
      </PageContentWrapper>
    </>
  );
};

export default RiSpCoverage;
