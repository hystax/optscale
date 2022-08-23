import React from "react";
import PropTypes from "prop-types";
import WrapperCard from "components/WrapperCard";
import MetricChart from "../MetricChart";

const MetricCard = ({ title, isLoading, chartProps, dataTestIds = {} }) => (
  <WrapperCard title={title} variant="outlined" dataTestIds={dataTestIds} needAlign>
    <MetricChart isLoading={isLoading} {...chartProps} />
  </WrapperCard>
);

MetricCard.propTypes = {
  title: PropTypes.node.isRequired,
  isLoading: PropTypes.bool,
  chartProps: PropTypes.object,
  dataTestIds: PropTypes.object
};

export default MetricCard;
