import React from "react";
import PropTypes from "prop-types";
import ArchivedResourcesCountBarChart from "components/ArchivedResourcesCountBarChart";
import BarChartLoader from "components/BarChartLoader";

const ArchivedRecommendationsBreakdownContainer = ({ isLoading, breakdown, onBarChartSelect }) =>
  isLoading ? <BarChartLoader /> : <ArchivedResourcesCountBarChart onSelect={onBarChartSelect} breakdown={breakdown} />;

ArchivedRecommendationsBreakdownContainer.propTypes = {
  breakdown: PropTypes.object.isRequired,
  onBarChartSelect: PropTypes.func.isRequired,
  isLoading: PropTypes.bool
};

export default ArchivedRecommendationsBreakdownContainer;
