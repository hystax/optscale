import React from "react";
import { FormattedMessage } from "react-intl";
import useChartPropsByMetricType from "components/ResourceMetrics/utils/getChartPropsByMetricType";
import getTitleMessageIdByMetricType from "components/ResourceMetrics/utils/getTitleMessageIdByMetricType";

const useMetric = (type, metrics) => {
  const chartProps = useChartPropsByMetricType(type, metrics);

  return {
    type,
    title: <FormattedMessage id={getTitleMessageIdByMetricType(type)} />,
    chartProps,
    cardDataTestIds: {
      wrapper: `block_${type}`
    }
  };
};

export default useMetric;
