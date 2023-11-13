import ArchivedResourcesCountBarChart from "components/ArchivedResourcesCountBarChart";
import BarChartLoader from "components/BarChartLoader";

const ArchivedRecommendationsBreakdownContainer = ({ isLoading, breakdown, onBarChartSelect }) =>
  isLoading ? <BarChartLoader /> : <ArchivedResourcesCountBarChart onSelect={onBarChartSelect} breakdown={breakdown} />;

export default ArchivedRecommendationsBreakdownContainer;
