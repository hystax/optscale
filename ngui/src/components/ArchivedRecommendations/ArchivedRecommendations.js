import React from "react";
import { Grid, Typography } from "@mui/material";
import PropTypes from "prop-types";
import { FormattedMessage } from "react-intl";
import ActionBar from "components/ActionBar";
import { getBasicRangesSet } from "components/DateRangePicker/defaults";
import PageContentWrapper from "components/PageContentWrapper";
import PanelLoader from "components/PanelLoader";
import WrapperCard from "components/WrapperCard";
import ArchivedRecommendationsBreakdownContainer from "containers/ArchivedRecommendationsBreakdownContainer";
import ArchivedRecommendationsDetailsContainer from "containers/ArchivedRecommendationsDetailsContainer";
import RangePickerFormContainer from "containers/RangePickerFormContainer";
import { isEmpty as isEmptyArray } from "utils/arrays";
import { DATE_RANGE_TYPE } from "utils/constants";
import { SPACING_2 } from "utils/layouts";

const ArchivedRecommendations = ({
  onBarChartSelect,
  onTimeRangeChange,
  dateRange,
  archivedRecommendationsChartBreakdown,
  archivedRecommendationsBreakdown,
  isChartLoading = false,
  isLoading = false
}) => {
  const renderArchivedRecommendationsDetails = () => {
    if (isLoading) {
      return <PanelLoader />;
    }
    if (isEmptyArray(archivedRecommendationsBreakdown)) {
      return (
        <Typography align="center">
          <FormattedMessage id="noRecommendations" />
        </Typography>
      );
    }
    return <ArchivedRecommendationsDetailsContainer archivedRecommendationsBreakdown={archivedRecommendationsBreakdown} />;
  };

  const actionBarDefinition = {
    title: {
      messageId: "archivedRecommendations",
      dataTestId: "lbl_archived_recommendations"
    }
  };

  return (
    <>
      <ActionBar data={actionBarDefinition} />
      <PageContentWrapper>
        <Grid container spacing={SPACING_2}>
          <Grid item xs={12} sx={{ display: "flex", justifyContent: "flex-end" }}>
            <RangePickerFormContainer
              onApply={onTimeRangeChange}
              initialStartDateValue={dateRange.startDate}
              initialEndDateValue={dateRange.endDate}
              rangeType={DATE_RANGE_TYPE.ARCHIVED_RECOMMENDATIONS}
              definedRanges={getBasicRangesSet()}
            />
          </Grid>
          <Grid item xs={12}>
            <WrapperCard>
              <ArchivedRecommendationsBreakdownContainer
                isLoading={isChartLoading}
                onBarChartSelect={onBarChartSelect}
                breakdown={archivedRecommendationsChartBreakdown}
              />
            </WrapperCard>
          </Grid>
          <Grid item xs={12}>
            <WrapperCard>{renderArchivedRecommendationsDetails()}</WrapperCard>
          </Grid>
        </Grid>
      </PageContentWrapper>
    </>
  );
};

ArchivedRecommendations.propTypes = {
  onTimeRangeChange: PropTypes.func.isRequired,
  dateRange: PropTypes.shape({
    startDate: PropTypes.number,
    endDate: PropTypes.number
  }).isRequired,
  archivedRecommendationsChartBreakdown: PropTypes.object.isRequired,
  archivedRecommendationsBreakdown: PropTypes.array.isRequired,
  onBarChartSelect: PropTypes.func.isRequired,
  isChartLoading: PropTypes.bool,
  isLoading: PropTypes.bool
};

export default ArchivedRecommendations;
