import React from "react";
import PropTypes from "prop-types";
import Breakdown from "./Breakdown";
import Layout from "./Layout";

const RunsBreakdowns = ({ runs, isLoading }) => {
  if (isLoading) {
    return <Layout isLoading />;
  }

  return <Breakdown runs={runs} />;
};

const runShape = PropTypes.shape({
  name: PropTypes.string.isRequired,
  number: PropTypes.number.isRequired,
  duration: PropTypes.number.isRequired,
  cost: PropTypes.number.isRequired,
  data: PropTypes.object,
  goals: PropTypes.array
});

RunsBreakdowns.propTypes = {
  runs: PropTypes.arrayOf(runShape).isRequired,
  isLoading: PropTypes.bool
};

export default RunsBreakdowns;
